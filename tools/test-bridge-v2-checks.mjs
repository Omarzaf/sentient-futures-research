import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {fileURLToPath, pathToFileURL} from 'node:url';
import {checkBridgeV2, checkBridgeFiles, checkSchema} from './bridge-v2-checks.mjs';

const dir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../research/halal-cultivated/bridge-v2');
const read = name => JSON.parse(fs.readFileSync(path.join(dir, name), 'utf8'));
const schema = read('schema.json');
const example = () => read('synthetic-example.json');
const blocked = () => read('production-state.json');
const s = d => d.scenarios[0];
const b = d => d.baselines[0];
const o = d => d.expected_outputs[0];
function assessment(d, dimension, status, id) {
 return {id, institution_id: `SYN-INSTITUTION-${dimension}`, jurisdiction: s(d).scope.geo, territorial_scope: 'national', segment_scope: s(d).scope.segment, product_id: s(d).product_id, process_profile_id: s(d).process_profile_id, dimension, status, conditions: [], source_ids: ['SYN-001'], passage_locators: ['Synthetic fixture paragraph 1'], issued_at: '2029-01-01', effective_from: '2029-01-01', effective_to: '2031-12-31', checked_at: '2030-01-01', interpretation_limits: 'Synthetic scoped test; no actual institution or act.', evidence_review_status: 'agent_checked', human_review_status: 'pending', not_applicable_reason: null, search_scope: null, document_type: dimension === 'product_certificate' ? 'certificate' : dimension === 'religious_position' ? 'religious_position' : 'adopted_instrument', instrument_id: 'SYN-INSTRUMENT', binding: dimension === 'food_authorization', amendments_checked: true};
}
function evidenceLed(d) {
 d.assessments = [assessment(d, 'religious_position', 'permitted', 'A-REL'), assessment(d, 'product_certificate', 'certificate_issued', 'A-CERT'), assessment(d, 'food_authorization', 'authorized', 'A-FOOD')];
 Object.assign(s(d).gate, {basis: 'evidence_led', assessment_ids: d.assessments.map(x => x.id), assumed_conditions: [], counterfactual_label: null, assumption_rationale: null});
}
function secondScenario(d) {
 const extra = structuredClone(s(d)); extra.id = 'SC-TWO'; extra.capacity.allocation_id = 'ALLOC-TWO'; extra.capacity.value = 10; s(d).capacity.value = 30;
 d.scenarios.push(extra); o(d).Q_feasible = 30; o(d).cultivated_biomass = 6;
 d.expected_outputs.push({...o(d), scenario_id: extra.id, Q_feasible: 10, cultivated_biomass: 2});
 return extra;
}
const negativeCases = [
 ['legacy schema version', d => {d.version = '1.0.0';}, 'enum'],
 ['unrecognized field', d => {s(d).hidden_discount = .8;}, 'unknown field'],
 ['survey as sales', d => {b(d).evidence_type = 'survey_willingness';}, 'survey willingness'],
 ['value share without prices', d => {b(d).relative_price = null;}, 'missing price needs reason'],
 ['zero relative price', d => {b(d).relative_price = 0;}, 'positive relative price'],
 ['missing currency basis', d => {b(d).scope.currency=null;}, 'value conversion needs currency and price year'],
 ['cultivated over conventional ratio as share', d => {b(d).scope.denominator = 'conventional_only';}, 'inclusive two-component denominator'],
 ['mass ratio is not a total-market share', d => {Object.assign(b(d),{basis:'mass_share',relative_price:null,price_scope:null,price_source_ids:[]});b(d).scope.denominator='conventional_only';b(d).conditioning.permitted_transformations=['transfer_mass_share'];}, 'mass share requires total compatible'],
 ['retail over all-channel denominator', d => {b(d).scope.channel = 'all';}, 'channel mismatch'],
 ['chicken over all-meat denominator', d => {b(d).scope.species = 'all_meat';}, 'denominator, year or channel mismatch'],
 ['incompatible D scope', d => {s(d).quantity.scope.channel = 'all';}, 'D and target estimand differ'],
 ['carcass weight used without conversion', d => {s(d).scope.mass_basis = 'tonnes_carcass_equivalent';}, 'unsupported mass basis'],
 ['prices from another year', d => {b(d).price_scope.year = 2029;}, 'prices must describe identical'],
 ['prices from another geography', d => {b(d).price_scope.geo = 'GBR';}, 'prices must describe identical'],
 ['prices from another channel', d => {b(d).price_scope.channel = 'foodservice';}, 'prices must describe identical'],
 ['new year silently interpolated', d => {b(d).scope.year = 2035;}, 'year or channel mismatch'],
 ['transfer portrayed as observed', d => {s(d).transfer.status = 'not_required';}, 'must be labeled an assumption'],
 ['conditioning unknown', d => {b(d).conditioning.reference = 'unknown';}, 'undocumented baseline conditioning'],
 ['conditioning undocumented', d => {b(d).conditioning.documented = false;}, 'undocumented baseline conditioning'],
 ['unconditional sales treated as full-access', d => {b(d).conditioning.reference = 'unconditional_sales';}, 'owner restructuring'],
 ['unpermitted baseline transformation', d => {b(d).conditioning.permitted_transformations = [];}, 'transformation not permitted'],
 ['embedded religious rejection adjusted twice', d => {b(d).conditioning.embedded_mechanisms.push('religious_acceptance');}, 'double adjustment'],
 ['embedded supply constraint applied twice', d => {b(d).conditioning.embedded_mechanisms.push('supply');}, 'double adjustment'],
 ['embedded legal timing applied twice', d => {b(d).conditioning.embedded_mechanisms.push('legal_access');}, 'double adjustment'],
 ['q10 divided by q10 labeled output q10', d => {Object.assign(b(d).uncertainty,{method:'marginal_quantile_ratio',output_label:'q10'});}, 'marginal quantile ratios'],
 ['quantile label without joint model', d => {b(d).uncertainty.output_label = 'q90';}, 'marginal quantile ratios'],
 ['missing baseline not zero', d => {d.baselines=[];s(d).baseline_id=null;s(d).gate.state='closed';Object.assign(o(d),{p_mass:0,G:0,Q_unconstrained:0,Q_feasible:0,cultivated_biomass:0});}, 'p_mass expected output'],
 ['missing demand not zero under closed gate', d => {s(d).quantity.value=null;s(d).quantity.missing_reason='Missing';s(d).gate.state='closed';Object.assign(o(d),{G:0,Q_unconstrained:0,Q_feasible:0,cultivated_biomass:0});}, 'Q_unconstrained expected output'],
 ['missing capacity not feasible quantity', d => {s(d).capacity=null;}, 'Q_feasible expected output'],
 ['unresolved evidence not zero gate', d => {s(d).gate.state='unresolved';Object.assign(o(d),{G:0,Q_unconstrained:0,Q_feasible:0,cultivated_biomass:0});}, 'G expected output'],
 ['missing certificate', d => {evidenceLed(d);s(d).gate.assessment_ids.pop();}, 'open gate lacks applicable support'],
 ['religious permission mistaken for certificate', d => {evidenceLed(d);d.assessments[1].status='permitted';}, 'status is incompatible with evidence dimension'],
 ['certificate mistaken for food approval', d => {evidenceLed(d);s(d).gate.required_dimensions=['religious_position','product_certificate'];s(d).gate.assessment_ids=['A-REL','A-CERT'];}, 'food authorization cannot be replaced'],
 ['unknown assessment not open', d => {evidenceLed(d);d.assessments[0].status='unknown';}, 'unknown is not permission'],
 ['institutional conflict preserved', d => {evidenceLed(d);d.assessments[0].status='conflicting';}, 'conflicting evidence'],
 ['opposed institutions cannot collapse to closure', d => {evidenceLed(d);const other={...d.assessments[0],id:'A-OPPOSED',institution_id:'SYN-OTHER',status:'prohibited'};d.assessments.push(other);s(d).gate.assessment_ids.push(other.id);s(d).gate.state='closed';}, 'conflicting institutions require unresolved'],
 ['positive label does not erase unmet conditions', d => {evidenceLed(d);d.assessments[0].conditions=[{id:'C1',status:'unmet',source_ids:['SYN-001'],locator:'Synthetic'}];}, 'open gate lacks applicable support'],
 ['condition unresolved', d => {evidenceLed(d);d.assessments[0].status='conditional';d.assessments[0].conditions=[{id:'C-1',status:'unknown',source_ids:[],locator:null}];}, 'open gate lacks applicable support'],
 ['conditional with no conditions', d => {evidenceLed(d);d.assessments[0].status='conditional';}, 'conditional assessment needs conditions'],
 ['met condition without evidence', d => {evidenceLed(d);d.assessments[0].status='conditional';d.assessments[0].conditions=[{id:'C-1',status:'met',source_ids:[],locator:null}];}, 'met condition needs locator'],
 ['India religious prohibition does not close all national sales', d => {evidenceLed(d);s(d).scope.geo='IND';s(d).quantity.scope.geo='IND';s(d).scope.segment='all_consumers';s(d).quantity.scope.segment='all_consumers';d.assessments.forEach(a=>{a.jurisdiction='IND';a.segment_scope='all_consumers';});d.assessments[0].status='prohibited';s(d).gate.state='closed';}, 'national closure needs binding access restriction'],
 ['cross-country evidence', d => {evidenceLed(d);d.assessments[0].jurisdiction='SGP';}, 'scope transfer'],
 ['cross-product evidence', d => {evidenceLed(d);d.assessments[0].product_id='another_product';}, 'scope transfer'],
 ['cross-process evidence', d => {evidenceLed(d);d.assessments[0].process_profile_id='another_process';}, 'scope transfer'],
 ['cross-segment evidence', d => {evidenceLed(d);d.assessments[0].segment_scope='different_segment';}, 'scope transfer'],
 ['subnational approval not national coverage', d => {evidenceLed(d);d.assessments[2].territorial_scope='subnational';}, 'subnational access evidence'],
 ['undated legal effect unresolved', d => {evidenceLed(d);d.assessments[2].effective_from=null;}, 'open gate lacks applicable support'],
 ['proposal not effective law', d => {evidenceLed(d);d.assessments[2].document_type='proposal';}, 'open gate lacks applicable support'],
 ['amendment not checked', d => {evidenceLed(d);d.assessments[2].amendments_checked=false;}, 'amendment-unchecked'],
 ['expired certificate', d => {evidenceLed(d);d.assessments[1].effective_to='2029-12-31';}, 'expired, future'],
 ['invalid calendar date', d => {evidenceLed(d);d.assessments[1].effective_to='2031-02-30';}, 'invalid effective_to'],
 ['certificate identifier missing', d => {evidenceLed(d);d.assessments[1].instrument_id=null;}, 'certificate requires identifier'],
 ['counterfactual unlabeled', d => {s(d).gate.counterfactual_label=null;}, 'counterfactual gate needs label'],
 ['counterfactual contradiction not disclosed', d => {d.assessments=[assessment(d,'religious_position','prohibited','A-REL')];s(d).gate.assessment_ids=['A-REL'];}, 'contradiction must be disclosed'],
 ['supply allocation exceeds pool', d => {secondScenario(d).capacity.value=30;}, 'allocations exceed source pool'],
 ['same allocation spent twice', d => {secondScenario(d).capacity.allocation_id=s(d).capacity.allocation_id;}, 'allocation used twice'],
 ['capacity year mismatch', d => {d.capacity_pools[0].year=2035;}, 'capacity year mismatch'],
 ['capacity belongs to another product', d => {d.capacity_pools[0].eligible_product_ids=['other_product'];}, 'capacity pool product/process incompatibility'],
 ['capacity belongs to another process', d => {d.capacity_pools[0].eligible_process_profile_ids=['other_process'];}, 'capacity pool product/process incompatibility'],
 ['hybrid counted as cultivated too', d => {const extra=secondScenario(d);s(d).aggregation_group='TOTAL';extra.aggregation_group='TOTAL';extra.product_form='cultivated';extra.cultivated_fraction=1;}, 'hybrid or observation counted twice'],
 ['overlapping segment totals', d => {const extra=secondScenario(d);s(d).aggregation_group='TOTAL';extra.aggregation_group='TOTAL';extra.observation_id='other';}, 'overlapping segment totals'],
 ['alternative worlds aggregated', d => {const extra=secondScenario(d);s(d).aggregation_group='TOTAL';extra.aggregation_group='TOTAL';extra.allocation_group='ALTERNATIVE';}, 'alternative worlds cannot be aggregated'],
 ['overlapping partition members', d => {d.partitions=[{id:'PART',geo:'PAK',year:2030,definition:'invalid overlapping consumer groups',source_ids:['SYN-001'],segments:[{id:'A',members:['one']},{id:'B',members:['one']}]}];}, 'overlapping segment membership'],
 ['fraction is not displacement', d => {s(d).displacement=8;}, 'unknown field'],
 ['pure product given hybrid fraction', d => {s(d).product_form='cultivated';}, 'pure cultivated product fraction'],
 ['price shock called substitution', d => {s(d).mechanisms=[{mechanism:'price',target_parameter:'baseline_share',source_ids:['SYN-001'],assumed:true,rationale:'Unvalidated behavioral change'}];}, 'no price-induced substitution'],
 ['shock mechanism repeated', d => {const m={mechanism:'animal_disease',target_parameter:'D',source_ids:['SYN-001'],assumed:true,rationale:'Synthetic'};s(d).mechanisms=[m,m];}, 'repeated shock mechanism'],
 ['orphan baseline source', d => {b(d).source_ids=['MISSING'];}, 'orphan source'],
 ['missing citation locator', d => {d.sources[0].locator='';}, 'empty text'],
 ['orphan evidence source', d => {evidenceLed(d);d.assessments[0].source_ids=['MISSING'];}, 'orphan source'],
 ['orphan assessment', d => {s(d).gate.assessment_ids=['MISSING'];}, 'orphan assessment'],
 ['synthetic example relabeled production', d => {d.mode='research';d.status='candidate_pending_review';}, 'synthetic source cannot enter research production'],
 ['NaN demand', d => {s(d).quantity.value=NaN;}, 'finite number required'],
 ['negative demand', d => {s(d).quantity.value=-1;}, 'below minimum'],
 ['negative allocation', d => {s(d).capacity.value=-1;}, 'below minimum'],
 ['duplicate scenario id', d => {secondScenario(d).id=s(d).id;}, 'duplicate ID'],
];

