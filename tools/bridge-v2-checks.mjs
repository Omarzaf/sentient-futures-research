// Pure, dependency-free contract checks. Synthetic fixtures do not certify research.
export const BRIDGE_VERSION = '2.0.0';
const present = value => typeof value === 'string' && value.trim().length > 0;
const close = (a, b) => a === b || (Number.isFinite(a) && Number.isFinite(b) && Math.abs(a - b) <= 1e-9 * Math.max(1, Math.abs(a), Math.abs(b)));
const date = value => /^\d{4}-\d{2}-\d{2}$/.test(value ?? '') && !Number.isNaN(Date.parse(value)) && new Date(value).toISOString().slice(0, 10) === value;
const scopeKeys = ['geo', 'segment', 'year', 'species', 'product_definition', 'channel', 'denominator', 'mass_basis', 'currency', 'price_year'];
const sameScope = (a, b, keys = scopeKeys) => keys.every(key => a?.[key] === b?.[key]);
const dimensionStatuses = {
 religious_position: ['permitted', 'prohibited', 'conditional'],
 certification_route: ['route_available', 'route_unavailable', 'conditional'],
 product_certificate: ['certificate_issued', 'certificate_refused', 'certificate_expired', 'conditional'],
 food_authorization: ['authorized', 'refused', 'pending', 'conditional'],
 import_access: ['access_allowed', 'access_refused', 'pending', 'conditional'],
};
const openStatuses = new Set(['permitted', 'route_available', 'certificate_issued', 'authorized', 'access_allowed']);
const closedStatuses = new Set(['prohibited', 'route_unavailable', 'certificate_refused', 'certificate_expired', 'refused', 'access_refused']);
const commonStatuses = ['unknown', 'conflicting', 'not_found_in_bounded_search', 'not_applicable'];
const mechanismFor = {religious_position: 'religious_acceptance', certification_route: 'certification', product_certificate: 'certification', food_authorization: 'legal_access', import_access: 'legal_access'};

// This implements only the JSON Schema keywords used by the shipped schema.
// Schema dialect growth must add support here and fixtures; it cannot silently pass.
export function checkSchema(value, schema) {
 const failures = []; let checks = 0;
 const check = (ok, msg) => { checks++; if (!ok) failures.push(msg); };
 const keywords = new Set(['$schema', '$id', '$defs', '$ref', 'title', 'description', 'type', 'enum', 'required', 'properties', 'additionalProperties', 'items', 'minItems', 'minLength', 'pattern', 'minimum', 'maximum']);
 function visit(v, rule, at) {
  for (const key of Object.keys(rule)) check(keywords.has(key), `${at}: unsupported schema keyword ${key}`);
  if (rule.$ref) {
   const target = rule.$ref.startsWith('#/$defs/') ? schema.$defs?.[rule.$ref.slice(8)] : null;
   check(!!target, `${at}: unresolved schema reference`); if (target) visit(v, target, at); return;
  }
  const type = v === null ? 'null' : Array.isArray(v) ? 'array' : typeof v;
  const types = [].concat(rule.type ?? []);
  check(types.length === 0 || types.some(t => t === type || t === 'integer' && Number.isInteger(v)), `${at}: invalid type`);
  if (rule.enum) check(rule.enum.some(x => x === v), `${at}: value not in allowed enum`);
  if (typeof v === 'number') {
   check(Number.isFinite(v), `${at}: finite number required`);
   if (rule.minimum != null) check(v >= rule.minimum, `${at}: below minimum`);
   if (rule.maximum != null) check(v <= rule.maximum, `${at}: above maximum`);
  }
  if (typeof v === 'string') {
   if (rule.minLength != null) check(v.trim().length >= rule.minLength, `${at}: empty text`);
   if (rule.pattern) check(new RegExp(rule.pattern).test(v), `${at}: pattern mismatch`);
  }
  if (Array.isArray(v)) {
   if (rule.minItems != null) check(v.length >= rule.minItems, `${at}: too few items`);
   if (rule.items) v.forEach((x, i) => visit(x, rule.items, `${at}[${i}]`));
  }
  if (type === 'object') {
   for (const key of rule.required ?? []) check(Object.hasOwn(v, key), `${at}.${key}: required`);
   if (rule.additionalProperties === false) for (const key of Object.keys(v)) check(Object.hasOwn(rule.properties ?? {}, key), `${at}.${key}: unknown field`);
   for (const [key, r] of Object.entries(rule.properties ?? {})) if (Object.hasOwn(v, key)) visit(v[key], r, `${at}.${key}`);
  }
 }
 visit(value, schema, 'bridge'); return {checks, failures};
}

