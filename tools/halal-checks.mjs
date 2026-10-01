// Checks for the halal conditionality workstream (research/halal-cultivated).
// Field names and allowed values come from datapackage.json. The numbered rules
// follow the double-counting rules in PLAN.md section 5.

export function parseCsv(text) {
 const rows=[];let row=[],field='',quoted=false,wasQuoted=false;
 text=text.replace(/^﻿/,'');
 for(let i=0;i<text.length;i++){
  const c=text[i];
  if(quoted){if(c==='"'){if(text[i+1]==='"'){field+='"';i++;}else quoted=false;}else field+=c;}
  else if(c==='"'&&field===''&&!wasQuoted){quoted=true;wasQuoted=true;}
  else if(c===','){row.push(field);field='';wasQuoted=false;}
  else if(c==='\n'||c==='\r'){if(c==='\r'&&text[i+1]==='\n')i++;row.push(field);rows.push(row);row=[];field='';wasQuoted=false;}
  else field+=c;
 }
 if(quoted)throw Error('Unterminated quoted field');
 if(field!==''||row.length){row.push(field);rows.push(row);}
 return rows.filter(r=>!(r.length===1&&r[0]===''));
}

function cast(field,raw) {
 if(raw==='')return {ok:true,value:null};
 switch(field.type){
  case 'integer':return /^-?\d+$/.test(raw)?{ok:true,value:Number(raw)}:{ok:false};
  case 'number':return /^-?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?$/.test(raw)?{ok:true,value:Number(raw)}:{ok:false};
  case 'boolean':return raw==='true'?{ok:true,value:true}:raw==='false'?{ok:true,value:false}:{ok:false};
  case 'date':{const d=new Date(raw+'T00:00:00Z');return /^\d{4}-\d{2}-\d{2}$/.test(raw)&&!isNaN(d)&&d.toISOString().slice(0,10)===raw?{ok:true,value:raw}:{ok:false};}
  default:return {ok:true,value:raw};
 }
}

const tokens=v=>v==null?[]:String(v).split(';');
const close=(a,b)=>Math.abs(a-b)<=1e-9+1e-6*Math.max(Math.abs(a),Math.abs(b));

