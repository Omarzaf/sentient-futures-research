import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';

// Stage 1 only. No source is fetched, audited, or promoted by this transformation.
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const base = 'research/halal-cultivated';
const original = `${base}/phase1`;
const output = `${base}/paper`;
const read = p => fs.readFileSync(path.join(root, p), 'utf8');
const json = p => JSON.parse(read(p));
const sha256 = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const unique = values => [...new Set(values)];
const requireTrue = (condition, message) => { if (!condition) throw new Error(message); };

function filesBelow(directory) {
  return fs.readdirSync(path.join(root, directory), {withFileTypes: true})
    .sort((a, b) => a.name.localeCompare(b.name))
    .flatMap(entry => entry.isDirectory() ? filesBelow(`${directory}/${entry.name}`)
      : entry.isFile() ? [`${directory}/${entry.name}`] : []);
}

function normalizeQuote(value) {
  return value.normalize('NFC').replace(/[\u064b-\u0652\u0670\u0640]/gu, '')
    .replace(/[أإآٱ]/gu, 'ا').replace(/ى/gu, 'ي')
    .replace(/[‘’]/gu, "'").replace(/[“”]/gu, '"')
    .replace(/[‐‑‒–—−]/gu, '-').replace(/\s+/gu, ' ').trim();
}

const sources = json(`${original}/source-register.json`);
const claims = json(`${original}/claims.json`);
const counters = json(`${original}/counter-evidence.json`);
const gaps = json(`${original}/gaps.json`);
const schools = json(`${original}/school-questions.json`);
const countries = json(`${original}/country-findings.json`);
const histories = json(`${original}/historical-comparisons.json`);
const families = json(`${original}/source-independence.json`).families;
const discovery = json(`${base}/source-register.json`);
const continuationSources = json(`${base}/phase1-continuation/source-register.json`);
const continuationClaims = json(`${base}/phase1-continuation/claims.json`);
const continuationCoverage = json(`${base}/phase1-continuation/coverage.json`);
const estimates = json(`${base}/phase1-continuation/elasticity-estimates.json`);
const production = json(`${base}/bridge-v2/production-state.json`);
const byId = new Map(sources.map(row => [row.id, row]));
const claimById = new Map(claims.map(row => [row.id, row]));
const discoveryById = new Map(discovery.map(row => [row.id, row]));
requireTrue(sources.length === 76 && claims.length === 74 && counters.length === 7
  && gaps.length === 12 && schools.length === 45 && countries.length === 7 && histories.length === 4,
  'Unexpected historical Phase One record counts.');
requireTrue(byId.size === sources.length && claimById.size === claims.length,
  'Historical registers contain duplicate IDs.');

// These are passage groups specified in PAPER-PLAN section 13, not whole-work merges.
// Shared URLs alone are insufficient: the retained locators must overlap as below.
const aliasGroups = [
  {key: 'HAN', alias: 'H1', locator_tokens: ['327'], reason: 'Same displayed volume 1 page 327 transformation paragraph; different excerpts remain separate.'},
  {key: 'HAN-D', alias: 'H2', locator_tokens: ['311'], reason: 'Same detached-part paragraph on displayed volume 6 page 311; H2 also records page 310 and the gloss.'},
  {key: 'SHA-D', alias: 'S3', locator_tokens: ['580', '581'], reason: 'Same detached-part branch on displayed volume 2 pages 580–581; quote differs in Arabic diacritics.'},
  {key: 'SHA-T', alias: 'S4', locator_tokens: ['597'], reason: 'Same transformation discussion on displayed volume 2 page 597; S4 also records the preceding page and a distinct excerpt.'},
  {key: 'SIS-EN', alias: 'J4', locator_tokens: ['189', '191'], reason: 'Same official transformation rulings 189–191 and identical retained quotation.'},
];
const canonical = new Map(sources.map(row => [row.id, row.id]));
for (const group of aliasGroups) {
  const first = byId.get(group.key);
  const second = byId.get(group.alias);
  requireTrue(first && second && first.url === second.url, `Alias URL mismatch: ${group.key}/${group.alias}`);
  requireTrue(group.locator_tokens.every(token => first.locator.includes(token) && second.locator.includes(token)),
    `Alias locator mismatch: ${group.key}/${group.alias}`);
  canonical.set(group.alias, group.key);
}
const canonicalKeys = ids => unique(ids.map(id => {
  requireTrue(canonical.has(id), `Unknown historical source ID: ${id}`);
  return canonical.get(id);
}));
const familyFor = id => Object.entries(families).find(([, ids]) => ids.includes(id))?.[0] ?? byId.get(id).source_family;

