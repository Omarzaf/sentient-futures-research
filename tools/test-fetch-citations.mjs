import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';

// Every child receives an in-process fetch replacement and socket/DNS guards.
// Fixture directories are retained under the system temporary directory for review.
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const script = fs.readFileSync(path.join(root, 'tools/fetch-citations.mjs'));
const temporaryRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'sf-citation-fetch-fixtures-'));
const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const fixtureText = 'A bounded source account retains its exact words, provenance and unresolved interpretation. '.repeat(5);
const source = (id = 'A', extra = {}) => ({id, key: id, aliases: [], url: `https://sources.example.org/${id}`, ...extra});
const fixtureBody = (body = fixtureText, contentType = 'text/plain; charset=utf-8') => ({
  status: 200, headers: {'content-type': contentType}, body_base64: Buffer.from(body).toString('base64'),
});
const preload = `
import fs from 'node:fs';
import net from 'node:net';
import tls from 'node:tls';
import http from 'node:http';
import https from 'node:https';
import dns from 'node:dns';
import dgram from 'node:dgram';
import {syncBuiltinESMExports} from 'node:module';
const fixture=JSON.parse(fs.readFileSync(process.env.CITATION_FIXTURE_CONFIG,'utf8'));
fs.writeFileSync(fixture.preload_marker,'installed');
const deny=(...args)=>{fs.appendFileSync(fixture.network_attempts,'blocked network attempt\\n');throw Error('Real network disabled by offline citation fixture');};
net.connect=deny;net.createConnection=deny;net.Socket.prototype.connect=deny;
tls.connect=deny;http.request=deny;http.get=deny;https.request=deny;https.get=deny;
dgram.createSocket=deny;
for(const name of ['lookup','lookupService','resolve','resolve4','resolve6','resolveAny','resolveCname','resolveMx','resolveNaptr','resolveNs','resolvePtr','resolveSoa','resolveSrv','resolveTxt','reverse']){
 if(typeof dns[name]==='function')dns[name]=deny;
 if(typeof dns.promises[name]==='function')dns.promises[name]=deny;
}
syncBuiltinESMExports();
globalThis.fetch=async (url,options)=>{
 fs.appendFileSync(fixture.requests,JSON.stringify({url:String(url),redirect:options?.redirect})+'\\n');
 if(fixture.mutate_input)fs.writeFileSync(fixture.input,JSON.stringify([{id:'CHANGED',url:'https://sources.example.org/changed'}]));
 const response=fixture.routes[String(url)];
 if(!response)throw Error('No mocked response for requested source');
 if(response.throw_message)throw new TypeError(response.throw_message,{cause:{code:'OFFLINE_FIXTURE_FAILURE'}});
 return new Response(response.body_base64===null?null:Buffer.from(response.body_base64??'','base64'),{status:response.status,headers:response.headers});
};
`;

let fixtureCount = 0;
let fakeRequests = 0;
let realNetworkAttempts = 0;
const results = [];

function runFixture(rows, options = {}) {
  const directory = path.join(temporaryRoot, String(++fixtureCount).padStart(2, '0'));
  fs.mkdirSync(path.join(directory, 'tools'), {recursive: true});
  fs.writeFileSync(path.join(directory, 'tools/fetch-citations.mjs'), script);
  fs.writeFileSync(path.join(directory, 'mock-fetch.mjs'), preload);
  const input = path.join(directory, 'input.json');
  const inputBytes = Buffer.from(`${JSON.stringify(rows, null, 2)}\n`);
  fs.writeFileSync(input, inputBytes);
  const routes = options.routes ?? Object.fromEntries(rows.map(row => [row.url, fixtureBody()]));
  const config = {
    input, routes, mutate_input: options.mutateInput ?? false,
    requests: path.join(directory, 'requests.jsonl'),
    network_attempts: path.join(directory, 'network-attempts.txt'),
    preload_marker: path.join(directory, 'preload-marker.txt'),
  };
  const configPath = path.join(directory, 'fixture.json');
  fs.writeFileSync(configPath, JSON.stringify(config));
  const args = ['--import', path.join(directory, 'mock-fetch.mjs'), path.join(directory, 'tools/fetch-citations.mjs'),
    '--input', 'input.json', '--run', 'fixture', ...(options.args ?? [])];
  const result = spawnSync(process.execPath, args, {
    cwd: directory, encoding: 'utf8', timeout: 15000, maxBuffer: 1024 * 1024,
    env: {...process.env, NODE_OPTIONS: '', CITATION_FIXTURE_CONFIG: configPath},
  });
  assert.equal(fs.readFileSync(config.preload_marker, 'utf8'), 'installed', 'Offline preload must be installed.');
  const blockedAttempts = fs.existsSync(config.network_attempts)
    ? fs.readFileSync(config.network_attempts, 'utf8').trim().split('\n').filter(Boolean).length : 0;
  realNetworkAttempts += blockedAttempts;
  assert.equal(blockedAttempts, 0, 'The capture tool attempted real network access.');
  assert.equal(result.error, undefined, `Fixture child failed: ${result.error?.message}`);
  const requests = fs.existsSync(config.requests)
    ? fs.readFileSync(config.requests, 'utf8').trim().split('\n').filter(Boolean).map(line => JSON.parse(line)) : [];
  fakeRequests += requests.length;
  const output = path.join(directory, 'working/citations/fixture');
  const manifestPath = path.join(output, 'manifest.json');
  const manifest = fs.existsSync(manifestPath) ? JSON.parse(fs.readFileSync(manifestPath, 'utf8')) : null;
  if (manifest) {
    assert.equal(manifest.count, manifest.receipts.length);
    for (const receipt of manifest.receipts) assert.equal(receipt.audit_verdict, 'pending', 'Retrieval cannot verify a citation.');
  }
  return {directory, output, input, inputBytes, result, requests, manifest};
}

