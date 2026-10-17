// Rebuild source inventories and attributed observations; never estimate a market.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import assert from 'node:assert/strict';

export function containedFile(root, relative) {
  if (typeof relative !== 'string' || path.isAbsolute(relative)) throw new Error('Invalid capture path');
  const candidate = fs.realpathSync(path.resolve(root, relative));
  const base = fs.realpathSync(root);
  const rel = path.relative(base, candidate);
  if (rel === '..' || rel.startsWith(`..${path.sep}`) || path.isAbsolute(rel)) throw new Error('Capture escapes evidence directory');
  return candidate;
}

export function verifyCapture(root, record) {
  const file = containedFile(root, record.file);
  const bytes = fs.readFileSync(file);
  const actual = crypto.createHash('sha256').update(bytes).digest('hex');
  assert.equal(actual, record.sha256, `Changed raw source: ${record.id}`);
  assert.equal(bytes.length, record.bytes, `Changed source size: ${record.id}`);
  return {file, bytes};
}

export function tradeObservations(bytes, source) {
  const data = JSON.parse(bytes.toString('utf8'));
  if (data.error || !Array.isArray(data.data) || data.count !== data.data.length) throw new Error('Invalid or incomplete preview response');
  const seen = new Set();
  return data.data.map((row, index) => {
    if (row.typeCode !== 'C' || row.freqCode !== 'A' || row.classificationCode !== 'H6' || row.classificationSearchCode !== 'HS' || row.reporterCode !== 586 || row.period !== '2025' || row.flowCode !== 'M' || row.partnerCode !== 0 || row.partner2Code !== 0 || row.customsCode !== 'C00' || row.motCode !== 0 || !['210610', '350400'].includes(row.cmdCode)) throw new Error('Trade response outside registered query');
    if (['isReported','isAggregate','isNetWgtEstimated'].some(field=>typeof row[field]!=='boolean')) throw new Error('Missing trade provenance flags');
    if (seen.has(row.cmdCode)) throw new Error('Duplicate trade aggregate');
    seen.add(row.cmdCode);
    if (typeof row.primaryValue !== 'number' || !Number.isFinite(row.primaryValue) || row.primaryValue < 0) throw new Error('Invalid trade value');
    return {claim_id:`CTX-PK-IMPORT-${row.cmdCode}-2025`, source_id:source.id, raw_sha256:source.sha256, source_url:source.url, captured_at_utc:source.captured_at_utc, raw_row:`data[${index}]`, country:'Pakistan', period:row.period, hs_code:row.cmdCode, classification:row.classificationCode, primary_value_as_returned:row.primaryValue, net_weight_as_returned:row.netWgt, is_reported:row.isReported, is_aggregate:row.isAggregate, is_net_weight_estimated:row.isNetWgtEstimated, accepted_pillar_market_size:false, reason:'Upstream aggregate; no final-food, process, end-use or domestic-sales allocation'};
  });
}

function writeCsv(file, rows, fields) {
  const cell = value => `"${String(value ?? '').replaceAll('"', '""')}"`;
  fs.writeFileSync(file, [fields.map(cell).join(','), ...rows.map(row => fields.map(field => cell(row[field])).join(','))].join('\n')+'\n');
}

