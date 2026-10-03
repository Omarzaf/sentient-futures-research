import fs from 'node:fs';
import {checkPaper} from './paper-checks.mjs';
import {bibliographyEntry,citedSourceKeys} from './paper-bibliography.mjs';

const fragmentPath=process.argv[2];
if(!fragmentPath)throw Error('Usage: node tools/verify-paper-section.mjs PATH_TO_SECTION.md');
const base='research/halal-cultivated/',paper=base+'paper/';
const files=Object.fromEntries(fs.readdirSync(paper).filter(f=>/\.(json|md)$/.test(f)).map(f=>[f,fs.readFileSync(paper+f,'utf8')]));
const state=JSON.parse(files['execution-state.json']);
if(state.outlineApproved!==true||state.stage<5)throw Error('The actual author outline checkpoint is required.');
const fragment=fs.readFileSync(fragmentPath,'utf8');
const sections=[...fragment.matchAll(/^## (\d+)\./gm)].map(m=>m[1]);
if(!sections.length)throw Error('The fragment must identify its actual numbered section.');
const sources=JSON.parse(files['source-register.json']),alias=new Map(sources.flatMap(s=>[s.key,...s.aliases].map(key=>[key,s])));
const used=[...new Set(citedSourceKeys(fragment).map(key=>alias.get(key)))];
if(used.includes(undefined))throw Error('Unresolved footnote source key in section.');
const bib=used.sort((a,b)=>a.bibliographic.author.localeCompare(b.bibliographic.author)||a.key.localeCompare(b.key)).map(bibliographyEntry).join('\n\n');
files['paper.md']='# Section validation only\n\nAI-assisted working draft; human verification pending\n\n'+fragment+'\n\n## Bibliography\n\n'+bib+'\n';
const traced=new Set([...fragment.matchAll(/<!--\s*trace:\s*([^|]*?)\s*\|/g)].flatMap(m=>m[1].trim().split(/\s+/)));
// Scope only this in-memory check. The authoritative coverage file is never
// changed, and this command cannot report whole-manuscript completeness.
const coverage=JSON.parse(files['coverage.json']).map(row=>{
 const trace=(row.kind==='gap'?'gap:':row.kind==='counter_evidence'?'ce:':row.kind==='historical'?'historical:':'')+row.id;
 return {...row,disposition:traced.has(trace)?'included':'excluded',reason:traced.has(trace)?'Present in this isolated section.':'Outside this isolated section check; no change to manuscript coverage.'};
});
files['coverage.json']=JSON.stringify(coverage);
const phaseOneFiles=Object.fromEntries(fs.readdirSync(base+'phase1/').filter(f=>f.endsWith('.json')).map(f=>[f,fs.readFileSync(base+'phase1/'+f,'utf8')]));
const result=checkPaper(files,{phaseOneFiles});
const warnings=result.warnings.filter(w=>!/^Paper: section /.test(w)||sections.some(section=>w.startsWith('Paper: section '+section+' ')));
console.log(JSON.stringify({scope:'isolated section; not complete manuscript validation',sections,status:result.failures.length?'FAIL':'PASS',checks:result.checks,failures:result.failures,warnings},null,2));
process.exitCode=result.failures.length?1:0;
