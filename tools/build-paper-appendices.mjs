/** Build source-bounded appendix candidates; never change manuscript or coverage. */
import fs from 'node:fs';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {checkPaper} from './paper-checks.mjs';
import {bibliographyEntry, citedSourceKeys, normalizeCitation} from './paper-bibliography.mjs';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const base='research/halal-cultivated/',paper=base+'paper/';
const inputNames=[base+'phase1/school-questions.json',base+'phase1/country-findings.json',base+'phase1/claims.json',paper+'source-register.json',paper+'citation-audit.json',paper+'claims-added.json'];
const inputs=new Map(inputNames.map(name=>[name,fs.readFileSync(path.join(root,name),'utf8')]));
const load=name=>JSON.parse(inputs.get(name));
const schools=load(inputNames[0]),countries=load(inputNames[1]),originalClaims=load(inputNames[2]);
const sources=load(inputNames[3]),audits=load(inputNames[4]),added=load(inputNames[5]);
const byKey=new Map(sources.map(s=>[s.key,s])),auditByKey=new Map(audits.map(a=>[a.key,a]));
const alias=new Map(sources.flatMap(s=>[s.key,...s.aliases].map(k=>[k,s.key])));
const claims=new Map([...originalClaims,...added].map(c=>[c.id,c]));
const qualified=new Set(['verified','verified_with_note']),supported=new Set(['supported','premise_supported']);
const assert=(condition,message)=>{if(!condition)throw Error(message);};
assert(schools.length===45&&new Set(schools.map(s=>s.id)).size===45,'Expected 45 distinct school slots.');
assert(countries.length===7&&new Set(countries.map(c=>c.id)).size===7,'Expected seven distinct country records.');
assert(sources.length===95&&audits.length===sources.length,'Source inventory changed; review the appendix scope.');
assert(new Set(sources.map(s=>s.key)).size===sources.length,'Duplicate canonical source.');
for(const s of sources)assert(auditByKey.get(s.key)?.verdict===s.audit_verdict,'Audit/register disagreement: '+s.key);