function sourceRecord(row) {
  const group = aliasGroups.find(value => value.key === row.id);
  const originals = group ? [row, byId.get(group.alias)] : [row];
  const bibliographic = Object.fromEntries(['author', 'title', 'translator', 'editor', 'publisher', 'place', 'year', 'volume', 'page']
    .map(field => [field, row[field] ?? null]));
  return {
    id: row.id, key: row.id, aliases: group ? [group.alias] : [],
    title: row.title, url: row.url, host: new URL(row.url).hostname,
    short_exact_quote: row.short_exact_quote, locator: row.locator,
    family: familyFor(row.id), source_family: row.source_family,
    language: row.language, accessed: row.accessed, status: row.status,
    audit_verdict: 'pending', human_verification: 'Pending', bibliographic,
    bibliographic_note: 'Only explicit structured fields from the canonical original record are copied. Missing fields remain null until citation audit; author, edition and translator are not inferred from a title or family label.',
    limits: row.limits ?? null,
    original_records: originals,
    quote_variants: originals.map(item => ({source_id: item.id, quote: item.short_exact_quote,
      locator: item.locator, status: item.status})),
    ...(group ? {alias_review: {
      method: 'retained_record_url_and_overlapping_locator_comparison',
      scope: 'Same cited passage scope in the dated register; original page not retrieved during consolidation.',
      reason: group.reason,
      quote_relationship: originals[0].short_exact_quote === originals[1].short_exact_quote ? 'identical'
        : normalizeQuote(originals[0].short_exact_quote) === normalizeQuote(originals[1].short_exact_quote)
          ? 'normalization_equivalent' : 'different_excerpts_preserved',
      fresh_passage_verification: false,
    }} : {}),
  };
}

const register = sources.filter(row => canonical.get(row.id) === row.id).map(sourceRecord);
requireTrue(register.length === 71, 'Expected 71 passage records after the five explicit alias merges.');
requireTrue(register.flatMap(row => row.original_records).length === 76, 'Original source preservation failed.');
for (const row of sources) {
  const retained = register.find(item => item.key === canonical.get(row.id)).original_records.find(item => item.id === row.id);
  requireTrue(JSON.stringify(retained) === JSON.stringify(row), `Original source row changed: ${row.id}`);
}

function claimSections(id) {
  const question = /^(?:HN|M|S|HB|J)-Q([1-9])$/.exec(id)?.[1];
  if (question) return [({1: '8', 2: '8', 3: '5', 4: '6', 5: '5', 6: '7', 7: '6', 8: '8', 9: '5'})[question], 'Appendix A'];
  if (id.startsWith('C-')) return ['9.4', 'Appendix B'];
  const sections = {
    R01: ['1', '5', '9.1'], R02: ['1', '9.1'], R03: ['9.1'], R04: ['9.4'], R05: ['5', '9.1'], R06: ['9.1', '9.4'],
    S01: ['5'], S02: ['7'], S03: ['5'], S04: ['7'], S05: ['7'], S06: ['6'],
    G01: ['5', '8'], G02: ['5'], T01: ['2', '8'], T02: ['5'], I01: ['5', '11'], I03: ['1', '11'],
    H01: ['7', '10'], H02: ['6', '10'], H03: ['6', '10'], H04: ['5', '10'],
  };
  requireTrue(sections[id], `No section map for claim ${id}`);
  return sections[id];
}

