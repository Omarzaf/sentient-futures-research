import {isExcludedPath, privacyHazards} from './privacy-checks.mjs';

const NOTICE='AI-assisted working draft; human verification pending';
const CITABLE=new Set(['verified','verified_with_note']);
const VERDICTS=new Set([...CITABLE,'replace_link','not_retrieved','quote_not_found','failed','held']);
const RECHECKS=new Set(['supported','premise_supported','partly_supported','unsupported','not_retrieved','held','quote_not_found']);
const SUPPORT=new Set(['supported','premise_supported']);
const KINDS=new Set(['evidence','inference','mixed','gap','framing']);
const TARGETS={Abstract:250,1:800,2:900,3:800,4:900,5:1300,6:1200,7:1000,8:800,9:1600,10:800,11:1200,12:450,13:300};
const keyPattern=/^[A-Z][A-Z0-9-]*$/;
const nonempty=value=>typeof value==='string'&&value.trim().length>0;
const object=value=>value!==null&&typeof value==='object'&&!Array.isArray(value);
const escape=value=>value.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');

/** Normalize exact quotations without removing punctuation or translating text. */
export function normalizeQuote(text) {
 return String(text??'').normalize('NFC')
  .replace(/[\u064B-\u0652\u0670\u0640]/g,'')
  .replace(/[أإآٱ]/g,'ا').replace(/ى/g,'ي')
  .replace(/[“”„‟«»]/g,'"').replace(/[‘’‚‛]/g,"'")
  .replace(/[‐‑‒–—―−]/g,'-').replace(/\s+/gu,' ').trim();
}

function terminalKeys(text) {
 const suffix=text.match(/((?:\s*\[[A-Z][A-Z0-9-]*(?:\s*[;,]\s*[A-Z][A-Z0-9-]*)*\])+)[\s.]*$/);
 return suffix?[...suffix[1].matchAll(/\[([^\]]+)\]/g)].flatMap(match=>match[1].split(/[;,]/).map(key=>key.trim())):[];
}

function visible(text) {
 return text.replace(/<!--[\s\S]*?-->/g,'').replace(/\[\^[^\]]+\]/g,'')
  .replace(/!?\[([^\]]*)\]\([^)]*\)/g,'$1').replace(/<[^>]*>/g,'').replace(/[*_`]/g,'').trim();
}

// Parse the supported manuscript Markdown dialect: ATX headings, paragraphs,
// tables/lists, fenced code, and indented continuation lines in footnotes.
function manuscript(text) {
 const lines=text.split(/\r?\n/),paragraphs=[],notes=[],bibliography=[];
 let buffer=[],start=0,section=null,inBibliography=false,bibliographyLevel=0,fence=null;
 const flush=()=>{
  if(buffer.length){const block={text:buffer.join('\n'),line:start+1,section};
   (inBibliography?bibliography:paragraphs).push(block);buffer=[];}
 };
 for(let index=0;index<lines.length;index++) {
  const line=lines[index],fenced=line.match(/^\s*(`{3,}|~{3,})/);
  if(fenced){flush();if(!fence)fence=fenced[1][0];else if(fence===fenced[1][0])fence=null;continue;}
  if(fence)continue;
  const heading=line.match(/^(#{1,6})\s+(.+?)\s*#*$/);
  if(heading){
   flush();const title=heading[2],number=title.match(/^(?:§\s*)?(\d{1,2})(?:\.\d+)*(?:[.)\s]|$)/);
   if(inBibliography&&heading[1].length<=bibliographyLevel)inBibliography=false;
   if(/^Bibliography(?:\s|$)/i.test(title)){inBibliography=true;bibliographyLevel=heading[1].length;}
   else if(/^Abstract$/i.test(title))section='Abstract';
   else if(number)section=Number(number[1]);
   else if(/^(?:Appendix\s+)?[A-E](?:[.:\s]|$)/.test(title))section='appendix';
   continue;
  }
  const definition=line.match(/^ {0,3}\[\^([^\]\s]+)\]:\s*(.*)$/);
  if(definition){
   flush();const pieces=[definition[2]];
   while(index+1<lines.length&&(/^(?: {4}|\t)\S?/.test(lines[index+1])||(!lines[index+1].trim()&&/^(?: {4}|\t)/.test(lines[index+2]||''))))pieces.push(lines[++index].replace(/^(?: {4}|\t)/,''));
   notes.push({id:definition[1],text:pieces.join('\n'),line:index+1});continue;
  }
  if(!line.trim()){flush();continue;}
  // A trace on its own line after a blank line still annotates the preceding
  // paragraph; two traces remain an error, rather than silently choosing one.
  if(/^\s*<!--\s*trace:/.test(line)&&!buffer.length&&!inBibliography&&paragraphs.at(-1)?.section===section){paragraphs.at(-1).text+='\n'+line;continue;}
  if(!buffer.length)start=index;
  buffer.push(line);
 }
 flush();return {paragraphs,notes,bibliography};
}

