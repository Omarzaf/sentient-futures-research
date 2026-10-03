import assert from 'node:assert/strict';
import fs from 'node:fs';
import {fileURLToPath} from 'node:url';
import {checkSurvey} from './survey-checks.mjs';

const directory=fileURLToPath(new URL('../research/protein-survey-data/',import.meta.url));
const fixture=Object.fromEntries(fs.readdirSync(directory).map(name=>[name,fs.readFileSync(directory+name,'utf8')]));
const valid=checkSurvey(fixture);
assert.deepEqual(valid.failures,[],'Published survey fixture must pass');

const alterJson=(files,mutate)=>{const data=JSON.parse(files['survey-data.json']);mutate(data);files['survey-data.json']=JSON.stringify(data);};
const cases=[
 ['duplicate study ID',files=>alterJson(files,data=>{data.sources[1].id='S01';}),'study IDs must be S01-S09'],
 ['unresolved finding source',files=>alterJson(files,data=>{data.observations[0].source_id='UNKNOWN';}),'unknown source_id'],
 ['bad proportion',files=>alterJson(files,data=>{data.observations[0].value=1.2;}),'proportion value'],
 ['qualitative upgraded to number',files=>alterJson(files,data=>{data.observations.find(r=>r.record_id==='R29').value=0.2;}),'qualitative row must not have numeric value'],
 ['machine CSV disagrees with JSON',files=>{files['findings.csv']=files['findings.csv'].replace('"R01","S07","Indonesia","Cultivated meat","Would eat lab-grown meat: Yes","0.31"', '"R01","S07","Indonesia","Cultivated meat","Would eat lab-grown meat: Yes","0.32"');},'findings.csv mismatch value'],
 ['study CSV IDs are incomplete',files=>{files['studies.csv']=files['studies.csv'].replace('"S02","Maqsood et al.', '"S01","Maqsood et al.');},'must contain S01-S09 exactly once'],
 ['finding CSV IDs are incomplete',files=>{files['findings.csv']=files['findings.csv'].replace('"R02","S07","Malaysia"', '"R01","S07","Malaysia"');},'must contain R01-R29 exactly once'],
 ['extra CSV field rejected',files=>{files['findings.csv']=files['findings.csv'].replace('"R01","S07","Indonesia","Cultivated meat","Would eat lab-grown meat: Yes","0.31","proportion","Reported","8305","","Hypothetical willingness","Country page 13",""', '"R01","S07","Indonesia","Cultivated meat","Would eat lab-grown meat: Yes","0.31","proportion","Reported","8305","","Hypothetical willingness","Country page 13","","extra"');},'findings.csv row width'],
 ['source page must expose JSON',files=>{files['index.html']=files['index.html'].replace('survey-data.json','missing.json');},'missing link survey-data.json'],
 ['source page must link back to index',files=>{files['index.html']=files['index.html'].replace('../../index.html','../index.html');},'missing link ../../index.html'],
 ['source page must carry visible draft notice',files=>{files['index.html']=files['index.html'].replace('AI-assisted extraction; human verification pending.','AI-assisted extraction.');},'index.html must state human verification pending'],
 ['xlsx link reintroduced',files=>{files['index.html']=files['index.html'].replace('studies.csv','original.xlsx');},'must not link an xlsx']
];

for(const [name,mutate,expected] of cases){
 const files={...fixture};mutate(files);
 const result=checkSurvey(files);
 assert(result.failures.some(message=>message.includes(expected)),name+' must be rejected');
}

console.log(JSON.stringify({status:'PASS',validFixtureChecks:valid.checks,cases:cases.length,failed:0}));
