import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {checkReviewedSupervisorExports,checkInlineScripts,isExcludedPath} from './privacy-checks.mjs';

const digest=value=>crypto.createHash('sha256').update(value).digest('hex');
const prefix='research/india-pakistan/report/';
const evidencePrefix='provenance/supervisor-export-text/';
const markdown=prefix+'REPORT.md';
const canonical=evidencePrefix+'canonical.txt';
const evidence=evidencePrefix+'parity.json';
const verifier='tools/verify_edition.py';
const authored='Protein supply is 8.72 kg per person. Human verification pending.\n';
function fixture(){
 const files=new Map([
  [markdown,Buffer.from('# Protein supply\n\n'+authored)],
  [canonical,Buffer.from(authored)],
  [verifier,Buffer.from('# Authored-body verifier fixture\n')],
  [prefix+'report.pdf',Buffer.from('%PDF-1.7\nSynthetic reviewed fixture; no real PDF QA claimed.')],
  [prefix+'report.docx',Buffer.from('PK\x03\x04Synthetic reviewed fixture; no real Word export QA claimed.')],
  [evidencePrefix+'report-pdf.txt',Buffer.from(authored)],
  [evidencePrefix+'report-docx.txt',Buffer.from(authored)],
 ]);
 const bind=p=>({path:p,sha256:digest(files.get(p))});
 const exports=['pdf','docx'].map(extension=>({...bind(prefix+'report.'+extension),license:'Authored working report; no blanket reuse license.',text_path:evidencePrefix+'report-'+extension+'.txt',text_sha256:digest(files.get(evidencePrefix+'report-'+extension+'.txt'))}));
 const receipt={schema_version:1,method:'supervisor-c12-authored-body-parity',checked_at:'2026-10-14T12:00:00Z',markdown:bind(markdown),canonical_text:bind(canonical),verifier:bind(verifier),exports:exports.map(({license,...record})=>record)};
 files.set(evidence,Buffer.from(JSON.stringify(receipt)));
 const registry={schema_version:1,human_verification:'pending',markdown:bind(markdown),canonical_text:bind(canonical),parity_evidence:bind(evidence),exports};
 return {files,registry};
}
const inspect=f=>checkReviewedSupervisorExports(f.registry,p=>{if(!f.files.has(p))throw Error('Missing fixture '+p);return f.files.get(p);});
const valid=inspect(fixture());
assert.deepEqual(valid.failures,[]);
assert.deepEqual([...valid.allowedPaths].sort(),[prefix+'report.docx',prefix+'report.pdf']);
assert(isExcludedPath(prefix+'report.pdf'));
assert(isExcludedPath(prefix+'report.docx'));
const mutations=[
 ['extra binary',f=>f.registry.exports.push({...f.registry.exports[0],path:prefix+'other.pdf'})],
 ['wrong export path',f=>{f.registry.exports[0].path='research/other/report.pdf';}],
 ['duplicate export',f=>{f.registry.exports[1]=structuredClone(f.registry.exports[0]);}],
 ['changed PDF bytes',f=>f.files.set(prefix+'report.pdf',Buffer.from('%PDF-1.7\nChanged value 8720'))],
 ['changed Word bytes',f=>f.files.set(prefix+'report.docx',Buffer.from('PK\x03\x04Changed value 8720'))],
 ['stale Markdown binding',f=>f.files.set(markdown,Buffer.from('Different report'))],
 ['stale extraction hash',f=>f.files.set(evidencePrefix+'report-pdf.txt',Buffer.from('Changed extraction'))],
 ['invalid canonical binding',f=>{f.registry.canonical_text.sha256='0'.repeat(64);}],
 ['unreviewed license',f=>{f.registry.exports[0].license='unknown';}],
 ['missing parity receipt',f=>f.files.delete(evidence)],
 ['changed parity receipt',f=>f.files.set(evidence,Buffer.from('{}'))],
 ['source verifier changed',f=>f.files.set(verifier,Buffer.from('Different verifier'))],
 ['human approval invented',f=>{f.registry.human_verification='approved';}],
 ['escaping text surrogate',f=>{f.registry.exports[0].text_path='../private.txt';}],
 ['PDF signature invalid',f=>{const value=Buffer.from('Not a PDF');f.files.set(prefix+'report.pdf',value);f.registry.exports[0].sha256=digest(value);}],
 ['changed body with updated hashes',f=>{const p=evidencePrefix+'report-pdf.txt';f.files.set(p,Buffer.from('Protein supply is 8720 kg per person. Human verification pending.\n'));f.registry.exports[0].text_sha256=digest(f.files.get(p));const receipt=JSON.parse(f.files.get(evidence));receipt.exports[0].text_sha256=f.registry.exports[0].text_sha256;f.files.set(evidence,Buffer.from(JSON.stringify(receipt)));f.registry.parity_evidence.sha256=digest(f.files.get(evidence));}],
 ['private surrogate content',f=>{const text='Contact '+['researcher','example.org'].join('@');for(const p of [canonical,evidencePrefix+'report-pdf.txt',evidencePrefix+'report-docx.txt'])f.files.set(p,Buffer.from(text));f.registry.canonical_text.sha256=digest(f.files.get(canonical));for(const record of f.registry.exports)record.text_sha256=digest(f.files.get(record.text_path));const receipt=JSON.parse(f.files.get(evidence));receipt.canonical_text=f.registry.canonical_text;receipt.exports=f.registry.exports.map(({license,...record})=>record);f.files.set(evidence,Buffer.from(JSON.stringify(receipt)));f.registry.parity_evidence.sha256=digest(f.files.get(evidence));}],
];
for(const [name,change] of mutations){const data=fixture();change(data);assert(inspect(data).failures.length>0,name);}
for(const p of ['other.pdf','other.docx','vendor/bundle.js','private/report.pdf','research/halal-cultivated/paper/exports/paper.pdf'])assert(isExcludedPath(p),p);
const scripts=[
 ['JSON object','<script type="application/json">{"value":8.72}</script>',true],
 ['JSON array',"<script type='application/json'>[1,2]</script>",true],
 ['normal executable','<script>const value=8.72;</script>',true],
 ['malformed JSON','<script type="application/json">{"value":}</script>',false],
 ['JS disguised as JSON','<script type="application/json">const value=8.72;</script>',false],
 ['non-JSON numeric value','<script type="application/json">{"value":NaN}</script>',false],
 ['broken executable','<script>const = ;</script>',false],
 ['mixed valid scripts','<script type="application/json">{"value":8.72}</script><script>const data=JSON.parse("{}");</script>',true],
 ['later broken script','<script type="application/json">{}</script><script>let = ;</script>',false],
];
for(const [name,html,accepted] of scripts)assert.equal(checkInlineScripts(html).failures.length===0,accepted,name);
console.log(JSON.stringify({status:'PASS',reviewedExportMutations:mutations.length,scriptCases:scripts.length,excludedPathsRetained:true}));