const questions=[
 'Who decides tayyib and khabith?',
 'Is the four-item prohibition formula exhaustive?',
 'Carcasses and parts detached from living animals',
 'Flowing blood, liver and spleen',
 'Invocation: omission and forgetting',
 'Transformation and its limits',
 'Serum, enzymes, gelatin and other inputs',
 'Aquatic animals and slaughter',
 'Living cells and the limits of analogy',
];
const order=['HN','M','S','HB','J'];
const labels={HN:'Hanafi sources',M:'Maliki sources',S:'Shafii sources',HB:'Hanbali sources',J:'Sistani: a named Jafari authority'};
const statusLabel={blind_agent_checked:'Agent-checked historical finding',inference:'Historical inference',open:'Open question'};
const answers={
 'HN-Q3':{text:'Ibn Abidin distinguishes a part severed from a living animal from a part removed after effective slaughter.',keys:['HAN-D']},
 'HN-Q4':{claim:'P-H-BLOOD-DISTINCTIONS',text:'The reviewed Radd al-Muhtar passage distinguishes flowing from retained or non-flowing blood, with further qualifications concerning origin and circumstance.',keys:['H5'],gap:'Only the narrower blood distinction is admitted; the original organ-specific component is not repeated.'},
 'HN-Q6':{text:'Ibn Abidin presents complete change of substance as purifying in the selected view and records Abu Yusuf’s disagreement.',keys:['HAN']},
 'HN-Q7':{text:'Inference: transformation and the recorded rennet disagreement suggest separate source and process inquiries; neither passage supplies an industrial-serum or gelatin ruling.',keys:['HAN','H6']},
 'HN-Q9':{text:'Inference: assess donor removal and any later change of substance separately; applying the detached-part rule to cultured descendants requires a further argument.',keys:['HAN-D','HAN']},
 'M-Q1':{text:'Al-Qurtubi attributes a legal-permission reading of tayyibat to Malik; personal repulsion alone does not create prohibition in that account. Ibn Rushd describes a competing reading.',keys:['M-QUR7157','M-BID-Q1']},
 'M-Q3':{text:'Al-Dardir/al-Dasuqi classify specified parts detached from a living animal whose carcass is impure as impure; flesh, sinews and veins are included.',keys:['M-DAS30']},
 'M-Q4':{text:'Al-Qarafi distinguishes flowing from non-flowing blood, with the latter pure on the sounder view; al-Dardir explains the retained-blood case after lawful slaughter.',keys:['M-DHAK','M-DAS28'],gap:'A Maliki passage naming the liver and spleen exception remains unverified; the held food-book component adds no support.'},
 'M-Q6':{text:'Al-Qarafi distinguishes complete loss of impurity-defining qualities from partial change and records disagreement over ash. Al-Dardir/al-Dasuqi list vinegar conversion and musk.',keys:['M-DHAK','M-DAS28']},
 'M-Q7':{text:'Inference: al-Qarafi’s discussion of meat cooked in impure water supports examining contact, removal and surviving material; it does not decide industrial inputs.',keys:['M-DHAK']},
 'M-Q8':{text:'The admitted al-Dardir passage treats marine carcasses as pure. This is only the purity component of the original wider question.',keys:['M-DAS28'],gap:'The wider marine-edibility account depends on held or unretrieved texts and is not asserted.'},
 'M-Q9':{text:'Inference: detached-tissue and transformation premises raise distinct questions about donor material and later biomass; the admitted passages do not decide viable cell lines.',keys:['M-DAS30','M-DHAK']},
 'HB-Q3':{text:'Ibn Qudama treats excision during stable life as carrion and distinguishes separation after effective slaughter.',keys:['H-MUGH-PARTS']},
 'HB-Q4':{text:'Ibn Qudama invokes the liver-and-spleen permission report in a discussion of the word meat in oaths.',keys:['H-MUGH-LIVER'],gap:'This is not a complete blood taxonomy; the al-Insaf component remains held.'},
 'HB-Q6':{text:'The admitted al-Mughni passage rejects general purification of intrinsically impure substances through transformation.',keys:['H-MUGH-IST'],gap:'The planned contrasting positions remain held, so this entry is limited to the admitted author passage.'},
 'HB-Q7':{text:'Inference: al-Mughni’s carrion-milk and rennet discussion records impurity and purity alternatives; a modern ingredient analogy must establish source and process similarity.',keys:['H-MUGH-RENNET']},
 'HB-Q9':{text:'Inference: the stable-life excision rule supplies a procurement premise, without deciding the classification of cultured cells or their descendants.',keys:['H-MUGH-PARTS']},
 'J-Q2':{text:'Inference: Sistani’s additional prohibitions on birds and animal parts show that the four-item formula is not the complete operative list in the cited manual.',keys:['J6']},
 'J-Q3':{text:'Sistani distinguishes impure carcasses and life-containing detached parts from specified legally lifeless parts, including wool and bone.',keys:['J2']},
 'J-Q4':{text:'Sistani distinguishes gush-blood animal blood from blood retained under stated slaughter and drainage conditions. For land animals, spleen is prohibited; listed bird organs beyond blood and droppings carry obligatory precaution.',keys:['J3','J6']},
 'J-Q5':{text:'Sistani requires invocation by the slaughterer, excuses forgetting and treats omission through ignorance as disqualifying.',keys:['J5']},
 'J-Q6':{text:'Sistani requires transformation of essence into a new pure thing; grinding or baking alone does not suffice, and doubt leaves impurity.',keys:['SIS-EN']},
 'J-Q7':{claim:'P-J-GELATIN',text:'Sistani’s gelatin answers distinguish uncertain source, known animal origin, slaughter, limited minute absorption and established transformation. The Arabic answers do not assume manufacturing transformation is established.',keys:['J8','J9'],gap:'Only the narrower gelatin claim is used here. Related rennet and heat rules do not establish gelatin conditions or every serum/enzyme process.'},
 'J-Q8':{text:'Sistani’s scaled-fish rules require the stated capture conditions, distinguish death in water and retain a net-capture exception.',keys:['J7']},
 'J-Q9':{text:'Inference: donor species, detachment and later transformation require separate analysis; the cited rules do not themselves decide cultivated cells.',keys:['J2','SIS-EN','J7']},
};

