import assert from 'node:assert/strict';
import fs from 'node:fs';
import {checkContinuation} from './continuation-checks.mjs';
const directory=new URL('../research/halal-cultivated/phase1-continuation/',import.meta.url);
const fixture=Object.fromEntries(fs.readdirSync(directory).map(name=>[name,fs.readFileSync(new URL(name,directory),'utf8')]));
assert.deepEqual(checkContinuation(fixture).failures,[]);
const alter=(files,name,mutate)=>{const value=JSON.parse(files[name]);mutate(value);files[name]=JSON.stringify(value);};
const cases=[
 ['orphan source',f=>alter(f,'claims.json',r=>{r[0].source_ids=['missing'];}),'unresolved claim source'],
 ['orphan review',f=>alter(f,'claims.json',r=>{r[0].review_id='missing';}),'missing independent claim review'],
 ['omitted named country',f=>alter(f,'coverage.json',r=>{r.countries.pop();}),'named-country coverage lost'],
 ['false full completion',f=>alter(f,'coverage.json',r=>{r.completion_established=true;}),'promoted to complete'],
 ['stage code treated as approval',f=>alter(f,'observations.json',r=>{r.fssai.decision_outcome='approved';}),'ambiguous stage promoted'],
 ['receipt date treated as approval',f=>alter(f,'observations.json',r=>{r.fssai.approval_date=r.fssai.receipt_date;}),'ambiguous stage promoted'],
 ['export rule treated as domestic access',f=>alter(f,'observations.json',r=>{r.export_policy.domestic_food_approval_established=true;}),'export rule promoted'],
 ['August instead of February time origin',f=>alter(f,'observations.json',r=>{r.export_policy.egypt_transition.origin_date='2026-08-05';}),'transition origin'],
 ['legal preference treated as demographic estimate',f=>alter(f,'observations.json',r=>{r.geography.constitutional_rule_is_population_estimate=true;}),'legal rule promoted'],
 ['agent check treated as human review',f=>alter(f,'claims.json',r=>{r[0].human_review='approved';}),'unsupported human claim approval'],
 ['valid claim assigned to wrong country',f=>alter(f,'coverage.json',r=>{r.countries.find(c=>c.id==='CHN').claim_ids=['P1C-C01'];}),'country scope/claim link'],
 ['unsupported country completion',f=>alter(f,'coverage.json',r=>{r.countries.find(c=>c.id==='CHN').coverage='complete';}),'unsupported country completion'],
 ['invented population share',f=>alter(f,'coverage.json',r=>{r.countries[0].populationSchoolShares={Hanafi:100};}),'unsupported school population shares'],
 ['empty export source chain',f=>alter(f,'observations.json',r=>{r.export_policy.source_ids=[];}),'export policy source/scope lost'],
 ['observation human approval invented',f=>alter(f,'observations.json',r=>{r.human_review='approved';}),'unsupported observation human approval'],
 ['filename mistaken for regulatory identity',f=>alter(f,'source-register.json',r=>{r.find(s=>s.id==='P1C-IN-MISMATCH').status='accepted_regulation';}),'mislabeled download promoted'],
 ['history-only China replaces a geography country',f=>alter(f,'geography.json',r=>{r.countries.find(c=>c.id==='EGY').id='CHN';}),'geography roster'],
 ['geography cites another country claim',f=>alter(f,'geography.json',r=>{r.countries.find(c=>c.id==='IND').historical_affiliation[0].claim_id='P1C2-PAK-DEMOGRAPHY';}),'geography affiliation lineage'],
 ['Muslim-population estimate becomes total-population share',f=>alter(f,'geography.json',r=>{r.countries[0].historical_affiliation[0].denominator='Total population';}),'Pew 2009 scope'],
 ['historical estimate given a current year',f=>alter(f,'geography.json',r=>{r.countries[0].historical_affiliation[0].year=2026;}),'Pew 2009 scope'],
 ['approximate point converted into a range',f=>alter(f,'geography.json',r=>{Object.assign(r.countries.find(c=>c.id==='ARE').historical_affiliation[0],{lower:10,upper:10,point:null});}),'Pew point/range'],
 ['Pew estimate range becomes confidence interval',f=>alter(f,'geography.json',r=>{r.countries[0].historical_affiliation[0].range_is_confidence_interval=true;}),'Pew 2009 scope'],
 ['historical estimates promoted to current affiliation',f=>alter(f,'geography.json',r=>{r.countries[0].current_affiliation=r.countries[0].historical_affiliation[0];}),'unestablished geography field'],
 ['Shia estimate subtracted to invent Ibadi remainder',f=>alter(f,'geography.json',r=>{r.countries.find(c=>c.id==='OMN').numerical_remainder={Ibadi:90};}),'unestablished geography field'],
 ['Iraq publication date treated as survey fieldwork',f=>alter(f,'geography.json',r=>{r.countries.find(c=>c.id==='IRQ').historical_affiliation[1].year=2014;}),'Iraq survey design'],
 ['Iran legal school becomes population predominance',f=>alter(f,'geography.json',r=>{r.countries.find(c=>c.id==='IRN').predominant_juristic_schools=['Twelver Jafari'];}),'unestablished geography field'],
 ['Maliki organ locator becomes school consensus',f=>alter(f,'school-gap-progress.json',r=>{r.readings[0].school_wide_consensus_established=true;}),'classical locator overclaimed'],
 ['bounded negative search becomes proposition absence',f=>alter(f,'school-gap-progress.json',r=>{r.unresolved[0].proposition_absent=true;}),'negative search promoted']
];
for(const [name,mutate,expected] of cases){const f={...fixture};mutate(f);assert(checkContinuation(f).failures.some(s=>s.includes(expected)),name+' must reject');}
console.log(JSON.stringify({status:'PASS',suite:'phase1-continuation',validFixtureChecks:checkContinuation(fixture).checks,negativeCases:cases.length}));
