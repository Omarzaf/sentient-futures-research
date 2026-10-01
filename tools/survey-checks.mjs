import {parseCsv} from './halal-checks.mjs';

const studyFields=['Study ID','Citation / short title','Population','Total sample n','Fieldwork','Study type and method','DOI','Findings','Limitations / corrections','Read / download URL','Primary source URL','Access status','Respondent-level data'];
const findingFields=['record_id','source_id','geography','protein','measure','value','unit','qualifier','sample_n','numerator','measurement_type','source_location','note'];
const workbookFindingFields=['Record ID','Study ID','Country / group','Protein','Measure','Value','Unit','Qualifier','Sample n','Numerator','Measurement type','Source location','Note'];
const expectedStudyIds=Array.from({length:9},(_,i)=>'S'+String(i+1).padStart(2,'0'));
const expectedObservationIds=Array.from({length:29},(_,i)=>'R'+String(i+1).padStart(2,'0'));
const allowedUnits=new Set(['proportion','respondents','qualitative']);
const allowedMeasurementTypes=new Set([
 'Hypothetical willingness',
 'Self-reported consumption',
 'Awareness / trial history',
 'Awareness',
 'Hypothetical purchase intent',
 'Hypothetical willingness to pay',
 'Stated preference',
 'Sample composition',
 'Sample size',
 'Association',
 'Self-reported past consumption',
 'Hypothetical acceptance',
 'Attitude / association'
]);

function rowsByHeader(text) {
 const rows=parseCsv(text);
 if(!rows.length)return {header:[],records:[],widths:[]};
 const header=rows[0];
 const records=rows.slice(1).map(cells=>Object.fromEntries(header.map((name,i)=>[name,cells[i]??''])));
 const widths=rows.slice(1).map(cells=>cells.length);
 return {header,records,widths};
}

const headerEquals=(header,expected)=>JSON.stringify(header)===JSON.stringify(expected);
const idSet=records=>new Set(records.map(r=>r.id));
const exactIds=(actual,expected)=>JSON.stringify([...actual].sort())===JSON.stringify([...expected].sort());
const isHttp=value=>/^https?:\/\//.test(value||'');
const isInteger=value=>Number.isInteger(value);
const textOf=value=>value==null?'':String(value);
const close=(a,b)=>Math.abs(a-b)<=0.005;
const exactColumnIds=(records,column,expected)=>JSON.stringify(records.map(r=>r[column]).sort())===JSON.stringify([...expected].sort());
const allWidths=(table,width)=>table.widths.every(n=>n===width);

function normalizeStudy(record) {
 return {
  'Study ID':record.id,
  'Citation / short title':`${record.authors} (${record.year}). ${record.title}`,
  'Population':record.geography,
  'Total sample n':textOf(record.total_n),
  'Fieldwork':record.fieldwork,
  'Study type and method':`${record.kind}. ${record.method}`,
  'DOI':record.doi||'',
  'Findings':record.findings,
  'Limitations / corrections':record.notes,
  'Read / download URL':record.access_url,
  'Primary source URL':record.source_url,
  'Access status':record.access,
  'Respondent-level data':record.raw_data
 };
}

function normalizeObservation(record) {
 return {
  record_id:record.record_id,
  source_id:record.source_id,
  geography:record.geography,
  protein:record.protein,
  measure:record.measure,
  value:textOf(record.value),
  unit:record.unit,
  qualifier:record.qualifier,
  sample_n:textOf(record.sample_n),
  numerator:textOf(record.numerator),
  measurement_type:record.measurement_type,
  source_location:record.source_location,
  note:record.note||''
 };
}

const workbookToMachine={
 'Record ID':'record_id',
 'Study ID':'source_id',
 'Country / group':'geography',
 Protein:'protein',
 Measure:'measure',
 Value:'value',
 Unit:'unit',
 Qualifier:'qualifier',
 'Sample n':'sample_n',
 Numerator:'numerator',
 'Measurement type':'measurement_type',
 'Source location':'source_location',
 Note:'note'
};

function mappedWorkbookFinding(row) {
 return Object.fromEntries(Object.entries(workbookToMachine).map(([from,to])=>[to,row[from]??'']));
}

