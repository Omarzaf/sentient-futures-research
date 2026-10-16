import { mkdir, readFile, writeFile, access } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { resolve, join } from 'node:path';
import { execFileSync } from 'node:child_process';

const workspace = resolve(import.meta.dirname, '../../../..');
const rawDir = join(workspace, 'OUTPUTS/Deep Research 2026-10/policy-review/raw');
const planFile = process.argv[2] || 'retrieval-plan.json';
if (!['retrieval-plan.json', 'retrieval-fallbacks.json', 'retrieval-final.json'].includes(planFile)) throw new Error('Unknown checked retrieval plan');
const plan = JSON.parse(await readFile(new URL('./' + planFile, import.meta.url), 'utf8'));
await mkdir(rawDir, { recursive: true });
const receipts = [];
async function capture(item) {
  const receipt = { id: item.id, requested_url: item.url, prior_failed_attempts: item.prior_failed_attempts, attempts: [], licence: 'No redistribution licence established; retained privately for source inspection.' };
  const ext = /\.pdf(?:$|\?)/i.test(item.url) ? 'pdf' : 'html';
  const out = join(rawDir, item.id + '.' + ext);
  try {
    await access(out);
    const b = await readFile(out);
    receipt.status = 'existing_capture_preserved'; receipt.path = out; receipt.bytes = b.length; receipt.sha256 = createHash('sha256').update(b).digest('hex');
    receipts.push(receipt); console.log(item.id + ': preserved existing capture'); return;
  } catch {}
  for (let attempt = 1; attempt <= Math.min(item.max_attempts ?? 3, 3 - item.prior_failed_attempts); attempt++) {
    const started_at = new Date().toISOString();
    try {
      const r = await fetch(item.url, { signal: AbortSignal.timeout(40000), redirect: 'follow', headers: { 'User-Agent': 'SentientFuturesPolicyResearch/1.0' } });
      if (!r.ok) throw new Error('HTTP ' + r.status);
      const b = Buffer.from(await r.arrayBuffer());
      if (b.length > 35000000) throw new Error('Response exceeds private-capture limit 35 MB');
      if (ext === 'pdf' && b.subarray(0,5).toString() !== '%PDF-') throw new Error('Expected PDF signature; received ' + (r.headers.get('content-type') || 'unknown'));
      await writeFile(out, b, { flag: 'wx' });
      receipt.attempts.push({ attempt, started_at, retrieved_at: new Date().toISOString(), status: 'success', final_url: r.url, http_status: r.status, content_type: r.headers.get('content-type') });
      receipt.status = 'captured'; receipt.path = out; receipt.bytes = b.length; receipt.sha256 = createHash('sha256').update(b).digest('hex');
      if (ext === 'pdf') {
        try { execFileSync('pdftotext', ['-layout', out, join(rawDir, item.id + '.txt')]); receipt.text_path = join(rawDir, item.id + '.txt'); }
        catch(e) { receipt.text_extraction_error = String(e.message).slice(0,500); }
      }
      console.log(item.id + ': captured ' + b.length + ' bytes'); break;
    } catch(e) { receipt.attempts.push({ attempt, started_at, status: 'failed', error: String(e.message).slice(0,500) }); }
  }
  if (!receipt.status) receipt.status = 'retrieval_gap_after_attempt_limit';
  receipts.push(receipt);
}
for (let i=0;i<plan.length;i+=4) await Promise.all(plan.slice(i,i+4).map(capture));
receipts.sort((a,b)=>a.id.localeCompare(b.id));
const receiptPath = join(rawDir, 'retrieval-receipts.json');
try { await writeFile(receiptPath, JSON.stringify({ captured_at: new Date().toISOString(), receipts }, null, 2) + '\n', { flag:'wx' }); }
catch(e) { console.log('Existing receipts preserved; writing a dated additional receipt.'); await writeFile(join(rawDir, 'retrieval-receipts-' + Date.now() + '.json'), JSON.stringify({captured_at:new Date().toISOString(),receipts},null,2)+'\n',{flag:'wx'}); }
console.log(JSON.stringify({rawDir,captured:receipts.filter(r=>r.sha256).length,gaps:receipts.filter(r=>!r.sha256).map(r=>r.id)}));