const coverage = claims.map(row => ({
  id: row.id, kind: 'claim', sections: claimSections(row.id), disposition: 'planned',
  reason: row.status === 'open' ? 'Retain as an unresolved question; no factual answer or status promotion.'
    : row.status === 'inference' ? 'Retain as explicitly labeled reasoning, with premises, alternative and defeat condition.'
      : 'Planned attributed account, conditional on the new source audit; historical checking is not paper citation approval.',
  source_ids: row.source_ids, canonical_source_keys: canonicalKeys(row.source_ids),
  status: row.status, statement: row.statement, claim_kind: row.kind,
  citation_audit_state: 'pending', original_record: row,
}));
for (const row of schools) coverage.push({
  id: row.id, kind: 'school', sections: claimSections(row.id), disposition: 'planned',
  reason: 'Retain the full school-question account, counterpoint and modern-application limit alongside its separate claim record.',
  source_ids: row.source_ids, canonical_source_keys: canonicalKeys(row.source_ids),
  status: row.status, proposition: row.proposition, question: row.question,
  citation_audit_state: 'pending', original_record: row,
});
for (const row of countries) coverage.push({
  id: row.id, kind: 'country', sections: ['9.4', 'Appendix B'], disposition: 'planned',
  reason: 'Retain separate food-authorization, halal, product-evidence and gap fields; no dated framework account becomes a current approval.',
  source_ids: row.source_ids, canonical_source_keys: canonicalKeys(row.source_ids),
  status: row.status, country: row.country, citation_audit_state: 'pending', original_record: row,
});
for (const row of histories) coverage.push({
  id: row.id, kind: 'historical', sections: claimSections(row.id), disposition: 'planned',
  reason: 'Retain the analogy, premise, reasoning, counter-evidence and missing test separately from the claim with the same ID; analogy remains inference.',
  trace_id: `historical:${row.id}`, source_ids: row.source_ids, canonical_source_keys: canonicalKeys(row.source_ids),
  status: row.status, analogy: row.analogy, citation_audit_state: 'pending', original_record: row,
});
const counterSections = [['5', '11'], ['5', '11'], ['7', '11'], ['6', '11'], ['6', '11'], ['9.4', '11'], ['6', '11']];
for (const [index, row] of counters.entries()) coverage.push({
  id: `CE${index + 1}`, kind: 'counter_evidence', sections: counterSections[index], disposition: 'planned',
  reason: 'Retain the tested shortcut and its original limiting result; audit the supporting passage before use.',
  source_ids: row.counter_source_ids, canonical_source_keys: canonicalKeys(row.counter_source_ids),
  claim_tested: row.claim_tested, result: row.result, original_record: row,
});
for (const row of gaps) {
  const related = (row.rows ?? []).map(id => claimById.get(id)).filter(Boolean);
  const sourceIds = unique(related.flatMap(item => item.source_ids));
  coverage.push({
    id: row.id, kind: 'gap', sections: unique([...related.flatMap(item => claimSections(item.id)), '12', 'Appendix C']),
    disposition: 'planned', reason: 'Preserve this dated unresolved record. Later continuation evidence requires separate intake and audit.',
    source_ids: sourceIds, canonical_source_keys: canonicalKeys(sourceIds), status: 'open',
    text: row.description ?? row.text, related_claim_ids: row.rows ?? [], original_record: row,
  });
}
for (const row of sources) {
  const uses = coverage.filter(item => item.source_ids.includes(row.id));
  const leadOnly = row.status === 'held_language';
  coverage.push({
    id: row.id, kind: 'source', sections: unique([...uses.flatMap(item => item.sections),
      ...(leadOnly ? ['9.1'] : row.id === 'M-RIS-INDEX' ? ['4'] : []),
      ...(['GOOD-DOSSIER', 'SG-LIST', 'HAN-D', 'SIS-EN', 'IIFA198', 'IIFA210'].includes(canonical.get(row.id)) ? ['2'] : []), 'Appendix D']),
    disposition: 'planned', reason: leadOnly ? 'List only as an untranslated lead and in the audit summary; not evidence under the default language policy.'
      : row.id === 'M-RIS-INDEX' ? 'Uncited editorial metadata retained for the edition/translation audit and method account.'
        : 'Retain in source audit and planned record support; no source is citable before an allowed audit verdict.',
    source_ids: [row.id], canonical_source_keys: [canonical.get(row.id)],
    canonical_key: canonical.get(row.id), status: row.status, audit_verdict: 'pending',
    evidence_use: leadOnly ? 'untranslated_lead_only' : 'pending_audit',
    original_record: row,
  });
}
requireTrue(coverage.length === 225 && new Set(coverage.map(row => `${row.kind}:${row.id}`)).size === 225,
  'Coverage must contain exactly 225 distinct kind/ID records: 169 required records plus 45 school, seven country and four historical accounts.');
