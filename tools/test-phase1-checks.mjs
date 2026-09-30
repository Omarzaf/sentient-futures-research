import assert from 'node:assert/strict';
import fs from 'node:fs';
import {fileURLToPath} from 'node:url';
import {checkPhaseOne} from './phase1-checks.mjs';

const directory=fileURLToPath(new URL('../research/halal-cultivated/phase1/',import.meta.url));
const fixture=Object.fromEntries(fs.readdirSync(directory).map(name=>[name,fs.readFileSync(directory+name,'utf8')]));
assert.deepEqual(checkPhaseOne(fixture).failures,[],'Published fixture must pass');
const alter=(files,name,mutate)=>{const value=JSON.parse(files[name]);mutate(value);files[name]=JSON.stringify(value);};
const cases=[
 ['missing source lineage',files=>alter(files,'claims.json',rows=>{rows[0].source_ids=['UNKNOWN'];}),'unresolved source'],
 ['missing review lineage',files=>alter(files,'claims.json',rows=>{rows[0].verification_id='UNKNOWN';}),'unresolved review'],
 ['unresolved question upgraded',files=>alter(files,'school-questions.json',rows=>{rows.find(r=>r.id==='J-Q1').status='blind_agent_checked';}),'unresolved Sistani'],
 ['analogy mislabeled as evidence',files=>alter(files,'historical-comparisons.json',rows=>{rows[0].status='blind_agent_checked';}),'historical analogy upgraded'],
 ['private interview reference',files=>{files['review.md']+='\n[INTERVIEW]\n';},'private-source reference'],
 ['held-language source promoted',files=>{files['review.md']=files['review.md'].replace('## Main findings','## Main findings\n\n[WP595]');},'held source cited'],
 ['false scholarly approval',files=>alter(files,'release.json',record=>{record.human_scholarly_review=true;}),'review limits lost'],
 ['missing school slot',files=>alter(files,'school-questions.json',rows=>{rows.pop();}),'school coverage']
];
for(const [name,mutate,expected] of cases){
 const files={...fixture};mutate(files);
 assert(checkPhaseOne(files).failures.some(message=>message.includes(expected)),name+' must be rejected');
}
console.log(JSON.stringify({status:'PASS',validFixtureChecks:checkPhaseOne(fixture).checks,cases:cases.length,failed:0}));