const escapeCell=text=>String(text??'Not established').replaceAll('|','&#124;').replace(/\s+/g,' ').trim();
const trace=(ids,kind)=>`<!-- trace: ${[...new Set(ids)].join(' ')} | kind: ${kind} -->`;
const sourceName=key=>{const s=byKey.get(alias.get(key)??key);return s?.bibliographic?.title??s?.title??key;};
const notes=new Map();
function component(id,keys,text,dimension=null){
 const claim=claims.get(id);assert(claim,'Unknown claim '+id);
 for(const key of keys){
  const s=byKey.get(key),a=auditByKey.get(key);
  assert(s&&qualified.has(s.audit_verdict)&&qualified.has(a?.verdict),'Unqualified source '+key);
  assert(claim.source_ids.some(k=>alias.get(k)===key),'Source outside claim '+id+' / '+key);
  assert(supported.has(a.claims_rechecked.find(r=>r.id===id)?.result),'Unsupported claim-source pair '+id+' / '+key);
 }
 return {claim_id:id,kind:claim.kind,source_keys:keys,text,dimension,locators:keys.map(key=>({key,locator:auditByKey.get(key).claims_rechecked.find(r=>r.id===id).locator??byKey.get(key).locator}))};
}
function footnote(item){
 const name='abd-'+String(notes.size+1).padStart(2,'0');
 const entries=item.locators.map(({key,locator})=>{const s=byKey.get(key),b=s.bibliographic;return b.author.replaceAll(';', ',')+', *'+b.title+'* ('+(b.year??'n.d.')+'), '+locator+'.';});
 notes.set(name,normalizeCitation(entries.join(' '))+' '+item.source_keys.map(key=>'['+key+']').join(' '));
 return '[^'+name+']';
}
function originalSourceStates(row){return row.source_ids.map(id=>{
 const key=alias.get(id),audit=auditByKey.get(key);
 return {original_source_id:id,canonical_key:key,verdict:audit.verdict,recheck:audit.claims_rechecked.find(x=>x.id===row.id)?.result??null};
});}
function gapText(states){
 const missing=states.filter(s=>!qualified.has(s.verdict)||!supported.has(s.recheck));
 if(!missing.length)return 'No additional source hold for this bounded answer; modern application remains a separate inference.';
 return [...new Set(missing.map(s=>sourceName(s.canonical_key)+': '+(s.verdict==='held'?'held from substantive citation':s.verdict==='not_retrieved'?'passage not retrieved':'original compound claim only partly supported')))].join('; ')+'.';
}
const schoolRows=order.flatMap(prefix=>schools.filter(q=>q.id.startsWith(prefix+'-')).sort((a,b)=>Number(a.id.split('Q')[1])-Number(b.id.split('Q')[1])).map(q=>{
 const answer=answers[q.id],states=originalSourceStates(q);
 const admitted=answer?component(answer.claim??q.id,answer.keys,answer.text):null;
 const open=q.id==='J-Q1';
 const gap=open?'Open: the specific customary-repugnance decision rule was not located. General taqlid and impurity rules are background, not an answer.':answer?.gap??gapText(states);
 return {original_id:q.id,tradition:labels[prefix],question_number:Number(q.id.split('Q')[1]),question:questions[Number(q.id.split('Q')[1])-1],historical_status:q.status,historical_kind:q.kind,current_admission:open?'open':!admitted?'not_admitted':answer.claim?'atomic_replacement':states.some(s=>!qualified.has(s.verdict)||!supported.has(s.recheck))?'partial':'bounded',admitted,gap,source_states:states,coverage_recommendation:{id:q.id,kinds:['claim','school'],disposition:admitted?.claim_id===q.id||open?'included':'excluded',reason:open?'Explicitly open in Appendix A.':admitted?.claim_id===q.id?'Only the stated, cited components appear in Appendix A; remaining components stay gaps.':answer?.claim?'Original compound finding is not reasserted; the narrower '+answer.claim+' supplies the admitted answer.':'Historical slot retained in the appendix inventory; no substantive assertion admitted because its required passages are held or unretrieved.'}};
}));