function rejectedBeforeCapture(fixture, pattern) {
  assert.notEqual(fixture.result.status, 0, 'Invalid input must fail.');
  assert.match(fixture.result.stderr, pattern);
  assert.equal(fs.existsSync(fixture.output), false, 'Preflight failure must precede capture-directory creation.');
  assert.equal(fixture.requests.length, 0, 'Preflight failure must precede all requests.');
}

function successfulRun(fixture) {
  assert.equal(fixture.result.status, 0, fixture.result.stderr);
  assert.ok(fixture.manifest, 'A completed capture attempt needs a manifest.');
  assert.equal(fixture.manifest.input_sha256, sha(fixture.inputBytes));
  const snapshot = fs.readFileSync(path.join(fixture.output, 'input-snapshot.json'));
  assert.deepEqual(snapshot, fixture.inputBytes);
  assert.equal(fixture.manifest.selected_rows_sha256, sha(fs.readFileSync(path.join(fixture.output, 'selected-rows.json'))));
  return fixture.manifest.receipts;
}

function test(name, action) {
  try { action(); results.push({name, status: 'PASS'}); }
  catch (error) { results.push({name, status: 'FAIL', error: error.message}); }
}

test('Stored raw bytes and text round-trip their receipt hashes without verification', () => {
  const fixture = runFixture([source()]);
  const [receipt] = successfulRun(fixture);
  const bytes = fs.readFileSync(path.join(fixture.output, 'A.bin'));
  assert.deepEqual(bytes, Buffer.from(fixtureText));
  assert.equal(receipt.bytes, bytes.length);
  assert.equal(receipt.sha256, sha(bytes));
  assert.equal(receipt.text_sha256, sha(fs.readFileSync(path.join(fixture.output, 'A.txt'))));
  assert.equal(receipt.capture_status, 'retrieved_candidate');
  assert.equal(fixture.requests.length, 1);
});

test('Alias selection preserves canonical identity and the original full input snapshot', () => {
  const rows = [source('A', {aliases: ['OLD-A']}), source('B')];
  const fixture = runFixture(rows, {args: ['--keys', 'OLD-A']});
  const [receipt] = successfulRun(fixture);
  assert.equal(receipt.key, 'A');
  assert.deepEqual(receipt.aliases, ['OLD-A']);
  assert.equal(fixture.requests.length, 1);
  assert.deepEqual(JSON.parse(fs.readFileSync(path.join(fixture.output, 'selected-rows.json'))), [rows[0]]);
});

test('Duplicate canonical keys fail before directory creation', () => {
  rejectedBeforeCapture(runFixture([source(), source('A', {url: 'https://sources.example.org/other'})]), /Duplicate|ambiguous/i);
});

test('Unsafe canonical keys fail before directory creation', () => {
  rejectedBeforeCapture(runFixture([source('../outside')]), /Unsafe source key/i);
});

test('Alias and canonical-key collisions fail before directory creation', () => {
  rejectedBeforeCapture(runFixture([source('A', {aliases: ['B']}), source('B')]), /Duplicate|ambiguous/i);
});

test('Unknown requested keys fail instead of silently reducing the batch', () => {
  rejectedBeforeCapture(runFixture([source()], {args: ['--keys', 'A,MISSING']}), /Unknown requested key/i);
});

test('Input mutation during a request cannot change the recorded input identity', () => {
  const row = source();
  const fixture = runFixture([row], {mutateInput: true});
  const [receipt] = successfulRun(fixture);
  assert.equal(receipt.key, 'A');
  assert.notEqual(sha(fs.readFileSync(fixture.input)), fixture.manifest.input_sha256);
  assert.deepEqual(JSON.parse(fs.readFileSync(path.join(fixture.output, 'selected-rows.json'))), [row]);
});

test('Plain text retains angle-bracket and entity-like text exactly', () => {
  const body = `Literal <cultured> and &amp; wording. ${fixtureText}`;
  const fixture = runFixture([source()], {routes: {'https://sources.example.org/A': fixtureBody(body)}});
  successfulRun(fixture);
  assert.equal(fs.readFileSync(path.join(fixture.output, 'A.txt'), 'utf8'), body);
});