function quotations(text) {
 const quotes=[];
 for(const pattern of [/"([^"\n]+)"/g,/“([^”]+)”/g,/«([^»]+)»/g,/(?:^|[\s([{])'([^'\n]+)'/g,/(?:^|[\s([{])‘([^’]+)’/g]) {
  for(const match of text.matchAll(pattern))if(normalizeQuote(match[1]).split(/\s+/).length>=4)quotes.push(match[1]);
 }
 if(/^\s*>/m.test(text))quotes.push(text.split('\n').filter(line=>/^\s*>/.test(line)).map(line=>line.replace(/^\s*>\s?/, '')).join(' '));
 return quotes.filter(quote=>normalizeQuote(quote).split(/\s+/).length>=4);
}

function claimsApproval(text) {
 const positive=/(?:mentor[- ]approved|scholarly[- ]approved|institutionally approved|approved by (?:a |the |our )?(?:mentor|scholar|institution)|(?:received|has|have) (?:scholarly|mentor|institutional) (?:approval|endorsement)|(?:scholarly|mentor|institutional) (?:approval|endorsement) (?:has been|was|is) (?:given|granted|received|obtained|confirmed))/gi;
 for(const match of text.matchAll(positive)) {
  const before=text.slice(Math.max(0,match.index-80),match.index);
  if(/\b(?:no|not|never|without)(?:\s+(?:yet|been|received|regarded|considered|as|formally|ever)){0,4}\s*$/i.test(before))continue;
  return true;
 }
 return false;
}

function forbiddenReviewFlags(value,path='') {
 if(!object(value)&&!Array.isArray(value))return [];
 return Object.entries(value).flatMap(([key,child])=>{
  const normalized=key.replace(/[_-]/g,'').toLowerCase();
  const flag=/(?:human|mentor|scholar|institution).*(?:review|approv|endorse)|(?:review|approv).*(?:human|mentor|scholar)/.test(normalized);
  const nested=forbiddenReviewFlags(child,path+key+'.');
  return flag&&child===true?[path+key,...nested]:nested;
 });
}

function bibliographyEssentials(source,verdict) {
 const bibliography=source.bibliographic;
 if(!object(bibliography)||!nonempty(bibliography.title)||!nonempty(bibliography.author??source.issuer))return false;
 const type=String(source.source_type??source.type??'').toLowerCase();
 if(/quran|translation|translated/.test(type)&&!nonempty(bibliography.translator))return false;
 if(/classical|book/.test(type)&&(!nonempty(String(bibliography.volume??''))||!nonempty(String(bibliography.page??''))))return false;
 if(/article|peer.review/.test(type)&&(!nonempty(source.doi)||!nonempty(String(bibliography.year??''))))return false;
 if(/translation|translated/.test(type)&&verdict==='verified'&&(!nonempty(bibliography.publisher)||!bibliography.year))return false;
 return true;
}

