// Structural and known semantic boundaries for the October Phase One supplement.
// These checks do not establish scholarly correctness or full research completion.
export function checkContinuation(files) {
 const failures=[];let checks=0;
 const check=(ok,message)=>{checks++;if(!ok)failures.push('Continuation: '+message);};
 const read=name=>{try{return JSON.parse(files[name]);}catch{check(false,'missing or invalid '+name);return null;}};
 const sources=read('source-register.json'),claims=read('claims.json'),reviews=read('reviews.json');
 const coverage=read('coverage.json'),observations=read('observations.json');
 const geography=read('geography.json'),schoolProgress=read('school-gap-progress.json');
 const dossier=read('manufacturing-dossier.json'),egypt=read('egypt-institutions.json'),china=read('china-asf-history.json');
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
 // Edition-specific observations: older affiliation estimates are not madhhab shares.
 const geographyIds=expected.filter(id=>id!=='CHN');
 const geographyRows=Array.isArray(geography?.countries)?geography.countries:[];
 check(geographyRows.length===15&&new Set(geographyRows.map(r=>r.id)).size===15&&geographyIds.every(id=>geographyRows.some(r=>r.id===id)),'geography roster must retain fifteen countries and separate China history');
 check(coverage.countries?.find(r=>r.id==='CHN')?.role==='historical disease shock','China historical scope lost');
 check(geography?.complete===false&&geography.human_review==='pending','geography prematurely completed or human approved');
 const pewValues={IND:[10,15,null],PAK:[10,15,null],SAU:[10,15,null],ARE:[null,null,10],QAT:[null,null,10],KWT:[20,25,null],BHR:[65,75,null],OMN:[5,10,null],IRN:[90,95,null],IRQ:[65,70,null],YEM:[35,40,null]};
 const linkedSources=(ids,claim)=>Array.isArray(ids)&&ids.length>0&&new Set(ids).size===ids.length&&ids.every(id=>sourceIds.has(id)&&claim?.source_ids?.includes(id));
 for(const country of geographyRows){
  const sameCountry=id=>claims.find(r=>r.id===id&&r.country===country.id);
  check(Array.isArray(country.legal_claim_ids)&&country.legal_claim_ids.every(id=>sameCountry(id)),'geography legal claim lineage: '+country.id);
  check(country.predominant_juristic_schools===null&&Array.isArray(country.school_prevalence_source_ids)&&country.school_prevalence_source_ids.length===0&&country.current_affiliation===null&&country.numerical_remainder===null&&country.main_fatwa_bodies===null,'unestablished geography field promoted or zero-filled: '+country.id);
  check(country.complete===false,'geography country prematurely completed: '+country.id);
  if(country.id==='IRN'){
   const legal=country.legally_named_state_school;
   check(legal?.name==='Twelver Jafari'&&!!legal.scope&&legal.current_consolidation_verified===false&&country.legal_claim_ids.includes('P1C2-IRN-LEGAL')&&linkedSources(legal.source_ids,sameCountry('P1C2-IRN-LEGAL')),'Iran Article 12 source/scope boundary lost');
  }else check(country.legally_named_state_school===null,'unsupported legally named state school: '+country.id);
  const affiliations=Array.isArray(country.historical_affiliation)?country.historical_affiliation:[];
  check(Array.isArray(country.historical_affiliation)&&affiliations.length===(country.id==='IRQ'?2:pewValues[country.id]?1:0),'historical affiliation coverage: '+country.id);
  for(const item of affiliations){
   check(linkedSources(item.source_ids,sameCountry(item.claim_id)),'geography affiliation lineage: '+country.id);
   if(item.design==='self_identification_survey'){
    check(country.id==='IRQ'&&item.year===2011&&item.fieldwork==='late 2011'&&item.reported_in===2014&&item.denominator==='Iraqi Muslim survey respondents as described in the report'&&item.unit==='percent'&&item.source_ids?.length===1&&item.source_ids[0]==='P1C2-PEW14-IRAQ','Iraq survey design, timing or denominator changed');
    const categories=item.reported_categories;
    check(categories&&Object.keys(categories).length===3&&categories.Shia===51&&categories.Sunni===42&&categories.just_a_Muslim===5&&item.unreported_remainder===null&&item.age_sampling_weighting_details===null,'Iraq survey categories or unreported remainder invented');
    check(item.directly_comparable_to_2009_estimate===false&&item.population_change_estimate===null,'Iraq incomparable designs promoted to population change');
   }else{
    check(item.design==='synthesized_demographic_estimate'&&item.year===2009&&item.group==='Shia'&&item.denominator==='Muslim population in the country'&&item.unit==='percent'&&item.approximate===true&&item.range_is_confidence_interval===false,'Pew 2009 scope, denominator or uncertainty changed: '+country.id);
    const values=pewValues[country.id];
    check(values&&item.lower===values[0]&&item.upper===values[1]&&item.point===values[2],'Pew point/range or missing-value semantics changed: '+country.id);
    check(item.source_ids?.length===2&&['P1C2-PEW09','P1C2-PEW09-METHOD'].every(id=>item.source_ids.includes(id)),'Pew estimate/method lineage missing: '+country.id);
   }
  }
 }
 check(schoolProgress?.human_review==='pending','unsupported classical progress human approval');
 const readings=Array.isArray(schoolProgress?.readings)?schoolProgress.readings:[];
 check(readings.length===1&&readings[0].question_id==='M-Q4'&&readings[0].gap_id==='G-M-LIVER','classical progress question/gap lineage lost');
 for(const reading of readings){
  const claim=claims.find(r=>r.id===reading.claim_id);
  check(reading.claim_id==='P1C2-M-Q4-TEXT'&&reading.source_id==='P1C2-QURTUBI-2173'&&claim?.country===null&&linkedSources([reading.source_id],claim),'classical progress source/claim lineage lost');
  check(reading.direct_organ_locator_found===true&&reading.school_wide_consensus_established===false&&reading.printed_edition_authenticated===false&&reading.qualified_translation_approved===false&&reading.modern_serum_or_cells_ruling_established===false&&reading.question_complete===false,'classical locator overclaimed');
 }
 const unresolved=Array.isArray(schoolProgress?.unresolved)?schoolProgress.unresolved:[];
 check(unresolved.length===2&&[['J-Q1','G1'],['J-Q4','G6']].every(([question,gap])=>unresolved.some(r=>r.question_id===question&&r.gap_id===gap)),'unresolved classical question/gap lineage lost');
 for(const row of unresolved)check(row.status==='not_located_in_bounded_search'&&row.proposition_absent===false&&!!row.next_action,'negative search promoted to absence: '+row.question_id);
 // Run 03 artifacts link every scoped claim to its registered source and jurisdiction.
 const validSourceRefs=ids=>Array.isArray(ids)&&ids.length>0&&new Set(ids).size===ids.length&&ids.every(id=>sourceIds.has(id));
 const artifactLineage=(record,country)=>validSourceRefs(record?.source_ids)&&Array.isArray(record.claim_ids)&&record.claim_ids.length>0&&new Set(record.claim_ids).size===record.claim_ids.length&&record.claim_ids.every(id=>{
  const claim=claims.find(r=>r.id===id);
  return claim&&(country===undefined||claim.country===country)&&claim.source_ids.every(source=>record.source_ids.includes(source));
 });
 check([dossier,egypt,china].every(r=>r?.human_review==='pending'),'new artifact human review unsupported');
 check(artifactLineage(dossier),'dossier source/claim lineage');
 const processClaim=id=>claims.find(r=>r.id==='P1C3-PROCESS-'+id);
 check(dossier?.dossier_id==='GOODMEAT-US-CCC000001-PUBLIC-20230320'&&dossier.processIdentity?.manufacturer==='GOOD Meat, Inc.'&&dossier.processIdentity.species==='Gallus gallus'&&dossier.processIdentity.cellLine?.includes('UMNSAH/DF1')&&dossier.processIdentity.cellLine.includes('C1F-P1'),'named manufacturing process identity lost');
 check(dossier?.claim_ids?.every(id=>{const c=claims.find(r=>r.id===id);return id==='P1C3-PROCESS-C11'?c?.country==='SGP'&&c.jurisdiction==='SGP':c?.country===null&&c.jurisdiction==='USA';}),'process jurisdiction crosswalk lost');
 check(['currentFacilityStatus','retailProductSKU','current2026Process'].every(key=>dossier?.processIdentity?.[key]===null)&&dossier?.full_phase1_complete===false,'historical process promoted to current product or completion');
 check(dossier?.donor?.liveAdultDonor===false&&['adultSlaughterEvidence','embryoIndividualIdentity','halalProcurementCertificate'].every(key=>dossier.donor[key]===null)&&linkedSources(dossier.donor.sources,processClaim('C02')),'embryonic donor source/procurement boundary lost');
 const stages=Array.isArray(dossier?.stages)?dossier.stages:[];
 check(['Seed expansion','Bioreactor proliferation'].every(name=>stages.some(s=>s.stage===name&&s.animalInputs?.includes('FBS')))&&['Master cell bank','Master working cell bank'].every(name=>stages.some(s=>s.stage===name&&s.animalInputs?.includes('Bovine serum in bank establishment'))),'documented serum stages lost');
 check(dossier?.publicNamedComponents?.completeFormulaPublic===false&&dossier.publicNamedComponents.componentProvenanceComplete===false&&dossier?.animalMaterialControls?.halalSlaughterEvidence===null&&dossier?.scaffoldsAndAids?.certifiedAnimalFree===null,'undisclosed process inputs promoted to complete or certified');
 const versions=Array.isArray(dossier?.versionCrosswalk)?dossier.versionCrosswalk:[];
 check(versions.every(v=>sourceIds.has(v.source)&&dossier.source_ids?.includes(v.source))&&[['Main dossier','2022-03-04','P1C3-PROCESS-S01'],['FDA response','2023-03-20','P1C3-PROCESS-S02'],['FDA labeling correction','2023-06-09','P1C3-PROCESS-S04']].every(([document,date,source])=>versions.some(v=>v.document===document&&v.date===date&&v.source===source)),'process version crosswalk lost');
 const singapore=dossier?.separateSingaporeRecord;
 check(singapore?.id==='GOODMEAT-SGP-SERUMFREE-ANNOUNCED-20230118'&&singapore.id!==dossier.dossier_id&&linkedSources(singapore.evidence,processClaim('C11'))&&['approvalInstrument','fullFormulation','exactCellBankMatchToUS','animalComponentFree','halalCertificate'].every(key=>singapore[key]===null),'Singapore process separation lost');
 const certificate=dossier?.certificateMatch;
 check(dossier?.current_certificate_verified===false&&certificate?.status==='unestablished_in_bounded_retrieval'&&['certifier','certificateNumber','issueDate','expiryDate','manufacturerSite','productSKU','cellBank','mediumVersion','processVersion','religiousRulingByThisDossier'].every(key=>certificate[key]===null)&&linkedSources([certificate.conditionalAdviceSource],processClaim('C12')),'unestablished certificate promoted or lineage lost');
 const residuals=dossier?.residuals,cellBsa=residuals?.bsaHarvestedCellMaterial,washBsa=residuals?.bsaFinalWash;
 check(cellBsa?.unit==='micrograms/g'&&washBsa?.unit==='mg/L'&&cellBsa.n===4&&Array.isArray(cellBsa.batches)&&cellBsa.n===cellBsa.batches.length&&cellBsa.batches.every(v=>Number.isFinite(v)&&v>0),'BSA matrix/unit separation lost');
 check(washBsa?.lod===0.31&&washBsa.n===6&&Array.isArray(washBsa.values)&&washBsa.n===washBsa.values.length&&washBsa.values.filter(v=>typeof v==='string').length===3&&washBsa.values.every(v=>v==='<0.31'||Number.isFinite(v)&&v>=washBsa.lod),'wash censoring or detection-limit semantics lost');
 check(residuals?.zeroResidueEstablished===false&&residuals.totalFBSQuantified===false&&residuals.halalPurityConclusion===null,'BSA evidence promoted to zero total serum or religious purity');
 const composition=dossier?.composition;
 check(composition?.matrix==='Harvested cultured-cell biomass; wet basis'&&composition.finishedProductComposition===null&&composition.n===6&&['proteinPercent','moisturePercent','fatPercent','ashPercent'].every(key=>Array.isArray(composition[key])&&composition[key].length===composition.n&&composition[key].every(v=>Number.isFinite(v)&&v>0&&v<=100)),'biomass composition scope or units lost');
 check(Array.isArray(composition?.carbohydratePercent)&&composition.carbohydratePercent.length===composition.n&&composition.carbohydratePercent.filter(v=>typeof v==='string').length===4&&composition.carbohydratePercent.every(v=>v==='<0.1'||Number.isFinite(v)&&v>=0.1),'composition censoring changed to zero or imputed value');
 const institutions=Array.isArray(egypt?.institutions)?egypt.institutions:[];
 check(institutions.length===2&&['INST-077','INST-078'].every(id=>institutions.some(r=>r.requirement_id===id))&&egypt?.accepted_institutional_consensus===false,'Egypt institutional coverage or consensus boundary lost');
 const conditions=['species','slaughtered_donor_vs_live_biopsy','growth_medium','istihala_applies_to_cell_culture','whether_slaughter_is_required','safety','labelling'];
 for(const institution of institutions){
  check(institution.country==='EGY'&&artifactLineage(institution,'EGY'),'Egypt source/country lineage: '+institution.institution_id);
  check(institution.claim_ids?.every(id=>claims.find(c=>c.id===id)?.evidence_level==='checked_attributed_report_not_accepted_institutional_ruling'),'Egypt attributed claim promoted to accepted ruling');
  check(institution.original_ruling_date===null&&institution.binding_law_established===false&&institution.product_certificate_established===false&&institution.human_review==='pending','Egypt report promoted to dated ruling, law or certificate');
  const matrix=Array.isArray(institution.seven_condition_matrix)?institution.seven_condition_matrix:[];
  check(matrix.length===7&&new Set(matrix.map(r=>r.condition)).size===7&&conditions.every(condition=>matrix.some(r=>r.condition===condition)),'Egypt seven-condition matrix incomplete');
  const held=institution.requirement_id==='INST-077'?'held_reported_officeholder_position':'held_secondary_attribution';
  for(const cell of matrix){
   check(Array.isArray(cell.claim_ids)&&cell.claim_ids.every(id=>institution.claim_ids?.includes(id)&&claims.some(c=>c.id===id&&c.country==='EGY')),'Egypt matrix claim lineage');
   check(cell.position===null?cell.status==='not_established_in_retrieved_report'&&cell.claim_ids?.length===0:typeof cell.position==='string'&&cell.position.length>0&&cell.status===held&&cell.claim_ids?.length>0,'Egypt held position promoted or unknown filled');
  }
  check(institution.later_and_counterstatements?.status==='incomplete'&&Array.isArray(institution.later_and_counterstatements.counterlead_source_ids)&&institution.later_and_counterstatements.counterlead_source_ids.every(id=>sourceIds.has(id)&&institution.source_ids?.includes(id)),'Egypt later/counterstatement scope or lineage lost');
 }
 check(china?.country==='CHN'&&china.id==='HISTORY-18'&&artifactLineage(china,'CHN'),'China history source/claim lineage');
 const production=china?.production,household=china?.household;
 check(production?.baseline_year===2018&&production.baseline_is_unexposed===false,'China baseline exposure lost');
 check(production?.unit==='million tons as published by NBS'&&production.measure==='annual production output'&&production.preliminary===true&&production.protein_mass===false&&linkedSources(production.source_ids,claims.find(r=>r.id==='P1C3-CN-OUTPUT')),'China production scope or source lineage lost');
 check(production?.causal_substitution_fraction===null,'China causal substitution fraction manufactured');
 check(household?.unit==='kg of food per person'&&household.away_from_home_included===false&&household.protein_mass===false&&household.covid_comparability_caveat===true&&linkedSources([household.source_id],claims.find(r=>r.id==='P1C3-CN-HOUSEHOLDS')),'China household scope or source lineage lost');
 check(Array.isArray(china?.drivers)&&china.drivers.every(d=>validSourceRefs(d.source_ids)&&d.source_ids.every(id=>china.source_ids?.includes(id))),'China driver source lineage');
 check(china?.speed?.adoption_half_life===null&&china.speed.durable_poultry_conversion_established===false,'China observed change promoted to durable conversion');
 check(china?.elasticity?.identified_numeric_value===null&&china.elasticity.unit===null&&china.elasticity.status==='not_established_by_retrieved_complete_methods','China elasticity unestablished but numeric value supplied');
 const transfer=china?.transport_to_cultivated_chicken;
 check(transfer?.causal_transfer_established===false&&['penetration_parameter','religious_gate','capacity_input'].every(key=>transfer[key]===null),'China cultivated transfer or adoption gate manufactured');
 return {checks,failures};
}
