import { mkdir, readFile, writeFile, access } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { resolve, join, basename } from 'node:path';
import { execFileSync } from 'node:child_process';

const rawDir = resolve(import.meta.dirname, '../../../../OUTPUTS/Deep Research 2026-10/halal/raw');
const planName = process.argv[2] ?? 'retrieval-plan.json';
if (!/^retrieval-[a-z-]+\.json$/.test(planName)) throw new Error('Use a named local retrieval plan.');
const plan = JSON.parse(await readFile(new URL(planName, import.meta.url), 'utf8'));
await mkdir(rawDir, { recursive: true });
const receipts = [];
async function capture(item) {
  const target = join(rawDir, item.id + (item.format === 'pdf' ? '.pdf' : '.html'));
  try { await access(target); throw new Error('Existing capture preserved: ' + basename(target)); }
  catch (e) { if (e.code !== 'ENOENT') throw e; }
  const receipt = { id: item.id, requested_url: item.url, prior_failed_attempts: item.prior_failed_attempts ?? 0, attempts: [], licence: 'No reuse or redistribution licence established. Full source retained privately for inspection; authored files use short excerpts only.' };
  for (let n = 1; n <= Math.min(item.max_attempts ?? 1, 3 - receipt.prior_failed_attempts); n++) {
    const started_at = new Date().toISOString();
    try {
      let r, b;
      if (item.transport === 'curl') {
        const output = execFileSync('curl', ['--fail', '--location', '--silent', '--show-error', '--max-time', '25', '--user-agent', 'SentientFuturesSourceInspection/1.0', '--write-out', '\n%{json}', item.url], { maxBuffer: 36000000 });
        const boundary = output.lastIndexOf(Buffer.from('\n{"'));
        if (boundary < 0) throw new Error('Missing curl response metadata.');
        const metadata = JSON.parse(output.subarray(boundary + 1).toString());
        b = output.subarray(0, boundary);
        r = { ok: metadata.http_code >= 200 && metadata.http_code < 300, status: metadata.http_code, url: metadata.url_effective, headers: { get: () => metadata.content_type } };
      } else {
        r = await fetch(item.url, { redirect: 'follow', signal: AbortSignal.timeout(25000), headers: { 'User-Agent': 'SentientFuturesSourceInspection/1.0' } });
        b = Buffer.from(await r.arrayBuffer());
      }
      if (!r.ok) throw new Error('HTTP ' + r.status);
      if (b.length > 35000000) throw new Error('Capture exceeds 35 MB.');
      if (item.format === 'pdf' && b.subarray(0, 5).toString() !== '%PDF-') throw new Error('Not a PDF: ' + r.headers.get('content-type'));
      await writeFile(target, b, { flag: 'wx' });
      const done = { status: 'success', started_at, retrieved_at: new Date().toISOString(), final_url: r.url, http_status: r.status, content_type: r.headers.get('content-type') };
      receipt.attempts.push(done);
      Object.assign(receipt, { status: 'captured', file: basename(target), bytes: b.length, sha256: createHash('sha256').update(b).digest('hex'), retrieved_at: done.retrieved_at, final_url: r.url });
      if (item.format === 'pdf') {
        try { execFileSync('pdftotext', ['-layout', target, target.replace(/\.pdf$/, '.txt')]); receipt.text_file = basename(target).replace(/\.pdf$/, '.txt'); }
        catch (e) { receipt.text_extraction_error = String(e.message).slice(0, 300); }
      }
      break;
    } catch (e) { receipt.attempts.push({ status: 'failed', started_at, error: String(e.message).slice(0, 300) }); }
  }
  receipt.status ??= 'held_retrieval_gap';
  receipts.push(receipt);
  console.log(item.id + ': ' + receipt.status + (receipt.bytes ? ' ' + receipt.bytes + ' bytes' : ''));
}
for (let i = 0; i < plan.length; i += 3) await Promise.all(plan.slice(i, i + 3).map(capture));
receipts.sort((a, b) => a.id.localeCompare(b.id));
await writeFile(join(rawDir, planName.replace('retrieval-', 'receipts-')), JSON.stringify({ captured_at: new Date().toISOString(), route: 'Agent-Reach workflow; local CLIs unavailable, native search and public GET fallback.', receipts }, null, 2) + '\n', { flag: 'wx' });