/** Check immutable file contents; no filesystem, network, or approval mutation. */
export function checkPaper(files,{phaseOneFiles={},stage:stageOverride}={}) {
 const failures=[],warnings=[];let checks=0;
 const check=(ok,message)=>{checks++;if(!ok)failures.push('Paper: '+message);};
 const warn=(ok,message)=>{checks++;if(!ok)warnings.push('Paper: '+message);};
 if(!object(files)){check(false,'files must be an object');return {checks,failures,warnings};}
 const read=(name,container=files,array=true)=>{
  try {const value=JSON.parse(container[name]);if(array?!Array.isArray(value):!object(value))throw Error('shape');return value;}
  catch {check(false,'missing or invalid '+name+(container===files?'':' in Phase One'));return array?[]:{};}
 };
 const sources=read('source-register.json'),audits=read('citation-audit.json'),added=read('claims-added.json');
 const coverage=read('coverage.json'),allowlist=read('allowlist.json'),searches=read('search-log.json');
 const state=read('execution-state.json',files,false),stage=stageOverride??state.stage;
 check(Number.isInteger(stage)&&stage>=0&&stage<=7,'stage must be an integer from 0 to 7');
 check(stageOverride===undefined||state.stage===stageOverride,'stage override disagrees with execution state');
 const drafting=stage>=5;
 check(typeof files['paper.md']==='string','missing paper.md');
 for(const [name,text] of Object.entries(files)) {
  check(typeof text==='string','non-text input: '+name);
  if(typeof text!=='string')continue;
  check(!isExcludedPath(name),'excluded file or path: '+name);
  for(const hazard of privacyHazards(text))check(false,hazard+': '+name);
  check(!/\bINTERVIEW\b|\bEN0[1-6]\b|IMG 7313|interview-map\.json|\/private\/tmp\//.test(text),'private-source reference: '+name);
 }
 // A parse failure must never fall through into success with empty registers.
 if(failures.some(item=>/missing or invalid|files must|stage must|missing paper\.md|non-text/.test(item)))return {checks,failures,warnings};
 const phase={};
 for(const name of ['claims','school-questions','counter-evidence','gaps','source-register','historical-comparisons','country-findings']) {
  if(stage>=1||phaseOneFiles[name+'.json']!==undefined)phase[name]=read(name+'.json',phaseOneFiles);
  else phase[name]=[];
 }
 if(failures.some(item=>/missing or invalid/.test(item)))return {checks,failures,warnings};
 for(const [name,rows] of Object.entries({sources,audits,added,coverage,allowlist,searches,...phase}))check(rows.every(object),'non-object record: '+name);
 if(failures.some(item=>/non-object record/.test(item)))return {checks,failures,warnings};
 // Validate nested collections before traversing them. Malformed evidence must
 // produce a failed check rather than throw or silently become an empty list.
 const structuralFailures=failures.length;
 for(const row of [...added,...phase.claims,...phase['school-questions'],...phase['historical-comparisons'],...phase['country-findings']])check(Array.isArray(row.source_ids)&&row.source_ids.every(nonempty),'invalid record source list: '+row.id);
 for(const [index,row] of phase['counter-evidence'].entries())check(Array.isArray(row.counter_source_ids)&&row.counter_source_ids.every(nonempty),'invalid counter-evidence source list: CE'+(index+1));
 for(const audit of audits) {
  check(audit.passages===undefined||(Array.isArray(audit.passages)&&audit.passages.every(row=>object(row)&&nonempty(row.locator)&&nonempty(row.text))),'invalid stored audit passage: '+audit.key);
  check(Array.isArray(audit.claims_rechecked)&&audit.claims_rechecked.every(row=>object(row)&&nonempty(row.id)&&RECHECKS.has(row.result)),'invalid claim recheck result: '+audit.key);
 }
 if(failures.length>structuralFailures)return {checks,failures,warnings};
 for(const [name,value] of Object.entries({state,sources,audits,added,coverage}))for(const flag of forbiddenReviewFlags(value))check(false,'review flag must remain false: '+name+'.'+flag);
 if(drafting)check(state.outlineApproved===true,'drafting requires the recorded human outline checkpoint');
 const validAllowRules=new Set(['phrase','source_scope']);
 for(const row of allowlist)check(validAllowRules.has(row.rule)&&nonempty(row.match)&&nonempty(row.reason),'invalid allowlist entry or missing reason');
 const allowed=(rule,match)=>allowlist.some(row=>row.rule===rule&&row.match===match&&nonempty(row.reason));
 const aliases=new Map(),byKey=new Map();
 for(const source of sources) {
  const key=source.key??source.id;
  check(keyPattern.test(key||''),'invalid canonical source key');
  check(!byKey.has(key),'duplicate canonical source: '+key);byKey.set(key,source);
  check(Array.isArray(source.aliases)&&source.aliases.every(alias=>keyPattern.test(alias)),'invalid aliases: '+key);
  for(const alias of [key,...(Array.isArray(source.aliases)?source.aliases:[])]) {
   check(!aliases.has(alias),'ambiguous or duplicate alias: '+alias);
   if(!aliases.has(alias))aliases.set(alias,key);
  }
  check(source.id===undefined||source.id===key,'source id differs from canonical key: '+key);
  if(stage>=1) {
   check(nonempty(source.title)&&nonempty(source.url)&&nonempty(source.locator),'missing source identity or locator: '+key);
   check(object(source.bibliographic)&&['author','title','translator','editor','publisher','place','year','volume','page'].every(field=>Object.hasOwn(source.bibliographic,field)),'missing bibliographic fields: '+key);
  }
  if(stage>=2)check(VERDICTS.has(source.audit_verdict),'missing audit verdict: '+key);
 }
 const auditByKey=new Map();
 for(const audit of audits) {
  const key=aliases.get(audit.key);
  check(!!key&&audit.key===key,'audit key is unknown or noncanonical: '+audit.key);
  check(!auditByKey.has(key),'duplicate citation audit: '+audit.key);auditByKey.set(key,audit);
  check(VERDICTS.has(audit.verdict),'invalid audit verdict: '+audit.key);
  if(key)check(byKey.get(key).audit_verdict===audit.verdict,'register/audit verdict mismatch: '+key);
  const passages=Array.isArray(audit.passages)?audit.passages:[];
  check(passages.every(passage=>object(passage)&&nonempty(passage.locator)&&nonempty(passage.text)),'invalid stored audit passage: '+audit.key);
  if(CITABLE.has(audit.verdict)) {
   if(audit.verdict==='verified_with_note')check(nonempty(audit.notes),'verified_with_note lacks its qualification: '+audit.key);
   check(Number.isInteger(audit.http_status)&&audit.http_status>=200&&audit.http_status<300&&/^https?:\/\//.test(audit.final_url||'')&&nonempty(audit.content_type)&&nonempty(audit.retrieved_at)&&Number.isFinite(Date.parse(audit.retrieved_at)),'verified audit lacks successful retrieval metadata: '+audit.key);
   check(nonempty(audit.host_type)&&nonempty(audit.family)&&/^[a-f0-9]{64}$/i.test(audit.sha256??audit.capture_sha256??''),'verified audit lacks host, family or capture hash: '+audit.key);
   check(audit.quote_found===true&&audit.locator_found===true&&audit.bibliographic_complete===true,'verified audit lacks passage, locator or bibliography: '+audit.key);
   const checkedUndated=audit.verdict==='verified_with_note'&&audit.identity?.date===false&&audit.date_status==='undated'&&nonempty(audit.date_note)&&byKey.get(key)?.bibliographic?.year===null;
   check(object(audit.identity)&&['title','issuer'].every(field=>audit.identity[field]===true)&&(audit.identity.date===true||checkedUndated),'verified audit lacks identity check: '+audit.key);
   check(nonempty(audit.quote_expected)&&passages.some(passage=>normalizeQuote(passage.text).includes(normalizeQuote(audit.quote_expected))),'verified quote absent from stored passages: '+audit.key);
   const source=byKey.get(key);
   if(source){
    check(nonempty(source.short_exact_quote)&&passages.some(passage=>normalizeQuote(passage.text).includes(normalizeQuote(source.short_exact_quote))),'register quote absent from stored passages: '+key);
    check(bibliographyEssentials(source,audit.verdict),'verified source lacks bibliographic essentials: '+key);
   }
  }
  check(Array.isArray(audit.claims_rechecked)&&audit.claims_rechecked.every(row=>object(row)&&nonempty(row.id)&&RECHECKS.has(row.result)),'invalid claim recheck result: '+audit.key);
  if(Array.isArray(audit.claims_rechecked))check(new Set(audit.claims_rechecked.map(row=>row.id)).size===audit.claims_rechecked.length,'duplicate claim recheck: '+audit.key);
 }
 if(stage>=2)for(const key of byKey.keys())check(auditByKey.has(key),'source has no citation audit: '+key);
 const records=new Map(),expectedCoverage=[];
 const registerRecords=(rows,kind,prefix='',sourceField='source_ids')=>{
  for(const [index,row] of rows.entries()) {
   const id=row.id??(kind==='counter_evidence'?'CE'+(index+1):undefined),trace=prefix+id;
   check(nonempty(id),'missing record ID: '+kind);
   if(records.has(trace)&&kind!=='school'&&kind!=='country')check(false,'duplicate record ID: '+trace);
   if(!records.has(trace))records.set(trace,{...row,id,source_ids:row[sourceField]??[],recordKind:kind});
   expectedCoverage.push({kind,id,trace});
  }
 };
 registerRecords(phase.claims,'claim');
 registerRecords(phase['school-questions'],'school');
 registerRecords(phase['counter-evidence'],'counter_evidence','ce:','counter_source_ids');
 registerRecords(phase.gaps,'gap','gap:');
 registerRecords(phase['historical-comparisons'],'historical','historical:');
 registerRecords(phase['country-findings'],'country');
 for(const claim of added){check(/^P-[A-Z0-9-]+$/.test(claim.id||''),'new claim lacks P- namespace');check(nonempty(claim.status)&&nonempty(claim.kind)&&Array.isArray(claim.source_ids),'new claim lacks status or sources: '+claim.id);}
 registerRecords(added,'claim');
 const claimIds=new Set([...phase.claims,...added].map(row=>row.id));
 if(stage>=2) {
  for(const audit of audits)for(const recheck of audit.claims_rechecked??[])check(claimIds.has(recheck.id),'unknown rechecked claim: '+recheck.id);
  for(const claim of [...phase.claims,...added])for(const id of claim.source_ids??[]) {
   const canonical=aliases.get(id),audit=auditByKey.get(canonical);
   check(!!canonical,'claim has unresolved source: '+claim.id+' / '+id);
   check(audit?.claims_rechecked?.some(row=>row.id===claim.id&&RECHECKS.has(row.result)),'claim-source pair has no recorded recheck: '+claim.id+' / '+id);
  }
 }
 for(const source of phase['source-register'])expectedCoverage.push({kind:'source',id:source.id,trace:null});
 const coverageById=new Map();
 for(const row of coverage) {
  const identity=row.kind+':'+row.id;
  check(!coverageById.has(identity),'duplicate coverage: '+identity);coverageById.set(identity,row);
  check(expectedCoverage.some(expected=>expected.id===row.id&&expected.kind===row.kind),'unknown coverage record: '+identity);
  check(['planned','included','excluded'].includes(row.disposition),'invalid coverage disposition: '+identity);
  check(Array.isArray(row.sections),'invalid coverage sections: '+identity);
  check(row.disposition==='excluded'?nonempty(row.reason):Array.isArray(row.sections)&&row.sections.length>0,'coverage requires section or exclusion reason: '+identity);
 }
 if(stage>=1)for(const row of expectedCoverage)check(coverageById.has(row.kind+':'+row.id),'missing coverage: '+row.kind+':'+row.id);
 for(const search of searches)check(nonempty(search.date)&&Array.isArray(search.terms)&&search.terms.length>0&&Array.isArray(search.hosts)&&search.hosts.length>0&&nonempty(search.result),'incomplete search record');
 const text=files['paper.md'],firstLines=text.split(/\r?\n/).map(line=>line.trim()).filter(Boolean);
 check(/^#\s+\S/.test(firstLines[0]||'')&&firstLines[1]?.replace(/^[*_]+|[*_]+$/g,'')===NOTICE,'draft notice must appear immediately under title');
 const prose=visible(text);
 check(!claimsApproval(prose),'unwarranted scholarly or mentor approval');
 if(drafting)check(!/^\s*(?:`{3,}|~{3,})/m.test(text),'manuscript prose cannot be hidden in fenced code');
 const parsed=manuscript(text),definitions=new Map(),usedNotes=new Set(),citedKeys=new Set(),traced=new Set();
 if(!drafting) {
  const nonNotice=parsed.paragraphs.map(paragraph=>visible(paragraph.text)).filter(body=>body&&body!==NOTICE);
  check(!/^#{2,6}\s/m.test(text)&&parsed.notes.length===0&&parsed.bibliography.length===0&&nonNotice.length<=1&&nonNotice.every(body=>/^Scaffold(?: only)?\. (?:Manuscript drafting awaits|Drafting has not begun|Drafting is pending)[^.]*\.$/.test(body)),'draft body is not permitted before stage 5');
 }
 for(const note of parsed.notes) {
  check(!definitions.has(note.id),'duplicate footnote definition: '+note.id);
  note.keys=terminalKeys(note.text);
  check(note.keys.length>0,'footnote definition lacks terminal source key: '+note.id);
  note.canonical=[];
  for(const key of note.keys){const canonical=aliases.get(key);check(!!canonical,'unknown footnote source: '+key);if(canonical)note.canonical.push(canonical);}
  definitions.set(note.id,note);
 }
 const sectionWords=new Map();
 for(const paragraph of parsed.paragraphs) {
  const traceMatches=[...paragraph.text.matchAll(/<!--\s*trace:\s*([^|]*?)\s*\|\s*kind:\s*([a-z_]+)([^]*?)-->/g)];
  const ids=traceMatches[0]?.[1].trim().split(/\s+/).filter(Boolean)??[],kind=traceMatches[0]?.[2];
  const annotation=traceMatches[0]?.[3]??'',notes=[...paragraph.text.matchAll(/\[\^([^\]\s]+)\]/g)].map(match=>match[1]);
  const body=visible(paragraph.text),substantive=!!body&&!body.includes(NOTICE)&&!/^[-:|\s]+$/.test(body);
  sectionWords.set(paragraph.section,(sectionWords.get(paragraph.section)||0)+(body.match(/[\p{L}\p{N}]+(?:['’-][\p{L}\p{N}]+)*/gu)||[]).length);
  if(notes.length||(drafting&&substantive&&paragraph.section>=5&&paragraph.section<=11))check(traceMatches.length===1,'paragraph requires exactly one trace at line '+paragraph.line);
  if(traceMatches.length){
   check(traceMatches.length===1&&paragraph.text.trim().endsWith(traceMatches.at(-1)[0]),'trace must end its paragraph at line '+paragraph.line);
   check(KINDS.has(kind),'invalid trace kind at line '+paragraph.line);
   check(ids.length>0||kind==='framing','empty non-framing trace at line '+paragraph.line);
   check(kind!=='framing'||notes.length===0,'framing paragraph has a footnote at line '+paragraph.line);
   for(const id of ids){check(records.has(id),'unresolved traced ID: '+id);traced.add(id);}
   const tracedRecords=ids.map(id=>records.get(id)).filter(Boolean);
   if(tracedRecords.some(row=>row.kind==='inference'||row.status==='inference'))check(['inference','mixed'].includes(kind),'inference trace upgraded at line '+paragraph.line);
   if(ids.includes('J-Q1'))check((kind==='gap'||(kind==='mixed'&&/\|\s*open:\s*J-Q1(?:\s|$)/.test(annotation)))&&/\bopen\b|not located|not established|unresolved/i.test(body),'J-Q1 must remain explicitly open at line '+paragraph.line);
   if(tracedRecords.some(row=>row.status==='held_language'))check(kind==='gap','held-language record used as evidence at line '+paragraph.line);
  }
  const paragraphKeys=new Set();
  for(const noteId of notes) {
   usedNotes.add(noteId);const note=definitions.get(noteId);
   check(!!note,'undefined footnote: '+noteId);
   for(const key of note?.canonical??[]){paragraphKeys.add(key);citedKeys.add(key);}
  }
  const scope=new Set(ids.flatMap(id=>records.get(id)?.source_ids??[]).map(id=>aliases.get(id)).filter(Boolean));
  if(drafting&&['evidence','mixed','inference'].includes(kind)&&scope.size>0)check(notes.length>0||allowed('source_scope','uncited|'+ids.join(' ')),'source-backed paragraph requires a footnote at line '+paragraph.line);
  for(const key of paragraphKeys){
   check(CITABLE.has(byKey.get(key)?.audit_verdict)&&CITABLE.has(auditByKey.get(key)?.verdict),'uncitable source: '+key);
   check(scope.has(key)||allowed('source_scope',key+'|'+ids.join(' ')),'footnote source outside traced records: '+key+' at line '+paragraph.line);
  }
  if(drafting)for(const id of ids.filter(id=>claimIds.has(id))) {
   const record=records.get(id);
   if(record?.status==='open'||record?.status==='held_language'||kind==='gap'||kind==='framing')continue;
   const relevantKeys=[...paragraphKeys].filter(key=>(record.source_ids??[]).some(sourceId=>aliases.get(sourceId)===key));
   const results=relevantKeys.map(key=>auditByKey.get(key)?.claims_rechecked?.find(row=>row.id===id)?.result);
   check((results.length>0&&results.every(result=>SUPPORT.has(result)))||allowed('source_scope','uncited|'+ids.join(' ')),'paragraph claim lacks cited supporting recheck: '+id+' at line '+paragraph.line);
  }
  const passages=[...paragraphKeys].flatMap(key=>auditByKey.get(key)?.passages??[]).map(passage=>normalizeQuote(passage.text));
  for(const quote of quotations(body))check(passages.some(passage=>passage.includes(normalizeQuote(quote))),'quotation does not match same-paragraph cited passage at line '+paragraph.line+': '+quote);
  for(const id of records.keys())if(new RegExp('(?<![\\w-])'+escape(id)+'(?![\\w-])').test(body))check(false,'raw record ID in prose: '+id+' at line '+paragraph.line);
 }
 for(const id of definitions.keys())check(usedNotes.has(id),'unused footnote definition: '+id);
 if(drafting)for(const row of expectedCoverage) {
  const disposition=coverageById.get(row.kind+':'+row.id);
  if(row.kind==='source')continue;
  // School and country IDs also occur in the claims register; their traces
  // are shared. Historical IDs are separately namespaced to avoid H01 collisions.
  const included=traced.has(row.trace);
  check(included||(disposition?.disposition==='excluded'&&nonempty(disposition.reason)),'record neither traced nor explicitly excluded: '+row.kind+':'+row.id);
  if(disposition?.disposition==='excluded')check(!included,'excluded record is nevertheless traced: '+row.kind+':'+row.id);
 }
 const bibliographyKeys=[];
 for(const entry of parsed.bibliography) {
  const keys=terminalKeys(entry.text);
  check(keys.length===1,'bibliography entry must end in one canonical key at line '+entry.line);
  for(const key of keys){check(byKey.has(key),'bibliography key is unknown or an alias: '+key);bibliographyKeys.push(key);}
 }
 check(new Set(bibliographyKeys).size===bibliographyKeys.length,'duplicate bibliography key');
 for(const key of citedKeys)check(bibliographyKeys.includes(key),'cited key missing from bibliography: '+key);
 for(const key of bibliographyKeys)check(citedKeys.has(key),'uncited bibliography key: '+key);
 const scanned=parsed.paragraphs.map(paragraph=>visible(paragraph.text)).join('\n');
 const phrases=/\bis halal\b|\bare halal\b|\bhalal[- ]certified\b|\bunanimous\b|\bconsensus\b|\ball schools\b|\bproves\b|\bconfirms\b|\bsettles\b|\bIslam permits\b|\bIslam forbids\b|\bapproved\b/gi;
 for(const match of scanned.matchAll(phrases)) {
  if(/^approved$/i.test(match[0])) {
   const nearby=scanned.slice(Math.max(0,match.index-100),match.index+match[0].length+100);
   if(!/\b(?:India|Pakistan|Saudi Arabia|UAE|United Arab Emirates|Singapore|Malaysia|Indonesia|GOOD Meat|Eat Just|Upside|chicken|product|cultivated meat)\b/i.test(nearby))continue;
  }
  const acknowledged=allowed('phrase',match[0]);
  warn(acknowledged,'unacknowledged phrase: '+match[0]);
  if(drafting)check(acknowledged,'phrase requires correction or reasoned allowlist: '+match[0]);
 }
 const counts={claims:phase.claims.length,findings:phase.claims.length,sources:phase['source-register'].length,'source records':phase['source-register'].length,slots:phase['school-questions'].length,'school questions':phase['school-questions'].length,'school slots':phase['school-questions'].length,countries:phase['country-findings'].length,'country accounts':phase['country-findings'].length,'counter-evidence records':phase['counter-evidence'].length,gaps:phase.gaps.length,'gap records':phase.gaps.length,'historical analogies':phase['historical-comparisons'].length,'historical comparisons':phase['historical-comparisons'].length};
 for(const match of scanned.matchAll(/\b(\d+)\s+(claims|findings|sources|source records|slots|school questions|school slots|countries|country accounts|counter-evidence records|gaps|gap records|historical analogies|historical comparisons)\b/gi)) {
  const label=match[2].toLowerCase(),before=scanned.slice(Math.max(0,match.index-70),match.index);
  let expected=counts[label];
  if(/(?:paper|canonical)(?:\s+source)?\s+register[^.!?\n]*$/i.test(before))expected=['sources','source records'].includes(label)?sources.length:label==='claims'?phase.claims.length+added.length:expected;
  check(Number(match[1])===expected,'stated register count mismatch: '+match[0]+' (expected '+expected+')');
 }
 if(drafting)for(const [section,target] of Object.entries(TARGETS)) {
  const words=sectionWords.get(section==='Abstract'?section:Number(section))||0;
  warn(words>=target*0.8&&words<=target*1.2,'section '+section+' word count '+words+' outside '+Math.ceil(target*0.8)+'–'+Math.floor(target*1.2));
 }
 return {checks,failures,warnings};
}
