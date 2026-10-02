import assert from 'node:assert/strict';
import {checkPaper,normalizeQuote} from './paper-checks.mjs';

const json=value=>JSON.stringify(value);
const source=(key,aliases,quote)=>({id:key,key,aliases,title:'Example work '+key,url:'https://example.org/'+key,locator:'Chapter 1',short_exact_quote:quote,family:key,bibliographic:{author:'Example author',title:'Example work',translator:null,editor:null,publisher:'Example publisher',place:null,year:2026,volume:1,page:1},audit_verdict:'verified'});
const sources=[source('HAN',['H1'],'four exact words appear'),source('B',[],'a second exact passage exists')];
const audit=row=>({key:row.key,aliases:row.aliases,verdict:'verified',http_status:200,final_url:row.url,content_type:'text/html',retrieved_at:'2026-10-02T12:00:00Z',host_type:'issuer',family:row.family,sha256:'a'.repeat(64),quote_expected:row.short_exact_quote,quote_found:true,locator_found:true,bibliographic_complete:true,identity:{title:true,issuer:true,date:true},passages:[{locator:'Chapter 1',text:row.short_exact_quote+'. More contextual text.'}],claims_rechecked:row.key==='HAN'?[{id:'E01',result:'supported'},{id:'H01',result:'premise_supported'}]:row.key==='B'?[{id:'I01',result:'premise_supported'}]:[]});
const claim=(id,source_ids,kind='evidence',status='blind_agent_checked')=>({id,source_ids,kind,status,statement:'Example bounded finding',locator:'Chapter 1'});
const phase={
 'claims.json':json([claim('E01',['HAN']),claim('I01',['B'],'inference','inference'),claim('J-Q1',[],'evidence','open'),claim('H01',['HAN'],'inference','inference')]),
 'school-questions.json':json([claim('HN-Q3',['H1']),claim('J-Q1',[],'evidence','open')]),
 'counter-evidence.json':json([{counter_source_ids:['H1'],result:'A qualification'}]),
 'gaps.json':json([{id:'G1',rows:['J-Q1'],text:'An unresolved question'}]),
 'source-register.json':json(sources),
 'historical-comparisons.json':json([claim('H01',['HAN'],'inference','inference')]),
 'country-findings.json':json([claim('C-IN',['B'])])
};
const coverage=[];
for(const [file,kind] of [['claims','claim'],['school-questions','school'],['counter-evidence','counter_evidence'],['gaps','gap'],['source-register','source'],['historical-comparisons','historical'],['country-findings','country']]) {
 for(const [index,row] of JSON.parse(phase[file+'.json']).entries())coverage.push({id:row.id??'CE'+(index+1),kind,sections:[5],disposition:'included'});
}
const paper=`# Test manuscript

AI-assisted working draft; human verification pending

## 1. Introduction

Phase One contains 4 claims, 2 sources and 2 slots.

## 5. Donor and procurement

The named author writes “four exact words appear”.[^one] <!-- trace: E01 HN-Q3 ce:CE1 | kind: evidence -->

## 6. Culture inputs

We infer a conditional application in the country account.[^two] <!-- trace: I01 C-IN | kind: mixed -->

## 8. Category and edibility

The criterion remains open and was not located in the reviewed material. <!-- trace: J-Q1 gap:G1 | kind: gap -->

## 10. Historical analogies

We use this analogy as an inference with a missing product test.[^one] <!-- trace: H01 historical:H01 | kind: inference -->

[^one]: Example author, Example work, chapter 1. [H1]
[^two]: Another author, Another work, chapter 1. [B]

## Bibliography

Example author. Example work. [HAN]

Another author. Another work. [B]
`;
const fixture={
 'paper.md':paper,
 'source-register.json':json(sources),
 'citation-audit.json':json(sources.map(audit)),
 'claims-added.json':'[]',
 'coverage.json':json(coverage),
 'search-log.json':'[]',
 'allowlist.json':'[]',
 'execution-state.json':json({stage:5,status:'draft',outlineApproved:true,humanReview:false})
};
const alter=(files,name,mutate)=>{const value=JSON.parse(files[name]);mutate(value);files[name]=json(value);};
const check=files=>checkPaper(files,{phaseOneFiles:phase});
const valid=check(fixture);
assert.deepEqual(valid.failures,[],'valid alias-aware, same-paragraph manuscript must pass');
assert(valid.warnings.some(message=>message.includes('section 5 word count')),'rule 13 must warn for a short section');
assert.equal(normalizeQuote('“أَلِفٌ ـ إِلى” — ٱلْكِتاب\n  word'),'"الف الي" - الكتاب word');
assert.equal(normalizeQuote('Cafe\u0301\t  text'),'Café text');
assert.notEqual(normalizeQuote('four exact words appear'),normalizeQuote('four similar words appear'),'normalization cannot paraphrase');

