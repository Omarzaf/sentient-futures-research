// Structural and known semantic boundaries for the October Phase One supplement.
// These checks do not establish scholarly correctness or full research completion.
export function checkContinuation(files) {
 const failures=[];let checks=0;
 const check=(ok,message)=>{checks++;if(!ok)failures.push('Continuation: '+message);};
 const read=name=>{try{return JSON.parse(files[name]);}catch{check(false,'missing or invalid '+name);return null;}};
 const sources=read('source-register.json'),claims=read('claims.json'),reviews=read('reviews.json');
 const coverage=read('coverage.json'),observations=read('observations.json');
 if(failures.length)return {checks,failures};
 for(const [name,rows] of [['sources',sources],['claims',claims],['reviews',reviews]])check(Array.isArray(rows)&&rows.length>0,'invalid '+name);
 if(failures.length)return {checks,failures};
 const sourceIds=new Set(sources.map(r=>r.id));
 const claimIds=new Set(claims.map(r=>r.id));
 for(const [name,rows] of [['sources',sources],['claims',claims],['reviews',reviews]])check(new Set(rows.map(r=>r.id)).size===rows.length,'duplicate '+name+' IDs');
 for(const source of sources){
  check(/^https:\/\//.test(source.url||'')&&!!source.locator&&!!source.source_family,'source locator/family missing: '+source.id);
  check(!!source.language&&!!source.document_type&&!!source.accessed&&!!source.limits,'source scope missing: '+source.id);
  check(source.sha256===null||/^[a-f0-9]{64}$/.test(source.sha256),'invalid source hash: '+source.id);
  check(source.human_verification==='Pending','unsupported human source approval: '+source.id);
 }
 const mismatched=sources.find(r=>r.id==='P1C-IN-MISMATCH');
 check(mismatched?.status==='rejected_for_regulation_evidence'&&mismatched.document_type==='application_register_returned_under_regulation_link','mislabeled download promoted to regulation evidence');
 for(const claim of claims){
  check(claim.source_ids?.length>0&&claim.source_ids.every(id=>sourceIds.has(id)),'unresolved claim source: '+claim.id);
  check(!!claim.assertion&&!!claim.locator&&!!claim.limits,'claim scope missing: '+claim.id);
  check(claim.human_review==='pending','unsupported human claim approval: '+claim.id);
  check(claim.status==='independently_checked'&&reviews.some(r=>r.id===claim.review_id&&r.claim_ids?.includes(claim.id)),'missing independent claim review: '+claim.id);
 }
 for(const review of reviews)check(review.claim_ids?.every(id=>claimIds.has(id))&&!!review.method&&!!review.scope&&review.human_review===false,'invalid review scope: '+review.id);
 const expected=['IND','PAK','SAU','ARE','SGP','MYS','IDN','QAT','KWT','BHR','OMN','IRN','IRQ','YEM','EGY','CHN'];
 const roster=coverage.countries?.map(r=>r.id)||[];
 check(roster.length===expected.length&&new Set(roster).size===expected.length&&expected.every(id=>roster.includes(id)),'named-country coverage lost');
 for(const country of coverage.countries||[]){
  check(!!country.role&&!!country.scopeBasis&&Array.isArray(country.claim_ids)&&country.claim_ids.every(id=>claims.some(r=>r.id===id&&r.country===country.id)),'country scope/claim link: '+country.id);
  check(['partial_new_evidence','queued_or_prior_evidence_needs_revalidation'].includes(country.coverage),'unsupported country completion: '+country.id);
  check(country.populationSchoolShares===null,'unsupported school population shares: '+country.id);
 }
 check(coverage.completion_established===false&&coverage.full_phase1_review_complete===false&&coverage.human_review==='pending','partial supplement promoted to complete');
 const entry=observations.fssai;
 check(entry?.source_id==='P1C-IN-NSF'&&entry.stage_code===7&&entry.section==='Under Process','FSSAI source/stage boundary lost');
 check(entry?.possible_decisions?.length===3&&['clarification','approval','rejection'].every(s=>entry.possible_decisions.includes(s)),'FSSAI decision ambiguity lost');
 check(entry?.decision_outcome===null&&entry.approval_date===null&&entry.certificate===null,'FSSAI ambiguous stage promoted to approval/rejection');
 const policy=observations.export_policy;
 check(Array.isArray(policy?.source_ids)&&policy.source_ids.length===3&&['P1C-IN34','P1C-IN59','P1C-IN28'].every(id=>policy.source_ids.includes(id)&&sourceIds.has(id))&&policy.scope==='specified_halal_exports','export policy source/scope lost');
 check(policy?.cultivated_tariff_classification===null&&policy.domestic_food_approval_established===false&&policy.unconditional_country_access_established===false,'export rule promoted to product access');
 check(policy?.egypt_transition?.months===9&&policy.egypt_transition.origin_date==='2026-02-09'&&policy.egypt_transition.amending_notification_date==='2026-08-05'&&policy.egypt_transition.calendar_derived_endpoint==='2026-11-09'&&policy.egypt_transition.endpoint_is_printed_date===false,'Egypt transition origin or derived-date distinction lost');
 check(observations.geography?.school_population_percentages_established===false&&observations.geography.constitutional_rule_is_population_estimate===false&&observations.geography.federal_territories_rule_is_national_rule===false,'legal rule promoted to population/national claim');
 check(observations.human_review==='pending','unsupported observation human approval');
 return {checks,failures};
}