const countrySpecs={
 'C-IN':{components:[['Food authorization','P-IN-APPROVAL',['IN2017'],'The 2022 compendium of the 2017 rules requires prior FSSAI approval before manufacture or import, followed by a separate licence. Form I includes novel foods and technologies.'],['Geography context','P-GEO-SOUTHASIA-CLAIM',['P-GEO-SOUTHASIA'],'Kirmani and Zaidi’s 2010 Pakistan study describes Barelvi and Deobandi Hanafi currents in South Asia; this is dated regional background.']],gap:'A current India-specific predominance account, a cultivated-chicken product decision and matching halal certificate were not established in this corpus.',question:'Which current FSSAI decision covers the named product and process, and which authority or certifier accepts that same dossier?',document:'Current product decision, applicable licence, process-matched religious position and certificate.'},
 'C-PK':{components:[['Halal mechanism','P-PK-HALAL-REMIT',['PK2016'],'The 2016 Act assigns standards, accreditation, certification and logo functions, with nationwide international/interprovincial trade scope and distinct Islamabad purposes.'],['Authority context','P-GEO-PKCONST-CLAIM',['P-GEO-PKCONST'],'The reviewed 2025 Constitution preserves sect-specific personal-law interpretation, different-school representation and the Council of Islamic Ideology’s advisory functions.'],['Geography context','P-GEO-SOUTHASIA-CLAIM',['P-GEO-SOUTHASIA'],'The 2010 Karachi/Sindh study supplies regional Hanafi-current context, without a current population estimate.']],gap:'The cultivated-food pathway, provincial responsibilities, operative commencement notifications and a named product certificate/decision remain unresolved.',question:'Which federal or provincial body has jurisdiction over this product and transaction, and what separate halal decision is required?',document:'Applicable food instrument and classification, commencement notices, product authorization and scope-matched certificate.'},
 'C-SA':{components:[['Novel-food requirements','P-SA-NOVEL-SCOPE',['SA-NOVEL'],'The retrieved English requirements cover animal cell/tissue culture, prior marketing approval, halal sources and production/safety information; the cover reads 513/2020.'],['Application guide','P-SA-GUIDE',['SA-GUIDE'],'The undated English guide requests production, safety and exposure information and refers to 5031:2020; Arabic prevails.'],['Administrative announcement','P-SA-ANNOUNCEMENT',['SA-2025'],'The 22 December 2025 announcement names 5013, a dedicated guideline and the SFDA Platform.'],['Authority context','P-GEO-SA-BASIC-CLAIM',['P-GEO-SA-BASIC'],'Articles 1 and 45 of the reviewed Basic Law text identify the Quran and Sunnah and religious-ruling institutions, without naming a national school.']],gap:'The three instrument numbers remain unreconciled. The controlling Arabic version, named-product decision, certificate/import route and current country-specific school predominance were not established.',question:'Which operative Arabic instrument and process-specific decision govern this product, and which halal/import documents are required?',document:'Authoritative current Arabic rule and version history, product decision, certificate and import requirements.'},
 'C-AE':{components:[['Halal mechanism','P-AE-HALAL-SYSTEM',['AE-HALAL'],'The MOIAT portal describes certification through registered bodies and separately makes the Halal National Mark optional. Optional marking does not remove certificate obligations within their scope.']],gap:'The announcement lead did not yield an operative cultivated-food route. A national school assignment, direct Fatwa Council statute and named product food decision/certificate were not established.',question:'Which federal or emirate food route and product category apply, and what certificate is required independently of the optional mark?',document:'Operative food instrument, jurisdiction/product classification, competent-authority decision and current certificate.'},
 'C-SG':{components:[['Food authorization','P-SG-FOOD-FRAME',['SG-FRAME'],'SFA’s August 2026 framework requires premarket approval for covered novel foods.'],['Named process evidence','P-SG-PROCESS-LIST',['SG-LIST'],'The August 2026 list records Eat Just’s FBS process in 2020, its serum-free process in 2023 and Vital Meat’s embryonic chicken-cell biomass in 2025; these are food-process entries.'],['Religious guidance','P-MUIS-RELEASE',['MUIS2024'],'MUIS’s February 2024 release requires permitted animal sources, halal ingredients and a clean, non-toxic product.'],['Certification framework','P-MUIS-BOOK-DONOR',['MUIS-BOOK'],'The 2024 booklet describes then-current slaughter requirements, an egg-embryo exception and further guideline development before certification.'],['Community context','P-GEO-SG-READER-CLAIM',['P-GEO-SG-READER'],'Gulam’s 2021 publication describes Shafii and Hanafi practice and a Shia presence; no demographic percentage is used.'],['Institutional method','P-GEO-MUIS33-CLAIM',['P-GEO-MUIS33'],'MUIS’s explanation of a prayer ruling discusses opinions beyond the Shafii school and public interest; it is a distinct case.']],gap:'The food entries are not halal certificates. A matching current certificate and complete cell-bank/media history remain unestablished; the direct AMLA statutory capture was unavailable.',question:'Does a current certificate cover exactly the food-listed product, founder line, media history and manufacturing process?',document:'Current product certificate and its scope, full manufacturing dossier and matched SFA decision.'},
 'C-MY':{components:[['Foreign certification','P-MY-CERTIFIERS',['MY-HALAL'],'JAKIM’s English portal describes recognized foreign certifiers and imported halal descriptions, citing the 2011 order and an older standards edition.'],['Authority context','P-GEO-MY505-CLAIM',['P-GEO-MY505'],'Section 39 in the 2013 Act 505 reprint describes the Federal Territories Mufti’s Shafii starting point and specified recourse to other schools or judgment; it is not a rule for every state.']],gap:'Malay substantive leads remain held. A current cultivated-product religious position, food route, standard and matching product certificate were not established by these English sources.',question:'Which current standard, state or national authority and product-specific decisions apply to the proposed transaction?',document:'Suitable primary position in the permitted language lane, current standard, food decision and product certificate.'},
 'C-ID':{components:[['Foreign certificate registration','C-ID',['ID221'],'The issuer’s English 2025 decree requires recognized foreign halal certificates to be registered with BPJPH before circulation, through an importer or official representative using SIHALAL. This decree supplies no cultivated-food safety authorization.'],['Geography context','P-GEO-ID-STUDY-CLAIM',['P-GEO-ID-STUDY'],'Zulkifli’s 2014 study distinguishes its Shia subjects’ Jafari jurisprudence from a described Shafii majority; it is a dated qualitative account.']],gap:'The Indonesian magazine lead remains held. The named product’s category, food authorization, registration and any applicable transitional rules remain to be established.',question:'Does the recognized foreign certificate and BPJPH registration cover this precise product, and is its separate food authorization documented?',document:'Certificate scope and recognition, BPJPH registration, current category/transitional rules and food decision.'},
};
const countryRows=countries.map(c=>{const spec=countrySpecs[c.id];assert(spec,'Missing country specification '+c.id);return {original_id:c.id,country:c.country,historical_status:c.status,components:spec.components.map(([dimension,id,keys,text])=>component(id,keys,text,dimension)),bounded_gap:spec.gap,qualitative_question:spec.question,confirming_document:spec.document,numerical_or_gate_input_populated:false,assessment_object_populated:false,coverage_recommendation:{id:c.id,kinds:['claim','country'],disposition:'included',reason:c.id==='C-ID'?'The registration component is cited, with product gaps stated separately.':'The original compound record is traced only as an explicit audit gap; atomic claims supply the admitted components.'}};});