// At least one meaningful negative fixture for every mandatory section 9 rule.
const cases=[
 ['1 terminal register keys',files=>{files['paper.md']=paper.replace('chapter 1. [H1]','chapter 1.');},'footnote definition lacks terminal'],
 ['1 unresolved alias',files=>{files['paper.md']=paper.replace('[H1]','[MISSING]');},'unknown footnote source'],
 ['1 ambiguous alias',files=>alter(files,'source-register.json',rows=>{rows[1].aliases=['H1'];}),'ambiguous or duplicate alias'],
 ['1 duplicate canonical key',files=>alter(files,'source-register.json',rows=>{rows.push(rows[0]);}),'duplicate canonical source'],
 ['2 uncitable verdict',files=>{alter(files,'source-register.json',rows=>{rows[0].audit_verdict='held';});alter(files,'citation-audit.json',rows=>{rows[0].verdict='held';});},'uncitable source'],
 ['2 register and audit disagree',files=>alter(files,'citation-audit.json',rows=>{rows[0].verdict='failed';}),'register/audit verdict mismatch'],
 ['2 qualification absent',files=>{alter(files,'source-register.json',rows=>{rows[0].audit_verdict='verified_with_note';});alter(files,'citation-audit.json',rows=>{rows[0].verdict='verified_with_note';});},'verified_with_note lacks its qualification'],
 ['2 missing audit',files=>alter(files,'citation-audit.json',rows=>{rows.pop();}),'source has no citation audit'],
 ['2 fabricated verification flag',files=>alter(files,'citation-audit.json',rows=>{rows[0].quote_found=false;}),'verified audit lacks passage'],
 ['2 missing identity',files=>alter(files,'citation-audit.json',rows=>{rows[0].identity.date=false;}),'verified audit lacks identity'],
 ['2 fabricated stored quote',files=>alter(files,'citation-audit.json',rows=>{rows[0].passages[0].text='Different passage.';}),'verified quote absent'],
 ['2 malformed stored passage',files=>alter(files,'citation-audit.json',rows=>{rows[0].passages=[null];}),'invalid stored audit passage'],
 ['2 malformed recheck record',files=>alter(files,'citation-audit.json',rows=>{rows[0].claims_rechecked=[null];}),'invalid claim recheck result'],
 ['2 register quote mismatch',files=>alter(files,'source-register.json',rows=>{rows[0].short_exact_quote='Invented wording from memory.';}),'register quote absent'],
 ['2 retrieval metadata missing',files=>alter(files,'citation-audit.json',rows=>{delete rows[0].retrieved_at;}),'verified audit lacks successful retrieval metadata'],
 ['2 unsuccessful retrieval',files=>alter(files,'citation-audit.json',rows=>{rows[0].http_status=404;}),'verified audit lacks successful retrieval metadata'],
 ['2 capture hash missing',files=>alter(files,'citation-audit.json',rows=>{rows[0].sha256=null;}),'verified audit lacks host, family or capture hash'],
 ['2 bibliographic author missing',files=>alter(files,'source-register.json',rows=>{rows[0].bibliographic.author=null;}),'verified source lacks bibliographic essentials'],
 ['2 translation identity missing',files=>alter(files,'source-register.json',rows=>{rows[0].source_type='English translation';}),'verified source lacks bibliographic essentials'],
 ['2 claim recheck missing',files=>alter(files,'citation-audit.json',rows=>{rows[0].claims_rechecked=[];}),'claim-source pair has no recorded recheck'],
 ['2 unrecognized claim recheck',files=>alter(files,'citation-audit.json',rows=>{rows[0].claims_rechecked[0].result='probably';}),'invalid claim recheck result'],
 ['2 unsupported claim cited',files=>alter(files,'citation-audit.json',rows=>{rows[0].claims_rechecked[0].result='unsupported';}),'paragraph claim lacks cited supporting recheck'],
 ['3 footnoted paragraph lacks trace',files=>{files['paper.md']=paper.replace('<!-- trace: E01 HN-Q3 ce:CE1 | kind: evidence -->','');},'paragraph requires exactly one trace'],
 ['3 uncited substantive paragraph lacks trace',files=>{files['paper.md']=paper.replace('## 6. Culture inputs','A substantive assertion without a note.\n\n## 6. Culture inputs');},'paragraph requires exactly one trace'],
 ['3 unresolved trace',files=>{files['paper.md']=paper.replace('E01 HN-Q3','E99 HN-Q3');},'unresolved traced ID'],
 ['3 trace must be last',files=>{files['paper.md']=paper.replace('kind: evidence -->','kind: evidence --> More factual prose.');},'trace must end its paragraph'],
 ['3 duplicate traces',files=>{files['paper.md']=paper.replace('kind: evidence -->','kind: evidence --> <!-- trace: E01 | kind: evidence -->');},'paragraph requires exactly one trace'],
 ['3 undefined note',files=>{files['paper.md']=paper.replace('[^two] <!--','[^missing] <!--');},'undefined footnote'],
 ['3 unused note',files=>{files['paper.md']=paper.replace('## Bibliography','[^unused]: Example author, Work. [HAN]\n\n## Bibliography');},'unused footnote'],
 ['3 duplicate note',files=>{files['paper.md']=paper.replace('## Bibliography','[^one]: Example author, Work. [HAN]\n\n## Bibliography');},'duplicate footnote'],
 ['3 fenced prose cannot evade traces',files=>{files['paper.md']=paper.replace('## 6. Culture inputs','```text\nA factual assertion.\n```\n\n## 6. Culture inputs');},'manuscript prose cannot be hidden'],
 ['3 framing cannot carry citation',files=>{files['paper.md']=paper.replace('kind: evidence -->','kind: framing -->');},'framing paragraph has a footnote'],
 ['3 source-backed trace without note',files=>{files['paper.md']=paper.replace('We infer a conditional application in the country account.[^two]','We infer a conditional application in the country account.');},'source-backed paragraph requires a footnote'],
 ['4 note source outside trace',files=>{files['paper.md']=paper.replace('[^one] <!-- trace: E01','[^two] <!-- trace: E01');},'footnote source outside traced records'],
 ['4 reasonless scope allowlist',files=>alter(files,'allowlist.json',rows=>rows.push({rule:'source_scope',match:'B|E01 HN-Q3 ce:CE1',reason:''})),'invalid allowlist'],
 ['5 inference upgraded',files=>{files['paper.md']=paper.replace('I01 C-IN | kind: mixed','I01 C-IN | kind: evidence');},'inference trace upgraded'],
 ['5 J-Q1 upgraded',files=>{files['paper.md']=paper.replace('J-Q1 gap:G1 | kind: gap','J-Q1 gap:G1 | kind: evidence');},'J-Q1 must remain explicitly open'],
 ['5 J-Q1 lost open wording',files=>{files['paper.md']=paper.replace('The criterion remains open and was not located in the reviewed material.','The criterion is established.');},'J-Q1 must remain explicitly open'],
 ['6 missing original coverage',files=>alter(files,'coverage.json',rows=>{rows.splice(rows.findIndex(row=>row.kind==='claim'&&row.id==='E01'),1);}),'missing coverage'],
 ['6 untraced original record',files=>{files['paper.md']=paper.replace('E01 HN-Q3 ce:CE1','HN-Q3 ce:CE1');},'record neither traced nor explicitly excluded'],
 ['6 exclusion without reason',files=>alter(files,'coverage.json',rows=>{rows[0].disposition='excluded';rows[0].sections=[];}),'coverage requires section or exclusion reason'],
 ['6 falsely excluded traced record',files=>alter(files,'coverage.json',rows=>{rows[0].disposition='excluded';rows[0].reason='A bounded exclusion';}),'excluded record is nevertheless traced'],
 ['6 unknown coverage identity',files=>alter(files,'coverage.json',rows=>{rows.push({id:'UNRESOLVED',kind:'claim',sections:[5],disposition:'included'});}),'unknown coverage record'],
 ['7 altered quotation',files=>{files['paper.md']=paper.replace('“four exact words appear”','“four different words appear”');},'quotation does not match'],
 ['7 quote from different cited source',files=>{files['paper.md']=paper.replace('“four exact words appear”','“a second exact passage exists”');},'quotation does not match same-paragraph'],
 ['7 uncited long quote',files=>{files['paper.md']=paper.replace('The criterion remains open','“four exact words appear”. The criterion remains open');},'quotation does not match'],
 ['7 straight single quotation',files=>{files['paper.md']=paper.replace('“four exact words appear”',"'four invented words appear'");},'quotation does not match'],
 ['7 block quotation',files=>{files['paper.md']=paper.replace('The named author writes “four exact words appear”.','> Four invented words appear here.');},'quotation does not match'],
 ['8 unacknowledged dangerous phrase',files=>{files['paper.md']=paper.replace('The named author writes','The named author confirms and writes');},'phrase requires correction or reasoned allowlist'],
 ['8 approval near product',files=>{files['paper.md']=paper.replace('The named author writes','The approved chicken dossier author writes');},'phrase requires correction or reasoned allowlist'],
 ['9 wrong claim count',files=>{files['paper.md']=paper.replace('4 claims','74 claims');},'stated register count mismatch'],
 ['9 alias inflation',files=>{files['paper.md']=paper.replace('2 sources','3 sources');},'stated register count mismatch'],
 ['10 private-source reference',files=>{files['paper.md']+='\n[INTERVIEW]\n';},'private-source reference'],
 ['10 local home path',files=>{files['paper.md']+='\n'+['','Users','example','notes'].join('/')+'\n';},'absolute home path'],
 ['10 private cloud URL',files=>{files['paper.md']+='\nhttps://'+'drive'+'.google.com/file/example\n';},'private document URL'],
 ['10 email',files=>{files['paper.md']+='\nname'+'@'+'example.org\n';},'email address'],
 ['10 excluded artifact',files=>{files[['work','ing'].join('')+'/capture.md']='Example';},'excluded file or path'],
 ['11 notice missing',files=>{files['paper.md']=paper.replace('AI-assisted working draft; human verification pending','Draft paper');},'draft notice must appear immediately'],
 ['11 notice buried',files=>{files['paper.md']=paper.replace('\n\nAI-assisted','\n\nStatus text.\n\nAI-assisted');},'draft notice must appear immediately'],
 ['11 false approval prose',files=>{files['paper.md']=paper.replace('Phase One contains','This is mentor-approved. Phase One contains');},'unwarranted scholarly or mentor approval'],
 ['11 approval granted prose',files=>{files['paper.md']=paper.replace('Phase One contains','Scholarly approval has been granted. Phase One contains');},'unwarranted scholarly or mentor approval'],
 ['11 false human-review flag',files=>alter(files,'execution-state.json',state=>{state.humanReview=true;}),'review flag must remain false'],
 ['11 camelcase mentor flag',files=>alter(files,'execution-state.json',state=>{state.mentorApproved=true;}),'review flag must remain false'],
 ['12 missing bibliography entry',files=>{files['paper.md']=paper.replace('Another author. Another work. [B]','');},'cited key missing from bibliography'],
 ['12 bibliography alias instead of canonical',files=>{files['paper.md']=paper.replace('Example author. Example work. [HAN]','Example author. Example work. [H1]');},'bibliography key is unknown or an alias'],
 ['12 duplicate bibliography',files=>{files['paper.md']+='\nExample author. Example work. [HAN]\n';},'duplicate bibliography key'],
 ['12 uncited bibliography entry',files=>{alter(files,'source-register.json',rows=>rows.push(source('UNUSED',[],'extra stored passage')));alter(files,'citation-audit.json',rows=>rows.push(audit(source('UNUSED',[],'extra stored passage'))));files['paper.md']+='\nUnused author. Unused work. [UNUSED]\n';},'uncited bibliography key'],
 ['corrupt JSON fails closed',files=>{files['coverage.json']='{';},'missing or invalid coverage.json'],
 ['wrong JSON shape fails closed',files=>{files['source-register.json']='{}';},'missing or invalid source-register.json'],
 ['non-object register row fails closed',files=>{files['source-register.json']='[null]';},'non-object record'],
 ['draft without checkpoint',files=>alter(files,'execution-state.json',state=>{state.outlineApproved=false;}),'drafting requires the recorded human outline checkpoint'],
 ['draft concealed by stage downgrade',files=>alter(files,'execution-state.json',state=>{state.stage=4;}),'draft body is not permitted before stage 5'],
 ['raw IDs in prose',files=>{files['paper.md']=paper.replace('The named author writes','E01: The named author writes');},'raw record ID in prose']
];
for(const [name,mutate,expected] of cases) {
 const files={...fixture};mutate(files);const result=check(files);
 assert(result.failures.some(message=>message.includes(expected)),name+' must fail with '+expected+'; got '+json(result.failures));
}

