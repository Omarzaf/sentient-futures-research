import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import vm from 'node:vm';
import {fileURLToPath} from 'node:url';
import {checkHalal,parseCsv} from './halal-checks.mjs';
import {checkPhaseOne} from './phase1-checks.mjs';
import {checkPaper} from './paper-checks.mjs';
import {checkContinuation} from './continuation-checks.mjs';
import {checkSurvey} from './survey-checks.mjs';
import {isExcludedPath, privacyHazards, privacyHazardNames, reviewedBinaryExports, isReviewedBinaryExport} from './privacy-checks.mjs';
import {repoFiles,unescapeEntities} from './repo-files.mjs';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
const json=p=>JSON.parse(read(p));
const failures=[];let checks=0;
const check=(ok,msg)=>{checks++;if(!ok)failures.push(msg);};
const paths=repoFiles(root);
const manifest=json('provenance/file-manifest.json').files;
check(new Set(manifest.map(f=>f.path)).size===manifest.length,'Duplicate manifest paths');
check(JSON.stringify(paths.filter(p=>p!=='provenance/file-manifest.json'))===JSON.stringify(manifest.map(f=>f.path).sort()),'Manifest does not match repository files');
for(const f of manifest){const b=fs.readFileSync(path.join(root,f.path));check(b.length===f.bytes&&crypto.createHash('sha256').update(b).digest('hex')===f.sha256,'Hash/size mismatch: '+f.path);}

for(const p of paths){check(!isExcludedPath(p),'Excluded file type or path: '+p);check(!fs.lstatSync(path.join(root,p)).isSymbolicLink(),'Symlink: '+p);if(Object.hasOwn(reviewedBinaryExports,p)){check(isReviewedBinaryExport(p,fs.readFileSync(path.join(root,p))),'Reviewed export bytes changed: '+p);continue;}const s=read(p);const foundHazards=new Set(privacyHazards(s));for(const name of privacyHazardNames)check(!foundHazards.has(name),name+': '+p);if(p.endsWith('.json')){try{JSON.parse(s);check(true,'JSON');}catch{check(false,'Invalid JSON: '+p);}}}