requireTrue(coverage.every(row => row.sections.length && row.reason), 'Every coverage record needs a destination and reason.');

const originalFiles = filesBelow(original);
const originalText = originalFiles.map(read).join('\n');
const discoveryMatrix = read(`${base}/consensus-matrix.csv`);
const citedOriginalIds = new Set(claims.flatMap(row => row.source_ids));
const problem = (id, confirmed, finding, evidence, action) => ({
  id, status: confirmed ? 'confirmed_in_local_records' : 'requires_local_recheck',
  finding, evidence, action, source_truth_verified: false, human_review: 'pending',
});
const problems = [
  problem('PLAN-01', aliasGroups.every(group => byId.has(group.alias)),
    'Five alias pairs refer to the same retained passage scopes. Distinct excerpts and original review statuses are preserved; canonicalization adds no independent evidence.',
    aliasGroups.map(({key, alias, reason}) => ({ids: [key, alias], reason})), 'Use 71 canonical passage records for 76 original IDs; audit each quote variant.'),
  problem('PLAN-02', histories.every(row => claimById.has(row.id)),
    'H01–H04 occur in both claims and historical comparisons. Hanafi H1–H7 differ from Hanbali H-*; G01/G02 claims differ from G1–G8 gaps.',
    ['phase1/claims.json', 'phase1/historical-comparisons.json', 'phase1/gaps.json'], 'Use kind namespaces in coverage, gap: and ce: trace prefixes, and canonical source keys; no raw IDs in prose.'),
  problem('PLAN-03', byId.get('S2').url.includes('dokumen.pub') && byId.get('H4').url.includes('studylib.net'),
    'H4 and S2 link to file-sharing hosts rather than their publishers.', ['H4', 'S2'], 'Verify print editions through a publisher or catalogue; footnotes omit file-sharing links. Retain original URLs only as provenance.'),
  problem('PLAN-04', byId.get('M-RIS29').limits.includes('Alhaj Bello Mohammad Daura') && byId.get('H7').url.includes('camquran.site'),
    'English Umdat metadata and several host-edition page identities remain unestablished. M-RIS29 records its named translator and non-final translation warning.',
    ['H-UM-FOOD', 'H-UM-FOOD2', 'H-UM-SLAUGHTER', 'M-RIS29', 'H7', 'G-BIBLIO', 'G-ENGLISH', 'G4', 'G8'], 'Complete bibliographic audit without inferring publication details; preserve translation and edition holds.'),
  problem('PLAN-05', ['Q6', 'Q6121'].every(id => byId.get(id).limits.includes('The Clear Quran'))
    && ['Q5', 'Q7'].every(id => !JSON.stringify(byId.get(id)).includes('The Clear Quran')),
    'Only Q6 and Q6121 name The Clear Quran in the retained records; Q5 and Q7 do not identify a translation.',
    ['Q5', 'Q6', 'Q6121', 'Q7'], 'Identify the actual fetched translation for every quoted verse; do not supply translator names from memory.'),
  problem('PLAN-06', /Albani/i.test(byId.get('AD2858').limits),
    'AD2858 records a grading attributed to al-Albani, not an independent adjudication.', ['AD2858'], 'Retain the attribution and both displayed numbering systems.'),
  problem('PLAN-07', ['513/2020', '5031:2020', '5013'].every(value => originalText.includes(value)),
    'SFDA records retain the inconsistent identifiers 513/2020, 5031:2020 and 5013.',
    ['SA-NOVEL', 'SA-GUIDE', 'SA-2025'], 'Keep the discrepancy open until authoritative instrument identity and current Arabic text are checked.'),
  problem('PLAN-08', ['HS-010', 'HS-011', 'HS-012', 'HS-024'].every(id => discoveryById.get(id).url.includes('consensus.app')),
    'Four discovery scholarship entries link to aggregator summaries rather than publications.',
    ['HS-010', 'HS-011', 'HS-012', 'HS-024'], 'Resolve and match publisher/DOI metadata and inspect relied-on passages before new-source intake.'),
  problem('PLAN-09', discoveryMatrix.includes('KMF 2025') && discoveryMatrix.includes('Known through news reports.')
    && byId.get('MKI128').status === 'held_language',
    'The KMF/JAKIM discovery cells rely on secondary reports, while MKI128 remains held in Malay.',
    ['consensus-matrix.csv', 'HS-004', 'HS-005', 'MKI128'], 'A checked news report remains a report; rebuild institutional cells only from accepted original statements.'),
  problem('PLAN-10', discoveryById.get('HS-014').type.includes('Individual') && discoveryById.get('HS-015').type.includes('Forum'),
    'The individual fatwa and Ask Ghamidi forum entries do not establish institutional positions.',
    ['HS-014', 'HS-015'], 'Do not cite them in the paper; the published GHAMIDI essay remains the sole Ghamidi source under this plan.'),
  problem('PLAN-11', discoveryById.get('HS-016').url.includes('archive.org'),
    'The discovery Mizan entry is an unread Internet Archive listing.', ['HS-016'], 'If ever considered separately, verify the publisher edition first; it is excluded from this paper by the published-essay-only rule.'),
  problem('PLAN-12', gaps.some(row => 'description' in row) && gaps.some(row => 'text' in row),
    'The twelve gap records use description/scope and text/priority variants.', ['phase1/gaps.json'], 'Coverage exposes one text field while preserving every original record unchanged.'),
  problem('PLAN-13', ['FormI', 'AnnexI chaptersI–II', 'The2013', 'Rejected;2015'].every(value => originalText.includes(value)),
    'Extraction spacing defects are present in the dated records.', ['FormI', 'AnnexI chaptersI–II', 'The2013', 'Rejected;2015'], 'Preserve originals; correct spacing only in new prose, never inside a purported verbatim quote without original-source checking.'),
  problem('PLAN-14', ['M-RIS-INDEX', 'WP595', 'MKI128'].every(id => !citedOriginalIds.has(id)),
    'M-RIS-INDEX is uncited metadata; WP595 and MKI128 are uncited held-language leads.',
    ['M-RIS-INDEX', 'WP595', 'MKI128'], 'Retain all three in coverage with explicit use limits; no disappearance through deduplication.'),
  problem('PLAN-15', byId.get('SG-LIST').source_date === '2026-08-14' && byId.get('SG-FRAME').source_date === '2026-08-27',
    'The SFA list and framework are dated 14 and 27 August 2026 respectively, with historical 30 September readings.',
    ['SG-LIST', 'SG-FRAME'], 'Re-retrieve during audit and report any change; the earlier recorded checking does not establish present status.'),
  problem('CURRENT-01', continuationSources.length > 76 && estimates.estimates.length > 0,
    'PAPER-PLAN is based on the older edition. Continuation already has literature, geography, process, historical, elasticity and feed records; its statement that no driver/elasticity/feed records exist is stale.',
    {continuation_sources: continuationSources.length, continuation_claims: continuationClaims.length,
      elasticity_estimates: estimates.estimates.length, coverage_countries: continuationCoverage.countries.length},
    'Preserve the full sixteen-country research scope. Treat continuation as versioned intake candidates, retain provenance, and audit any selected source/claim before paper use; defaults about paper body scope do not delete research requirements.'),
  problem('CURRENT-02', json('research/library.json').documents.length === 9,
    'The current library contains nine documents; the plan\'s stage 7 instruction to increase seven to eight is stale.',
    ['research/library.json', 'tools/build-library.mjs', 'tools/verify.mjs'], 'Do not add the paper during consolidation; release must increment the actual count when authorized.'),
  problem('CURRENT-03', production.version === '2.0.0' && production.status === 'blocked_missing_baseline',
    'The paper plan names legacy Phase Two fields and gate shortcuts. Active bridge v2 supersedes that numerical contract, with missing compatible inputs and unresolved assessments.',
    ['bridge-v2/METHOD.md', 'bridge-v2/schema.json', 'bridge-v2/production-state.json', 'bridge-v2/LEGACY-CROSSWALK.md'],
    'Use active v2 dimensions and compatibility rules. No L_includes_halal bypass or numeric gate, mass, supply-to-adoption transfer, or production estimate is established by this manuscript.'),
  problem('CURRENT-04', continuationCoverage.completion_established === false && continuationCoverage.full_phase1_review_complete === false,
    'Historical question coverage and handoff flags do not establish completed expanded Phase One research. The continuation expressly records incomplete full-scope review and pending human review.',
    ['phase1/release.json', 'phase1-continuation/coverage.json', 'phase1-continuation/REPAIR-REPORT-2026-10-02.md'],
    'Describe the paper as a draft synthesis of dated, incomplete evidence; retain 143-requirement/sixteen-country research scope and both human checkpoints.'),
  problem('CURRENT-05', new Set(sources.map(row => row.source_family)).size !== Object.keys(families).length,
    'Literal source-family strings differ from the historical independence grouping. Canonicalization does not prove independent corroboration.',
    {literal_family_strings: new Set(sources.map(row => row.source_family)).size, historical_family_groups: Object.keys(families).length},
    'Keep source_family unchanged, retain the historical grouping separately as family, and audit authorship/independence before reliance.'),
];
requireTrue(problems.slice(0, 15).every(row => row.status === 'confirmed_in_local_records'),
  'At least one problem from PAPER-PLAN section 13 could not be confirmed in local records.');

