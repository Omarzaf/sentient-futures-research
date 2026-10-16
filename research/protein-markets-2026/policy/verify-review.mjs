import { readFile, writeFile, realpath } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { resolve, join, dirname, sep } from 'node:path';
import { Script, runInNewContext } from 'node:vm';

const ownDir=import.meta.dirname;
const workspace=resolve(ownDir,'../../../..');
const privateDir=join(workspace,'OUTPUTS/Deep Research 2026-10/policy-review');
const args=process.argv.slice(2);
let outputPath=null;
if(args.length){
  if(args.length!==2||args[0]!=='--output'||!args[1])throw Error('Usage: node verify-review.mjs [--output PRIVATE_NEW_RECEIPT_PATH]');
  outputPath=resolve(args[1]);
  const parent=await realpath(dirname(outputPath));
  const privateBase=await realpath(privateDir);
  if(parent!==privateBase&&!parent.startsWith(privateBase+sep))throw Error('Verification output must remain inside the private policy-review directory');
}
const hash=b=>createHash('sha256').update(b).digest('hex');
const load=async path=>JSON.parse(await readFile(path,'utf8'));
const register=await load(join(ownDir,'instrument-register.json'));
const codebook=await load(join(ownDir,'codebook.json'));
const frozen=await load(join(ownDir,'freeze-receipt.json'));
const agent=await load(join(ownDir,'agent-codes.frozen.json'));
const blank=await load(join(privateDir,'author-coding.blank.json'));
const html=await readFile(join(privateDir,'author-form.html'),'utf8');
let assertions=0;
const assert=(v,m)=>{if(!v)throw Error(m);assertions+=1};
assert(register.instruments.length===20,'20 instruments required');
const ids=register.instruments.map(i=>i.id);
assert(new Set(ids).size===20,'Duplicate instrument IDs');
assert(new Set(register.instruments.map(i=>i.source.sha256)).size===20,'Duplicate raw-source bytes require review');
const validCodes=new Set(codebook.categories.map(c=>c.code));
assert(validCodes.size===8,'Codebook categories');
assert(agent.assignments.length===20&&new Set(agent.assignments.map(a=>a.instrument_id)).size===20,'Agent sample count');
assert(agent.assignments.every(a=>ids.includes(a.instrument_id)&&validCodes.has(a.primary_function)&&a.rationale&&a.text_locator),'Agent codes or evidence missing');
assert(blank.assignments.length===20&&blank.assignments.every(a=>a.primary_function===null&&a.rationale===''&&a.text_locator===''&&a.coding_status==='blank'),'Author form is not blank');
assert(blank.independence_attested===false&&blank.completed_at===null,'Author attestation fabricated');
for(const [file,expected] of [['codebook.json',frozen.codebook.sha256],['instrument-register.json',frozen.sample.sha256],['agent-codes.frozen.json',frozen.agent_round_1.sha256]])assert(hash(await readFile(join(ownDir,file)))===expected,'Frozen hash mismatch: '+file);
const coverage=new Map();
for(const i of register.instruments){
  assert(i.source.official_url.startsWith('https://'),'Missing original official URL');
  const b=await readFile(join(workspace,i.source.raw_file));
  assert(b.subarray(0,5).toString()==='%PDF-'&&hash(b)===i.source.sha256,'Raw source mismatch: '+i.id);
  coverage.set(i.country+':'+i.jurisdiction,(coverage.get(i.country+':'+i.jurisdiction)||0)+1);
}
for(const key of ['India:national','Pakistan:federal','Pakistan:Punjab','Pakistan:Sindh','Pakistan:Khyber Pakhtunkhwa','Pakistan:Balochistan'])assert(coverage.has(key),'Missing coverage '+key);
assert(register.instruments.some(i=>i.id==='IN-DBT-BIOE3-2024')&&register.instruments.some(i=>i.id==='IN-DBT-SMART-CALL-2025'),'Missing BioE3/DBT coverage');
const payloadText=html.match(/<script id="packet" type="application\/json">([\s\S]*?)<\/script>/)?.[1];
assert(payloadText,'Missing author packet');
const packet=JSON.parse(payloadText);
assert(packet.blank.assignments.every(a=>a.primary_function===null),'Exposed answers in author packet');
assert(!html.includes('agent-codes.frozen.json')&&!html.includes('frozen_agent_codes')&&!html.includes('rationale_agent'),'Agent answers linked or embedded');
assert((html.match(/<select data-id=/g)||[]).length===20,'20 author controls required');
const inline=html.match(/<script>([\s\S]*?)<\/script>/)?.[1];
new Script(inline);
const elements=new Map();
elements.set('#packet',{textContent:payloadText});
elements.set('#independent',{checked:false});
elements.set('#progress',{textContent:''});
elements.set('#message',{textContent:''});
elements.set('#draft',{addEventListener(){}});
elements.set('#finish',{addEventListener(){}});
const selects=ids.map(id=>({value:'',addEventListener(){},id}));
for(const id of ids){elements.set('select[data-id="'+id+'"]',selects.find(x=>x.id===id));elements.set('[data-note="'+id+'"]',{value:''});elements.set('[data-locator="'+id+'"]',{value:''});}
const context={document:{querySelector:q=>{assert(elements.has(q),'Unexpected selector '+q);return elements.get(q)},querySelectorAll:q=>q==='select[data-id]'?selects:[],createElement:()=>{throw Error('Unexpected download from blank author form')}},structuredClone,setTimeout,URL,Blob,JSON};
runInNewContext(inline,context);
const gathered=context.gather(false);
assert(gathered.assignments.every(a=>a.primary_function===null&&a.rationale===''),'Runtime author defaults not blank');
context.save(true);
assert(elements.get('#message').textContent.startsWith('Complete all 20'),'Blank final author submission not rejected');
assert(frozen.kappa===null&&frozen.author_status==='pending_independent_20_item_coding','Kappa or human completion fabricated');
const result={verified_at:new Date().toISOString(),status:'pass',assertions,instruments:20,distinct_primary_source_pdfs:20,blank_author_responses:20,coverage:Object.fromEntries(coverage),codebook_sha256:frozen.codebook.sha256,sample_sha256:frozen.sample.sha256,agent_sha256:frozen.agent_round_1.sha256,author_agreement:{status:'pending',kappa:null},limits:['Source identity/function review is not comprehensive legal-currency verification.','BioE3 source is an official summary brochure, with full-policy URL retrieval gap.','Selected scanned pages support function coding; technical schedules not exhaustively reviewed.']};
if(outputPath)await writeFile(outputPath,JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify(result,null,2));

