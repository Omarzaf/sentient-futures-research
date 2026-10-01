// Integrity checks for the public-source Phase One edition, independent of private inputs.
export function checkPhaseOne(files) {
 const failures=[];let checks=0;
 const check=(ok,message)=>{checks++;if(!ok)failures.push('Phase One: '+message);};
 const read=name=>JSON.parse(files[name]);
 const sources=read('source-register.json'),claims=read('claims.json'),schools=read('school-questions.json');
 const countries=read('country-findings.json'),history=read('historical-comparisons.json');
 const reconciliation=read('reconciliation.json'),verification=read('verification.json'),release=read('release.json');
 const sourceIds=new Set(sources.map(r=>r.id));
 const reviewIds=new Set([...verification.map(r=>r.id),...reconciliation.school_decisions.map(r=>r.id),reconciliation.country_history.id]);
 for(const [name,rows,count] of [['sources_including_held_leads',sources,76],['claims',claims,74],['school_questions',schools,45],['countries',countries,7],['historical_comparisons',history,4]]) {
  check(rows.length===count&&release.counts[name]===count,'count mismatch: '+name);
  check(new Set(rows.map(r=>r.id)).size===rows.length,'duplicate IDs: '+name);
 }
 for(const r of sources){
  check(/^https?:\/\//.test(r.url||'')&&!!r.locator,'missing public locator: '+r.id);
  check(!!r.status&&!!r.language&&!!r.accessed,'missing source metadata: '+r.id);
  if(!['held_language','unverified_translation'].includes(r.status))check(!!r.short_exact_quote,'missing supporting passage: '+r.id);
 }
 for(const [name,rows] of [['claim',claims],['school',schools],['country',countries],['history',history]])for(const r of rows){
  check(r.source_ids?.length>0&&r.source_ids.every(id=>sourceIds.has(id)),'unresolved source in '+name+' '+r.id);
  if(r.verification_id)check(reviewIds.has(r.verification_id),'unresolved review in '+name+' '+r.id);
  if(r.kind==='inference')check(r.status==='inference','inference upgraded: '+r.id);
 }
 const expected=new Set(['HN','M','S','HB','J'].flatMap(prefix=>Array.from({length:9},(_,i)=>prefix+'-Q'+(i+1))));
 check(schools.every(r=>expected.delete(r.id))&&expected.size===0,'school coverage');
 const decisions=reconciliation.school_decisions;
 check(decisions.length===45&&new Set(decisions.map(r=>r.question_id)).size===45,'school reconciliation coverage');
 for(const r of schools){
  check(decisions.some(d=>d.id===r.verification_id&&d.question_id===r.id),'school review mismatch: '+r.id);
  check(!!r.counterpoint&&!!r.verification_scope,'missing school qualifications: '+r.id);
 }
 for(const [status,count] of Object.entries(release.school_status_counts))check(schools.filter(r=>r.status===status).length===count,'status count: '+status);
 check(schools.find(r=>r.id==='J-Q1')?.status==='open','unresolved Sistani criterion lost');
 check(history.every(r=>r.status==='inference'),'historical analogy upgraded');
 check(!release.human_scholarly_review&&!release.mentor_approved&&!release.all_research_questions_resolved,'review limits lost');
 for(const r of read('counter-evidence.json'))check(r.counter_source_ids.every(id=>sourceIds.has(id)),'counter-evidence source missing');
 const families=Object.values(read('source-independence.json').families).flat();
 check(families.every(id=>sourceIds.has(id))&&sources.every(r=>families.includes(r.id)),'source family coverage');
 const narrative=files['review.md'].split('## Primary source references')[0];
 const cited=[...narrative.matchAll(/\[([A-Z][A-Z0-9-]*(?:;\s*[A-Z][A-Z0-9-]*)*)\](?!\()/g)].flatMap(m=>m[1].split(';').map(s=>s.trim()));
 check(cited.length>50,'narrative citation extraction unexpectedly empty');
 const bibliography=files['review.md'].split('## Primary source references')[1]||'';
 for(const id of new Set(cited)){
  check(sourceIds.has(id),'unresolved report citation: '+id);
  check(bibliography.includes('['+id+' ')||new RegExp('\\[[^\\]\\n]*\\b'+id+'\\s').test(bibliography),'missing bibliography entry: '+id);
  check(!['held_language','unverified_translation'].includes(sources.find(r=>r.id===id)?.status),'held source cited as evidence: '+id);
 }
 for(const [name,text] of Object.entries(files))check(!/\bINTERVIEW\b|\bEN0[1-6]\b|IMG 7313|interview-map\.json|\/private\/tmp\//.test(text),'private-source reference or temporary path: '+name);
 check(!claims.some(r=>['I02','I04'].includes(r.id)),'private interview claim retained');
 return {checks,failures};
}