const holdReasons={
 'SHA-D':'Edition and required second-library passage check incomplete; contradictory transcription detail remains unresolved.',
 'SHA-T':'Edition and required second-library passage check incomplete.',
 'M-RIS29':'Translation edition not established; host calls the translation non-final; second-library passage check incomplete.',
 'M-BID-FOOD':'Print pagination not established; host segment is not a print volume.',
 'H-UM-FOOD':'Translator, print edition and pagination unestablished; second-library check incomplete.',
 'H-UM-FOOD2':'Translator and print edition unestablished; host pagination is not verified print pagination.',
 'H-UM-SLAUGHTER':'Translator and print edition unestablished; second-library check incomplete.',
 'H-MUGH-FOOD':'Print pagination unestablished; host segment is not a print volume.',
 'H-MUBDI':'Edition and required second-library passage check incomplete.',
 'H-TAY-IST':'Edition and required second-library passage check incomplete.',
 'H-INS-BLOOD':'Author/pagination evidence and second-library check incomplete.',
 'H3':'Second-library authority and passage checks incomplete.',
 'H7':'Print edition/pagination and second-library check incomplete.',
 'S1':'Locator corrected to displayed pages 27–29; edition and second-library check incomplete.',
 'S5':'Edition and required second-library passage check incomplete.',
 'S6':'Displayed page 78 located within a wider container; edition and second-library check incomplete.',
 'S7':'Edition and required second-library passage check incomplete.',
 'WP595':'Malay substantive text held under the language policy.',
 'MKI128':'Meeting/title/year metadata captured; Malay substantive text held under the language policy.',
 'P-BANURI-2019':'Urdu substantive text outside the approved language lane; institution distinct from CII and Deoband.',
 'P-LPPOM-MUI-2023':'Indonesian publisher magazine held; not a retrieved Fatwa Commission resolution.',
 'P-GEO-GEORGETOWN':'Second-edition publication year unestablished; landing-page date not transferred to the PDF.',
};
const unavailableReasons={
 'GHAMIDI':'Raw capture blocked; separate web-tool reading does not supply an admissible raw capture or verified issue date. Published essay only.',
 'AD2858':'Raw capture blocked; translation edition and date unestablished.',
 'AE-2025':'HTTP-success response contained a JavaScript shell, not the article.',
 'M-MUW25':'Raw capture blocked; separate web visibility does not replace the missing raw passage receipt.',
 'H4':'Raw passage blocked; catalogue metadata does not establish the identity of the blocked copy.',
 'S2':'Print edition matched by catalogue, but the legal passage was not retrieved.',
 'HS-012':'Article identity unresolved; attempted DOI endpoints returned 404. No absence-of-publication conclusion follows.',
 'P-GEO-SGAMLA':'Direct statutory capture returned HTTP 403.',
 'P-GEO-SA-IRF':'Both routes returned technical-difficulties pages rather than the report.',
 'P-GEO-UAE-FATWA':'Official statutory PDF capture returned HTTP 403.',
};
const metadataOnly=new Set(['M-RIS-INDEX']);
function sourceScope(s,a){
 if(a.verdict==='held')return 'Held; metadata only';
 if(!qualified.has(a.verdict))return 'Passage not retrieved';
 if(metadataOnly.has(s.key))return 'Host/index metadata only';
 if(s.reading_scope==='abstract_only')return 'English abstract only';
 if(s.reading_scope==='full_text_scoped_passages')return 'Selected full-text passages';
 return 'Specified document passages';
}
function metadataNote(s,a){
 if(a.verdict==='held'){assert(holdReasons[s.key],'Missing non-doctrinal hold note '+s.key);return holdReasons[s.key];}
 if(!qualified.has(a.verdict)){assert(unavailableReasons[s.key],'Missing retrieval note '+s.key);return unavailableReasons[s.key];}
 const b=s.bibliographic,parts=[];
 if(metadataOnly.has(s.key))parts.push('Index metadata only; does not qualify the substantive translated chapter.');
 if(b.year===null)parts.push('Publication year unestablished; no year inferred from a foreword, upload path or access date.');
 if(b.volume||b.page)parts.push('Recorded locator: '+[b.volume?'vol. '+b.volume:null,b.page?'p. '+b.page:null].filter(Boolean).join(', ')+'.');
 if(b.translator)parts.push('Translation credit: '+b.translator+'.');
 if(b.editor)parts.push('Editor: '+b.editor+'.');
 if(/classical/.test(s.source_type??''))parts.push('Cited digital transcription; print-edition identity remains qualified.');
 if(s.key==='HS-006')parts.push('Institutional abstract; 2017 online publication, 2018 issue. Publisher full text blocked.');
 if(s.key==='HS-008')parts.push('2022 online publication; 2023 issue citation.');
 if(s.key==='HS-010')parts.push('Publisher/Crossref and first page give 5(2); later running heads give 6(2).');
 if(s.key==='HS-011')parts.push('Arabic body unreviewed; separate from the Malay/Indonesian language hold.');
 if(s.key==='HS-024')parts.push('Indonesian body held; June issue and October article metadata retained separately.');
 if(s.key==='P-GEO-ID-STUDY')parts.push('PDF mononym retained; Crossref duplicates the author name.');
 if(s.key==='P-WAAG-EN-2024'||s.key==='P-WAAG-AR-2024')parts.push('Paired publisher reports, one family; underlying Council decision not retrieved.');
 if(s.key==='SA-NOVEL')parts.push('Cover number 513/2020; Arabic prevails; related references unreconciled.');
 if(s.key==='SA-GUIDE')parts.push('Guide reference 5031:2020; Arabic prevails; related references unreconciled.');
 if(s.key==='SA-2025')parts.push('Announcement reference 5013; not a reconciled controlling rule.');
 return parts.join(' ')||'Admission limited to the cited locator and recorded claim rechecks.';
}
const sourceRows=sources.map(s=>{const a=auditByKey.get(s.key);return {key:s.key,title:s.bibliographic.title??s.title,author:s.bibliographic.author??null,bibliographic:s.bibliographic,url:s.url,aliases:s.aliases,alias_titles:s.aliases.map(id=>({id,title:s.original_records.find(r=>r.id===id)?.title??s.title})),family:a.family??s.family,host_type:a.host_type,verdict:a.verdict,reading_scope:sourceScope(s,a),locator:s.locator??null,metadata_note:metadataNote(s,a),retrieved_at:a.retrieved_at??null,human_scholarly_review:false};});
const countBy=(rows,field)=>Object.fromEntries([...new Set(rows.map(r=>r[field]))].sort().map(value=>[value,rows.filter(r=>r[field]===value).length]));
const data={schema_version:1,generator:'tools/build-paper-appendices.mjs',input_files:inputNames.map(name=>({path:name,sha256:crypto.createHash('sha256').update(inputs.get(name)).digest('hex')})),scope:'Appendices A, B and D candidate; not a coverage mutation or complete-paper validation.',counts:{school_slots:schoolRows.length,countries:countryRows.length,canonical_sources:sourceRows.length,aliases:sources.reduce((sum,s)=>sum+s.aliases.length,0),source_verdicts:countBy(sourceRows,'verdict'),host_types:countBy(sourceRows,'host_type'),reading_scopes:countBy(sourceRows,'reading_scope')},school_slots:schoolRows,countries:countryRows,sources:sourceRows,coverage_recommendations:[...schoolRows.map(r=>r.coverage_recommendation),...countryRows.map(r=>r.coverage_recommendation)],human_scholarly_review:false,numerical_or_gate_input_populated:false};
data.counts.school_historical_status=countBy(schoolRows,'historical_status');
data.counts.school_current_admission=countBy(schoolRows,'current_admission');
data.counts.admitted_article_reading_scopes=countBy(sourceRows.filter(s=>qualified.has(s.verdict)&&/article/.test(byKey.get(s.key).source_type??'')),'reading_scope');