const selectedInputs = [
  `${base}/archive/PAPER-PLAN.md`, `${base}/PLAN.md`, `${base}/archive/AGENTIC-PLAN.md`,
  `${base}/source-register.json`, `${base}/consensus-matrix.csv`,
  ...['source-register.json', 'claims.json', 'coverage.json', 'reviews.json', 'SYNTHESIS.md', 'gate-table.json',
    'school-gap-progress.json', 'geography.json', 'institution-matrix.json', 'literature-review.json',
    'standards-review.json', 'manufacturing-dossier.json', 'historical-cases.json', 'historical-synthesis.json',
    'driver-map.json', 'elasticity-review.json', 'elasticity-estimates.json', 'feed-review.json',
    'REPAIR-REPORT-2026-10-02.md'].map(file => `${base}/phase1-continuation/${file}`),
  ...['METHOD.md', 'schema.json', 'production-state.json', 'LEGACY-CROSSWALK.md'].map(file => `${base}/bridge-v2/${file}`),
];
const manifest = {
  schema_version: 1, generated_by: 'tools/consolidate-paper.mjs',
  scope: 'Immutable historical edition plus selected public scope/continuation inputs. Inclusion is not source acceptance or fresh verification.',
  input_counts: {claims: claims.length, counter_evidence: counters.length, gaps: gaps.length,
    original_sources: sources.length, canonical_passages: register.length, school_questions: schools.length,
    country_accounts: countries.length, historical_accounts: histories.length, coverage_records: coverage.length},
  files: unique([...originalFiles, ...selectedInputs]).sort().map(file => {
    const bytes = fs.readFileSync(path.join(root, file));
    return {path: file, bytes: bytes.length, sha256: sha256(bytes),
      role: file.startsWith(`${original}/`) ? 'frozen_phase1_input' : 'scope_or_continuation_reference'};
  }),
};

