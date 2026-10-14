import crypto from 'node:crypto';
import vm from 'node:vm';

const forbiddenPath=/(^|\/)(?:\.env(?:\.[^/]*)?|node_modules|\.venv(?:-[^/]+)?|\.playwright-mcp|\.agents|\.codex|\.tools|vendor|tool-cache|private|working|Research Loop Working|AGENTS\.md|\.DS_Store)(\/|$)|\.(?:docx?|xlsx?|pptx?|pdf|zip|pem|key|log)$/i;

const localHomePath=/\/(?:Users|home)\/[A-Za-z0-9._-]+\//g;
const httpUrlPrefix=/https?:\/\/[^\s"'`<>?#]*$/i;

function insideHttpUrlPath(text,index) {
 const before=text.slice(0,index);
 const boundary=Math.max(
  before.lastIndexOf(' '),
  before.lastIndexOf('\n'),
  before.lastIndexOf('\t'),
  before.lastIndexOf('"'),
  before.lastIndexOf("'"),
  before.lastIndexOf('`'),
  before.lastIndexOf('<'),
  before.lastIndexOf('>')
 );
 const tokenPrefix=before.slice(boundary+1);
 return httpUrlPrefix.test(tokenPrefix);
}

export function hasLocalHomePath(text) {
 localHomePath.lastIndex=0;
 for(const match of text.matchAll(localHomePath)) {
  if(!insideHttpUrlPath(text,match.index))return true;
 }
 return false;
}

const hazards=[
 ['absolute home path',hasLocalHomePath],
 ['private document URL',text=>/https?:\/\/(?:docs|drive)\.google\.com\//i.test(text)],
 ['email address',text=>/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/i.test(text)],
 ['private key',text=>/-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----/.test(text)],
 ['credential-like token',text=>/\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{25,}|sk-[A-Za-z0-9_-]{24,})\b/.test(text)],
 ['embedded raster',text=>/data:image\/(?:jpeg|png|webp);base64,/i.test(text)]
];

export function isExcludedPath(path) {
 return forbiddenPath.test(path);
}

export function privacyHazards(text) {
 return hazards.filter(([,check])=>check(text)).map(([name])=>name);
}

export const privacyHazardNames=hazards.map(([name])=>name);

const supervisorReport='research/india-pakistan/report/';
const supervisorExports=new Set([supervisorReport+'report.pdf',supervisorReport+'report.docx']);
const supervisorEvidence='provenance/supervisor-export-text/';
const sha256=value=>crypto.createHash('sha256').update(value).digest('hex');
const safeRelative=value=>typeof value==='string'&&value!==''&&!value.startsWith('/')&&!value.includes('\\')&&!value.split('/').some(part=>part==='..'||part==='.'||part==='');
const normalizedBody=text=>text.normalize('NFC').replaceAll('\u00ad','').replace(/[ﬀﬁﬂﬃﬄ]/g,char=>({'ﬀ':'ff','ﬁ':'fi','ﬂ':'fl','ﬃ':'ffi','ﬄ':'ffl'}[char])).replace(/\s+/g,' ').trim().replace(/\s+([,.;:!?)\]])/g,'$1').replace(/([(\[])\s+/g,'$1');

// Only locally regenerated, hash-bound authored exports can cross the ordinary
// binary exclusion. Node-only CI rechecks their supplied text and receipt; the
// local supervisor verifier performs the actual Pandoc/PDF regeneration.
export function checkReviewedSupervisorExports(registry,readFile) {
 const failures=[];let checks=0;
 const check=(ok,message)=>{checks++;if(!ok)failures.push(message);return Boolean(ok);};
 const bytes=p=>Buffer.from(readFile(p));
 const bound=(record,label,prefix=null)=>{
  if(!check(record&&safeRelative(record.path)&&/^[a-f0-9]{64}$/.test(record.sha256||''),label+' path/hash invalid'))return null;
  if(prefix&&!check(record.path.startsWith(prefix),label+' outside reviewed evidence directory'))return null;
  try{const value=bytes(record.path);check(sha256(value)===record.sha256,label+' hash mismatch');return value;}catch{check(false,label+' file absent');return null;}
 };
 let exports=[];
 try{
  check(registry?.schema_version===1,'Reviewed export registry schema');
  check(registry?.human_verification==='pending','Human scholarly verification must remain pending');
  check(registry?.markdown?.path===supervisorReport+'REPORT.md','Reviewed export Markdown path');
  const markdown=bound(registry?.markdown,'Reviewed Markdown');
  const canonical=bound(registry?.canonical_text,'Canonical body text',supervisorEvidence);
  const receiptBytes=bound(registry?.parity_evidence,'Export parity evidence',supervisorEvidence);
  exports=Array.isArray(registry?.exports)?registry.exports:[];
  check(exports.length===2&&new Set(exports.map(record=>record.path)).size===2&&exports.every(record=>supervisorExports.has(record.path)),'Exactly the two authored supervisor export paths are required');
  if(markdown)check(privacyHazards(markdown.toString('utf8')).length===0,'Private content in reviewed Markdown');
  if(canonical){check(normalizedBody(canonical.toString('utf8')).length>0,'Empty canonical export body');check(privacyHazards(canonical.toString('utf8')).length===0,'Private content in canonical export body');}
  let receipt=null;
  if(receiptBytes){try{receipt=JSON.parse(receiptBytes.toString('utf8'));}catch{check(false,'Export parity evidence is invalid JSON');}}
  if(receipt){
   check(receipt.schema_version===1&&receipt.method==='supervisor-c12-authored-body-parity','Export parity method/schema');
   check(typeof receipt.checked_at==='string'&&/T.*(?:Z|[+-]\d\d:\d\d)$/.test(receipt.checked_at)&&Number.isFinite(Date.parse(receipt.checked_at)),'Export parity timestamp requires timezone');
   for(const key of ['markdown','canonical_text'])check(receipt[key]?.path===registry[key]?.path&&receipt[key]?.sha256===registry[key]?.sha256,'Parity evidence '+key+' binding differs');
   bound(receipt.verifier,'Export verifier source');
   check(typeof receipt.verifier?.path==='string'&&receipt.verifier.path.endsWith('/verify_edition.py'),'Unexpected export verifier source');
   const records=Array.isArray(receipt.exports)?receipt.exports:[];
   check(records.length===2&&new Set(records.map(record=>record.path)).size===2,'Parity evidence export cardinality');
   for(const entry of exports){const match=records.find(record=>record.path===entry.path);check(match&&['path','sha256','text_path','text_sha256'].every(key=>match[key]===entry[key]),'Parity evidence export binding differs: '+entry.path);}
  }else check(false,'Export parity evidence absent');
  for(const entry of exports){
   const binary=bound(entry,'Reviewed export '+entry.path);
   check(typeof entry.license==='string'&&entry.license.trim().length>10&&!/unknown|unclear|pending|unreviewed/i.test(entry.license),'Reviewed export rights absent: '+entry.path);
   const text=bound({path:entry.text_path,sha256:entry.text_sha256},'Extracted body '+entry.path,supervisorEvidence);
   if(binary){const valid=entry.path.endsWith('.pdf')?binary.subarray(0,5).toString()==='%PDF-':binary.subarray(0,4).equals(Buffer.from([0x50,0x4b,0x03,0x04]));check(valid,'Reviewed export signature invalid: '+entry.path);}
   if(text){check(privacyHazards(text.toString('utf8')).length===0,'Private content in export surrogate: '+entry.path);check(canonical&&normalizedBody(text.toString('utf8'))===normalizedBody(canonical.toString('utf8')),'Export body differs from authored canonical text: '+entry.path);}
  }
 }catch(error){check(false,'Malformed reviewed export evidence: '+error.message);}
 return {checks,failures,allowedPaths:new Set(failures.length?[]:exports.map(entry=>entry.path))};
}

export function checkInlineScripts(html) {
 const failures=[];let checks=0;
 const scripts=[...html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/gi)];
 if(scripts.length!==[...html.matchAll(/<script\b/gi)].length)failures.push('Unclosed inline script element');
 for(const [index,match] of scripts.entries()){
  checks++;
  const attributes=[...match[1].matchAll(/\btype\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))/gi)];
  if(attributes.length>1){failures.push('Duplicate script type attribute '+index);continue;}
  const type=(attributes[0]?.slice(1).find(value=>value!==undefined)||'').trim().toLowerCase().split(';')[0];
  try{if(type==='application/json'||type==='application/ld+json')JSON.parse(match[2]);else new vm.Script(match[2]);}
  catch(error){failures.push((type==='application/json'||type==='application/ld+json'?'Invalid JSON script ':'Inline script syntax ')+index+': '+error.message);}
 }
 return {checks,failures};
}