// files: {relativeName: text} for everything in research/protein-survey-data.
export function checkSurvey(files) {
 const failures=[];let checks=0;
 const check=(ok,message)=>{checks++;if(!ok)failures.push('survey: '+message);};
 for(const name of ['survey_data.json','Study_Register.csv','Survey_Findings.csv','Alternative_Meat_Survey_Data_Studies.csv','Alternative_Meat_Survey_Data_Findings.csv','README.txt','Source_Links.html'])check(name in files,'missing '+name);
 if(failures.length)return {checks,failures};

 let data;
 try{data=JSON.parse(files['survey_data.json']);}catch(e){check(false,'survey_data.json invalid: '+e.message);return {checks,failures};}
 const sources=Array.isArray(data.sources)?data.sources:[];
 const observations=Array.isArray(data.observations)?data.observations:[];
 check(sources.length===9,'expected 9 studies');
 check(observations.length===29,'expected 29 findings');
 check(exactIds(idSet(sources),expectedStudyIds),'study IDs must be S01-S09');
 check(exactIds(new Set(observations.map(r=>r.record_id)),expectedObservationIds),'finding IDs must be R01-R29');
 check(new Set(sources.map(r=>r.id)).size===sources.length,'duplicate study IDs');
 check(new Set(observations.map(r=>r.record_id)).size===observations.length,'duplicate finding IDs');
 const sourceIds=idSet(sources);

 for(const source of sources) {
  check(sourceIds.has(source.id),source.id+': source ID retained');
  check(isInteger(source.year)&&source.year>=2020&&source.year<=2030,source.id+': publication year out of expected range');
  check(isInteger(source.total_n)&&source.total_n>0,source.id+': total_n must be a positive integer');
  check(source.doi===''||/^10\.\S+\/\S+/.test(source.doi),source.id+': invalid DOI');
  check(isHttp(source.source_url),source.id+': source_url must be public HTTP(S)');
  check(isHttp(source.access_url),source.id+': access_url must be public HTTP(S)');
  for(const key of ['title','authors','geography','fieldwork','kind','method','access','raw_data','notes','findings'])check(!!source[key],source.id+': missing '+key);
 }

 for(const row of observations) {
  check(sourceIds.has(row.source_id),row.record_id+': unknown source_id '+row.source_id);
  check(allowedUnits.has(row.unit),row.record_id+': unexpected unit '+row.unit);
  check(allowedMeasurementTypes.has(row.measurement_type),row.record_id+': unexpected measurement_type '+row.measurement_type);
  check(isInteger(row.sample_n)&&row.sample_n>0,row.record_id+': sample_n must be positive integer');
  check(!!row.geography&&!!row.protein&&!!row.measure&&!!row.qualifier&&!!row.source_location,row.record_id+': missing descriptive field');
  if(row.unit==='proportion'){
   check(typeof row.value==='number'&&row.value>=0&&row.value<=1,row.record_id+': proportion value must be 0-1');
   if(row.numerator!==null){
    check(isInteger(row.numerator)&&row.numerator>=0&&row.numerator<=row.sample_n,row.record_id+': numerator out of range');
    check(close(row.numerator/row.sample_n,row.value),row.record_id+': numerator and value disagree');
   }
  }
  if(row.unit==='respondents'){
   check(isInteger(row.value)&&row.value===row.sample_n,row.record_id+': respondent value must equal sample_n');
   check(row.numerator===null,row.record_id+': respondent count should not have numerator');
  }
  if(row.unit==='qualitative'){
   check(row.value===null,row.record_id+': qualitative row must not have numeric value');
   check(row.numerator===null,row.record_id+': qualitative row must not have numerator');
   check(row.qualifier==='Qualitative',row.record_id+': qualitative row qualifier');
  }
 }

 const studyCsv=rowsByHeader(files['Study_Register.csv']);
 const studyWorkbook=rowsByHeader(files['Alternative_Meat_Survey_Data_Studies.csv']);
 const findingCsv=rowsByHeader(files['Survey_Findings.csv']);
 const findingWorkbook=rowsByHeader(files['Alternative_Meat_Survey_Data_Findings.csv']);
 check(headerEquals(studyCsv.header,studyFields),'Study_Register.csv header');
 check(headerEquals(studyWorkbook.header,studyFields),'Alternative_Meat_Survey_Data_Studies.csv header');
 check(headerEquals(findingCsv.header,findingFields),'Survey_Findings.csv header');
 check(headerEquals(findingWorkbook.header,workbookFindingFields),'Alternative_Meat_Survey_Data_Findings.csv header');
 check(studyCsv.records.length===9,'Study_Register.csv row count');
 check(studyWorkbook.records.length===9,'Alternative_Meat_Survey_Data_Studies.csv row count');
 check(findingCsv.records.length===29,'Survey_Findings.csv row count');
 check(findingWorkbook.records.length===29,'Alternative_Meat_Survey_Data_Findings.csv row count');
 check(allWidths(studyCsv,studyFields.length),'Study_Register.csv row width');
 check(allWidths(studyWorkbook,studyFields.length),'Alternative_Meat_Survey_Data_Studies.csv row width');
 check(allWidths(findingCsv,findingFields.length),'Survey_Findings.csv row width');
 check(allWidths(findingWorkbook,workbookFindingFields.length),'Alternative_Meat_Survey_Data_Findings.csv row width');
 check(exactColumnIds(studyCsv.records,'Study ID',expectedStudyIds),'Study_Register.csv must contain S01-S09 exactly once');
 check(exactColumnIds(studyWorkbook.records,'Study ID',expectedStudyIds),'Alternative_Meat_Survey_Data_Studies.csv must contain S01-S09 exactly once');
 check(exactColumnIds(findingCsv.records,'record_id',expectedObservationIds),'Survey_Findings.csv must contain R01-R29 exactly once');
 check(exactColumnIds(findingWorkbook.records,'Record ID',expectedObservationIds),'Alternative_Meat_Survey_Data_Findings.csv must contain R01-R29 exactly once');
 check(JSON.stringify(studyCsv.records)===JSON.stringify(studyWorkbook.records),'study workbook CSV must match Study_Register.csv');

 const sourceById=new Map(sources.map(source=>[source.id,normalizeStudy(source)]));
 for(const row of studyCsv.records) {
  const expected=sourceById.get(row['Study ID']);
  check(!!expected,row['Study ID']+': study CSV ID exists in JSON');
  if(expected)for(const field of studyFields)check(row[field]===expected[field],row['Study ID']+': Study_Register.csv mismatch '+field);
 }

 const observationById=new Map(observations.map(row=>[row.record_id,normalizeObservation(row)]));
 for(const row of findingCsv.records) {
  const expected=observationById.get(row.record_id);
  check(!!expected,row.record_id+': finding CSV ID exists in JSON');
  if(expected)for(const field of findingFields)check(row[field]===expected[field],row.record_id+': Survey_Findings.csv mismatch '+field);
 }
 for(const row of findingWorkbook.records) {
  const mapped=mappedWorkbookFinding(row);
  const expected=observationById.get(mapped.record_id);
  check(!!expected,mapped.record_id+': workbook finding ID exists in JSON');
  if(expected)for(const field of findingFields)check(mapped[field]===expected[field],mapped.record_id+': Alternative_Meat_Survey_Data_Findings.csv mismatch '+field);
 }

 const html=files['Source_Links.html'];
 check((html.match(/<article>/g)||[]).length===9,'Source_Links.html must list 9 studies');
 check(!/\.xlsx\b/i.test(html),'Source_Links.html must not link an xlsx file');
 for(const file of ['../../index.html','survey_data.json','Alternative_Meat_Survey_Data_Findings.csv','Alternative_Meat_Survey_Data_Studies.csv','Survey_Findings.csv','Study_Register.csv','README.txt'])check(html.includes(file),'Source_Links.html missing link '+file);
 check(/human verification pending/i.test(html),'Source_Links.html must state human verification pending');
 check(/29 extracted findings/i.test(html)&&/nine studies/i.test(files['README.txt']),'survey package count notices');
 return {checks,failures};
}
