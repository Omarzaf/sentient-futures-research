import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import vm from 'node:vm';
import {fileURLToPath} from 'node:url';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
const json=p=>JSON.parse(read(p));
const failures=[];let checks=0;
const check=(ok,msg)=>{checks++;if(!ok)failures.push(msg);};
function walk(dir=''){return fs.readdirSync(path.join(root,dir),{withFileTypes:true}).filter(d=>d.name!=='.git').flatMap(d=>d.isDirectory()?walk(path.posix.join(dir,d.name)):[path.posix.join(dir,d.name)]).sort();}
const paths=walk();
const manifest=json('provenance/file-manifest.json').files;
check(new Set(manifest.map(f=>f.path)).size===manifest.length,'Duplicate manifest paths');
check(JSON.stringify(paths.filter(p=>p!=='provenance/file-manifest.json'))===JSON.stringify(manifest.map(f=>f.path).sort()),'Manifest does not match repository files');
for(const f of manifest){const b=fs.readFileSync(path.join(root,f.path));check(b.length===f.bytes&&crypto.createHash('sha256').update(b).digest('hex')===f.sha256,'Hash/size mismatch: '+f.path);}

const forbiddenPath=/(^|\/)(?:\.env(?:\.|$)|node_modules|\.venv|\.playwright-mcp|private|working|AGENTS\.md|\.DS_Store)(\/|$)|\.(?:docx?|xlsx?|pptx?|pdf|zip|pem|key|log)$/i;
const hazards=[
 ['absolute home path',/\/(?:Users|home)\/[A-Za-z0-9._-]+\//],
 ['private document URL',/https?:\/\/(?:docs|drive)\.google\.com\//i],
 ['email address',/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/i],
 ['private key',/-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----/],
 ['credential-like token',/\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{25,}|sk-[A-Za-z0-9_-]{24,})\b/],
 ['embedded raster',/data:image\/(?:jpeg|png|webp);base64,/i]
];
for(const p of paths){check(!forbiddenPath.test(p),'Excluded file type or path: '+p);check(!fs.lstatSync(path.join(root,p)).isSymbolicLink(),'Symlink: '+p);const s=read(p);for(const [name,re] of hazards)check(!re.test(s),name+': '+p);if(p.endsWith('.json')){try{JSON.parse(s);check(true,'JSON');}catch{check(false,'Invalid JSON: '+p);}}}

const unescape=s=>s.replaceAll('&amp;','&').replaceAll('&quot;','"').replaceAll('&#39;',"'");
let internalLinks=0;
for(const p of paths.filter(p=>/\.(html|md|svg)$/.test(p))){
 const text=read(p);let targets=[...text.matchAll(/(?:href|src)=["']([^"']*)["']/g)].map(m=>m[1]);
 if(p.endsWith('.md'))targets.push(...[...text.matchAll(/\[[^\]]*\]\(([^)]+)\)/g)].map(m=>m[1].replace(/^<|>$/g,'')));
 for(const raw of targets){
  const href=unescape(raw);if(/^(?:https?:|data:|mailto:)/i.test(href)||href==='')continue;
  if(/^[a-z]+:/i.test(href)){check(false,'Unexpected URL scheme '+p+': '+href);continue;}
  const [part,fragment]=href.split('#');let dest;
  try{dest=part?path.posix.normalize(path.posix.join(path.posix.dirname(p),decodeURIComponent(part.split('?')[0]))):p;}catch{check(false,'Invalid link encoding '+p);continue;}
  internalLinks++;check(!dest.startsWith('../')&&paths.includes(dest),'Broken or escaping relative link '+p+' -> '+href);
  if(fragment&&paths.includes(dest)&&/\.(html|svg)$/.test(dest)){
   const ids=[...read(dest).matchAll(/\bid=["']([^"']+)["']/g)].map(m=>m[1]);
   check(ids.includes(decodeURIComponent(fragment)),'Missing anchor '+p+' -> '+href);
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
const sourceIds=new Set(comparative.map(r=>r.id));
check(comparative.length===60&&sourceIds.size===60,'Comparative source count/IDs');
check(foundation.length===44&&new Set(foundation.map(r=>r.id)).size===44,'Foundation source count/IDs');
check(foundation.every(r=>r.human_verification==='Pending'),'Unexpected foundation review status');
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
const csvRows=read('research/comparative-protein/protein-data.csv').trim().split('\n');
const columns=csvRows[0].split(',');const parsed=csvRows.slice(1).map(line=>Object.fromEntries(line.match(/"(?:[^"]|"")*"|[^,]+/g).map(s=>s.replace(/^"|"$/g,'')).map((v,i)=>[columns[i],v])));
check(parsed.length===figures.countries.length,'CSV row count');
for(const r of parsed){const original=figures.countries.find(c=>c.country===r.country);check(!!original,'Unknown CSV country '+r.country);for(const k of ['total2010','animal2010','total2023','animal2023','plant2023','animalShare2023'])check(r[k]===''?!Number.isFinite(original?.[k]):Number(r[k])===original?.[k],'CSV/JSON value mismatch '+r.country+' '+k);}

const catalog=json('sources/catalog.json');
check(catalog.originalRegisterRecords===104,'Catalog register count');
check(catalog.records.length===catalog.uniqueSourceIdentities,'Catalog count metadata');
check(new Set(catalog.records.map(r=>r.id)).size===catalog.records.length,'Catalog IDs unique');
check(catalog.records.every(r=>!/^open source$/i.test(r.title)),'Generic source titles lost contextual labels');
for(const r of json('research/orientation/sources.json').sources)check(catalog.records.some(c=>c.occurrences.some(o=>o.recordPath==='research/orientation/sources.json'&&o.sourceId==='block-'+r.block&&o.document.endsWith(r.document.startsWith('Alt_Protein_Beginners')?'beginners-guide.html':'food-systems-briefing.html'))),'Missing orientation source block '+r.block);
const imports=json('provenance/import-records.json');
for(const p of paths.filter(p=>p.startsWith('research/orientation/')))check(imports.some(r=>r.path===p),'Missing orientation import provenance '+p);
for(const [rs,p] of [[comparative,'research/comparative-protein/source-register.json'],[foundation,'research/ai-protein/source-register.json']])for(const r of rs)check(catalog.records.some(c=>c.occurrences.some(o=>o.recordPath===p&&o.sourceId===r.id)),'Source missing from catalog '+r.id);
const library=json('research/library.json');check(library.documents.length===5,'Expected five research documents');
for(const d of library.documents){check(paths.includes(d.path),'Missing library document '+d.id);check(/human verification pending/i.test(read(d.path)),'Missing visible draft notice '+d.id);}
const ris=read('research/ai-protein/references.ris');check((ris.match(/^TY  - /gm)||[]).length===44&&(ris.match(/^ER  -/gm)||[]).length===44,'RIS record completeness');
const result={status:failures.length?'FAIL':'PASS',checks,files:paths.length,internalLinks,documents:library.documents.length,sourceIdentities:catalog.records.length,originalSourceRecords:104,countries:figures.countries.length,populatedCountries:populated.length,capabilityLocations:figures.hubs.length,claimPassages:passages.length,failures};
console.log(JSON.stringify(result,null,2));if(failures.length)process.exitCode=1;
