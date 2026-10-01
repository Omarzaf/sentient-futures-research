// Fixture tests for tools/halal-checks.mjs: a valid set passes, and each broken
// variant fails with the expected message. Run: node tools/test-halal-checks.mjs
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {checkHalal} from './halal-checks.mjs';

const dir=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../research/halal-cultivated');
const pkgText=fs.readFileSync(path.join(dir,'datapackage.json'),'utf8');
const pkg=JSON.parse(pkgText);
const header=name=>pkg.resources.find(r=>r.name===name).schema.fields.map(f=>f.name);
const q=v=>v==null?'':/[",\n]/.test(String(v))?'"'+String(v).replaceAll('"','""')+'"':String(v);
const table=(name,rows)=>[header(name).join(','),...rows.map(r=>header(name).map(k=>q(r[k])).join(','))].join('\n')+'\n';

function valid() {
 return {
  register:[{id:'HS-oecd-fao-2026',title:'OECD-FAO Agricultural Outlook 2026-2035',url:'https://www.oecd.org/'},{id:'HS-df-us-forecast',title:'Demand forecast workstream',url:'https://example.org/df'},{id:'HS-bryant-india',title:'Bryant et al.',url:'https://example.org/b'}],
  'rulings':[{ruling_id:'FT-001',institution:'MUIS',jurisdiction:'SGP',date:'2024-02-01',product_profile:'cultivated chicken, halal donor',position:'conditional',language:'en',english_available:'true',source_ids:'HS-oecd-fao-2026',verification_status:'unverified'},
   {ruling_id:'FT-002',institution:'News report',jurisdiction:'SGP',date:'2024-02-05',product_profile:'cultivated chicken',position:'conditional',repeats:'FT-001',language:'en',english_available:'true',verification_status:'unverified'}],
  'scripture-sources':[{source_id:'QS-001',kind:'quran',reference:'6:145',english_translation:'al_bayan_saleem',verification_status:'unverified'}],
  'claims':[{claim_id:'CL-001',segment_id:'TR-001',timestamp:'00:01:05',speaker:'ghamidi',text_ur:'مثال',text_en:'Example excerpt',claim_type:'quran',source_ids:'QS-001',locator:'6:145',verification_status:'verified'}],
  'consensus-matrix':[{condition:'species',column_id:'FT-001',stance:'conditional',citation:'MUIS 2024',date:'2024-02-01'}],
  'market-records':[{record_id:'MR-001',category:'chicken',geo:'PAK',year:'2025',metric:'volume',channel:'all',source_id:'HS-oecd-fao-2026',value:'1000',unit:'tonnes_cwe',evidence_type:'projection',madhhab_context:'hanafi',verification_status:'unverified'},
   {record_id:'MR-002',category:'hybrid_cultivated',geo:'SGP',year:'2025',metric:'sales_value',price_basis:'usd_2025_constant',channel:'retail',source_id:'HS-oecd-fao-2026',value:'10',unit:'usd_2025_constant',evidence_type:'sales',H_rel:'conditional',H_rel_ruling:'FT-001',cultivated_fraction:'0.03',carried_from:'conditional_markets_paper',verification_status:'carried_unverified'}],
  'madhhab-geography':[{record_id:'MD-001',geo:'PAK',predominant_schools:'hanafi;jafari',as_of:'2012-08-09',verification_status:'unverified'}],
  'certification':[{record_id:'CT-001',geo:'PAK',body:'Pakistan Halal Authority',mandatory:'unknown',novel_food_route:'none_found',searched_on:'2026-09-30',verification_status:'unverified'}],
  'elasticities':[{record_id:'EL-001',geo:'PAK',good:'chicken',type:'own_price',with_respect_to:'chicken',value:'-0.8',evidence_group:'hayat',verification_status:'unverified'}],
  'historical-parallels':[{parallel_id:'HP-001',group:'market_substitution',food_before:'butter',food_after:'margarine',driver:'price',informs:'D;p',elasticity_ids:'EL-001',verification_status:'unverified'}],
  'feed-inputs':[{record_id:'FI-001',geo:'PAK',input:'insect_meal',use:'poultry_feed',metric:'price',verification_status:'unverified'}],
  'scenarios':[
   {scenario_id:'SC-001',geo:'PAK',year:'2030',quantile:'q50',gate_state:'declared_halal',shock:'none',shock_mechanism:'none',acceptance_source:'p_US',df_question:'q2_cultivated',p:'0.001',H_rel:'permitted',H_rel_ruling:'FT-001',L:'approved',L_includes_halal:'false',G:'1',D:'1000',D_unit:'tonnes_cwe',K:'0.5',Q_uncapped:'1',Q:'0.5',cap_status:'capped'},
   {scenario_id:'SC-002',geo:'PAK',year:'2030',quantile:'q50',gate_state:'declared_halal',shock:'animal_disease',shock_mechanism:'D;conventional_price',acceptance_source:'p_US',df_question:'q2_cultivated',p:'0.001',H_rel:'permitted',H_rel_ruling:'FT-001',L:'approved',L_includes_halal:'false',G:'1',D:'900',D_unit:'tonnes_cwe',K:'0.5',Q_uncapped:'0.9',Q:'0.5',cap_status:'capped'},
   {scenario_id:'SC-003',geo:'SAU',year:'2030',quantile:'q50',gate_state:'declared_halal',shock:'none',shock_mechanism:'none',acceptance_source:'local_survey',local_survey_id:'HS-bryant-india',p:'0.002',H_rel:'conditional',H_rel_ruling:'FT-001',H_rel_condition_met:'false',L:'approved',L_includes_halal:'true',G:'1',D:'500',D_unit:'tonnes_cwe',Q_uncapped:'1',Q:'1',cap_status:'unknown'},
   {scenario_id:'SC-004',geo:'PAK',year:'2030',quantile:'q50',gate_state:'declared_haram',shock:'none',shock_mechanism:'none',acceptance_source:'p_US',df_question:'q2_cultivated',p:'0.001',H_rel:'prohibited',L:'approved',L_includes_halal:'false',G:'0',D:'1000',D_unit:'tonnes_cwe',Q_uncapped:'0',Q:'0',cap_status:'unknown',reason_code:'gate_closed_haram'}]
 };
}
function files(data) {
 const out={'datapackage.json':pkgText,'source-register.json':JSON.stringify(data.register)};
 for(const r of pkg.resources)out[r.path]=table(r.name,data[r.name]||[]);
 return out;
}

const cases=[
 ['text outside allowed values',d=>{d['market-records'][0].category='insects';},'not in allowed values'],
 ['renamed header',d=>d,'header differs',f=>{f['market-records.csv']=f['market-records.csv'].replace('category,','product_category,');}],
 ['blank read as zero placeholder',d=>{d['market-records'][0].value='NA';},'not a valid number'],
 ['rule 1: gate as a fraction',d=>{d.scenarios[0].G='0.7';},'not a valid integer'],
 ['rule 1/3: gate open without approval',d=>{d.scenarios[0].L='pending';},'rule 1/3'],
 ['rule 3: conditional needs condition unless approval includes halal',d=>{d.scenarios[2].L_includes_halal='false';},'rule 1/3'],
 ['rule 2: local survey multiplied with p_US',d=>{d.scenarios[2].df_question='q2_cultivated';},'rule 2'],
 ['rule 5: plant-based question used',d=>{d.scenarios[0].df_question='q1_plant_based';},'not in allowed values'],
 ['rule 4: fraction on a non-hybrid',d=>{d['market-records'][0].cultivated_fraction='0.5';},'rule 4'],
 ['rule 4: same observation as cultivated and hybrid',d=>{d['market-records'].push({...d['market-records'][1],record_id:'MR-003',category:'cultivated',cultivated_fraction:''});},'rule 4'],
 ['rule 6: insects as human food',d=>{d['feed-inputs'][0].use='human_food';},'not in allowed values'],
 ['rule 7: shock changes p',d=>{d.scenarios[1].p='0.002';d.scenarios[1].Q_uncapped='1.8';},'rule 7, a shock never changes p'],
 ['rule 7: disease shock changes K',d=>{d.scenarios[1].shock_mechanism='D;K';},'rule 7'],
 ['rule 8: consensus cites a report of a ruling',d=>{d['consensus-matrix'][0].column_id='FT-002';},'rule 8'],
 ['rule 8: two estimates from one evidence group',d=>{d.elasticities.push({...d.elasticities[0],record_id:'EL-002'});},'rule 8'],
 ['rule 9: percentage for a school',d=>{d['madhhab-geography'][0].predominant_schools='hanafi 80%';},'does not match pattern'],
 ['rule 10: carried value marked verified without re-check',d=>{d['market-records'][1].verification_status='verified';},'rule 10'],
 ['Q arithmetic',d=>{d.scenarios[0].Q_uncapped='2';},'D x p x G'],
 ['K cap ignored',d=>{d.scenarios[1].Q='0.9';},'capped by K'],
 ['zero Q without reason',d=>{d.scenarios[3].reason_code='';},'reason_code'],
 ['none_found without a search date',d=>{d.certification[0].searched_on='';},'searched_on'],
 ['H_rel without a ruling',d=>{d['market-records'][1].H_rel_ruling='';},'H_rel needs'],
 ['unknown source ID',d=>{d['market-records'][0].source_id='HS-missing';},'unknown ID'],
 ['Sunnah claim not checked against Mizan',d=>{Object.assign(d.claims[0],{claim_type:'sunnah',checked_against:'hadith_collections'});},'Mizan'],
 ['long excerpt',d=>{d.claims[0].text_en='x'.repeat(281);},'longer than 280'],
 ['bad Quran reference',d=>{d['scripture-sources'][0].reference='115:1';},'surah:ayah'],
 ['Quran ayah zero',d=>{d['scripture-sources'][0].reference='2:0';},'surah:ayah'],
 ['rule 7: disease shock opens the religious gate',d=>{Object.assign(d.scenarios[1],{H_rel:'conditional',H_rel_condition_met:'true'});},'rule 7, a shock never changes the religious ruling'],
 ['rule 7: disease shock changes L_includes_halal',d=>{d.scenarios[1].L_includes_halal='true';},'rule 7, L_includes_halal'],
 ['rule 8: H_rel credited to a report of a ruling',d=>{d['market-records'][1].H_rel_ruling='FT-002';},'rule 8, H_rel_ruling'],
 ['Q published with a missing input',d=>{Object.assign(d.scenarios[0],{D:'',D_unit:'',Q_uncapped:'1',Q:'0.5'});},'input_missing'],
 ['claim cited as a source',d=>{d['market-records'][0].source_id='CL-001';},'is a claim, not a source'],
 ['local survey that is not a source record',d=>{d.scenarios[2].local_survey_id='EL-001';},'local_survey_id'],
 ['text after a closing quote',d=>d,'Text after a closing quote',f=>{f['rulings.csv']=f['rulings.csv'].replace('FT-002,','"FT-002"x,');}],
 ['quote inside an unquoted field',d=>d,'Quote inside an unquoted field',f=>{f['rulings.csv']=f['rulings.csv'].replace('FT-002,','FT-0"02,');}]
];

let failed=0;
const base=checkHalal(files(valid()));
if(base.failures.length){failed++;console.error('Valid fixture failed:\n '+base.failures.join('\n '));}
for(const [label,mutate,expect,mutateFiles] of cases){
 const d=valid();mutate(d);const f=files(d);if(mutateFiles)mutateFiles(f);
 const r=checkHalal(f);
 if(!r.failures.some(m=>m.includes(expect))){failed++;console.error('Not caught: '+label+' (expected "'+expect+'")'+(r.failures.length?'\n got: '+r.failures.join('\n '):''));}
}
console.log(JSON.stringify({status:failed?'FAIL':'PASS',validFixtureChecks:base.checks,cases:cases.length,failed}));
if(failed)process.exitCode=1;