export function massShare(baseline) {
 if (baseline == null || baseline.share === null) return null;
 if (baseline.basis === 'mass_share') return baseline.share;
 if (baseline.basis === 'value_share_two_component' && baseline.relative_price !== null && baseline.relative_price > 0) {
  return baseline.share / (baseline.share + (1 - baseline.share) * baseline.relative_price);
 }
 return null;
}

export function checkBridgeV2(doc, schema) {
 const structural = checkSchema(doc, schema);
 const failures = [...structural.failures]; let checks = structural.checks;
 const check = (ok, msg) => { checks++; if (!ok) failures.push(`bridge-v2: ${msg}`); };
 // No arithmetic can run on malformed input, even if unrelated fields are valid.
 if (failures.length) return {checks, failures, results: [], status: 'invalid_contract'};
 check(doc.version === BRIDGE_VERSION, 'version must be 2.0.0; no implicit legacy migration');
 check((doc.mode === 'synthetic_test') === (doc.status === 'synthetic_test_only'), 'synthetic and research states must remain distinct');
 const index = (rows, label) => {
  const map = new Map();
  for (const row of rows) { check(!map.has(row.id), `${label}: duplicate ID ${row.id}`); map.set(row.id, row); }
  return map;
 };
 const sources = index(doc.sources, 'source');
 const assessments = index(doc.assessments, 'assessment');
 const baselines = index(doc.baselines, 'baseline');
 const pools = index(doc.capacity_pools, 'capacity pool');
 const partitions = index(doc.partitions, 'partition');
 index(doc.scenarios, 'scenario');
 const references = (ids, where, required = true) => {
  check(!required || ids.length > 0, `${where}: source required`);
  check(new Set(ids).size === ids.length, `${where}: duplicate source reference`);
  for (const id of ids) check(sources.has(id), `${where}: orphan source ${id}`);
 };
 for (const source of doc.sources) {
  check(source.kind !== 'synthetic' || doc.mode === 'synthetic_test', `${source.id}: synthetic source cannot enter research production`);
  check(present(source.locator), `${source.id}: citation locator required`);
  if (source.kind === 'public') check(/^https?:\/\//.test(source.url ?? ''), `${source.id}: public source URL required`);
 }
 for (const a of doc.assessments) {
  check([...dimensionStatuses[a.dimension], ...commonStatuses].includes(a.status), `${a.id}: status is incompatible with evidence dimension`);
  references(a.source_ids, a.id, !['unknown', 'not_found_in_bounded_search'].includes(a.status));
  check(a.passage_locators.length > 0 || ['unknown', 'not_found_in_bounded_search'].includes(a.status), `${a.id}: passage locator required`);
  for (const key of ['issued_at', 'effective_from', 'effective_to', 'checked_at']) check(a[key] === null || date(a[key]), `${a.id}: invalid ${key}`);
  check(date(a.checked_at), `${a.id}: checked_at required`);
  if (a.effective_from && a.effective_to) check(a.effective_from <= a.effective_to, `${a.id}: reversed effective dates`);
  if (a.status === 'not_applicable') check(present(a.not_applicable_reason), `${a.id}: not_applicable needs supported reason`);
  if (a.status === 'not_found_in_bounded_search') check(present(a.search_scope), `${a.id}: bounded search scope required`);
  if (a.status === 'conditional') check(a.conditions.length > 0, `${a.id}: conditional assessment needs conditions`);
  for (const c of a.conditions) { references(c.source_ids, `${a.id}/${c.id}`, c.status === 'met'); if (c.status === 'met') check(present(c.locator), `${a.id}/${c.id}: met condition needs locator`); }
  if (a.status === 'certificate_issued') check(present(a.instrument_id) && a.effective_from !== null && a.effective_to !== null, `${a.id}: certificate requires identifier and validity`);
 }
 for (const b of doc.baselines) {
  references(b.source_ids, b.id);
  check(['observed_sales', 'forecast_sales'].includes(b.evidence_type), `${b.id}: survey willingness is not sales penetration`);
  check(date(b.source_vintage), `${b.id}: source vintage required`);
  check(b.conditioning.reference !== 'unknown' && b.conditioning.documented, `${b.id}: undocumented baseline conditioning blocks transfer`);
  check(b.scope.denominator === 'cultivated_plus_conventional', `${b.id}: mass share requires total compatible cultivated-plus-conventional market`);
  references(b.conditioning.source_ids, `${b.id} conditioning`);
  check(b.conditioning.permitted_transformations.includes(b.basis === 'mass_share' ? 'transfer_mass_share' : 'value_to_mass_then_transfer'), `${b.id}: transformation not permitted by baseline contract`);
  check(new Set(b.conditioning.embedded_mechanisms).size === b.conditioning.embedded_mechanisms.length, `${b.id}: duplicate embedded mechanism`);
  if (b.share === null) check(present(b.missing_reason), `${b.id}: missing share needs reason`);
  if (b.basis === 'value_share_two_component') {
   check(b.scope.denominator === 'cultivated_plus_conventional', `${b.id}: value share needs inclusive two-component denominator`);
   check(present(b.scope.currency) && Number.isInteger(b.scope.price_year), `${b.id}: value conversion needs currency and price year`);
   check(b.relative_price === null || b.relative_price > 0, `${b.id}: positive relative price required`);
   check(b.price_scope !== null && sameScope(b.scope, b.price_scope), `${b.id}: prices must describe identical geography, period, channel and mass basis`);
   references(b.price_source_ids, `${b.id} prices`);
   if (b.relative_price === null) check(present(b.missing_reason), `${b.id}: missing price needs reason`);
  } else check(b.relative_price === null && b.price_scope === null && b.price_source_ids.length === 0, `${b.id}: mass share cannot silently carry a value conversion`);
  check(b.uncertainty.method === 'deterministic_sensitivity' && b.uncertainty.output_label === 'sensitivity', `${b.id}: marginal quantile ratios are not output quantiles; joint-draw methods need a new registered implementation`);
  check(present(b.uncertainty.dependence_assumption), `${b.id}: uncertainty interpretation required`);
 }
 for (const p of doc.capacity_pools) { references(p.source_ids, p.id); if (p.value === null) check(present(p.missing_reason), `${p.id}: missing pool needs reason`); }
 for (const p of doc.partitions) {
  references(p.source_ids, p.id);
  const members = new Set(); const ids = new Set();
  for (const s of p.segments) {
   check(!ids.has(s.id), `${p.id}: duplicate segment`); ids.add(s.id);
   for (const member of s.members) { check(!members.has(member), `${p.id}: overlapping segment membership ${member}`); members.add(member); }
  }
 }
 const usedAllocations = new Set(); const allocations = new Map(); const groups = new Map(); const calculated = [];
 for (const s of doc.scenarios) {
  const b = s.baseline_id === null ? null : baselines.get(s.baseline_id);
  check(s.baseline_id === null || !!b, `${s.id}: orphan baseline`);
  check(s.scope.mass_basis === 'kg_finished_product' || s.scope.mass_basis === 'tonnes_finished_product', `${s.id}: unsupported mass basis; explicit conversion needed before bridge`);
  check(s.quantity.value !== null || present(s.quantity.missing_reason), `${s.id}: missing demand needs reason`);
  references(s.quantity.source_ids, `${s.id} reference market`, s.quantity.value !== null);
  check(s.quantity.value === null || sameScope(s.scope, s.quantity.scope), `${s.id}: D and target estimand differ`);
  if (b) {
   check(sameScope(b.scope, s.scope, scopeKeys.filter(key => key !== 'geo' && key !== 'segment')), `${s.id}: baseline dimensional, denominator, year or channel mismatch`);
   if (!sameScope(b.scope, s.scope)) check(s.transfer.status === 'assumed' && present(s.transfer.rationale), `${s.id}: geographic or segment transfer must be labeled an assumption`);
   check(b.conditioning.reference === 'full_access_reference' || s.gate.state === 'unresolved', `${s.id}: unconditional sales baseline requires explicit owner restructuring before gates`);
  }
  check(new Set(s.gate.required_dimensions).size === s.gate.required_dimensions.length, `${s.id}: repeated required dimension`);
  check(s.gate.required_dimensions.includes('food_authorization'), `${s.id}: food authorization cannot be replaced by religious permission or certificate`);
  const evidence = s.gate.assessment_ids.map(id => assessments.get(id));
  check(evidence.every(Boolean), `${s.id}: orphan assessment`);
  check(new Set(s.gate.assessment_ids).size === evidence.length, `${s.id}: duplicate assessment reference`);
  for (const a of evidence.filter(Boolean)) {
   check(a.jurisdiction === s.scope.geo && a.product_id === s.product_id && a.process_profile_id === s.process_profile_id && (a.segment_scope === s.scope.segment || a.segment_scope === 'all_consumers'), `${s.id}: evidence product/process/jurisdiction/segment scope transfer`);
   check(s.gate.required_dimensions.includes(a.dimension), `${s.id}: evidence dimension is not requested; cannot substitute dimensions`);
   if (['food_authorization', 'import_access'].includes(a.dimension)) check(a.territorial_scope === 'national', `${s.id}: subnational access evidence cannot establish national coverage`);
  }
  const currentEvidence = evidence.filter(Boolean);
  const applicableNow = a => (a.issued_at === null || a.issued_at <= s.as_of) && (a.effective_from === null || a.effective_from <= s.as_of) && (a.effective_to === null || a.effective_to >= s.as_of) && a.amendments_checked;
  check(date(s.as_of) && Number(s.as_of.slice(0, 4)) === s.scope.year, `${s.id}: as_of must be in scenario year`);
  if (s.gate.basis === 'evidence_led' && s.gate.state !== 'unresolved') {
   check(currentEvidence.every(applicableNow), `${s.id}: expired, future or amendment-unchecked assessment`);
   check(!currentEvidence.some(a => a.status === 'conflicting'), `${s.id}: conflicting evidence cannot become a known gate`);
   for (const dimension of s.gate.required_dimensions) {
    const rows = currentEvidence.filter(a => a.dimension === dimension);
    check(!(rows.some(a => openStatuses.has(a.status)) && rows.some(a => closedStatuses.has(a.status))), `${s.id}: conflicting institutions require unresolved assessment or counterfactual`);
   }
   check(!s.gate.contradicts_current_evidence, `${s.id}: evidence-led gate cannot contradict evidence`);
   check(s.gate.assumed_conditions.length === 0, `${s.id}: assumed conditions require a counterfactual gate`);
   if (s.gate.state === 'open') for (const dim of s.gate.required_dimensions) {
    const rows = currentEvidence.filter(a => a.dimension === dim);
    const support = a => (openStatuses.has(a.status) || a.status === 'conditional' && a.conditions.length > 0) && a.conditions.every(c => c.status === 'met') && (['food_authorization', 'import_access'].includes(dim) ? a.document_type === 'adopted_instrument' && a.binding && a.effective_from !== null : true);
    check(rows.length > 0 && rows.every(support), `${s.id}: open gate lacks applicable support for ${dim}; unknown is not permission`);
   }
   if (s.gate.state === 'closed') {
    const support = currentEvidence.some(a => closedStatuses.has(a.status) && (s.scope.segment === 'all_consumers' ? ['food_authorization', 'import_access'].includes(a.dimension) && a.binding && a.territorial_scope === 'national' && a.document_type === 'adopted_instrument' && a.effective_from !== null : true));
    check(support, `${s.id}: national closure needs binding access restriction; institutional religion cannot close all India sales`);
   }
  }
  if (s.gate.basis === 'counterfactual') {
   check(present(s.gate.counterfactual_label) && present(s.gate.assumption_rationale), `${s.id}: counterfactual gate needs label and rationale`);
   if (s.gate.state === 'open' && currentEvidence.some(a => closedStatuses.has(a.status))) check(s.gate.contradicts_current_evidence, `${s.id}: counterfactual contradiction must be disclosed`);
  }
  const mechanisms = s.mechanisms.map(x => x.mechanism);
  check(new Set(mechanisms).size === mechanisms.length, `${s.id}: repeated shock mechanism`);
  for (const m of s.mechanisms) {
   references(m.source_ids, `${s.id} mechanism ${m.mechanism}`);
   check(m.target_parameter !== 'baseline_share', `${s.id}: fixed-penetration accounting has no price-induced substitution model`);
   check(present(m.rationale), `${s.id}: shock mechanism needs rationale`);
  }
  // Merely reporting a conventional price has no effect on this fixed-share
  // arithmetic. It must not be presented as a behavioral substitution effect.
  const applied = new Set([...s.mechanisms.filter(x => x.target_parameter !== 'conventional_price').map(x => x.mechanism), ...s.gate.required_dimensions.map(x => mechanismFor[x]), ...(s.capacity !== null && s.capacity.value !== null ? ['supply'] : [])]);
  if (b) for (const mechanism of b.conditioning.embedded_mechanisms) check(!applied.has(mechanism), `${s.id}: double adjustment for embedded ${mechanism}; owner replacement baseline required`);
  let compatibleCapacity = null; const reasons = [];
  if (s.capacity === null || s.capacity.value === null) reasons.push('missing_capacity');
  else {
   const cap = s.capacity; const pool = pools.get(cap.pool_id);
   check(!!pool, `${s.id}: orphan capacity pool`);
   check(!usedAllocations.has(cap.allocation_id), `${s.id}: supply allocation used twice`); usedAllocations.add(cap.allocation_id);
   const key = `${s.allocation_group}|${cap.pool_id}`;
   allocations.set(key, (allocations.get(key) ?? 0) + cap.value);
   if (pool) {
    check(pool.year === s.scope.year, `${s.id}: capacity year mismatch`);
    check(pool.eligible_product_ids.includes(s.product_id) && pool.eligible_process_profile_ids.includes(s.process_profile_id), `${s.id}: capacity pool product/process incompatibility`);
    if (pool.unit !== s.scope.mass_basis || cap.unit !== pool.unit) reasons.push('incompatible_capacity_basis');
    else if (pool.value === null) reasons.push('missing_pool_capacity');
    else compatibleCapacity = cap.value;
    if (pool.value !== null) check(allocations.get(key) <= pool.value + 1e-9, `${s.id}: capacity allocations exceed source pool`);
   }
  }
  if (s.aggregation_group !== null) {
   if (!groups.has(s.aggregation_group)) groups.set(s.aggregation_group, []); groups.get(s.aggregation_group).push(s);
  }
  if (s.product_form === 'cultivated') check(s.cultivated_fraction === 1, `${s.id}: pure cultivated product fraction must be one`);
  if (s.product_form === 'hybrid') check(s.cultivated_fraction > 0 && s.cultivated_fraction < 1, `${s.id}: hybrid fraction must be between zero and one`);
  const p = massShare(b); const G = {open: 1, closed: 0, unresolved: null}[s.gate.state];
  if (b == null) reasons.push('missing_baseline'); else if (p === null) reasons.push('missing_share_or_price');
  if (s.quantity.value === null) reasons.push('missing_reference_market');
  if (G === null) reasons.push('unresolved_gate');
  const Q = p === null || s.quantity.value === null || G === null ? null : s.quantity.value * p * G;
  const feasible = Q === null || compatibleCapacity === null ? null : Math.min(Q, compatibleCapacity);
  if (G === 0) reasons.push(s.gate.basis === 'counterfactual' ? 'counterfactual_closed' : 'scoped_evidence_closed');
  if (feasible === 0 && compatibleCapacity === 0) reasons.push('zero_allocated_capacity');
  calculated.push({scenario_id: s.id, p_mass: p, G, Q_unconstrained: Q, Q_feasible: feasible, cultivated_biomass: feasible === null ? null : feasible * s.cultivated_fraction, reason_codes: reasons});
 }
 for (const [id, rows] of groups) {
  const first = rows[0]; const observations = new Set(); const segmentIds = new Set();
  for (const s of rows) {
   check(sameScope(first.scope, s.scope, scopeKeys.filter(key => key !== 'segment')), `${id}: aggregation estimands differ`);
   check(s.allocation_group === first.allocation_group, `${id}: alternative worlds cannot be aggregated`);
   check(!observations.has(s.observation_id), `${id}: hybrid or observation counted twice`); observations.add(s.observation_id);
   check(!segmentIds.has(s.scope.segment), `${id}: overlapping segment totals`); segmentIds.add(s.scope.segment);
   if (rows.length > 1) {
    const p = partitions.get(s.partition_id);
    check(!!p && s.partition_id === first.partition_id && p.geo === s.scope.geo && p.year === s.scope.year && p.segments.some(x => x.id === s.scope.segment), `${id}: shared documented disjoint partition required`);
   }
  }
 }
 check(doc.status !== 'blocked_missing_baseline' || doc.baselines.length === 0, 'blocked baseline state must not contain a substituted baseline');
 if (doc.mode === 'research') check(doc.status === 'blocked_missing_baseline' || doc.baselines.length > 0, 'research candidate needs a baseline');
 check(doc.expected_outputs.length === calculated.length, 'expected outputs must cover every scenario');
 for (const [i, actual] of calculated.entries()) {
  const expected = doc.expected_outputs[i];
  if (!expected) continue;
  check(expected.scenario_id === actual.scenario_id, `${actual.scenario_id}: output identity mismatch`);
  for (const key of ['p_mass', 'G', 'Q_unconstrained', 'Q_feasible', 'cultivated_biomass']) check(close(expected[key], actual[key]), `${actual.scenario_id}: ${key} expected output disagrees with contract`);
  check(JSON.stringify(expected.reason_codes) === JSON.stringify(actual.reason_codes), `${actual.scenario_id}: reason codes differ`);
 }
 // Invalid input never leaks partially calculated numerical results.
 return {checks, failures, results: failures.length ? [] : calculated, status: failures.length ? 'invalid_contract' : doc.status};
}

export function checkBridgeFiles(files) {
 const failures = []; let checks = 0; let schema;
 try { schema = JSON.parse(files['bridge-v2/schema.json']); } catch { return {checks: 1, failures: ['bridge-v2: schema missing or invalid']}; }
 for (const name of ['bridge-v2/synthetic-example.json', 'bridge-v2/production-state.json']) {
  try { const result = checkBridgeV2(JSON.parse(files[name]), schema); checks += result.checks; failures.push(...result.failures.map(x => `${name}: ${x}`)); }
  catch (error) { checks++; failures.push(`${name}: unreadable contract (${error.message})`); }
 }
 return {checks, failures};
}