test('JSON extraction preserves literal source strings', () => {
  const body = JSON.stringify({wording: `<cultured> &amp; ${fixtureText}`});
  const fixture = runFixture([source()], {routes: {'https://sources.example.org/A': fixtureBody(body, 'application/json')}});
  successfulRun(fixture);
  assert.equal(fs.readFileSync(path.join(fixture.output, 'A.txt'), 'utf8'), body);
});

test('Declared Windows-1252 text decodes without altering retained bytes', () => {
  const bytes = Buffer.concat([Buffer.from('Caf'), Buffer.from([0xe9]), Buffer.from(` ${fixtureText}`)]);
  const fixture = runFixture([source()], {routes: {'https://sources.example.org/A': fixtureBody(bytes, 'text/plain; charset=windows-1252')}});
  const [receipt] = successfulRun(fixture);
  assert.equal(receipt.text_encoding, 'windows-1252');
  assert.equal(receipt.sha256, sha(bytes));
  assert.match(fs.readFileSync(path.join(fixture.output, 'A.txt'), 'utf8'), /^Café /u);
});

test('Invalid UTF-8 retains raw evidence and remains not retrieved', () => {
  const bytes = Buffer.concat([Buffer.from([0xc3, 0x28]), Buffer.from(fixtureText)]);
  const fixture = runFixture([source()], {routes: {'https://sources.example.org/A': fixtureBody(bytes)}});
  const [receipt] = successfulRun(fixture);
  assert.equal(receipt.capture_status, 'not_retrieved');
  assert.equal(receipt.sha256, sha(bytes));
  assert.equal(receipt.text_sha256, null);
  assert.match(receipt.extraction_error, /encoding/i);
});

test('Non-public literal addresses fail preflight without a request', () => {
  for (const host of ['127.0.0.1', '100.64.0.1', '[::1]', '192.168.1.1']) {
    rejectedBeforeCapture(runFixture([source('A', {url: `http://${host}/source`})]), /Non-public host rejected/i);
  }
});

test('A blocked HTTP 200 JavaScript shell does not become retrieved evidence', () => {
  const body = `<html><body><p>Enable JavaScript to continue.</p><p>${fixtureText}</p></body></html>`;
  const fixture = runFixture([source()], {routes: {'https://sources.example.org/A': fixtureBody(body, 'text/html')}});
  const [receipt] = successfulRun(fixture);
  assert.equal(receipt.http_status, 200);
  assert.equal(receipt.capture_status, 'not_retrieved');
  assert.equal(receipt.sha256, sha(Buffer.from(body)));
});

test('A publisher client challenge remains blocked despite HTTP 200 and long text', () => {
  const body = `<html><body><h1>Client Challenge</h1><p>${fixtureText}</p></body></html>`;
  const fixture = runFixture([source()], {routes: {'https://sources.example.org/A': fixtureBody(body, 'text/html')}});
  const [receipt] = successfulRun(fixture);
  assert.equal(receipt.http_status, 200);
  assert.equal(receipt.capture_status, 'not_retrieved');
  assert.equal(receipt.sha256, sha(Buffer.from(body)));
});

test('Unsafe redirect destinations are rejected before the next request', () => {
  const fixture = runFixture([source()], {routes: {'https://sources.example.org/A': {
    status: 302, headers: {location: 'http://127.0.0.1/source'}, body_base64: null,
  }}});
  const [receipt] = successfulRun(fixture);
  assert.equal(fixture.requests.length, 1);
  assert.equal(receipt.capture_status, 'not_retrieved');
  assert.equal(receipt.sha256, null);
  assert.match(receipt.error.message, /Non-public host rejected/i);
});

test('Request failure retains a null-hash receipt and completes the manifest', () => {
  const fixture = runFixture([source()], {routes: {'https://sources.example.org/A': {throw_message: 'Fixture request failed'}}});
  const [receipt] = successfulRun(fixture);
  assert.equal(receipt.capture_status, 'not_retrieved');
  assert.equal(receipt.http_status, null);
  assert.equal(receipt.sha256, null);
  assert.equal(receipt.text_sha256, null);
  assert.equal(receipt.error.cause, 'OFFLINE_FIXTURE_FAILURE');
  assert.equal(JSON.parse(fs.readFileSync(path.join(fixture.output, 'A.receipt.json'))).key, 'A');
});

const failures = results.filter(result => result.status === 'FAIL');
console.log(JSON.stringify({status: failures.length ? 'FAIL' : 'PASS', cases: results.length,
  passed: results.length - failures.length, failed: failures.length, capture_fixtures: fixtureCount,
  mocked_requests: fakeRequests, real_network_attempts: realNetworkAttempts, captured_script_sha256: sha(script),
  fixture_root: temporaryRoot, failures}, null, 2));
if (failures.length) process.exitCode = 1;