// Re-running stage 1 must neither conceal frozen-input changes nor erase completed audits.
if (fs.existsSync(path.join(root, output, 'input-manifest.json'))) {
  const previous = json(`${output}/input-manifest.json`);
  for (const record of previous.files ?? []) {
    if (record.role === 'frozen_phase1_input') {
      const current = manifest.files.find(item => item.path === record.path);
      requireTrue(current?.sha256 === record.sha256, `Frozen historical input changed: ${record.path}`);
    }
  }
}
if (fs.existsSync(path.join(root, output, 'source-register.json'))) {
  const existing = json(`${output}/source-register.json`);
  requireTrue(Array.isArray(existing) && existing.every(row => row.audit_verdict === 'pending'),
    'Refusing to overwrite an audited source register. Consolidation is a stage 1 operation.');
}
for (const [filename, value] of Object.entries({
  'source-register.json': register, 'coverage.json': coverage, 'problems.json': problems, 'input-manifest.json': manifest,
})) {
  fs.mkdirSync(path.join(root, output), {recursive: true});
  const destination = path.join(root, output, filename);
  const text = `${JSON.stringify(value, null, 2)}\n`;
  if (!fs.existsSync(destination) || fs.readFileSync(destination, 'utf8') !== text) fs.writeFileSync(destination, text);
}
console.log(JSON.stringify({stage: 1, original_sources: sources.length, canonical_sources: register.length,
  coverage_records: coverage.length, problems: problems.length, manifest_files: manifest.files.length,
  new_sources: 0, audited_sources: 0, original_phase1_modified: false}));