export function runBridgeFixtures() {
 let positives = 0; let negatives = 0;
 const pass = (d, label) => {const result=checkBridgeV2(d,schema);assert.deepEqual(result.failures,[],label);positives++;return result;};
 // Independent hand calculation uses two price-divided value components rather
 // than the implementation's value-share identity.
 const handMass=(10/2)/((10/2)+(90/1));
 const result=pass(example(),'synthetic example');assert.ok(Math.abs(result.results[0].p_mass-handMass)<1e-12);assert.equal(result.results[0].Q_feasible,40);assert.equal(result.results[0].cultivated_biomass,8);
 pass(blocked(),'production remains unestimated');
 const evidence=example();evidenceLed(evidence);pass(evidence,'scoped evidence-led open fixture');
 const missingCap=example();s(missingCap).capacity=null;Object.assign(o(missingCap),{Q_feasible:null,cultivated_biomass:null,reason_codes:['missing_capacity']});pass(missingCap,'uncapped demand separate from missing feasible quantity');
 const missingPrice=example();b(missingPrice).relative_price=null;b(missingPrice).missing_reason='Price unresolved';Object.assign(o(missingPrice),{p_mass:null,Q_unconstrained:null,Q_feasible:null,cultivated_biomass:null,reason_codes:['missing_share_or_price']});pass(missingPrice,'missing conversion input stays null');
 const mismatch=example();s(mismatch).capacity.unit='kg_cultivated_biomass';Object.assign(o(mismatch),{Q_feasible:null,cultivated_biomass:null,reason_codes:['incompatible_capacity_basis']});pass(mismatch,'incompatible capacity remains unestimated');
 const unknown=example();s(unknown).gate.state='unresolved';Object.assign(o(unknown),{G:null,Q_unconstrained:null,Q_feasible:null,cultivated_biomass:null,reason_codes:['unresolved_gate']});pass(unknown,'unknown stays unknown');
 const closed=example();s(closed).gate.state='closed';Object.assign(o(closed),{G:0,Q_unconstrained:0,Q_feasible:0,cultivated_biomass:0,reason_codes:['counterfactual_closed']});pass(closed,'explicit hypothetical closure');
 const noDemand=structuredClone(closed);s(noDemand).quantity.value=null;s(noDemand).quantity.missing_reason='Missing market';Object.assign(o(noDemand),{Q_unconstrained:null,Q_feasible:null,cultivated_biomass:null,reason_codes:['missing_reference_market','counterfactual_closed']});pass(noDemand,'closed scenario cannot fill absent demand');
 const poolMissing=example();poolMissing.capacity_pools[0].value=null;poolMissing.capacity_pools[0].missing_reason='Missing pool';Object.assign(o(poolMissing),{Q_feasible:null,cultivated_biomass:null,reason_codes:['missing_pool_capacity']});pass(poolMissing,'unknown capacity pool');
 const allocated=example();secondScenario(allocated);pass(allocated,'single pool allocated across simultaneous cells');
 const partitioned=example();const extra=secondScenario(partitioned);extra.scope.segment='second_disjoint_segment';extra.quantity.scope.segment='second_disjoint_segment';extra.observation_id='second_finished_product';for(const row of partitioned.scenarios){row.aggregation_group='TOTAL';row.partition_id='PART';}partitioned.partitions=[{id:'PART',geo:'PAK',year:2030,definition:'Two synthetic disjoint consumer cells, not a factual population claim',source_ids:['SYN-001'],segments:[{id:s(partitioned).scope.segment,members:['member-A']},{id:extra.scope.segment,members:['member-B']}]}];pass(partitioned,'documented disjoint aggregate');
 const scopedClosed=example();evidenceLed(scopedClosed);scopedClosed.assessments[0].status='prohibited';s(scopedClosed).gate.state='closed';Object.assign(o(scopedClosed),{G:0,Q_unconstrained:0,Q_feasible:0,cultivated_biomass:0,reason_codes:['scoped_evidence_closed']});pass(scopedClosed,'religious closure remains within specified segment');
 const fixedPrice=example();s(fixedPrice).mechanisms=[{mechanism:'price',target_parameter:'conventional_price',source_ids:['SYN-001'],assumed:true,rationale:'Restricted accounting: conventional price reported separately; penetration and quantity unchanged, no substitution effect.'}];pass(fixedPrice,'price reporting does not invent substitution');
 const mass=example();Object.assign(b(mass),{basis:'mass_share',share:handMass,relative_price:null,price_scope:null,price_source_ids:[]});b(mass).conditioning.permitted_transformations=['transfer_mass_share'];pass(mass,'native mass share');
 const met=example();evidenceLed(met);met.assessments[0].status='conditional';met.assessments[0].conditions=[{id:'C1',status:'met',source_ids:['SYN-001'],locator:'Synthetic condition'}];pass(met,'condition support remains separate from assumption');
 for (const [label, mutate, message] of negativeCases) {const d=example();mutate(d);const r=checkBridgeV2(d,schema);assert.ok(r.failures.some(x=>x.includes(message)),`${label}: expected ${message}\n${r.failures.join('\n')}`);assert.deepEqual(r.results,[],`${label}: invalid contract leaked numbers`);negatives++;}
 assert.ok(checkSchema({}, {...schema, oneOf:[]}).failures.some(x=>x.includes('unsupported schema keyword')));negatives++;
 assert.ok(checkBridgeFiles({}).failures.length);negatives++;
 const receipt={status:'PASS',suite:'bridge-v2',positiveCases:positives,negativeCases:negatives,assertions:'Every invalid contract rejects with its intended invariant and returns no numerical results.',productionState:'blocked_missing_baseline',syntheticExample:{p_mass:handMass,Q_unconstrained:1000*handMass,Q_feasible:40,cultivated_biomass:8}};
 console.log(JSON.stringify(receipt));return receipt;
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) runBridgeFixtures();