let out='## Appendix A. The 45 comparison slots\n\n';
out+='These tables preserve the original nine questions across five traditions. Historical agent checking and current citation admission are different states. Answers are limited to named authors and the cited passages; an inference is the paper’s proposed extension, not a contemporary product ruling. Held or unretrieved components are displayed without repeating their doctrinal propositions. '+trace(['P-METHOD-INTERNAL'],'evidence')+'\n\n';
for(const prefix of order){
 const rows=schoolRows.filter(r=>r.original_id.startsWith(prefix+'-'));
 out+='### '+labels[prefix]+'\n\n| Question | Historical status | Currently admitted answer |\n| --- | --- | --- |\n';
 const ids=[];
 for(const r of rows){
  const answer=r.admitted?r.admitted.text+footnote(r.admitted):r.current_admission==='open'?'Open; no answer admitted.':'No answer admitted in this version.';
  if(r.admitted)ids.push(r.admitted.claim_id);
  out+='| '+[r.question_number+'. '+r.question,statusLabel[r.historical_status]??r.historical_status,answer].map(escapeCell).join(' | ')+' |\n';
 }
 out+=trace(ids.length?ids:['P-METHOD-INTERNAL'],ids.some(id=>claims.get(id).kind==='inference')?'mixed':'evidence')+'\n\n';
 const limited=rows.filter(r=>r.current_admission!=='bounded'&&r.current_admission!=='open');
 if(limited.length){
  out+='Audit gaps by question:\n\n';
  for(const r of limited)out+='- Question '+r.question_number+': '+r.gap+' '+trace(['P-METHOD-INTERNAL'],'evidence')+'\n\n';
  out+='\n';
 }
 if(prefix==='J')out+='The question of who decides tayyib and khabith remains open in the reviewed Sistani material. General rules on following a jurist, impurity or harm do not establish the specific customary-repugnance test. '+trace(['J-Q1'],'gap')+'\n\n';
}
out+='## Appendix B. Seven countries by documentary layer\n\n';
out+='Each country table separates dated documentary evidence from the documents still needed for a named product, process, territory, transaction and date. The qualitative questions align with the active Phase Two distinction between religious position, certification, product certificate, food authorization and import access. No numerical input, national gate or assessment object is populated; the compatible demand baseline remains missing. '+trace(['P-METHOD-INTERNAL'],'evidence')+'\n\n';
for(const r of countryRows){
 out+='### '+r.country+'\n\n| Layer | Admitted documentary finding |\n| --- | --- |\n';
 for(const c of r.components)out+='| '+escapeCell(c.dimension)+' | '+escapeCell(c.text+footnote(c))+' |\n';
 out+=trace(r.components.map(c=>c.claim_id),'evidence')+'\n\n';
 out+='Bounded gap: '+r.bounded_gap+' The historical country record is retained; its compound statement is not treated as fully reverified. '+trace([r.original_id],'gap')+'\n\n';
 out+='Evidence question: '+r.qualitative_question+' Documents still needed: '+r.confirming_document+' '+trace(['P-METHOD-INTERNAL'],'evidence')+'\n\n';
}
out+='## Appendix D. Source readiness and edition notes\n\n';
out+='The inventory contains '+data.counts.canonical_sources+' canonical source records and '+data.counts.aliases+' alias identifiers, counted once under their canonical records. Verdict and reading-scope totals below are derived from the current registers. They describe evidence availability, not independent authorities, agreement, legal weight or scholarly approval. Host and work-family labels are retained from the audit; a shared family is not independent corroboration. Human scholarly verification remains pending. '+trace(['P-METHOD-INTERNAL'],'evidence')+'\n\n';
out+='Alias records refer to repeated entries for two Radd al-Muhtar passages, two al-Majmu passages and Sistani’s transformation rules. Paired language versions, repeated passages from one work and reports from one issuer retain their family relationships. Full authorship, locators, alias titles, family labels and edition notes accompany the machine-readable appendix data; the compact inventory below is a reading guide. '+trace(['P-METHOD-INTERNAL'],'evidence')+'\n\n';
const displayVerdict={verified:'Qualified',verified_with_note:'Qualified with limitations',held:'Held',not_retrieved:'Not retrieved'};
for(const [title,counts] of [['Current source verdict',data.counts.source_verdicts],['Audited host class',data.counts.host_types],['Reading scope',data.counts.reading_scopes],['Admitted journal articles only',data.counts.admitted_article_reading_scopes]]){
 out+='### '+title+'\n\n| Category | Canonical records |\n| --- | ---: |\n'+Object.entries(counts).map(([name,count])=>'| '+escapeCell(displayVerdict[name]??name.replaceAll('_',' '))+' | '+count+' |').join('\n')+'\n'+trace(['P-METHOD-INTERNAL'],'evidence')+'\n\n';
}
const briefNotes={
 'HS-006':'2017 online publication; 2018 issue. Institutional English abstract only; publisher full text blocked.',
 'HS-008':'2022 online publication; 2023 issue citation.',
 'HS-010':'Publisher/Crossref and first page give 5(2); later running heads give 6(2).',
 'HS-011':'English abstract only; Arabic body unreviewed.',
 'HS-024':'English abstract only; Indonesian body held. June issue and October article metadata remain distinct.',
 'P-GEO-ID-STUDY':'PDF mononym retained; Crossref duplicates the author name. Cited page visually reviewed.',
 'P-WAAG-EN-2024':'Paired publisher reports, one family; underlying Council decision not retrieved.',
 'P-WAAG-AR-2024':'Paired publisher reports, one family; underlying Council decision not retrieved.',
 'SA-NOVEL':'Cover 513/2020; Arabic prevails; related references unreconciled.',
 'SA-GUIDE':'Undated guide; reference 5031:2020; Arabic prevails; references unreconciled.',
 'SA-2025':'Announcement reference 5013; not a reconciled controlling rule.',
 'M-RIS-INDEX':'Index metadata only; does not qualify the translated substantive chapter.',
};
for(const verdict of Object.keys(data.counts.source_verdicts)){
 out+='### '+(displayVerdict[verdict]??verdict)+' — individual records\n\n| Source and recorded year | Reading scope | Edition or admission note |\n| --- | --- | --- |\n';
 for(const s of sourceRows.filter(s=>s.verdict===verdict)){
  const original=byKey.get(s.key);
  const duplicate=sourceRows.filter(other=>other.title===s.title).length>1;
  const title=normalizeCitation((s.key==='SG-LIST'?'SFA novel-food process list':s.title)+(duplicate&&s.locator?' — '+s.locator:''));
  const generic=[s.bibliographic.year===null?'Year unestablished.':null,/classical/.test(original.source_type??'')?'Digital transcription; edition qualified.':null,s.bibliographic.translator?'Translation credit retained in metadata.':null].filter(Boolean).join(' ');
  const note=briefNotes[s.key]??(!qualified.has(verdict)?s.metadata_note:generic||'Admission limited to audited passages and claim rechecks.');
  const aliasNote=s.aliases.length?' Includes '+s.aliases.length+' alias.':'';
  out+='| '+[`${title} (${s.bibliographic.year??'year unestablished'})`,s.reading_scope,note+aliasNote].map(escapeCell).join(' | ')+' |\n';
 }
 out+=trace(['P-METHOD-INTERNAL'],'evidence')+'\n\n';
}
out+='The bibliography lists the sources cited in evidential footnotes. Held and unretrieved leads remain in this inventory and the open-question appendix; their appearance here does not admit their substantive propositions. '+trace(['P-METHOD-INTERNAL'],'evidence')+'\n\n';
for(const [id,text] of notes)out+='[^'+id+']: '+text+'\n';