let internalLinks=0;
for(const p of paths.filter(p=>/\.(html|md|svg)$/.test(p))){
 const text=read(p);let targets=[...text.matchAll(/(?:href|src)=["']([^"']*)["']/g)].map(m=>m[1]);
 if(p.endsWith('.md'))targets.push(...[...text.matchAll(/\[[^\]]*\]\(([^)]+)\)/g)].map(m=>m[1].replace(/^<|>$/g,'')));
 for(const raw of targets){
  const href=unescapeEntities(raw);if(/^(?:https?:|data:|mailto:)/i.test(href)||href==='')continue;
  if(/^[a-z]+:/i.test(href)){check(false,'Unexpected URL scheme '+p+': '+href);continue;}
  const [part,fragment]=href.split('#');let dest;
  try{dest=part?path.posix.normalize(path.posix.join(path.posix.dirname(p),decodeURIComponent(part.split('?')[0]))):p;}catch{check(false,'Invalid link encoding '+p);continue;}
  internalLinks++;check(!dest.startsWith('../')&&paths.includes(dest),'Broken or escaping relative link '+p+' -> '+href);
  if(fragment&&paths.includes(dest)&&/\.(html|svg)$/.test(dest)){
   let anchor;try{anchor=decodeURIComponent(fragment);}catch{check(false,'Invalid anchor encoding '+p+' -> '+href);continue;}
   const ids=[...read(dest).matchAll(/\bid=["']([^"']+)["']/g)].map(m=>m[1]);
   check(ids.includes(anchor),'Missing anchor '+p+' -> '+href);
  }
 }
 if(p.endsWith('.html')){
  check(/<html[^>]+lang=/.test(text),'Missing document language '+p);
  check(/name=["']viewport["']/.test(text),'Missing viewport '+p);
  check(!/<(?:script|img|iframe|link)\b[^>]*(?:src|href)=["']https?:\/\//i.test(text),'Automatic external asset load '+p);
  for(const m of text.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)){try{new vm.Script(m[1]);check(true,'Inline script');}catch(e){check(false,'Inline script syntax '+p+': '+e.message);}}
 }
}

const comparative=json('research/comparative-protein/source-register.json');
const foundation=json('research/ai-protein/source-register.json');
const currentReview=json('research/india-pakistan/source-register.json');
const sourceIds=new Set(comparative.map(r=>r.id));
check(comparative.length===60&&sourceIds.size===60,'Comparative source count/IDs');
check(foundation.length===44&&new Set(foundation.map(r=>r.id)).size===44,'Foundation source count/IDs');
check(foundation.every(r=>r.human_verification==='Pending'),'Unexpected foundation review status');
check(currentReview.length===20&&new Set(currentReview.map(r=>r.id)).size===20,'Current-review source count/IDs');
check(currentReview.every(r=>r.human_verification==='Pending'),'Unexpected current-review status');
check(currentReview.every(r=>/^https?:\/\//.test(r.url||'')),'Current-review record without a public URL');
const passages=json('research/comparative-protein/claim-ledger.json').passages;
check(passages.every(p=>p.humanReview==='Pending'),'Unexpected claim review status');
for(const p of passages)for(const id of p.sourceIds)check(sourceIds.has(id),'Unknown passage source '+p.id+': '+id);
const figures=json('research/comparative-protein/figure-data.json');
const populated=figures.countries.filter(d=>Number.isFinite(d.total2023));
check(figures.countries.length===13&&populated.length===12,'Country observation/missing count');
check(figures.hubs.length===14,'Capability record count');
for(const r of populated){check(Math.abs(r.total2023-r.animal2023-r.plant2023)<0.11,'Plant supply arithmetic '+r.country);check(Math.abs(100*r.animal2023/r.total2023-r.animalShare2023)<0.051,'Share arithmetic '+r.country);}
const missing=figures.countries.find(r=>r.country==='Singapore');check(missing?.missing===true&&!Number.isFinite(missing.total2023),'Missing-country value was imputed');
for(const h of figures.hubs){check(Number.isFinite(h.lat)&&Number.isFinite(h.lon)&&Math.abs(h.lat)<=90&&Math.abs(h.lon)<=180,'Invalid location '+h.id);for(const id of h.sourceIds)check(sourceIds.has(id),'Unknown hub source '+id);}
// The page carries its own copy of the figure data for the interactive map.
const page=read('research/comparative-protein/index.html');
for(const k of ['countries','hubs']){let embedded=null;try{embedded=JSON.parse(new RegExp('const '+k+'=(\\[[\\s\\S]*?\\]);').exec(page)[1]);}catch{}check(JSON.stringify(embedded)===JSON.stringify(figures[k]),'Page data differs from figure-data.json: '+k);}
const [columns,...csvRows]=parseCsv(read('research/comparative-protein/protein-data.csv'));
const parsed=csvRows.map(cells=>Object.fromEntries(cells.map((v,i)=>[columns[i],v])));
check(parsed.length===figures.countries.length,'CSV row count');
for(const r of parsed){const original=figures.countries.find(c=>c.country===r.country);check(!!original,'Unknown CSV country '+r.country);for(const k of ['total2010','animal2010','total2023','animal2023','plant2023','animalShare2023'])check(r[k]===''?!Number.isFinite(original?.[k]):Number(r[k])===original?.[k],'CSV/JSON value mismatch '+r.country+' '+k);}

const catalog=json('sources/catalog.json');
const halalRegister=json('research/halal-cultivated/source-register.json');
const phaseOneRegister=json('research/halal-cultivated/phase1/source-register.json');
const continuationDir='research/halal-cultivated/phase1-continuation/';
const continuationRegister=json(continuationDir+'source-register.json');
const paperDir='research/halal-cultivated/paper/';
const paperRegister=json(paperDir+'source-register.json');
const registerRecords=comparative.length+foundation.length+currentReview.length+halalRegister.length+phaseOneRegister.length+continuationRegister.length+paperRegister.length;
check(catalog.originalRegisterRecords===registerRecords,'Catalog register count');
check(catalog.records.length===catalog.uniqueSourceIdentities,'Catalog count metadata');
check(new Set(catalog.records.map(r=>r.id)).size===catalog.records.length,'Catalog IDs unique');
check(catalog.records.every(r=>!/^open source$/i.test(r.title)),'Generic source titles lost contextual labels');
for(const r of json('research/orientation/sources.json').sources)check(catalog.records.some(c=>c.occurrences.some(o=>o.recordPath==='research/orientation/sources.json'&&o.sourceId==='block-'+r.block&&o.document.endsWith(r.document.startsWith('Alt_Protein_Beginners')?'beginners-guide.html':'food-systems-briefing.html'))),'Missing orientation source block '+r.block);
const imports=json('provenance/import-records.json');
for(const prefix of ['research/orientation/','research/india-pakistan/'])for(const p of paths.filter(p=>p.startsWith(prefix)))check(imports.some(r=>r.path===p),'Missing import provenance '+p);
for(const [rs,p] of [[comparative,'research/comparative-protein/source-register.json'],[foundation,'research/ai-protein/source-register.json'],[currentReview,'research/india-pakistan/source-register.json']])for(const r of rs)check(catalog.records.some(c=>c.occurrences.some(o=>o.recordPath===p&&o.sourceId===r.id)),'Source missing from catalog '+r.id);
const library=json('research/library.json');check(library.documents.length===10,'Expected ten research documents');
for(const d of library.documents){check(paths.includes(d.path),'Missing library document '+d.id);check(/human verification pending/i.test(read(d.path)),'Missing visible draft notice '+d.id);}
const ris=read('research/ai-protein/references.ris');check((ris.match(/^TY  - /gm)||[]).length===44&&(ris.match(/^ER  -/gm)||[]).length===44,'RIS record completeness');
const halalDir='research/halal-cultivated/';
const halal=checkHalal(Object.fromEntries(paths.filter(p=>p.startsWith(halalDir)).map(p=>[p.slice(halalDir.length),read(p)])));
checks+=halal.checks;failures.push(...halal.failures);
for(const r of halalRegister)check(catalog.records.some(c=>c.occurrences.some(o=>o.recordPath===halalDir+'source-register.json'&&o.sourceId===r.id)),'Source missing from catalog '+r.id);
const phaseOneDir=halalDir+'phase1/';
for(const r of phaseOneRegister)check(catalog.records.some(c=>c.occurrences.some(o=>o.recordPath===phaseOneDir+'source-register.json'&&o.sourceId===r.id)),'Phase One source missing from catalog '+r.id);
const phaseOne=checkPhaseOne(Object.fromEntries(paths.filter(p=>p.startsWith(phaseOneDir)).map(p=>[p.slice(phaseOneDir.length),read(p)])));
checks+=phaseOne.checks;failures.push(...phaseOne.failures);
// The two reviewed binaries are digest-checked above; do not decode them as
// manuscript text. Every other paper path still reaches the exclusion checks.
const paper=checkPaper(Object.fromEntries(paths.filter(p=>p.startsWith(paperDir)&&!Object.hasOwn(reviewedBinaryExports,p)).map(p=>[p.slice(paperDir.length),read(p)])),{phaseOneFiles:Object.fromEntries(paths.filter(p=>p.startsWith(phaseOneDir)).map(p=>[p.slice(phaseOneDir.length),read(p)]))});
checks+=paper.checks;failures.push(...paper.failures);
for(const r of paperRegister)if(r.url)check(catalog.records.some(c=>c.occurrences.some(o=>o.recordPath===paperDir+'source-register.json'&&o.sourceId===r.id)),'Paper source missing from catalog '+r.id);
const continuation=checkContinuation(Object.fromEntries(paths.filter(p=>p.startsWith(continuationDir)).map(p=>[p.slice(continuationDir.length),read(p)])));
checks+=continuation.checks;failures.push(...continuation.failures);
for(const r of continuationRegister)check(catalog.records.some(c=>c.occurrences.some(o=>o.recordPath===continuationDir+'source-register.json'&&o.sourceId===r.id)),'Continuation source missing from catalog '+r.id);
const surveyDir='research/protein-survey-data/';
const survey=checkSurvey(Object.fromEntries(paths.filter(p=>p.startsWith(surveyDir)).map(p=>[p.slice(surveyDir.length),read(p)])));
checks+=survey.checks;failures.push(...survey.failures);
const result={status:failures.length?'FAIL':'PASS',checks,files:paths.length,internalLinks,documents:library.documents.length,sourceIdentities:catalog.records.length,originalSourceRecords:registerRecords,countries:figures.countries.length,populatedCountries:populated.length,capabilityLocations:figures.hubs.length,claimPassages:passages.length,phaseOneChecks:phaseOne.checks,surveyChecks:survey.checks,failures};
console.log(JSON.stringify(result,null,2));if(failures.length)process.exitCode=1;