export function build(dataDir, outputDir) {
  const review = JSON.parse(fs.readFileSync(new URL('./reviews.json', import.meta.url), 'utf8'));
  const receipts = ['capture-receipt.json','capture-receipt-batch2.json','capture-receipt-batch3.json'].flatMap(name => JSON.parse(fs.readFileSync(path.join(dataDir,name),'utf8')).receipts);
  const ids = receipts.map(row => row.id);
  assert.equal(new Set(ids).size, ids.length, 'Duplicate source IDs');
  assert.equal(new Set(review.reviews.map(row=>row.id)).size, review.reviews.length, 'Duplicate review IDs');
  const sources = receipts.map(record => {
    verifyCapture(dataDir,record);
    const status = review.reviews.find(row => row.id === record.id);
    assert.ok(status, `Missing source review: ${record.id}`);
    return {...record, review_status:status.status, scope:status.scope};
  });
  for (const row of review.reviews) assert.ok(ids.includes(row.id),`Uncaptured reviewed source: ${row.id}`);
  const pakistan = sources.find(row=>row.id==='comtrade-pakistan-2025');
  assert.equal(pakistan.http_status,'200');
  const imports = tradeObservations(verifyCapture(dataDir,pakistan).bytes,pakistan);
  assert.ok(imports.length, 'No Pakistan import observations; preserve missing status, never infer zero');
  const passageReview = JSON.parse(fs.readFileSync(path.join(dataDir,'published-context-review.json'),'utf8'));
  const context = review.published_context.map(row=> {
    const source=sources.find(item=>item.id===row.source_id);
    assert.equal(source?.http_status,'200');
    assert.equal(row.new_estimate,false);
    assert.equal(row.accepted_2026_numerator,false);
    const checked=passageReview.rows.find(item=>item.claim_id===row.id);
    assert.ok(checked,`Missing manual passage-check receipt: ${row.id}`);
    assert.equal(checked.source_sha256,source.sha256,'Passage review source changed');
    assert.equal(checked.source_value,row.source_value,'Published transcription changed since passage review');
    assert.equal(checked.locator,row.locator,'Published locator changed since passage review');
    for(const field of ['year','unit','country','attribution']) assert.equal(checked[field],row[field],`Published ${field} changed since passage review`);
    return {...row,raw_sha256:source.sha256,source_url:source.url,captured_at_utc:source.captured_at_utc,code_path:'market/build-evidence.mjs',passage_check:'agent_source_check_recorded_human_review_pending'};
  });
  const reconciliation=[];
  for(const country of ['India','Pakistan']) for(const pillar of ['plant-based','fermentation','cultivated']) for(const method of ['published top-down','bottom-up companies/products','HS210610/350400 imports']) {
    const reason=method==='published top-down'?(country==='India'&&pillar==='plant-based'?'Historical attributed estimates have incompatible year/definition; no accepted current numerator':'No auditable current pillar-specific consumer-sales estimate accepted'):method==='bottom-up companies/products'?'Product/R&D or diversified B2B records lack complete country/channel-specific consumer sales':'Broad upstream headings do not identify pillar or finished consumer sales';
    reconciliation.push({country,pillar,target_year:2026,method,accepted_value:null,currency:null,status:'UNRESOLVED',reason,twofold_disagreement:'NOT_ASSESSED_MISSING_COMPARABLE_VALUES',average:null});
  }
  fs.mkdirSync(outputDir,{recursive:true});
  writeCsv(path.join(outputDir,'sources.csv'),sources,['id','url','final_url','captured_at_utc','http_status','file','sha256','bytes','licence','review_status','scope']);
  writeCsv(path.join(outputDir,'import-context.csv'),imports,Object.keys(imports[0]));
  writeCsv(path.join(outputDir,'published-context.csv'),context,Object.keys(context[0]));
  writeCsv(path.join(outputDir,'reconciliation.csv'),reconciliation,Object.keys(reconciliation[0]));
  const output={scope:'Source audit and attributed observations only',research_complete:false,new_estimation_allowed:false,market_estimates_computed:0,raw_sources_verified:sources.length,import_observations:imports.length,published_context_rows:context.length,reconciliation_cells:reconciliation.length,reconciliation_complete:false,imports_are_consumer_market_sizes:false,method_rules:review.method_rules};
  fs.writeFileSync(path.join(outputDir,'market-readiness.json'),JSON.stringify(output,null,2)+'\n');
  return output;
}

if(process.argv[1] && path.resolve(process.argv[1])===fileURLToPath(import.meta.url)) {
  if(process.argv.length!==4) throw new Error('Usage: node market/build-evidence.mjs PRIVATE_MARKET_DATA_DIR OUTPUT_DIR');
  console.log(JSON.stringify(build(path.resolve(process.argv[2]),path.resolve(process.argv[3])),null,2));
}
