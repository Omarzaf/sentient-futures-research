// Fixture tests for tools/halal-checks.mjs: a valid set passes, and each broken
// variant fails with the expected message. Run: node tools/test-halal-checks.mjs
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {checkHalal} from './halal-checks.mjs';
import {runBridgeFixtures} from './test-bridge-v2-checks.mjs';

const dir=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../research/halal-cultivated');
const pkgText=fs.readFileSync(path.join(dir,'datapackage.json'),'utf8');
const pkg=JSON.parse(pkgText);
const header=name=>pkg.resources.find(r=>r.name===name).schema.fields.map(f=>f.name);
const csv=name=>pkg.resources.find(r=>r.name===name).path;
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
  'scenarios':[]
 };
}
function files(data) {
 const out={'datapackage.json':pkgText,[pkg.sourceRegister]:JSON.stringify(data.register)};
 for(const name of ['schema.json','synthetic-example.json','production-state.json'])out['bridge-v2/'+name]=fs.readFileSync(path.join(dir,'bridge-v2',name),'utf8');
 for(const r of pkg.resources)out[r.path]=table(r.name,data[r.name]||[]);
 return out;
}

const cases=[
 ['legacy scenario production blocked',d=>{d.scenarios.push({scenario_id:'SC-001',geo:'PAK',year:'2030',quantile:'q50',gate_state:'declared_halal',shock:'none',shock_mechanism:'none',acceptance_source:'p_US',df_question:'q2_cultivated',p:'0.001',H_rel:'permitted',L:'approved',L_includes_halal:'false',G:'1',D:'1000',D_unit:'tonnes_cwe',K:'0.5',Q_uncapped:'1',Q:'0.5',cap_status:'capped'});},'legacy scenario production blocked'],
 ['active v2 contract missing',d=>d,'schema missing',f=>{delete f['bridge-v2/schema.json'];}],
 ['unconverted value in synthetic output',d=>d,'p_mass expected output',f=>{const d=JSON.parse(f['bridge-v2/synthetic-example.json']);d.expected_outputs[0].p_mass=.1;f['bridge-v2/synthetic-example.json']=JSON.stringify(d);}],
 ['text outside allowed values',d=>{d['market-records'][0].category='insects';},'not in allowed values'],
 ['renamed header',d=>d,'header differs',f=>{f[csv('market-records')]=f[csv('market-records')].replace('category,','product_category,');}],
 ['blank read as zero placeholder',d=>{d['market-records'][0].value='NA';},'not a valid number'],
 ['rule 4: fraction on a non-hybrid',d=>{d['market-records'][0].cultivated_fraction='0.5';},'rule 4'],
 ['rule 4: same observation as cultivated and hybrid',d=>{d['market-records'].push({...d['market-records'][1],record_id:'MR-003',category:'cultivated',cultivated_fraction:''});},'rule 4'],
 ['rule 6: insects as human food',d=>{d['feed-inputs'][0].use='human_food';},'not in allowed values'],
 ['rule 8: consensus cites a report of a ruling',d=>{d['consensus-matrix'][0].column_id='FT-002';},'rule 8'],
 ['rule 8: two estimates from one evidence group',d=>{d.elasticities.push({...d.elasticities[0],record_id:'EL-002'});},'rule 8'],
 ['rule 9: percentage for a school',d=>{d['madhhab-geography'][0].predominant_schools='hanafi 80%';},'does not match pattern'],
 ['rule 10: carried value marked verified without re-check',d=>{d['market-records'][1].verification_status='verified';},'rule 10'],
 ['none_found without a search date',d=>{d.certification[0].searched_on='';},'searched_on'],
 ['H_rel without a ruling',d=>{d['market-records'][1].H_rel_ruling='';},'H_rel needs'],
 ['unknown source ID',d=>{d['market-records'][0].source_id='HS-missing';},'unknown ID'],
 ['Sunnah claim not checked against Mizan',d=>{Object.assign(d.claims[0],{claim_type:'sunnah',checked_against:'hadith_collections'});},'Mizan'],
 ['long excerpt',d=>{d.claims[0].text_en='x'.repeat(281);},'longer than 280'],
 ['bad Quran reference',d=>{d['scripture-sources'][0].reference='115:1';},'surah:ayah'],
 ['Quran ayah zero',d=>{d['scripture-sources'][0].reference='2:0';},'surah:ayah'],
 ['rule 8: H_rel credited to a report of a ruling',d=>{d['market-records'][1].H_rel_ruling='FT-002';},'rule 8, H_rel_ruling'],
 ['claim cited as a source',d=>{d['market-records'][0].source_id='CL-001';},'is a claim, not a source'],
 ['text after a closing quote',d=>d,'Text after a closing quote',f=>{f[csv('rulings')]=f[csv('rulings')].replace('FT-002,','"FT-002"x,');}],
 ['quote inside an unquoted field',d=>d,'Quote inside an unquoted field',f=>{f[csv('rulings')]=f[csv('rulings')].replace('FT-002,','FT-0"02,');}]
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

runBridgeFixtures();
