import { readFile, writeFile, readdir } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { resolve, join } from 'node:path';

const ownDir = import.meta.dirname;
const workspace = resolve(ownDir, '../../../..');
const privateDir = join(workspace, 'OUTPUTS/Deep Research 2026-10/policy-review');
const rawDir = join(privateDir, 'raw');
const sha = bytes => createHash('sha256').update(bytes).digest('hex');
const register = JSON.parse(await readFile(join(ownDir, 'instrument-register.json'), 'utf8'));
const codebookBytes = await readFile(join(ownDir, 'codebook.json'));
const codebook = JSON.parse(codebookBytes);
const args = process.argv.slice(2);
if(args.length && (args.length !== 1 || args[0] !== '--refresh-author-form'))throw Error('Usage: node prepare-review.mjs [--refresh-author-form]');
if(args[0] === '--refresh-author-form') {
  const frozen=JSON.parse(await readFile(join(ownDir,'freeze-receipt.json'),'utf8'));
  const registerBytes=await readFile(join(ownDir,'instrument-register.json'));
  const agentBytes=await readFile(join(ownDir,'agent-codes.frozen.json'));
  if(sha(codebookBytes)!==frozen.codebook.sha256 || sha(registerBytes)!==frozen.sample.sha256 || sha(agentBytes)!==frozen.agent_round_1.sha256)throw Error('Frozen policy input changed; refusing form refresh');
  const blank=JSON.parse(await readFile(join(privateDir,'author-coding.blank.json'),'utf8'));
  if(blank.codebook_sha256!==frozen.codebook.sha256 || blank.sample_sha256!==frozen.sample.sha256 || blank.assignments.length!==20 || blank.assignments.some(a=>a.primary_function!==null || a.rationale!=='' || a.text_locator!=='' || a.coding_status!=='blank') || blank.independence_attested!==false || blank.completed_at!==null)throw Error('Author blank packet changed; refusing to overwrite it or regenerate from responses');
  if(sha(await readFile(join(privateDir,'codebook.author-copy.json')))!==frozen.codebook.sha256)throw Error('Private author codebook differs from frozen codebook');
  await renderAuthorForm({register,codebook,blank,codebookHash:frozen.codebook.sha256,sampleHash:frozen.sample.sha256,refresh:true});
  console.log(JSON.stringify({status:'private_author_form_refreshed',instruments:20,blank_author_responses:20,codebook_sha256:frozen.codebook.sha256,sample_sha256:frozen.sample.sha256,agent_sha256:frozen.agent_round_1.sha256,frozen_files_modified:false,kappa:null},null,2));
  process.exit(0);
}
try {
  await readFile(join(ownDir,'freeze-receipt.json'));
  throw Error('Frozen review already exists; use --refresh-author-form to refresh only private HTML');
} catch(error) {
  if(error.code!=='ENOENT')throw error;
}
const receiptFiles = (await readdir(rawDir)).filter(n => /^retrieval-receipts(?:-[0-9]+)?\.json$/.test(n)).sort();
const receipts = [];
for (const name of receiptFiles) {
  const doc = JSON.parse(await readFile(join(rawDir, name), 'utf8'));
  for (const r of doc.receipts) receipts.push({ ...r, receipt_file: name });
}
const selected = new Map();
for (const r of receipts.filter(r => r.sha256)) selected.set(r.id, r);
for (const i of register.instruments) {
  const r = selected.get(i.id);
  if (!r) throw new Error('No successful private source capture: ' + i.id);
  const pdf = await readFile(join(rawDir, i.id + '.pdf'));
  if (pdf.subarray(0,5).toString() !== '%PDF-' || sha(pdf) !== r.sha256) throw new Error('Source hash/signature mismatch: ' + i.id);
  i.source = {
    official_url: r.attempts.find(a => a.status === 'success')?.final_url || r.requested_url,
    requested_url: r.requested_url,
    raw_file: 'OUTPUTS/Deep Research 2026-10/policy-review/raw/' + i.id + '.pdf',
    sha256: r.sha256,
    bytes: r.bytes,
    retrieved_at: r.attempts.find(a => a.status === 'success')?.retrieved_at || null,
    receipt_file: 'OUTPUTS/Deep Research 2026-10/policy-review/raw/' + r.receipt_file,
    licence: r.licence
  };
}
await writeFile(join(ownDir, 'instrument-register.json'), JSON.stringify(register, null, 2) + '\n');
const registerBytes = await readFile(join(ownDir, 'instrument-register.json'));
const codebookHash = sha(codebookBytes);
const sampleHash = sha(registerBytes);
const agentLabels = {
  'IN-FSSAI-NSF-2017': ['AUTHORISATION', 'The operative mechanism is prior case-specific food/ingredient approval, not a compositional rule.'],
  'IN-FSSAI-VEGAN-2022': ['INFORMATION', 'The vegan identity, integrity and consumer-facing logo govern a claim; apply the claim-specific endorsement tie-break.'],
  'IN-FSSAI-LABEL-2020': ['INFORMATION', 'Direct requirements concern food labels and displayed information.'],
  'IN-FSSAI-IMPORT-2017': ['TRADE', 'The specialised instrument organises border clearance and inspection for food imports.'],
  'IN-FSSAI-RECALL-2017': ['SAFETY', 'The central mechanism removes and manages food subject to recall.'],
  'IN-DBT-BIOE3-2024': ['INNOVATION', 'The policy supports biomanufacturing R&D, translation, infrastructure and capability.'],
  'IN-DBT-SMART-CALL-2025': ['INNOVATION', 'The distinct call defines research/scale-up scope, eligibility and funding arrangements.'],
  'PK-FED-PSQCA-1996': ['FRAMEWORK', 'A founding Act establishes the standards authority and assigns broad powers.'],
  'PK-FED-HALAL-2016': ['FRAMEWORK', 'A founding Act establishes the halal authority and its jurisdiction; use the enabling-Act rule.'],
  'PK-FED-BIOSAFETY-2005': ['SAFETY', 'The specialised regime addresses biosafety risk, contained use and release controls, even where licences are required.'],
  'PK-PUNJAB-ACT-2011': ['FRAMEWORK', 'A founding authority Act assigns broad regulatory and enforcement functions.'],
  'PK-PUNJAB-PRODUCT-2017': ['AUTHORISATION', 'The product itself requires registration and a CPR; the accompanying logo is incidental to that entry gate.'],
  'PK-PUNJAB-RECALL-2017': ['SAFETY', 'The specialised mechanism is food recall and associated operator duties.'],
  'PK-SINDH-ACT-2016': ['FRAMEWORK', 'A founding authority Act establishes institutional powers and jurisdiction.'],
  'PK-SINDH-PRODUCT-2023': ['FRAMEWORK', 'The complete captured four-page text supplies definitions; no product-approval procedure is inferred from its title.'],
  'PK-SINDH-BUSINESS-2023': ['AUTHORISATION', 'Chapter II establishes the business/premises licensing gate; apply the first dedicated operative-chapter tie-break.'],
  'PK-KP-ACT-2014': ['FRAMEWORK', 'The enabling Act establishes the authority and broad food safety/halal powers.'],
  'PK-BALOCH-ACT-2014': ['FRAMEWORK', 'The enabling Act establishes the food authority and broad powers.'],
  'PK-BALOCH-PRODUCT-2022': ['AUTHORISATION', 'The named specialised instrument establishes product registration and premises licensing.'],
  'PK-BALOCH-SAMPLING-2025': ['SAFETY', 'The operative rules prescribe inspection, corrective action and sampling.']
};
const frozenAgent = {
  schema_version: '1.0', round: 1, status: 'frozen_agent_codes_do_not_show_before_author_finalises',
  frozen_at: new Date().toISOString(), codebook_sha256: codebookHash, sample_sha256: sampleHash,
  coder: 'Codex specialist; AI-assisted, not human ground truth',
  assignments: register.instruments.map(i => ({ instrument_id:i.id, primary_function:agentLabels[i.id][0], rationale:agentLabels[i.id][1], text_locator:i.text_locator, coding_status:'coded' }))
};
const agentBytes = Buffer.from(JSON.stringify(frozenAgent, null, 2) + '\n');
await writeFile(join(ownDir, 'agent-codes.frozen.json'), agentBytes, { flag:'wx' });
const blank = {
  schema_version:'1.0', round:1, codebook_sha256:codebookHash, sample_sha256:sampleHash,
  coder_role:'author', independence_attested:false, completed_at:null, status:'blank_not_human_coded',
  assignments:register.instruments.map(i => ({instrument_id:i.id,primary_function:null,rationale:'',text_locator:'',coding_status:'blank'}))
};
await writeFile(join(privateDir, 'author-coding.blank.json'), JSON.stringify(blank,null,2)+'\n', {flag:'wx'});
const freeze = {
  schema_version:'1.0', frozen_at:frozenAgent.frozen_at, codebook:{file:'codebook.json',sha256:codebookHash},
  sample:{file:'instrument-register.json',sha256:sampleHash,count:register.instruments.length},
  agent_round_1:{file:'agent-codes.frozen.json',sha256:sha(agentBytes),count:frozenAgent.assignments.length},
  author_status:'pending_independent_20_item_coding', kappa:null,
  git_preregistration_status:'local_files_prepared_not_yet_recorded_as_committed_by_this_specialist',
  boundaries:'Hash freeze is an integrity receipt, not encryption or access control. Keep agent responses separate from the author packet until independent author coding is final.',
  source_access:'Twenty source PDFs captured; one is an official BioE3 policy summary brochure rather than the unavailable full policy text. Exact-date and legal-currency gaps remain in the register.'
};
await writeFile(join(ownDir, 'freeze-receipt.json'), JSON.stringify(freeze,null,2)+'\n', {flag:'wx'});
await renderAuthorForm({register,codebook,blank,codebookHash,sampleHash});
async function renderAuthorForm({register,codebook,blank,codebookHash,sampleHash,refresh=false}) {
const safe = s => String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const publicItems=register.instruments.map(i=>({id:i.id,title:i.title,jurisdiction:i.country+' / '+i.jurisdiction,url:i.source.official_url,raw_file:i.source.raw_file,text_locator:i.text_locator,access_limitations:i.access_limitations}));
const cards=publicItems.map((i,index)=>'<article><h2>'+ (index+1) + '. ' + safe(i.title) + '</h2><p class="meta">' + safe(i.id)+' · '+safe(i.jurisdiction)+'</p><p><a href="'+safe(i.url)+'" target="_blank" rel="noreferrer noopener">Official source</a> · <a href="raw/'+safe(i.id)+'.pdf" target="_blank">Private captured PDF</a></p><p><strong>Locator:</strong> '+safe(i.text_locator)+'</p>'+(i.access_limitations.length?'<details><summary>Source limitations</summary><ul>'+i.access_limitations.map(x=>'<li>'+safe(x)+'</li>').join('')+'</ul></details>':'')+'<label>Primary function<select data-id="'+safe(i.id)+'"><option value="">Choose independently</option>'+codebook.categories.map(c=>'<option value="'+c.code+'">'+safe(c.code+' — '+c.name)+'</option>').join('')+'<option value="__UNCODABLE__">Cannot classify from this source — explain why</option></select></label><label>Reason for your code<textarea data-note="'+safe(i.id)+'" rows="2"></textarea></label><label>Your checked text locator (or where inspection failed)<input data-locator="'+safe(i.id)+'"></label></article>').join('\n');
const payload=JSON.stringify({blank,items:publicItems}).replace(/</g,'\\u003c');
const template = await readFile(join(ownDir, 'author-form.template.html'), 'utf8');
if(!template.includes('{"__AUTHOR_PACKET_PLACEHOLDER__":true}'))throw Error('Valid JSON author-packet placeholder is missing');
const html = template.replaceAll('{{CODEBOOK_HASH}}', codebookHash).replaceAll('{{SAMPLE_HASH}}', sampleHash).replaceAll('{{CATEGORIES}}', codebook.categories.map(c=>'<dt><strong>'+safe(c.code+' — '+c.name)+'</strong></dt><dd>'+safe(c.definition)+' '+safe(c.exclude)+'</dd>').join('')).replaceAll('{{RULES}}',codebook.decision_rules.map(x=>'<li>'+safe(x)+'</li>').join('')).replaceAll('{{CARDS}}', cards).replaceAll('{"__AUTHOR_PACKET_PLACEHOLDER__":true}',payload).replace('href="codebook.json"','href="codebook.author-copy.json"');
await writeFile(join(privateDir,'author-form.html'),html,{flag:refresh?'w':'wx'});
if(!refresh)await writeFile(join(privateDir,'codebook.author-copy.json'),codebookBytes,{flag:'wx'});
}
const fallbackReceiptName = receiptFiles.find(n => n.includes('1792115981630'));
if(fallbackReceiptName){
  const fixed = JSON.parse(await readFile(join(ownDir,'retrieval-fallbacks.json'),'utf8'));
  await writeFile(join(rawDir,'retrieval-count-correction.json'),JSON.stringify({correction_for:fallbackReceiptName,reason:'The one-attempt fallback run limit was mistakenly encoded as prior_failed_attempts=2. Actual per-URL prior failure counts are listed here; the actual attempt arrays, retrieval times, source bytes and hashes are unchanged.',corrected_prior_failed_attempts:fixed.map(x=>({id:x.id,url:x.url,prior_failed_attempts:x.prior_failed_attempts,max_attempts:1}))},null,2)+'\n',{flag:'wx'});
}
console.log(JSON.stringify({instruments:register.instruments.length,source_pdfs:register.instruments.length,author_blank:blank.assignments.filter(a=>a.primary_function===null).length,private_author_form:join(privateDir,'author-form.html'),codebook_sha256:codebookHash,sample_sha256:sampleHash,agent_sha256:sha(agentBytes),kappa:null},null,2));

