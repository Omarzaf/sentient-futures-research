// Structural and known semantic boundaries for the October Phase One supplement.
// These checks do not establish scholarly correctness or full research completion.
import {parseCsv} from './halal-checks.mjs';
export function checkContinuation(files) {
 const failures=[];let checks=0;
 const check=(ok,message)=>{checks++;if(!ok)failures.push('Continuation: '+message);};
 const read=name=>{try{return JSON.parse(files[name]);}catch{check(false,'missing or invalid '+name);return null;}};
 const sources=read('source-register.json'),claims=read('claims.json'),reviews=read('reviews.json');
 const coverage=read('coverage.json'),observations=read('observations.json');
 const geography=read('geography.json'),schoolProgress=read('school-gap-progress.json');
 const dossier=read('manufacturing-dossier.json'),egypt=read('egypt-institutions.json'),china=read('china-asf-history.json');
 const institutionMatrix=read('institution-matrix.json'),literature=read('literature-review.json'),standardsReview=read('standards-review.json');
 const history=read('historical-cases.json'),driverMap=read('driver-map.json'),historySynthesis=read('historical-synthesis.json');
 const elasticity=read('elasticity-review.json'),elasticityData=read('elasticity-estimates.json'),feed=read('feed-review.json');
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
  // AGENTIC-PLAN statuses. 'independently_checked' means a second agent read of the same retrieved source, not independent retrieval or human review.
 const reviewed=reviews.some(r=>r.id===claim.review_id&&r.claim_ids?.includes(claim.id));
 check(['independently_checked','confirmed_original','inference','open','disputed'].includes(claim.status),'unsupported claim status: '+claim.id);
 check((claim.status!=='independently_checked'&&claim.status!=='confirmed_original')||reviewed,'missing independent claim review: '+claim.id);
 check(claim.review_id===undefined||reviewed,'claim review link does not resolve: '+claim.id);
 check(claim.status!=='inference'||(typeof claim.premise==='string'&&claim.premise.length>0&&typeof claim.confirmation_test==='string'&&claim.confirmation_test.length>0),'inference without premise or confirmation test: '+claim.id);
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
 const bodyScopes={
  SAU:{count:3,territory:'Saudi Arabia',sources:['P1C4-CORE-S02','P1C4-CORE-S03'],statuses:['institutional_description_only','partial_english_identity_arabic_mandate_lead_held','identity_only']},
  ARE:{count:1,territory:'Federal law; emirate allocation unresolved',sources:['P1C4-CORE-S04'],statuses:['partial_indexed_federal_law']},
  SGP:{count:2,territory:'Singapore',sources:['P1C4-CORE-S05','P1C4-CORE-S06'],statuses:['partial_indexed_statute_with_2025_amendment_annotations','dated_official_operational_description']},
  OMN:{count:1,territory:'Oman',sources:['P1C4-GULF-S01'],statuses:['undated_official_operational_description']}
 };
 for(const country of geographyRows){
  const sameCountry=id=>claims.find(r=>r.id===id&&r.country===country.id);
  check(Array.isArray(country.legal_claim_ids)&&country.legal_claim_ids.every(id=>sameCountry(id)),'geography legal claim lineage: '+country.id);
  check(country.predominant_juristic_schools===null&&Array.isArray(country.school_prevalence_source_ids)&&country.school_prevalence_source_ids.length===0&&country.current_affiliation===null&&country.numerical_remainder===null,'unestablished geography field promoted or zero-filled: '+country.id);
  const bodyScope=bodyScopes[country.id];
  if(bodyScope){
   const bodies=Array.isArray(country.main_fatwa_bodies)?country.main_fatwa_bodies:[];
   check(bodies.length===bodyScope.count&&new Set(bodies.map(b=>b.name)).size===bodyScope.count&&country.institutional_map_complete===false,'partial fatwa-body map coverage lost: '+country.id);
   for(const body of bodies){
    check(typeof body.name==='string'&&body.name.length>0&&typeof body.role==='string'&&body.role.length>0&&body.territory===bodyScope.territory&&bodyScope.statuses.includes(body.mandate_status),'fatwa body role/territory/partial mandate lost: '+country.id);
    check(Array.isArray(body.source_ids)&&body.source_ids.length>0&&new Set(body.source_ids).size===body.source_ids.length&&body.source_ids.every(id=>sourceIds.has(id)&&bodyScope.sources.includes(id)),'fatwa body source jurisdiction lost: '+country.id);
    check(Array.isArray(body.claim_ids)&&body.claim_ids.length>0&&new Set(body.claim_ids).size===body.claim_ids.length&&body.claim_ids.every(id=>{const c=sameCountry(id);return c&&c.source_ids.every(source=>body.source_ids?.includes(source));}),'fatwa body claim/source lineage lost: '+country.id);
    check(body.complete_operative_instrument_read===false&&body.exclusive_national_authority===null&&body.cultivated_product_ruling_established===false&&body.product_certificate===null,'fatwa body authority overclaimed: '+country.id);
   }
  }else check(country.main_fatwa_bodies===null,'unestablished fatwa bodies filled: '+country.id);
  if(country.id==='OMN'){
   const legal=country.legal_document_observation,source=sources.find(r=>r.id==='P1C4-OMN-STATUTE');
   check(legal?.source_ids?.length===1&&legal.source_ids[0]==='P1C4-OMN-STATUTE'&&legal.claim_ids?.length===1&&legal.claim_ids[0]==='P1C4-OMN-ARTICLE2'&&country.legal_claim_ids.includes(legal.claim_ids[0])&&linkedSources(legal.source_ids,sameCountry(legal.claim_ids[0])),'Oman legal observation source/claim lineage lost');
   check(legal?.issued==='2021-01-11'&&legal.effective===legal.issued&&source?.issue_date===legal.issued&&source.effective_date===legal.effective&&legal.landing_metadata_date==='2021-01-12'&&source.landing_metadata_date===legal.landing_metadata_date&&legal.gazette_publication_date===null&&source.gazette_publication_date===null,'Oman issue/effect date confused with landing or gazette date');
   check(legal?.clause==='Attached Statute Article 2'&&legal.school_named_in_this_clause===false&&legal.absence_of_school_in_all_law_established===false&&legal.current_consolidation_verified===false&&legal.qualified_translation_approved===false,'Oman clause scope or review status overclaimed');
  }
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
 // These hashes bind the followup acquisitions; earlier source-register access snapshots remain historical.
 const egyptCaptures={
  'P1C3-EGY-S01':{sha256:'74d88d999b8b813a6447e7bd8daa414322fcd679dcb1ac7e15c3716e80822101',bytes:274917},
  'P1C3-EGY-S02':{sha256:'fe6a7edbe0c3c310a8bcdee05be33b6ff81e549247585bacceedf3607971df3d',bytes:110337},
  'P1C3-EGY-S03':{sha256:'23884d5043add6b47cc31a71561f08495518058fc3953f860aaf856c7eb3958b',bytes:91573}
 };
 const followup=egypt?.followup_retrieval;
 check(followup?.original_rulings_obtained===false&&reviews.some(r=>r.id===followup.review_id&&r.human_review===false),'Egypt followup promoted or review lineage lost');
 const acquisitions=Array.isArray(followup?.article_acquisitions)?followup.article_acquisitions:[];
 check(acquisitions.length===3&&new Set(acquisitions.map(r=>r.source_id)).size===3&&acquisitions.every(r=>sourceIds.has(r.source_id)&&institutions.some(i=>i.source_ids?.includes(r.source_id))&&egyptCaptures[r.source_id]?.sha256===r.sha256&&egyptCaptures[r.source_id]?.bytes===r.bytes&&r.access==='direct_original_publisher_html'),'Egypt acquisition identity, bytes or source lineage lost');
 const newsLinks=['https://www.cairo24.com/1859385','https://www.vetogate.com/4965286','https://www.vetogate.com/4963141'];
 const trace=followup?.link_trace;
 check(trace?.original_fatwa_links_found===false&&Array.isArray(trace.destinations)&&trace.destinations.length===3&&new Set(trace.destinations).size===3&&trace.destinations.every(url=>newsLinks.includes(url)),'Egypt news-link trace promoted or changed');
 const waag=followup?.waag_metadata;
 check(waag?.article_publication==='2024-09-24'&&waag.html_modified_date==='2025-11-19'&&waag.modified_date_is_new_ruling===false&&waag.prior_article_text_version_verified===false,'WAAG metadata promoted to ruling or authenticated prior text');
 check(followup?.academic_locator_lead?.original_fatwa_locator_obtained===false&&followup.academic_locator_lead.access==='indexed_mention_only_original_retrieval_failed','Egypt academic lead promoted to acquired original locator');
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
 // Matrix coverage is not a vote among held, unknown or general-framework positions.
 const matrixConditions=['species','donor_procurement','medium','istihala','slaughter','safety','labelling'];
 const matrixColumns=['IIFA','MUIS','MUFTI-WP','GOOD-MEAT-ADVISERS','JAKIM-MKI','MUI','CII','IFAI','DEOBAND','AL-AZHAR','DAR-AL-IFTA-EGYPT','GHAMIDI-PUBLISHED'];
 const matrixInstitutions=Array.isArray(institutionMatrix?.institutions)?institutionMatrix.institutions:[];
 check(matrixInstitutions.length===12&&new Set(matrixInstitutions.map(i=>i.id)).size===12&&matrixColumns.every(id=>matrixInstitutions.some(i=>i.id===id)),'matrix column coverage lost');
 check(institutionMatrix?.conditions?.length===7&&new Set(institutionMatrix.conditions).size===7&&matrixConditions.every(c=>institutionMatrix.conditions.includes(c)),'matrix condition coverage lost');
 check(artifactLineage(institutionMatrix)&&reviews.some(r=>r.id===institutionMatrix.independent_review_id&&r.human_review===false&&institutionMatrix.claim_ids.every(id=>r.claim_ids.includes(id))),'matrix source/claim/review lineage lost');
 const acceptance=institutionMatrix?.acceptance;
 check(acceptance?.new_independent_review==='checked_scoped_reading'&&acceptance.human_scholarly_acceptance==='pending'&&acceptance.author_acceptance==='not_asserted'&&acceptance.phase_one_done===false&&acceptance.authoritative_status_promotion===false&&acceptance.retrieval_completeness_is_not_scholarly_acceptance===true,'matrix acceptance overclaimed');
 const sourceDates=Array.isArray(institutionMatrix?.source_dates)?institutionMatrix.source_dates:[];
 check(sourceDates.length===institutionMatrix.source_ids?.length&&new Set(sourceDates.map(d=>d.source_id)).size===sourceDates.length&&sourceDates.every(d=>sourceIds.has(d.source_id)&&institutionMatrix.source_ids.includes(d.source_id)&&Object.hasOwn(d,'publication')&&Object.hasOwn(d,'session')),'matrix source-date register incomplete');
 const missingColumns=['MUI','CII','IFAI','DEOBAND'];
 const allowedStatuses={IIFA:['attributed_primary_position','unknown_in_inspected_scope'],MUIS:['attributed_primary_position','unknown_in_inspected_scope','conflicting_official_passages','related_regulatory_context_only'],'MUFTI-WP':['held_language','unknown_in_inspected_scope'],'GOOD-MEAT-ADVISERS':['attributed_participant_report','unknown_in_inspected_scope'],'JAKIM-MKI':['held_language','unknown_in_inspected_scope'],'AL-AZHAR':['held_reported_officeholder_position','unknown_in_inspected_report'],'DAR-AL-IFTA-EGYPT':['held_secondary_attribution','unknown_in_inspected_report'],'GHAMIDI-PUBLISHED':['general_framework_only','unknown_in_inspected_scope']};
 const matrixCells=new Map(),statusCounts={};let nonNullPositions=0;
 for(const institution of matrixInstitutions){
  check(institution.human_scholarly_review==='pending'&&institution.binding_civil_law_established===false&&institution.product_certificate_established===false,'matrix institution authority overclaimed: '+institution.id);
  check(Array.isArray(institution.source_ids)&&institution.source_ids.every(id=>sourceIds.has(id)&&institutionMatrix.source_ids.includes(id)),'matrix institution source lineage: '+institution.id);
  const cells=institution.cells||{};
  check(Object.keys(cells).length===7&&matrixConditions.every(c=>Object.hasOwn(cells,c)),'matrix cell coverage lost: '+institution.id);
  const missing=missingColumns.includes(institution.id);
  if(missing)check(institution.type==='named_institution_position_unlocated'&&institution.source_ids.length===0&&institution.bounded_search?.status==='parked_after_two_unproductive_cycles'&&institution.bounded_search.cycles===2&&!!institution.bounded_search.reopen_trigger,'matrix bounded unknown disposition lost: '+institution.id);
  for(const [condition,cell] of Object.entries(cells)){
   matrixCells.set(institution.id+'/'+condition,cell);statusCounts[cell.status]=(statusCounts[cell.status]||0)+1;if(cell.position!==null)nonNullPositions++;
   check(cell.condition===condition&&(missing?cell.status==='researched_unknown_no_primary_instrument':allowedStatuses[institution.id]?.includes(cell.status)),'matrix source-role promotion: '+institution.id+'/'+condition);
   const unknown=['researched_unknown_no_primary_instrument','unknown_in_inspected_scope','unknown_in_inspected_report'].includes(cell.status);
   check(unknown?cell.position===null&&!!cell.unknown_reason&&!!cell.search_disposition:typeof cell.position==='string'&&cell.position.length>0&&cell.unknown_reason===null,'matrix unknown/status boundary lost: '+institution.id+'/'+condition);
   check(Array.isArray(cell.source_ids)&&new Set(cell.source_ids).size===cell.source_ids.length&&cell.source_ids.every(id=>institution.source_ids.includes(id))&&(missing?cell.source_ids.length===0:cell.source_ids.length>0)&&!!cell.locator&&!!cell.limits,'matrix cell source/locator missing: '+institution.id+'/'+condition);
   check(Array.isArray(cell.date)&&cell.date.length===cell.source_ids?.length&&new Set(cell.date.map(d=>d.source_id)).size===cell.date.length&&cell.date.every(d=>{const original=sourceDates.find(s=>s.source_id===d.source_id);return cell.source_ids.includes(d.source_id)&&original&&d.publication===original.publication&&JSON.stringify(d.session)===JSON.stringify(original.session)&&d.exact_adoption===null;}),'matrix cell date/source mismatch: '+institution.id+'/'+condition);
  }
 }
 const summary=institutionMatrix?.summary;
 check(summary?.institutions_and_adviser_columns===11&&summary.published_author_columns===1&&summary.conditions===7&&summary.cells===matrixCells.size&&matrixCells.size===84&&summary.non_null_positions===nonNullPositions&&summary.unknown_positions===84-nonNullPositions&&summary.bounded_missing_institution_searches===4,'matrix summary coverage inconsistent');
 check(Object.keys(summary?.status_counts||{}).length===Object.keys(statusCounts).length&&Object.entries(statusCounts).every(([status,count])=>summary.status_counts[status]===count),'matrix summary status counts inconsistent');
 const muis=matrixInstitutions.find(i=>i.id==='MUIS');
 check(['donor_procurement','slaughter'].every(c=>muis?.cells?.[c]?.status==='conflicting_official_passages'),'MUIS dispute prematurely resolved');
 const advisers=matrixInstitutions.find(i=>i.id==='GOOD-MEAT-ADVISERS'),selfReport=advisers?.historical_process_caveat;
 check(advisers?.type==='named_scholars_advice_reported_by_participants'&&selfReport?.source_id==='P1C5-INST-GOODMEAT'&&advisers.source_ids.includes(selfReport.source_id)&&selfReport.report_date==='2023-09-11'&&selfReport.current_noncompliance_established===false&&selfReport.process_version_match_established===false,'GOOD Meat dated self-report promoted or mislinked');
 const adviserFollowup=dossier?.adviser_report_followup;
 check(artifactLineage(adviserFollowup)&&adviserFollowup.report_date==='2023-09-11'&&adviserFollowup.company_reported_then_process_met_conditions===false&&adviserFollowup.current_process_conformity===null&&adviserFollowup.exact_failed_condition===null&&adviserFollowup.signed_opinion_obtained===false&&adviserFollowup.product_certificate_established===false&&adviserFollowup.process_version_match_established===false,'GOOD Meat followup promoted to current verdict or signed opinion');
 const matrixRows=Array.isArray(institutionMatrix?.rows)?institutionMatrix.rows:[];
 check(matrixRows.length===7&&new Set(matrixRows.map(r=>r.condition)).size===7&&matrixConditions.every(c=>matrixRows.some(r=>r.condition===c)),'matrix comparison-row coverage lost');
 for(const row of matrixRows){
  check(row.cell_ids?.length===12&&new Set(row.cell_ids).size===12&&matrixColumns.every(id=>row.cell_ids.includes(id+'/'+row.condition)),'matrix row/cell crosswalk lost');
  const support=row.supporting_cell_ids||[];
  check([null,'disputed','single_source'].includes(row.classification)&&(row.classification===null?support.length===0:Array.isArray(support)&&new Set(support).size===support.length&&support.length>0&&support.every(id=>row.cell_ids.includes(id)&&['attributed_primary_position','attributed_participant_report','conflicting_official_passages'].includes(matrixCells.get(id)?.status)))&&(row.classification!=='single_source'||support.length===1)&&(row.classification!=='disputed'||support.length>=2),'matrix classification support includes unsupported votes');
 }
 const classificationCounts={};for(const row of matrixRows){const key=row.classification??'unestablished';classificationCounts[key]=(classificationCounts[key]||0)+1;}
 check(Object.keys(summary?.row_classifications||{}).length===Object.keys(classificationCounts).length&&Object.entries(classificationCounts).every(([key,count])=>summary.row_classifications[key]===count),'matrix classification summary inconsistent');
 const alq=literature?.Alqurashi2026,hamdan=literature?.Hamdan2018;
 const litSourceIds=[...new Set([...(alq?.source_ids||[]),...(hamdan?.source_ids||[]),...(literature?.dependency_source_ids||[]),...(literature?.authority_source_ids||[])])];
 check(artifactLineage({source_ids:litSourceIds,claim_ids:literature?.claim_ids})&&reviews.some(r=>r.id===literature.independent_review_id&&r.human_review===false&&literature.claim_ids.every(id=>r.claim_ids.includes(id))),'literature source/claim/review lineage lost');
 check(literature?.complete===false&&literature.human_review==='pending'&&literature.independent_review==='checked_scoped_reading'&&literature.MUIS_IIFA_held_dispute?.status==='held_for_qualified_human_review','literature completion or dispute approval overclaimed');
 check(alq?.doi==='10.3390/foods15081288'&&alq.type==='narrative perspective'&&alq.authors?.length===4&&['Randah M. Alqurashi','Dominika Sikora','Piotr Rzymski','Barbara Poniedziałek'].every(name=>alq.authors.includes(name))&&alq.publication?.online==='2026-04-09'&&alq.publication.volume===15&&alq.publication.issue===8&&alq.publication.article==='1288'&&hamdan?.doi==='10.1007/s10943-017-0403-3'&&hamdan.authors?.length===4&&['Mohammad Naqib Hamdan','Mark J. Post','Mohd Anuar Ramli','Amin Rukaini Mustafa'].every(name=>hamdan.authors.includes(name))&&hamdan.publication?.online==='2017-04-29'&&hamdan.publication.issue==='2018-12','literature bibliographic identity/date boundary lost');
 check(alq?.source_ids?.length===2&&['P1C5-LIT-ALQ-XML','P1C5-LIT-ALQ-PDF'].every(id=>alq.source_ids.includes(id)&&sources.some(s=>s.id===id&&s.sha256!==null&&s.source_family==='Alqurashi2026'))&&alq.coverage?.all_cited_sources_independently_read===false,'Alqurashi fulltext/source-family boundary lost');
 check(hamdan?.fulltext_obtained===false&&hamdan.full_argument_review==='access_unresolved'&&hamdan.source_ids?.every(id=>sources.some(s=>s.id===id&&s.status==='independently_checked_metadata_only')),'Hamdan fulltext boundary lost');
 const argumentMap=Array.isArray(alq?.argument_map)?alq.argument_map:[];
 const expectedArguments=[6,7,4,5,9,5].flatMap((n,i)=>Array.from({length:n},(_,j)=>'S'+(i+1)+'.P'+(j+1)));
 check(argumentMap.length===36&&new Set(argumentMap.map(p=>p.locator)).size===36&&expectedArguments.every(id=>argumentMap.some(p=>p.locator===id))&&alq.coverage?.body_sections_read===6&&alq.coverage.body_paragraphs_mapped===36,'literature argument coverage incomplete');
 const referenceIndex=Array.isArray(alq?.reference_index)?alq.reference_index:[],referenceIds=new Set(referenceIndex.map(r=>r.id));
 check(referenceIndex.length===94&&referenceIds.size===94&&Array.from({length:94},(_,i)=>'B'+(i+1)+'-foods-15-01288').every(id=>referenceIds.has(id))&&referenceIndex.every(r=>!!r.text&&r.read_status==='bibliographic_entry_read; underlying-work retrieval is separate'),'literature bibliography index coverage or access overclaim');
 for(const node of argumentMap){
  check(validSourceRefs(node.source_ids)&&node.source_ids.every(id=>alq.source_ids.includes(id))&&!!node.article_argument&&!!node.counterargument_or_dependency_limit&&node.review_status==='human_review_pending','literature argument attribution/source boundary lost: '+node.locator);
  check(Array.isArray(node.reference_ids)&&node.reference_ids.every(id=>referenceIds.has(id)),'literature bibliography locator missing: '+node.locator);
 }
 for(const [key,suffix] of [['tables','t'],['figures','f']])check(Array.isArray(alq?.[key])&&alq[key].length===3&&[1,2,3].every(n=>alq[key].some(r=>r.id==='foods-15-01288-'+suffix+'00'+n&&!!r.finding)),'literature table/figure coverage lost: '+key);
 check(alq.coverage.tables_read===3&&alq.coverage.figures_visually_read===3,'literature table/figure reading scope lost');
 const evidence=literature?.acceptance_evidence;
 check(evidence?.table==='foods-15-01288-t001'&&evidence.paragraph==='S4.P3'&&evidence.source_id==='P1C5-LIT-ALQ-XML'&&evidence.malaysia_sample_n===102&&evidence.doubts_percent===56&&evidence.acceptance_range_validated===false&&evidence.pooled_adoption_estimate===null,'literature doubts/adoption boundary lost');
 const authority=literature?.authority_boundaries;
 check(authority?.author_proposals_are_adopted_rules===false&&authority.author_counterarguments_are_institutional_rulings===false&&authority.review_constitutes_product_certification===false,'literature author authority promoted');
 const reviewedStandards=Array.isArray(standardsReview?.standards)?standardsReview.standards:[];
 check(standardsReview?.complete===false&&standardsReview.human_review==='pending'&&standardsReview.independent_review==='checked_scoped_reading'&&standardsReview.independent_review_id==='R5-STANDARDS'&&reviews.some(r=>r.id==='R5-STANDARDS'&&r.human_review===false),'standards review acceptance or review lineage lost');
 check(artifactLineage(standardsReview),'standards aggregate source/claim lineage lost');
 check(reviewedStandards.length===2&&['OIC-SMIIC-1','GSO-2055-1'].every(id=>reviewedStandards.some(s=>s.id===id)),'required standards coverage lost');
 for(const standard of reviewedStandards){
  check(artifactLineage(standard)&&reviews.some(r=>r.id===standardsReview.independent_review_id&&standard.claim_ids.every(id=>r.claim_ids.includes(id))),'standard source/claim lineage lost: '+standard.id);
  check(standard.full_text_read===false,'standard fulltext boundary lost: '+standard.id);
  check(Array.isArray(standard.national_incorporation)&&standard.national_incorporation.length===1,'standard national reference coverage lost: '+standard.id);
  for(const national of standard.national_incorporation||[]){
   check(national.legal_enforceability===null&&national.product_application===null&&Array.isArray(national.claim_ids)&&national.claim_ids.length>0&&national.claim_ids.every(id=>standard.claim_ids.includes(id))&&(standard.id==='OIC-SMIIC-1'?national.country==='PAK'&&national.status==='modified_adoption_metadata'&&national.modifications_read===false:national.country==='ARE'&&national.status==='administrative_reference'&&national.edition===null&&national.full_decree_read===false),'standard national incorporation scope overclaimed');
  }
 }
 const smiic=reviewedStandards.find(s=>s.id==='OIC-SMIIC-1'),gso=reviewedStandards.find(s=>s.id==='GSO-2055-1');
 check(smiic?.edition==='OIC/SMIIC1:2019'&&smiic.relevant_clauses===null,'unread OIC/SMIIC clauses supplied');
 check(gso?.edition==='GSO2055-1:2015 edition2 English'&&gso.draft?.identifier==='GSO TC15/DS1 2055-1:2026'&&gso.draft.status==='initial_draft'&&gso.draft.adopted===null&&gso.draft.adoption_not_established===true&&gso.draft.full_text_read===false&&gso.draft.national_effective_date===null,'GSO draft adoption promoted or edition conflated');
 check(gso?.relevant_clauses?.length===3&&new Set(gso.relevant_clauses.map(c=>c.clause)).size===3&&gso.relevant_clauses.every(c=>c.clause==='1'?c.product_verdict===null:c.clause==='2.1–2.6'?c.referenced_texts_read_in_this_run===false:c.clause==='3.3–3.4,3.8–3.9'&&c.cultivated_meat_determination===null)&&gso.unavailable_clauses?.length===6&&['4','5','6','7','8','Annex1'].every(c=>gso.unavailable_clauses.includes(c)),'GSO preview promoted to product determination or unread clauses lost');
 // Run 06: an assessed historical analogy is not a completed forecast input.
 const sameMembers=(actual,expected)=>Array.isArray(actual)&&actual.length===expected.length&&new Set(actual).size===actual.length&&expected.every(value=>actual.includes(value));
 const historicalCases=Array.isArray(history?.cases)?history.cases:[];
 const historicalIds=Array.from({length:21},(_,i)=>'HP-'+String(i+1).padStart(2,'0'));
 const historicalClaimNumbers=[[1,2],[3],[4],[5,6,7],[8,9],[10,11],[12,13],[14,15],[16,21],[17,22],[18],[19,20]];
 const historyCase=id=>historicalCases.find(c=>c.id===id);
 const historyDetail=id=>historyCase(id)?.detail;
 const historyObservations=id=>historyDetail(id)?.observations||[];
 const reviewCovers=(id,claimRefs)=>reviews.some(r=>r.id===id&&r.human_review===false&&claimRefs.every(claim=>r.claim_ids?.includes(claim)));
 check(sameMembers(historicalCases.map(c=>c.id),historicalIds),'historical candidate roster lost');
 check(history?.complete===false&&history.human_review==='pending'&&history.external_forecast_join_verified===false,'historical assessment promoted to completion or forecast join');
 for(const c of historicalCases){
  const number=Number(c.id?.slice(3)),detail=c.detail;
  const expectedClaims=number<=12?(historicalClaimNumbers[number-1]||[]).map(n=>'P1C6-REL-C'+String(n).padStart(2,'0')):['R6E-HISTORY-'+String(number).padStart(2,'0')+'-SCOPE'];
  check(c.requirement_id==='HISTORY-'+String(number).padStart(2,'0')&&detail?.requirement_id===c.requirement_id&&sameMembers(c.claim_ids,expectedClaims),'historical case/requirement/claim identity lost: '+c.id);
  const adoptedSources=[...new Set((c.claim_ids||[]).flatMap(id=>claims.find(claim=>claim.id===id)?.source_ids||[]))];
  const permittedSources=number===7?[...adoptedSources,'P1C6-REL-MUI-AJI-HELD']:adoptedSources;
  check(c.country===({7:'IDN',16:'IND',17:'PAK',18:'CHN',20:'QAT',21:'ARE'}[number]??null)&&artifactLineage(c,c.country)&&sameMembers(c.source_ids,permittedSources)&&reviewCovers(c.review_id,c.claim_ids||[])&&c.claim_ids.every(id=>claims.find(claim=>claim.id===id)?.review_id===c.review_id),'historical case source/claim/review lineage lost: '+c.id);
  check(c.independent_review==='checked_with_scoped_limits'&&c.human_review==='pending'&&c.positive_resolution_of_all_requirements===false,'historical case acceptance overclaimed: '+c.id);
  check(!!c.time_place&&Object.hasOwn(c,'before')&&Object.hasOwn(c,'after')&&!!c.evidence_kind&&!!c.assessment&&Array.isArray(c.unknowns)&&c.unknowns.length>0&&!!c.reopen,'historical scope or unresolved evidence erased: '+c.id);
  check(c.forecast_inputs&&sameMembers(Object.keys(c.forecast_inputs),['D','p_mass','H_rel','K','elasticity','adoption_half_life'])&&Object.values(c.forecast_inputs).every(v=>v===null),'historical forecast input invented: '+c.id);
  if(number<=12){
   check(detail?.measured_speed===null&&detail.elasticity===null&&detail.numeric_transport&&sameMembers(Object.keys(detail.numeric_transport),['religious_gate','penetration_parameter','capacity_input','demand_parameter'])&&Object.values(detail.numeric_transport).every(v=>v===null),'juristic example promoted to measured uptake or numeric gate: '+c.id);
   check(detail?.review?.human_scholarly_review==='pending'&&detail.review.author_acceptance==='not_asserted'&&detail.review.phase_one_done===false,'historical detail human acceptance overclaimed: '+c.id);
   const families=[...new Set((c.source_ids||[]).map(id=>sources.find(s=>s.id===id)?.source_family))];
   check(sameMembers(detail?.source_families,families),'historical source-family count/identity inflated: '+c.id);
   for(const locator of detail?.locators||[])check(c.source_ids.includes(locator.source_id)&&!!locator.locator,'historical locator source lost: '+c.id);
   for(const counter of detail?.counterevidence||[])check(counter.source_ids?.length>0&&counter.source_ids.every(id=>c.source_ids.includes(id))&&!!counter.text,'historical counterevidence lineage lost: '+c.id);
  }else{
   check(detail?.elasticity?.value===null&&detail.elasticity.estimand===null&&detail.penetration_parameter===null&&detail.religious_permission_inferred_from_market_event===false&&detail.requirement_promoted_complete===false,'empirical case promoted to elasticity, adoption or permission: '+c.id);
   check(detail?.status==='human_review_pending'&&detail.acceptance_disposition?.positive_resolution_of_requirement===false&&detail.acceptance_disposition.human_review==='pending','empirical detail completion overclaimed: '+c.id);
   check(c.time_place?.period===detail?.period&&c.time_place?.place===detail?.place,'empirical time/place envelope differs from source assessment: '+c.id);
  }
  check((c.claim_ids||[]).every(id=>claims.find(claim=>claim.id===id)?.source_ids.every(source=>!sources.find(s=>s.id===source)?.status?.startsWith('held_'))),'held historical lead adopted as substantive claim: '+c.id);
 }
 // Repeated company publications and institutional editions remain one family.
 for(const ids of [['P1C6-REL-AJI2015','P1C6-REL-AJI2024','P1C6-REL-AJI2015-PDF'],['P1C6-REL-IIFA95','P1C6-REL-IIFA263'],['P1C6-EMP-E12','P1C6-EMP-E13'],['P1C6-EMP-E14','P1C6-EMP-E15'],['P1C6-EMP-E07','P1C6-EMP-PAK2025']])check(ids.every(id=>sourceIds.has(id))&&new Set(ids.map(id=>sources.find(s=>s.id===id)?.source_family)).size===1,'historical same-family evidence split into corroboration: '+ids[0]);
 const periods=historyDetail('HP-04')?.prescribed_periods;
 check(periods?.source_id==='P1C6-REL-ISTIBRA219'&&periods.kind==='recommended_precaution_under_Sistani219_not_observed_speed'&&periods.unit==='days'&&periods.values?.camel===40&&periods.values.cow===20&&periods.values.sheep===10&&sameMembers(periods.values.duck,[7,5])&&periods.values.domestic_hen===3,'jallala species precaution replaced by general seven-day rule');
 check(!!periods?.primary_condition&&/2649/.test(periods?.separate_pig_milk_subcase||''),'jallala primary condition or separate pig-milk subcase lost');
 const aji=historyDetail('HP-07');
 check(aji?.boundaries?.finished_product_porcine_residue_established===false&&aji.boundaries.current_product_certificate_established===false&&aji.boundaries.certificate_restoration_date===null,'Ajinomoto process controversy promoted to residue or certificate');
 check(aji?.held_evidence?.source_id==='P1C6-REL-MUI-AJI-HELD'&&sources.find(s=>s.id===aji.held_evidence.source_id)?.status==='held_original_language_lead','Ajinomoto untranslated instrument promoted');
 const instruments=historyDetail('HP-09')?.instrument_boundaries;
 check(instruments?.historical_resolution==='95 (3/10)'&&sameMembers(instruments.historical_session,['1997-06-28','1997-07-03'])&&instruments.later_resolution==='263 (8/26)'&&sameMembers(instruments.later_session,['2025-05-04','2025-05-08'])&&instruments.later_action==='postponement'&&instruments.current_consolidation_verified===false,'IIFA historical conditions and later postponement conflated');
 for(const [id,dates] of [['P1C6-REL-IIFA95',instruments?.historical_session],['P1C6-REL-IIFA263',instruments?.later_session]]){const source=sources.find(s=>s.id===id);check(Array.isArray(dates)&&sameMembers(source?.session_dates,dates)&&source?.exact_adoption_date===null,'IIFA source session/adoption date lineage lost: '+id);}
 const milk=historyDetail('HP-15'),milkModel=milk?.model_scope,milkRatio=milk?.observations?.find(o=>o.measure==='displacement ratio');
 check(sameMembers(historyCase('HP-15')?.source_ids,['lee_sumner_2026_plant_based_milk_displacement']),'shared Lee-Sumner source identity lost');
 check(milkModel?.design==='static_counterfactual'&&sameMembers(milkModel.market_years,[2018,2019,2020])&&milkModel.annual_household_scaling_year===2020&&milkModel.long_run_causal_ratio_established===false,'plant milk counterfactual market window/scaling year conflated');
 check(milk?.observations?.length===3&&milk.observations.every(o=>o.observed===false)&&milkRatio?.value===0.68&&milkRatio.is_price_elasticity===false&&/gallons/.test(milkRatio.unit||'')&&milk.speed?.observed_adoption_speed===null,'plant milk modeled displacement promoted to observation or elasticity');
 const vanaspati=historyObservations('HP-16'),pakistan=historyObservations('HP-17');
 check(vanaspati.length===3&&vanaspati[0]?.type==='forecast_not_realized_output'&&vanaspati[1]?.type==='forecast_not_observed_demand','vanaspati forecast promoted to observed production');
 check(pakistan.length===4&&pakistan[0]?.type==='statistically_calculated_using2005-06_statistics'&&pakistan[0]?.unit==='million numbers as table labels'&&pakistan.slice(1).every(o=>o.type==='official_estimate'&&o.unit==='thousand tonnes'),'Pakistan modeled output promoted to observed household substitution');
 const historicalChina=historyObservations('HP-18');
 check(historicalChina[0]?.status==='preliminary'&&historicalChina[0]?.unit==='million tons as NBS publishes'&&historicalChina[1]?.unit==='kg food per person; at-home only'&&historicalChina.slice(2).every(o=>o.unit==='kg food per person')&&historyDetail('HP-18')?.speed?.durable_conversion_established===false,'historical China output/purchase basis or permanence promoted');
 const qatar=historyCase('HP-20'),heldQatar=qatar?.held_national_series;
 check(historyObservations('HP-20').length===4&&historyObservations('HP-20').slice(0,3).every(o=>o.type?.startsWith('company '))&&historyObservations('HP-20')[3]?.type==='August2017plan_not_verified_realized_output','Qatar company plan promoted to national realized output');
 const qatarSourceIds=['P1C6-QAT-ABSTRACT2020','P1C6-QAT-ENV2020','P1C6-QAT-DATASET'];
 check(sameMembers(heldQatar?.source_ids,qatarSourceIds)&&qatarSourceIds.every(id=>sources.find(s=>s.id===id)?.status==='held_edition_specific_national_series_lead')&&new Set(qatarSourceIds.map(id=>sources.find(s=>s.id===id)?.source_family)).size===1,'Qatar held source lineage/status lost');
 check(heldQatar?.status==='held_edition_specific_indexed_leads'&&heldQatar.original_pages_obtained===false&&heldQatar.verified_national_outcome===false&&heldQatar.edition_reconciliation===null&&heldQatar.fresh_milk_equals_all_dairy===false&&heldQatar.dataset?.actual_rows_retrieved===false,'Qatar indexed lead promoted to original, reconciled outcome or all-dairy self-sufficiency');
 const qatarRows=heldQatar?.abstract2020?.rows||[];
 check(sameMembers(qatarRows.map(r=>r.year),[2017,2018,2019,2020])&&heldQatar?.abstract2020?.status==='indexed_candidates_not_original_page_verified'&&qatarRows.find(r=>r.year===2019)?.self_sufficiency_percent===73&&heldQatar?.environment2020?.year===2019&&heldQatar.environment2020.dairy_self_sufficiency_percent===72.8&&heldQatar.environment2020.status==='indexed_candidate_separate_edition','Qatar separate 2019 edition observations silently reconciled');
 check(historyObservations('HP-21').length===3&&sameMembers(historyObservations('HP-21').map(o=>o.type),['policy_scope','policy_design','target_not_outcome']),'UAE policy design promoted to realized Gulf outcomes');
 // Plan factors retain their exact shared names; mapped paths are hypotheses.
 const factorNames={'Mass-scaling production':['supply chain costs','AI-driven R&D speed'],Cheap:['price'],Taste:['taste and texture'],Premade:['convenience'],Nutrition:['health perceptions'],'Variety and cuisine':['cuisine fit']};
 const mappedDrivers=Array.isArray(driverMap?.drivers)?driverMap.drivers:[];
 check(sameMembers(mappedDrivers.map(d=>d.mind_map_factor),Object.keys(factorNames)),'six plan factor roster lost');
 check(driverMap?.plan?.section==='6.4C'&&/^[a-f0-9]{64}$/.test(driverMap.plan.sha256||'')&&driverMap.human_review==='pending'&&driverMap.empirical_weights_established===false&&driverMap.external_forecast_join_verified===false&&driverMap.baseline_available===false,'driver map empirical/baseline/external join overclaimed');
 const synthesisReview=reviews.find(r=>r.id==='R6-DRIVER-SYNTHESIS');
 check(driverMap?.review_id==='R6-DRIVER-SYNTHESIS'&&historySynthesis?.review_id===driverMap.review_id&&synthesisReview?.human_review===false&&!!synthesisReview?.method&&!!synthesisReview?.scope,'driver synthesis independent review missing');
 const gate=driverMap?.gate_boundaries;
 check(!!driverMap?.gate?.H_rel&&!!driverMap.gate.L&&!!driverMap.gate.scenario_gate&&gate?.religious_status_is_food_approval===false&&gate.gate_is_demand_weight===false&&gate.hypothetical_scenario_is_observed_decision===false&&gate.numeric_output_without_baseline===false,'driver religious/access/scenario gate conflated');
 for(const driver of mappedDrivers){
  check(sameMembers(driver.shared_driver_names,factorNames[driver.mind_map_factor]||[])&&driver.empirical_weight===null&&driver.coefficient===null&&driver.human_review==='pending','driver exact shared mapping or null coefficient lost: '+driver.id);
  check(Array.isArray(driver.case_ids)&&driver.case_ids.length>0&&new Set(driver.case_ids).size===driver.case_ids.length&&driver.case_ids.every(id=>historicalIds.includes(id)),'driver historical case link lost: '+driver.id);
  check(['mind_map_factor','shared_driver_names','definition','hypothesis','counter_hypothesis','socio_cultural_channel','variable_paths','case_ids'].every(key=>!!driver.field_provenance?.[key])&&['definition','hypothesis','counter_hypothesis','socio_cultural_channel','double_count_or_transfer_limit'].every(key=>typeof driver[key]==='string'&&driver[key].length>0)&&Array.isArray(driver.variable_paths)&&driver.variable_paths.length>0&&driver.variable_paths.every(path=>['K','p_mass'].includes(path)),'driver field provenance, competing hypothesis or variable path lost: '+driver.id);
 }
 const synthesisRows=Array.isArray(historySynthesis?.rows)?historySynthesis.rows:[];
 check(sameMembers(synthesisRows.map(r=>r.driver),['religious ruling','price','scarcity','disease','technology','policy or sovereignty','taste']),'seven historical drivers coverage lost');
 check(historySynthesis?.human_review==='pending'&&historySynthesis.full_phase_one_complete===false,'historical synthesis promoted to complete or human approved');
 for(const row of synthesisRows){
  const rowCases=Array.isArray(row.case_ids)?row.case_ids:[],rowClaims=[...new Set(rowCases.flatMap(id=>historyCase(id)?.claim_ids||[]))];
  check(rowCases.length>0&&new Set(rowCases).size===rowCases.length&&rowCases.every(id=>historicalIds.includes(id))&&sameMembers(row.claim_ids,rowClaims)&&reviewCovers(historySynthesis.review_id,rowClaims),'historical synthesis case/claim/review join lost: '+row.driver);
  check(row.inference_status==='analytical_hypothesis_from_bounded_cases'&&row.quantitative_effect===null&&row.ruling_speed===null&&['evidence_summary','conditional_mechanism','counterexample','transportability_limit'].every(key=>typeof row[key]==='string'&&row[key].length>0),'historical synthesis hypothesis promoted to measured effect or ruling time: '+row.driver);
 }
 // Run 07 keeps publication findings distinct from usable forecast parameters.
 const focalCountries=['IND','PAK','SAU','ARE'];
 const elStudies=Array.isArray(elasticity?.studies)?elasticity.studies:[],elRows=Array.isArray(elasticityData?.estimates)?elasticityData.estimates:[],elSlots=Array.isArray(elasticity?.requirements)?elasticity.requirements:[];
 const elStudyIds=['IND-DASTAGIRI-2004','PAK-AUJLA-2019','PAK-HAYAT-2023','SAU-ALBALAWI-2016','ARE-BASARIR-2013'];
 const elStudy=id=>elStudies.find(s=>s.id===id),elRow=id=>elRows.find(e=>e.id===id);
 const elExpectedSlots=focalCountries.flatMap(country=>['CHICKEN','BEEF','MUTTON'].map(good=>'EL-'+country+'-'+good));
 check(sameMembers(elSlots.map(r=>r.requirement_id),elExpectedSlots)&&sameMembers([...new Set(elSlots.map(r=>r.country))],focalCountries),'elasticity twelve-slot/four-country roster lost');
 check(sameMembers(elStudies.map(s=>s.id),elStudyIds),'elasticity five-study roster lost');
 check(elasticity?.estimate_file==='elasticity-estimates.json'&&elasticity.estimate_csv==='elasticity-estimates.csv'&&elasticity.estimate_count===186&&elasticityData?.row_count===186&&elRows.length===186&&new Set(elRows.map(e=>e.id)).size===186,'elasticity 186-estimate file/count identity lost');
 check(elasticity?.human_review==='pending'&&elasticity.full_phase_one_complete===false&&elasticityData?.review_status==='human_review_pending'&&elasticity.compatible_forecast_parameters===0&&elasticity.pooled_cross_study_estimate===null&&elasticity.inverse_flexibility_reciprocal_allowed===false&&elasticity.combined_categories_are_species_specific===false,'elasticity findings promoted to forecast, species specificity or approval');
 const elClaims=Array.from({length:13},(_,i)=>'R07-EL-C'+String(i+1).padStart(2,'0'));
 check(elasticity?.review_id==='R7-ELASTICITY'&&reviewCovers(elasticity.review_id,elClaims)&&sameMembers(reviews.find(r=>r.id===elasticity.review_id)?.claim_ids,elClaims),'elasticity independent review coverage lost');
 const indComp='not explicitly Marshallian or Hicksian; real-expenditure wording precludes silent classification';
 const pakComp='not explicitly labeled; uncompensated-intent only, model notation unresolved';
 const expComp='not applicable to expenditure estimand',sauComp='conditional compensated Slutsky/Hicksian-type';
 const uaeSample='pooled surveyed households across seven emirates; national representativeness unestablished';
 const indGoods=['mutton and goat meat','beef and buffalo meat','chicken'],pakGoods=['beef row / beef and buffalo category unresolved','mutton row / mutton and goat category unresolved','chicken'],sauGoods=['beef','chicken','lamb'],uaeGoods=['beef','lamb','goat','chicken'];
 const expectedElRows=[];
 const appendEl=(study_id,good,with_respect_to,sample,compensation)=>expectedElRows.push({id:'EST-'+String(expectedElRows.length+1).padStart(3,'0'),study_id,good,with_respect_to,sample,compensation});
 const appendMatrix=(study,goods,prices,sample,comp)=>goods.forEach(g=>prices.forEach(p=>appendEl(study,g,p,sample,comp)));
 for(const sample of ['rural state aggregates','urban state aggregates'])appendMatrix(elStudyIds[0],indGoods,['milk',...indGoods.slice(0,2),'chicken','eggs','fish','other food','non-food'],sample,indComp);
 indGoods.forEach(g=>['rural','urban','pooled'].forEach(sample=>appendEl(elStudyIds[0],g,'expenditure',sample,expComp)));
 for(const sample of ['urban','rural','pooled'])appendMatrix(elStudyIds[1],pakGoods,['beef and buffalo meat','mutton and goat meat','chicken','fish'],sample,pakComp);
 pakGoods.forEach(g=>['rural','urban','pooled'].forEach(sample=>appendEl(elStudyIds[1],g,'expenditure',sample,expComp)));
 appendMatrix(elStudyIds[3],sauGoods,['beef','chicken','lamb','fish'],'national annual 1985–2010',sauComp);
 sauGoods.forEach(g=>appendEl(elStudyIds[3],g,'expenditure','pooled/national','not applicable; meat/fish group expenditure elasticity'));
 for(const comp of ['Marshallian','Hicksian'])appendMatrix(elStudyIds[4],uaeGoods,['beef','lamb','goat','chicken','camel','fish'],uaeSample,comp+', conditional on six-product group');
 uaeGoods.forEach(g=>appendEl(elStudyIds[4],g,'expenditure',uaeSample,'not applicable; six-product group expenditure elasticity'));
 for(const comp of ['Marshallian','Hicksian'])appendMatrix(elStudyIds[2],['meat aggregate'],['cereals','pulses','milk','meat aggregate','fruits','vegetables','sugar','ghee/oils'],'pooled/national',comp+', conditional on eight-food budget');
 appendEl(elStudyIds[2],'meat aggregate','expenditure','pooled/national','not applicable; eight-food budget expenditure elasticity');
 const elPeriods=['1993–1994','2010–2011','2018–2019','1985–2010',null],elCounts=[57,45,17,15,52];
 for(const [i,id] of elStudyIds.entries()){
  const study=elStudy(id),studyClaims=claims.filter(c=>elClaims.includes(c.id)&&c.source_ids?.includes('P1C7-EL-'+id));
  check(study?.source_id==='P1C7-EL-'+id&&sourceIds.has(study.source_id)&&studyClaims.length>0&&studyClaims.every(c=>c.review_id===elasticity.review_id&&reviewCovers(c.review_id,[c.id])),'elasticity study source/claim/review lineage lost: '+id);
  check(study?.country===id.slice(0,3)&&study.observation_period===elPeriods[i]&&elRows.filter(e=>e.study_id===id).length===elCounts[i]&&study.review_status==='human_review_pending'&&study.transport_to_current_forecast===null,'elasticity study population period/count or transport changed: '+id);
  check(['population','method','conditioning','compensation','identification','uncertainty'].every(k=>typeof study?.[k]==='string'&&study[k].length>0)&&Array.isArray(study?.limitations)&&study.limitations.length>0&&Array.isArray(study?.public_locators)&&study.public_locators.length>0,'elasticity study method/uncertainty scope missing: '+id);
 }
 check(elStudy(elStudyIds[0])?.sample?.estimation_observation_sets_total===64&&elStudy(elStudyIds[1])?.sample?.table1_households===16107&&elStudy(elStudyIds[1])?.sample?.table3_households===16082&&elStudy(elStudyIds[1])?.sample?.estimation_n===null&&elStudy(elStudyIds[2])?.sample?.analysis_households===24620&&elStudy(elStudyIds[3])?.sample?.annual_levels===26&&elStudy(elStudyIds[4])?.sample?.questionnaires===500,'elasticity underlying surveys confused with estimation samples');
 for(const spec of expectedElRows){
  const row=elRow(spec.id),study=elStudy(spec.study_id);
  check(row&&['study_id','good','with_respect_to','sample','compensation'].every(k=>row[k]===spec[k]),'elasticity row direction/category/compensation changed: '+spec.id);
  const ownBundle=spec.study_id===elStudyIds[1]&&((spec.good===pakGoods[0]&&spec.with_respect_to==='beef and buffalo meat')||(spec.good===pakGoods[1]&&spec.with_respect_to==='mutton and goat meat'));
  const estimand=spec.with_respect_to==='expenditure'?'expenditure':ownBundle?'own_price_author_labeled_category_unresolved':spec.good===spec.with_respect_to?'own_price':'cross_price';
  check(row?.estimand===estimand&&Number.isFinite(row.value)&&row.unit==='dimensionless elasticity, percent quantity change per 1 percent regressor change as reported','elasticity estimand/value/unit changed: '+spec.id);
  check(row?.country===study?.country&&row?.population===study?.population&&row?.observation_period===study?.observation_period&&row?.conditioning===study?.conditioning&&row?.source_url===study?.source_url&&typeof row?.public_locator==='string'&&row.public_locator.length>0,'elasticity estimate study/source/population lineage lost: '+spec.id);
  check(row?.se===null&&row.ci===null&&(row.reported_t===null||Number.isFinite(row.reported_t))&&[null,'*','**','***'].includes(row.reported_mark)&&(spec.study_id===elStudyIds[0]||spec.study_id===elStudyIds[1]||row.reported_t===null),'elasticity missing uncertainty promoted or t-statistic repurposed: '+spec.id);
  check(row?.category_transport===null&&row.forecast_value===null&&row.review_status==='human_review_pending','elasticity estimate promoted to target parameter or human approval: '+spec.id);
  check(claims.some(c=>elClaims.includes(c.id)&&[...(c.estimate_ids||[]),...(c.supporting_estimate_ids||[])].includes(spec.id)&&c.source_ids?.includes(study?.source_id)&&c.review_id==='R7-ELASTICITY'&&reviewCovers(c.review_id,[c.id])),'elasticity estimate claim/review lineage lost: '+spec.id);
 }
 const elSlotSpecs=[
  [elStudyIds[0],'chicken','reported_estimates_with_method_hold'],[elStudyIds[0],indGoods[1],'category_mismatch'],[elStudyIds[0],indGoods[0],'category_mismatch'],
  [elStudyIds[1],'chicken','reported_estimates_with_method_hold'],[elStudyIds[1],pakGoods[0],'category_definition_hold'],[elStudyIds[1],pakGoods[1],'category_definition_hold'],
  [elStudyIds[3],'chicken','conditional_compensated_only'],[elStudyIds[3],'beef','conditional_compensated_only'],[elStudyIds[3],'lamb','category_mismatch'],
  [elStudyIds[4],'chicken','hold_internal_consistency'],[elStudyIds[4],'beef','hold_internal_consistency'],[elStudyIds[4],'lamb','category_mismatch_and_consistency_hold']
 ];
 for(const [i,requirement] of elExpectedSlots.entries()){
  const slot=elSlots.find(r=>r.requirement_id===requirement),[studyId,good,status]=elSlotSpecs[i],study=elStudy(studyId),primaryClaim=claims.find(c=>c.id===elClaims[i]);
  const entries=elRows.filter(e=>e.study_id===studyId&&e.good===good),own=entries.filter(e=>e.estimand?.startsWith('own_price'));
  const expectedClaims=[elClaims[i],...(requirement.startsWith('EL-PAK-')?[elClaims[12]]:[])],expectedSources=[study?.source_id,...(requirement.startsWith('EL-PAK-')?['P1C7-EL-PAK-HAYAT-2023']:[])];
  check(slot?.country===requirement.split('-')[1]&&slot.requested_good===requirement.split('-')[2].toLowerCase()&&slot.primary_study_id===studyId&&slot.reported_source_category===good&&slot.status===status,'elasticity slot species/category/disposition changed: '+requirement);
  check(artifactLineage(slot,slot?.country)&&sameMembers(slot?.source_ids,expectedSources)&&sameMembers(slot?.claim_ids,expectedClaims)&&slot?.review_id==='R7-ELASTICITY'&&reviewCovers(slot.review_id,expectedClaims)&&expectedClaims.every(id=>claims.find(c=>c.id===id)?.requirement_ids?.includes(requirement)),'elasticity slot source/claim/review lineage lost: '+requirement);
  check(sameMembers(slot?.study_estimate_ids,entries.map(e=>e.id))&&sameMembers(primaryClaim?.estimate_ids,entries.map(e=>e.id))&&sameMembers(primaryClaim?.requirement_ids,[requirement])&&sameMembers(slot?.cross_price_evidence_ids,entries.filter(e=>e.estimand==='cross_price').map(e=>e.id))&&sameMembers(slot?.expenditure_evidence_ids,entries.filter(e=>e.estimand==='expenditure').map(e=>e.id)),'elasticity slot estimate/estimand partition lost: '+requirement);
  check(sameMembers(slot?.own_price_evidence?.map(e=>e.estimate_id),own.map(e=>e.id))&&(slot?.own_price_evidence||[]).every(e=>{const original=elRow(e.estimate_id);return original&&['value','sample','compensation','reported_t','reported_mark','se','ci'].every(k=>e[k]===original[k]);}),'elasticity own-price summary differs from study evidence: '+requirement);
  check(['observation_period','population','method','compensation','conditioning','source_url'].every(k=>slot?.[k]===study?.[k])&&slot?.review_status==='human_review_pending'&&['forecast_parameter','forecast_cross_parameters','transport_justification','independent_corroborating_family'].every(k=>slot?.[k]===null)&&typeof slot?.reopening_trigger==='string'&&slot.reopening_trigger.length>0,'elasticity slot population/forecast/review boundary lost: '+requirement);
 }
 const goatIds=elRows.filter(e=>e.study_id===elStudyIds[4]&&e.good==='goat').map(e=>e.id),hayatIds=elRows.filter(e=>e.study_id===elStudyIds[2]).map(e=>e.id);
 check(sameMembers(claims.find(c=>c.id==='R07-EL-C12')?.supporting_estimate_ids,goatIds)&&!elSlots.find(r=>r.requirement_id==='EL-ARE-MUTTON')?.study_estimate_ids?.some(id=>goatIds.includes(id))&&sameMembers(claims.find(c=>c.id==='R07-EL-C13')?.estimate_ids,hayatIds)&&sameMembers(claims.find(c=>c.id==='R07-EL-C13')?.requirement_ids,elExpectedSlots.filter(id=>id.startsWith('EL-PAK-'))),'elasticity goat/aggregate supporting evidence promoted or orphaned');
 for(const [id,value] of Object.entries({'EST-020':-.432,'EST-044':-.328,'EST-087':-.859,'EST-092':-.807,'EST-103':-.204,'EST-104':.033,'EST-107':.011,'EST-108':-.088,'EST-118':.666,'EST-139':-.319,'EST-142':.568,'EST-163':-.531,'EST-166':.804,'EST-169':.690,'EST-173':-.12486,'EST-181':.090241})){check(elRow(id)?.value===value,'elasticity checked directional/sign anchor changed: '+id);}
 const excluded=Array.isArray(elasticity?.excluded_studies)?elasticity.excluded_studies:[],excludedIds=['USDA-ICP','PAK-MEMON-2012','SAU-ALMAHISH-2020','SAU-KOTB-2026'];
 check(sameMembers(excluded.map(s=>s.id),excludedIds),'elasticity held-study roster lost');
 for(const [i,id] of excludedIds.entries()){
  const study=excluded.find(s=>s.id===id);
  check(study?.source_id==='P1C7-EL-'+id&&sourceIds.has(study.source_id)&&study.coefficient===null&&study.review_status==='human_review_pending'&&study.disposition===['category_mismatch','hold_internal_table_label_conflict','exclude_estimand_mismatch','exclude_category_mismatch'][i]&&typeof study.reopen==='string'&&study.reopen.length>0&&!elRows.some(e=>e.study_id===id),'elasticity held inverse/aggregate study promoted: '+id);
 }
 const csvColumns=['id','study_id','country','population','observation_period','good','with_respect_to','estimand','value','unit','se','ci','reported_t','reported_mark','reported_significance','compensation','conditioning','sample','source_url','public_locator','forecast_value','review_status'];
 let elCsv=[];try{elCsv=parseCsv(files['elasticity-estimates.csv']||'');}catch{check(false,'elasticity CSV is invalid');}
 check(JSON.stringify(elCsv[0])===JSON.stringify(csvColumns)&&elCsv.length===187,'elasticity CSV header/count differs from JSON');
 for(const [i,cells] of elCsv.slice(1).entries())check(cells.length===csvColumns.length&&csvColumns.every((key,j)=>cells[j]===(elRows[i]?.[key]===null?'':String(elRows[i]?.[key]))),'elasticity CSV row differs from JSON or null semantics: '+(i+2));
 const feedCountries=Array.isArray(feed?.countries)?feed.countries:[],feedCountry=id=>feedCountries.find(c=>c.country===id);
 check(sameMembers(feedCountries.map(c=>c.country),focalCountries)&&sameMembers(feedCountries.map(c=>c.requirement_id),focalCountries.map(id=>'FEED-'+id)),'feed four-country roster lost');
 check(feed?.human_review==='pending'&&feed.full_phase_one_complete===false&&feed.human_protein_accounting_eligible===false&&sameMembers(feed.review_ids,['R7-FEED-ECONOMICS','R7-FEED-SCHOOLS-ETHNOGRAPHY']),'feed input promoted to human protein, completion or approval');
 const feedSources={IND:['R7-FEED-S01','R7-FEED-S02','R7-FEED-S03','R7-FEED-S04'],PAK:['R7-FEED-S05','R7-FEED-S06','R7-FEED-S11'],SAU:['R7-FEED-S07','R7-FEED-S08'],ARE:['R7-FEED-S09','R7-FEED-S10','R7-FEED-S12']};
 const feedClaims={IND:['R7-FEED-C01','R7-FEED-C02','R7-FEED-C03'],PAK:['R7-FEED-C04','R7-FEED-C05','R7-FEED-C06'],SAU:['R7-FEED-C07','R7-FEED-C08'],ARE:['R7-FEED-C09','R7-FEED-C10','R7-FEED-C11']};
 for(const c of feedCountries){
  check(c.requirement_id==='FEED-'+c.country&&artifactLineage(c,c.country)&&sameMembers(c.source_ids,feedSources[c.country]||[])&&sameMembers(c.claim_ids,feedClaims[c.country]||[])&&c.review_id==='R7-FEED-ECONOMICS'&&reviewCovers(c.review_id,c.claim_ids||[]),'feed country source/claim/review lineage lost: '+c.country);
  check(['market_value','market_currency','market_year','market_volume','market_volume_unit','market_observation_period','industry_chicken_cost_effect','forecast_parameter'].every(k=>c[k]===null)&&c.market_activity?.observed_sales_value===null,'feed unmeasured market/cost/forecast zero-filled or invented: '+c.country);
  check(c.human_review==='pending'&&c.final_requirement_completion===false&&typeof c.market_reopening_trigger==='string'&&c.market_reopening_trigger.length>0&&Array.isArray(c.reopen)&&c.reopen.length>0&&!!c.cost_assessment?.causal_scope,'feed country review or reopening boundary lost: '+c.country);
  if(c.trial)check(c.source_ids?.includes(c.trial.source_id)&&c.trial.experiment_dates===null&&['diet_cost','feed_cost_per_kg_gain','measured_fcr_values'].every(k=>c.trial[k]===null),'feed biological trial promoted to monetary cost or invented observation date: '+c.country);
 }
 const indiaTrial=feedCountry('IND')?.trial,pakTrial=feedCountry('PAK')?.trial,saudiTrial=feedCountry('SAU')?.trial;
 check(JSON.stringify(indiaTrial?.diet_inclusion_percent)===JSON.stringify([[0,2.5,5],[0,5,7.5,10]])&&indiaTrial?.soybean_replacement_percent===null,'India diet inclusion confused with soybean replacement');
 check(pakTrial?.n===150&&JSON.stringify(pakTrial.inclusion_g_per_kg_feed)===JSON.stringify([0,.5,1,1.5,2])&&pakTrial.net_profit_effect===null&&pakTrial.site===null&&pakTrial.soybean_replacement_percent===null&&feedCountry('PAK')?.market_activity?.quantity===400&&feedCountry('PAK').market_activity.unit==='kg mealworm meal during project'&&feedCountry('PAK').market_activity.annualized_quantity===null,'Pakistan supplement units, project period or cost effect promoted');
 check(saudiTrial?.n===360&&saudiTrial.site===null&&JSON.stringify(saudiTrial.treatment_period_days)===JSON.stringify([22,35])&&JSON.stringify(saudiTrial.soybean_replacement_percent)===JSON.stringify([0,10,20,30,40,50])&&JSON.stringify(saudiTrial.bsfl_g_per_kg_diet)===JSON.stringify([0,30,60,90,120,150])&&saudiTrial.bsfl_g_per_kg_diet[3]===90,'Saudi soybean replacement confused with whole-diet inclusion or trial site');
 check(saudiTrial?.diet_basis==='as-fed complete diet; Table 3 Ingredients per kg as fed','Saudi complete-diet as-fed basis lost');
 const saudiActivity=feedCountry('SAU')?.market_activity,uaeActivity=feedCountry('ARE')?.market_activity,uaeRecords=Array.isArray(uaeActivity?.records)?uaeActivity.records:[];
 check(saudiActivity?.actual_production===null&&saudiActivity.claimed_timeline?.find(t=>t.year===2026)?.state==='industrial facilities will launch'&&saudiActivity.advertised_design?.[0]?.input_value===1000000&&saudiActivity.advertised_design[0].output_value===200000&&saudiActivity.advertised_design[0].output_relation==='over'&&saudiActivity.advertised_design[0].status==='company system-design claim; deployment/actual production unverified','Saudi advertised design/timeline promoted to actual production');
 const uaeExpected=[['R7-FEED-S09',1200,'tons/year as stated','company-labelled insect protein produced annually','reported company annual-output wording; reporting period, measured utilization and mass basis unverified'],['R7-FEED-S09',6000,'tons/year as stated','food waste diverted annually','company waste-input/diversion claim; not feed-market volume'],['R7-FEED-S10',22000,'tonnes/year','planned full industrial-scale animal feed','future plan; not actual output'],['R7-FEED-S10',1.5,'tonnes/month','initial organic fertilizer','launch wording; excluded from insect-meal market']];
 check(uaeRecords.length===4&&uaeActivity?.national_aggregation_eligible===false&&uaeExpected.every(([source,value,unit,metric,status],i)=>{const r=uaeRecords[i];return r?.source_id===source&&r.value===value&&r.unit===unit&&r.metric===metric&&r.status===status&&r.year===null;}),'UAE participant output, waste, future plan or fertilizer conflated');
 const feedSchools=Array.isArray(feed?.schools)?feed.schools:[],schoolNames=['Hanafi','Maliki','Shafii','Hanbali','Jafari'];
 check(sameMembers(feedSchools.map(s=>s.school),schoolNames),'feed five-school route coverage lost');
 const schoolRefs={Hanafi:[['R7-F-ASK125569'],['R7-CO-HANAFI']],Maliki:[[],[]],Shafii:[['R7-F-JOR4015','R7-F-MAJMU-JALLALA'],['R7-CO-JOR','R7-CO-SHAFII']],Hanbali:[['R7-F-MUGHNI7800'],['R7-CO-HANBALI']],Jafari:[['P1C6-REL-ISTIBRA219','J6'],['R7-CO-JAFARI']]};
 for(const school of feedSchools){
  const refs=schoolRefs[school.school]||[[],[]];
  check(school.requirement_id==='FEED-SCHOOLS'&&sameMembers(school.source_ids,refs[0])&&sameMembers(school.claim_ids,refs[1])&&(school.school==='Maliki'||artifactLineage(school,null)&&reviewCovers('R7-FEED-SCHOOLS-ETHNOGRAPHY',school.claim_ids||[])&&school.claim_ids.every(id=>claims.find(c=>c.id===id)?.review_id==='R7-FEED-SCHOOLS-ETHNOGRAPHY')),'feed school source/claim/review lineage lost: '+school.school);
  check(school.human_review==='pending'&&school.school_consensus_established===false&&school.automatic_human_food_rule_transfer===false&&school.product_certificate===null&&Array.isArray(school.unknowns)&&school.unknowns.length>0&&typeof school.reopen==='string'&&school.reopen.length>0,'feed named authority promoted to consensus, human-food transfer or certificate: '+school.school);
 }
 const maliki=feedSchools.find(s=>s.school==='Maliki'),ethnography=feed?.ethnography;
 check(maliki?.status==='bounded_unresolved_primary_text_gap'&&sameMembers(maliki.held_source_ids,['R7-F-EGY1983-LEAD'])&&sourceIds.has('R7-F-EGY1983-LEAD')&&!claims.some(c=>c.source_ids?.includes('R7-F-EGY1983-LEAD')),'feed held Maliki attribution promoted to adopted rule');
 check(ethnography?.requirement_id==='INSECTS-SOUTH-ASIA'&&artifactLineage(ethnography,null)&&sameMembers(ethnography.source_ids,['R7-F-ETH2011','R7-F-ETH2013'])&&sameMembers(ethnography.claim_ids,['R7-CO-ETH2011','R7-CO-ETH2013'])&&reviewCovers('R7-FEED-SCHOOLS-ETHNOGRAPHY',ethnography.claim_ids),'feed ethnography source/claim/review lineage lost');
 check(ethnography?.paragraph_count===1&&typeof ethnography.paragraph==='string'&&ethnography.paragraph.trim().length>0&&ethnography.paragraph.trim().split(/\n\s*\n/).length===1&&ethnography.publication_year_is_observation_year===false&&ethnography.representative_population_prevalence===null&&ethnography.human_protein_total===null&&ethnography.clinical_efficacy_established===false&&ethnography.human_review==='pending','feed ethnography paragraph or population/clinical/protein boundary lost');

 // Gate table (2 October): evidence readings for the focal countries, never scenario gate values.
 check(files['gate-table.json']!==undefined,'gate table missing');
 if(files['gate-table.json']!==undefined){
  let gate=null;try{gate=JSON.parse(files['gate-table.json']);}catch{check(false,'gate table is invalid JSON');}
  check(gate!==null&&typeof gate==='object'&&!Array.isArray(gate),'gate table must be an object');
  if(gate){
   const religiousReadings=['supported_conditional','disputed','leans_closed','conditions_not_met','unresolved','no_institutional_text_located'];
   const layerReadings={certification:['general_route_no_cultivated_scheme','contested_domestic_route','no_route_identified','unverified'],food_authorization:['route_exists_no_approval','application_pending','route_announced_status_unknown','no_route_identified','unverified'],segment:['whole_market_gate','segment_gate','unverified']};
   // Both favorable and adverse conclusions need direct evidence. A general inference
   // or a checked statement that merely reports a source's existence cannot supply it.
   const substantive=['supported_conditional','disputed','leans_closed','conditions_not_met','route_exists_no_approval','application_pending','general_route_no_cultivated_scheme','contested_domestic_route','route_announced_status_unknown','whole_market_gate','segment_gate'];
   const profileIds=['P1','P2','P3','P4','P5','P6'];
   const profileIdentity={
    P1:['embryo_fibroblast','serum_present',['P1C3-PROCESS-S01','P1C3-PROCESS-S03']],
    P2:['unresolved_version_match','serum_free_formula_unresolved',['P1C3-PROCESS-S06','P1C3-PROCESS-S07']],
    P3:['embryonic_stem','animal_component_free_reported',['SG-LIST']],
    P4:['slaughtered_donor','permitted_inputs_hypothetical',['IIFA265','P1C5-INST-GOODMEAT']],
    P5:['live_adult_biopsy','permitted_inputs_hypothetical',['IIFA265']],
    P6:['feather_induced_pluripotent','permitted_inputs_hypothetical',['P1C8-S07']]
   };
   const profiles=Array.isArray(gate.process_profiles)?gate.process_profiles:[];
   const countries=Array.isArray(gate.countries)?gate.countries:[];
   const nonempty=value=>typeof value==='string'&&value.trim().length>0;
   const distinctList=(value,allowed,allowEmpty=false)=>Array.isArray(value)&&(allowEmpty||value.length>0)&&new Set(value).size===value.length&&value.every(id=>allowed.includes(id));
   const layers=['religious',...Object.keys(layerReadings)];
   const authorityIds=['GOOD-MEAT-ADVISERS','IIFA','SFDA','UAE-COUNCIL-FATWA','MUFTI-TAQI-USMANI-REPORTED-PANEL','BANURI-TOWN','MOIAT','ADAFSA','UAE-CODEX-DELEGATION','PSQCA','PUNJAB-FOOD-AUTHORITY','FSSAI','DGFT','UTTAR-PRADESH-GOVERNMENT','BUSINESS-STANDARD'];
   const allReadings=[...religiousReadings,...Object.values(layerReadings).flat()];
   const checkedClaim=claim=>['independently_checked','confirmed_original'].includes(claim?.status)&&reviews.some(r=>r.id===claim.review_id&&r.claim_ids?.includes(claim.id));
   check(gate.human_review==='pending'&&gate.profiles===undefined&&sameMembers(profiles.map(p=>p?.id),profileIds),'gate table review status or profiles invalid');
   for(const profile of profiles){
    check(['label','founder_cells','medium','documented_in','locator'].every(key=>nonempty(profile?.[key]))&&profile.real_product===['P1','P2','P3'].includes(profile.id),'gate profile identity or locator missing: '+profile?.id);
    check(Array.isArray(profile?.source_ids)&&profile.source_ids.length>0&&new Set(profile.source_ids).size===profile.source_ids.length&&profile.source_ids.every(id=>sourceIds.has(id)),'gate profile source provenance invalid: '+profile?.id);
    const identity=profileIdentity[profile?.id];
    check(identity&&profile.founder_route===identity[0]&&profile.medium_status===identity[1]&&sameMembers(profile.source_ids,identity[2]),'gate profile process version/source identity changed: '+profile?.id);
   }
   check(sameMembers(countries.map(c=>c?.id),['IND','PAK','SAU','ARE']),'gate table focal-country roster changed');
   const checkCell=(country,layer,cell,allowed)=>{
    const where=country+'/'+(layer==='religious'?cell?.profile:layer);
    const basis=Array.isArray(cell?.basis_claim_ids)?cell.basis_claim_ids:null;
    const basisClaims=(basis||[]).map(id=>claims.find(c=>c.id===id));
    const authorities=Array.isArray(cell?.authority_ids)?cell.authority_ids:[];
    check(allowed.includes(cell?.reading)&&['low','medium','high'].includes(cell?.confidence)&&nonempty(cell?.decisive_next)&&!!gate.reading_labels?.[cell?.reading],'gate cell reading, confidence or next document invalid: '+where);
    check(basis!==null&&new Set(basis).size===basis.length&&basis.every(id=>claimIds.has(id)),'gate cell basis does not resolve: '+where);
    check(distinctList(cell?.authority_ids,authorityIds,true)&&((basis?.length||0)===0?authorities.length===0:authorities.length>0)&&authorities.every(id=>basisClaims.some(claim=>claim?.gate_scope?.authority_ids?.includes(id))),'gate cell authority does not resolve: '+where);
    const applicable=basisClaims.map(claim=>{
     if(!claim)return false;
     const scope=claim.gate_scope;
     const valid=scope&&distinctList(scope.country_ids,focalCountries)&&distinctList(scope.layers,layers)&&distinctList(scope.profile_ids,profileIds,!scope.layers?.includes('religious'))&&(!scope.layers?.includes('religious')?scope.profile_ids?.length===0:true)&&distinctList(scope.authority_ids,authorityIds)&&['direct','context','inference'].includes(scope.evidence_role)&&distinctList(scope.supported_readings,allReadings,scope.evidence_role!=='direct')&&(scope.evidence_role==='direct'?claim.status!=='inference':scope.supported_readings?.length===0)&&(claim.status!=='inference'||scope.evidence_role==='inference');
     check(valid,'gate claim scope invalid: '+claim.id);
     const countryMatch=valid&&scope.country_ids.includes(country)&&(claim.country===null||claim.country===country);
     const layerMatch=valid&&scope.layers.includes(layer);
     const profileMatch=valid&&(layer!=='religious'||scope.profile_ids.includes(cell?.profile));
     const authorityMatch=valid&&scope.authority_ids.some(id=>authorities.includes(id));
     check(countryMatch,'gate claim country mismatch: '+where+'/'+claim.id);
     check(layerMatch,'gate claim layer mismatch: '+where+'/'+claim.id);
     check(profileMatch,'gate claim profile mismatch: '+where+'/'+claim.id);
     check(authorityMatch,'gate claim authority mismatch: '+where+'/'+claim.id);
     return countryMatch&&layerMatch&&profileMatch&&authorityMatch;
    });
    const directClaims=basisClaims.filter((claim,i)=>applicable[i]&&checkedClaim(claim)&&claim.gate_scope.evidence_role==='direct'&&claim.gate_scope.supported_readings.includes(cell?.reading));
    const directSupport=directClaims.length>0&&authorities.length>0&&authorities.every(id=>directClaims.some(claim=>claim.gate_scope.authority_ids.includes(id)));
    check(!substantive.includes(cell?.reading)||directSupport,'gate cell positive reading rests only on unchecked leads: '+where);
    check(cell?.confidence!=='high'||(basisClaims.length>0&&directSupport&&applicable.every(Boolean)&&basisClaims.every(checkedClaim)),'gate cell high confidence without checked basis: '+where);
   };
   for(const country of countries){
    const religious=Array.isArray(country?.religious)?country.religious:[];
    check(sameMembers(religious.map(c=>c?.profile),profileIds),'gate table religious profiles incomplete: '+country?.id);
    for(const cell of religious)checkCell(country?.id,'religious',cell,religiousReadings);
    for(const [layer,allowed] of Object.entries(layerReadings))checkCell(country?.id,layer,country?.[layer],allowed);
    check(nonempty(country?.summary),'gate table country summary missing: '+country?.id);
   }
  }
 }
 return {checks,failures};
}