// files: {relativeName: text} for everything in research/halal-cultivated.
export function checkHalal(files) {
 const failures=[];let checks=0;
 const check=(ok,msg)=>{checks++;if(!ok)failures.push('halal: '+msg);};
 let pkg;
 try{pkg=JSON.parse(files['datapackage.json']);}catch{check(false,'datapackage.json missing or invalid');return {checks,failures};}
 const t={};

 // Schema: exact headers in order, types, required, enum, pattern, bounds, unique keys.
 for(const res of pkg.resources){
  const fields=res.schema.fields;const name=res.name;
  if(!(res.path in files)){check(false,'missing '+res.path);t[name]=[];continue;}
  let rows;try{rows=parseCsv(files[res.path]);}catch(e){check(false,res.path+': '+e.message);t[name]=[];continue;}
  check(rows.length>0&&JSON.stringify(rows[0])===JSON.stringify(fields.map(f=>f.name)),res.path+': header differs from datapackage.json');
  t[name]=[];
  const keys=new Set();const pk=[].concat(res.schema.primaryKey||[]);
  rows.slice(1).forEach((cells,i)=>{
   const where=`${res.path} row ${i+2}`;
   check(cells.length===fields.length,where+': expected '+fields.length+' cells, found '+cells.length);
   const rec={};
   fields.forEach((f,j)=>{
    const raw=(cells[j]??'');const c=f.constraints||{};
    if(raw!==raw.trim())check(false,where+' '+f.name+': leading or trailing space');
    const v=cast(f,raw);
    if(!v.ok){check(false,where+' '+f.name+': not a valid '+f.type+' ('+raw+')');rec[f.name]=null;return;}
    rec[f.name]=v.value;
    if(c.required)check(v.value!==null,where+' '+f.name+': required');
    if(v.value===null)return;
    if(c.enum)check(c.enum.map(String).includes(raw),where+' '+f.name+': '+raw+' not in allowed values');
    if(c.pattern)check(new RegExp('^(?:'+c.pattern+')$').test(raw),where+' '+f.name+': '+raw+' does not match pattern');
    if(c.maxLength!=null)check(raw.length<=c.maxLength,where+' '+f.name+': longer than '+c.maxLength+' characters');
    if(c.minimum!=null)check(v.value>=c.minimum,where+' '+f.name+': below '+c.minimum);
    if(c.maximum!=null)check(v.value<=c.maximum,where+' '+f.name+': above '+c.maximum);
   });
   const key=pk.map(k=>rec[k]).join('|');check(!keys.has(key),where+': duplicate key '+key);keys.add(key);
   rec._where=where;t[name].push(rec);
  });
 }

 // Source register and cross-references.
 let register=[];try{register=JSON.parse(files[pkg.sourceRegister]);}catch{check(false,'source register missing or invalid');}
 check(Array.isArray(register),'source register must be an array');if(!Array.isArray(register))register=[];
 for(const r of register){check(/^(CO|SA|GP|HS)-[A-Za-z0-9-]+$/.test(r.id||''),'register id '+r.id+': expected CO-, SA-, GP- or HS- prefix');check(/^https?:\/\//.test(r.url||''),'register '+r.id+': public url required');check(!!r.title,'register '+r.id+': title required');}
 const ids=new Set(register.map(r=>r.id));
 for(const [res,key] of [['claims','claim_id'],['scripture-sources','source_id'],['historical-parallels','parallel_id'],['rulings','ruling_id'],['madhhab-geography','record_id'],['certification','record_id'],['elasticities','record_id']])for(const r of t[res]||[])ids.add(r[key]);
 check(ids.size===register.length+['claims','scripture-sources','historical-parallels','rulings','madhhab-geography','certification','elasticities'].reduce((n,k)=>n+(t[k]||[]).length,0),'the same ID is used in more than one register');
 for(const rows of Object.values(t))for(const r of rows){
  for(const k of ['source_ids','source_id','H_rel_ruling','local_survey_id','repeats','elasticity_ids','column_id'])for(const id of tokens(r[k]))check(ids.has(id),r._where+' '+k+': unknown ID '+id);
 }
 const rulingIds=new Set((t.rulings||[]).map(r=>r.ruling_id));
 for(const rows of [t['market-records'],t.scenarios])for(const r of rows||[])if(r.H_rel_ruling)check(rulingIds.has(r.H_rel_ruling),r._where+': H_rel_ruling must be an FT- ruling');

 // Missing stays missing: a named institution for H_rel; dated registry searches for none_found.
 for(const r of t['market-records']||[]){
  if(r.H_rel&&r.H_rel!=='unknown')check(!!r.H_rel_ruling,r._where+': H_rel needs the FT- ruling it comes from');
  if(r.cert_route==='none_found')check(!!r.cert_searched_on,r._where+': none_found needs cert_searched_on');
  if(r.metric==='sales_value')check(r.price_basis==='usd_2025_constant'&&r.unit==='usd_2025_constant',r._where+': sales_value must be in constant 2025 USD');
  if(r.metric==='volume')check(/^tonnes_/.test(r.unit),r._where+': volume needs a tonnes unit');
  if(r.metric==='market_share')check(/^share_/.test(r.unit),r._where+': market_share needs share_volume or share_value');
 }
 for(const r of t.certification||[])if(r.novel_food_route==='none_found')check(!!r.searched_on,r._where+': none_found needs searched_on');

 // Claims register: only the speaker's claims, sourced where verified, Sunnah checked against Mizan.
 for(const r of t.claims||[]){
  if(['verified','partially_verified','misattributed'].includes(r.verification_status))check(!!r.source_ids&&!!r.locator,r._where+': '+r.verification_status+' needs source_ids and locator');
  if(r.claim_type==='sunnah')check(tokens(r.checked_against).includes('mizan'),r._where+': Sunnah claims are checked against Mizan');
  for(const id of tokens(r.source_ids))check(/^(QS|HP)-/.test(id),r._where+': claim sources must be QS- or HP- records');
 }
 for(const r of t['scripture-sources']||[]){
  if(r.kind==='quran'){const m=/^(\d{1,3}):(\d{1,3})(?:-(\d{1,3}))?$/.exec(r.reference||'');check(!!m&&+m[1]>=1&&+m[1]<=114&&(!m[3]||+m[3]>=+m[2]),r._where+': Quran reference must be surah:ayah');}
  if(r.kind==='hadith')check(!!(r.collection&&r.grading&&r.graded_by),r._where+': hadith needs collection, grading and graded_by');
  check(!!r.english_translation||r.flag_no_english===true,r._where+': english_translation or flag_no_english');
 }
 for(const r of t.elasticities||[]){
  if(r.type==='own_price')check(r.with_respect_to===r.good,r._where+': own-price elasticity must respond to its own price');
  if(r.type==='cross_price')check(r.with_respect_to!==r.good&&r.with_respect_to!=='expenditure',r._where+': cross-price elasticity needs another good');
  if(r.type==='expenditure')check(r.with_respect_to==='expenditure',r._where+': expenditure elasticity');
 }

 // Rule 1 and 3: G is a 0/1 switch; halal status counted once through the gate.
 for(const r of t.scenarios||[]){
  const expectH={declared_halal:['permitted','conditional'],declared_haram:['prohibited'],prolonged_silence:['silent']}[r.gate_state]||[];
  check(expectH.includes(r.H_rel),r._where+': H_rel '+r.H_rel+' does not match gate_state '+r.gate_state);
  if(r.H_rel==='conditional')check(r.H_rel_condition_met!==null,r._where+': conditional H_rel needs H_rel_condition_met');
  const halalOk=r.L_includes_halal===true||r.H_rel==='permitted'||(r.H_rel==='conditional'&&r.H_rel_condition_met===true);
  const g=r.gate_state==='declared_halal'&&r.L==='approved'&&halalOk?1:0;
  check(r.G===g,r._where+': rule 1/3, G should be '+g);
 }

 // Rule 2 and 5: one acceptance carrier; only the cultivated part of the demand forecast.
 for(const r of t.scenarios||[]){
  if(r.acceptance_source==='p_US')check(r.df_question==='q2_cultivated'&&!r.local_survey_id,r._where+': rule 2/5, p_US comes from q2_cultivated only, with no local survey');
  if(r.acceptance_source==='local_survey')check(!!r.local_survey_id&&!r.df_question,r._where+': rule 2, a local survey replaces p_US and is never combined with it');
 }

 // Q = D x p x G, capped by K; a reason code for every zero or missing Q.
 for(const r of t.scenarios||[]){
  if(r.D!==null&&r.p!==null&&r.G!==null)check(r.Q_uncapped!==null&&close(r.Q_uncapped,r.D*r.p*r.G),r._where+': Q_uncapped must equal D x p x G');
  if(r.Q_uncapped!==null){
   const want=r.K===null?r.Q_uncapped:Math.min(r.Q_uncapped,r.K);
   check(r.Q!==null&&close(r.Q,want),r._where+': Q must equal Q_uncapped capped by K');
   check(r.cap_status===(r.K===null?'unknown':r.K<r.Q_uncapped?'capped':'not_binding'),r._where+': cap_status does not match K');
  }
  if(r.D!==null)check(!!r.D_unit,r._where+': D needs D_unit');
  if(r.Q===null||r.Q===0)check(!!r.reason_code,r._where+': zero or missing Q needs reason_code');
 }

 // Rule 4: hybrids counted once, at the finished product.
 const seen=new Map();
 for(const r of t['market-records']||[]){
  if(r.cultivated_fraction!==null)check(r.category==='hybrid_cultivated',r._where+': rule 4, cultivated_fraction is for hybrid_cultivated only');
  if(r.category==='cultivated'||r.category==='hybrid_cultivated'){
   const k=[r.source_id,r.geo,r.year,r.metric,r.channel,r.quantile,r.evidence_type,r.locator].join('|');
   const other=seen.get(k);if(other&&other!==r.category)check(false,r._where+': rule 4, the same observation is counted as both cultivated and hybrid_cultivated');
   seen.set(k,r.category);
  }
 }

 // Rule 6: insects are a poultry feed input only.
 const excludedWords=/insect|larva|cricket|mealworm/i;
 for(const r of t['market-records']||[])check(!excludedWords.test(r.category||''),r._where+': rule 6, insects are never human protein');
 for(const r of t['feed-inputs']||[])check(r.use==='poultry_feed',r._where+': rule 6, insects enter only as poultry feed');

 // Rule 7: each shock has one mechanism and never touches p.
 const allowed={none:['none'],animal_disease:['D','conventional_price'],food_sovereignty:['K','L']};
 const groups=new Map();
 for(const r of t.scenarios||[]){
  const m=tokens(r.shock_mechanism);
  check(m.length>0&&m.every(x=>(allowed[r.shock]||[]).includes(x))&&(r.shock==='none'||!m.includes('none')),r._where+': rule 7, '+r.shock+' cannot change '+r.shock_mechanism);
  const k=[r.geo,r.year,r.quantile,r.gate_state,r.acceptance_source,r.local_survey_id].join('|');
  if(!groups.has(k))groups.set(k,[]);groups.get(k).push(r);
 }
 for(const rows of groups.values()){
  const base=rows.find(r=>r.shock==='none');if(!base)continue;
  for(const r of rows){
   if(r===base)continue;const m=tokens(r.shock_mechanism);
   check(r.p===base.p,r._where+': rule 7, a shock never changes p');
   if(!m.includes('D'))check(r.D===base.D,r._where+': rule 7, D changed by a shock whose mechanism excludes D');
   if(!m.includes('K'))check(r.K===base.K,r._where+': rule 7, K changed by a shock whose mechanism excludes K');
   if(!m.includes('L'))check(r.L===base.L,r._where+': rule 7, L changed by a shock whose mechanism excludes L');
  }
 }

 // Rule 8: related evidence counts once.
 const repeating=new Set();
 for(const r of t.rulings||[])if(r.repeats){check(r.repeats!==r.ruling_id&&rulingIds.has(r.repeats),r._where+': rule 8, repeats must name another ruling');repeating.add(r.ruling_id);}
 for(const r of t['consensus-matrix']||[])check(!repeating.has(r.column_id),r._where+': rule 8, cite the original ruling, not a report of it');
 const groupCountry=new Map();
 for(const r of t.elasticities||[])if(r.evidence_group){const k=r.evidence_group+'|'+r.geo+'|'+r.good+'|'+r.type+'|'+r.with_respect_to;check(!groupCountry.has(k),r._where+': rule 8, one estimate per evidence_group for the same elasticity');groupCountry.set(k,r.record_id);}

 // Rule 9: madhhab is context, never a weight.
 const md=pkg.resources.find(r=>r.name==='madhhab-geography');
 check(!md.schema.fields.some(f=>/weight|share|percent|pct/i.test(f.name)),'rule 9, madhhab-geography has no weight or share fields');
 for(const r of t['madhhab-geography']||[])check(!/\d\s*%|\bpercent\b/i.test(r.predominant_schools||''),r._where+': rule 9, no percentages for schools');

 // Rule 10: carried claims start unverified and change only after a dated re-check.
 for(const rows of Object.values(t))for(const r of rows){
  if(!('carried_from' in r))continue;
  if(r.verification_status==='carried_unverified')check(!!r.carried_from,r._where+': rule 10, carried_unverified needs carried_from');
  if(r.carried_from&&r.verification_status!=='carried_unverified')check(!!r.rechecked_on,r._where+': rule 10, a carried value changes status only with rechecked_on');
 }
 return {checks,failures};
}