const normalized={...fixture};
normalized['paper.md']=paper.replace('“four exact words appear”','“four  exact\nwords appear”');
assert.deepEqual(check(normalized).failures,[],'whitespace normalization must preserve valid exact quotes');
const noApproval={...fixture};
noApproval['paper.md']=paper.replace('Phase One contains','This paper is not yet mentor-approved and has not received scholarly approval. Phase One contains');
assert.deepEqual(check(noApproval).failures,[],'explicitly denied approval must remain a valid limitation');
const ack={...fixture};
ack['paper.md']=paper.replace('The named author writes','The named author confirms and writes');
ack['allowlist.json']=json([{rule:'phrase',match:'confirms',reason:'A synthetic attributed fixture verifies the explicit acknowledgement mechanism.'}]);
assert.deepEqual(check(ack).failures,[],'reasoned phrase acknowledgement must work');
const scope={...fixture};
scope['paper.md']=paper.replace('The named author writes “four exact words appear”.[^one]','The named author provides a separate context.[^two]');
scope['allowlist.json']=json([{rule:'source_scope',match:'B|E01 HN-Q3 ce:CE1',reason:'Separate process context, explicitly reviewed for this paragraph.'}]);
assert(check(scope).failures.some(message=>message.includes('paragraph claim lacks cited supporting recheck')),'a source-scope exception must not fabricate support for a traced claim');
const extraContext={...fixture};
extraContext['paper.md']=paper.replace('appear”.[^one]','appear”.[^one][^two]');
extraContext['allowlist.json']=scope['allowlist.json'];
assert.deepEqual(check(extraContext).failures,[],'a reasoned source-scope exception may add context while the traced claim retains its supporting citation');
const mixed={...fixture};
mixed['paper.md']=paper.replace('J-Q1 gap:G1 | kind: gap','J-Q1 gap:G1 | kind: mixed | open: J-Q1');
assert.deepEqual(check(mixed).failures,[],'a mixed paragraph can preserve an explicitly open record');
const scaffold={...fixture,'paper.md':'# Manuscript scaffold\n\nAI-assisted working draft; human verification pending\n','source-register.json':'[]','citation-audit.json':'[]','coverage.json':'[]','execution-state.json':json({stage:0,status:'scaffold',outlineApproved:false,humanReview:false})};
assert.deepEqual(checkPaper(scaffold).failures,[],'stage zero permits intentionally empty registers');
const consolidated={...fixture,'paper.md':scaffold['paper.md'], 'execution-state.json':json({stage:1,status:'consolidated',outlineApproved:false,humanReview:false})};
assert.deepEqual(check(consolidated).failures,[],'stage one permits complete mapped registers without a manuscript');
const undated={...fixture};
alter(undated,'source-register.json',rows=>{rows[0].source_type='classical Arabic text';rows[0].audit_verdict='verified_with_note';rows[0].bibliographic.year=null;rows[0].bibliographic.publisher=null;});
alter(undated,'citation-audit.json',rows=>{rows[0].verdict='verified_with_note';rows[0].notes='Edition and publication year are not established on the host; author, work, volume and page are displayed.';});
assert.deepEqual(check(undated).failures,[],'an explicitly qualified unknown edition must remain unknown');
assert.deepEqual(checkPaper({...scaffold,'execution-state.json':json({stage:1,status:'consolidation',outlineApproved:false,humanReview:false})},{phaseOneFiles:phase}).failures.filter(message=>message.includes('missing coverage')).length,coverage.length,'stage one requires complete original coverage');
assert(checkPaper({...scaffold,'execution-state.json':json({stage:2})},{phaseOneFiles:{...phase,'claims.json':'broken'}}).failures.some(message=>message.includes('missing or invalid claims.json')),'malformed Phase One input must fail closed');
assert(checkPaper(scaffold,{stage:5}).failures.some(message=>message.includes('stage override disagrees')),'a caller cannot silently override recorded stage');
assert(valid.warnings.length>=Object.keys({Abstract:1,1:1,2:1,3:1,4:1,5:1,6:1,7:1,8:1,9:1,10:1,11:1,12:1,13:1}).length,'rule 13 checks every section, including absent sections');
console.log(JSON.stringify({status:'PASS',validFixtureChecks:valid.checks,negativeFixtures:cases.length,wordCountWarningFixture:true,failed:0}));