const markdownPath='working/draft-sections/appendices-abd.md',dataPath=paper+'appendices-data.json';
const outputs=new Map([[markdownPath,out],[dataPath,JSON.stringify(data,null,2)+'\n']]);
const checkOnly=process.argv.includes('--check');
assert(process.argv.slice(2).every(arg=>arg==='--check'),'Usage: node tools/build-paper-appendices.mjs [--check]');
const state=JSON.parse(fs.readFileSync(path.join(root,paper,'execution-state.json'),'utf8'));
assert(state.outlineApproved===true&&state.stage>=5,'Actual outline approval is required for appendix generation.');
if(checkOnly){for(const [name,text] of outputs)assert(fs.existsSync(path.join(root,name))&&fs.readFileSync(path.join(root,name),'utf8')===text,'Generated output drift: '+name);}
else for(const [name,text] of outputs){fs.mkdirSync(path.dirname(path.join(root,name)),{recursive:true});fs.writeFileSync(path.join(root,name),text);}

// Run the actual manuscript validator with appendix-local coverage in memory.
const files=Object.fromEntries(fs.readdirSync(path.join(root,paper)).filter(f=>/\.(json|md)$/.test(f)).map(f=>[f,fs.readFileSync(path.join(root,paper,f),'utf8')]));
const cited=citedSourceKeys(out).map(key=>byKey.get(key));
const bib=cited.sort((a,b)=>a.bibliographic.author.localeCompare(b.bibliographic.author)||a.key.localeCompare(b.key)).map(bibliographyEntry).join('\n\n');
files['paper.md']='# Isolated appendix validation\n\nAI-assisted working draft; human verification pending\n\n'+out+'\n\n## Bibliography\n\n'+bib+'\n';
const traced=new Set([...out.matchAll(/<!--\s*trace:\s*([^|]*?)\s*\|/g)].flatMap(m=>m[1].trim().split(/\s+/)).filter(Boolean));
files['coverage.json']=JSON.stringify(JSON.parse(files['coverage.json']).map(r=>{
 const id=(r.kind==='gap'?'gap:':r.kind==='counter_evidence'?'ce:':r.kind==='historical'?'historical:':'')+r.id;
 return {...r,disposition:traced.has(id)?'included':'excluded',reason:traced.has(id)?'Present in this isolated appendix candidate.':'Outside this isolated appendix check; authoritative manuscript coverage unchanged.'};
}));
const phaseOneFiles=Object.fromEntries(fs.readdirSync(path.join(root,base,'phase1')).filter(f=>f.endsWith('.json')).map(f=>[f,fs.readFileSync(path.join(root,base,'phase1',f),'utf8')]));
const checked=checkPaper(files,{phaseOneFiles});
const warnings=checked.warnings.filter(w=>!/^Paper: section /.test(w));
console.log(JSON.stringify({scope:'isolated Appendices A/B/D; not complete manuscript validation',mode:checkOnly?'reproducibility check':'build',status:checked.failures.length?'FAIL':'PASS',checks:checked.checks,counts:data.counts,footnotes:notes.size,outputs:[...outputs].map(([name,text])=>({path:name,sha256:crypto.createHash('sha256').update(text).digest('hex')})),failures:checked.failures,warnings},null,2));
process.exitCode=checked.failures.length?1:0;
