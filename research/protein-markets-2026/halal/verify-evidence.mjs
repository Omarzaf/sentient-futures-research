import { readFile, access } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { resolve, join } from 'node:path';
import { readReviewState } from './review-state.mjs';

const here = import.meta.dirname;
const privateDir = resolve(here, '../../../../OUTPUTS/Deep Research 2026-10/halal');
const read = async name => JSON.parse(await readFile(join(here,name),'utf8'));
const register = await read('source-register.json');
const ledger = await read('claims.json');
const signposts = await read('signposts.json');
const authorReview = await readReviewState(here);
let assertions = 0;
function check(value,message) { assertions++; if(!value) throw new Error(message); }
check(register.sources.length === 17, 'Capture count changed; review the source register.');
check(register.held.length === 2, 'Held-original inventory changed.');
const ids = new Set();
for (const s of register.sources) {
  check(!ids.has(s.id),'Duplicate source id'); ids.add(s.id);
  check(/^https:\/\//.test(s.original_url),'Missing original HTTPS URL');
  check(s.raw_file.startsWith('raw/') && !s.raw_file.includes('..'),'Invalid private source path');
  const bytes = await readFile(join(privateDir,s.raw_file));
  check(createHash('sha256').update(bytes).digest('hex') === s.sha256,'Source hash mismatch: '+s.id);
  check(bytes.length === s.bytes,'Source byte length mismatch: '+s.id);
  check(Number.isFinite(Date.parse(s.retrieved_at)),'Invalid retrieval time');
  check(s.locator && s.scope && s.limits && s.date_basis && s.source_family,'Missing scope/locator/date boundaries');
  check(s.human_review === 'pending','Unapproved source review promoted');
  check(s.licence.includes('privately'),'Missing private rights boundary');
}
const manifest = JSON.parse(await readFile(join(privateDir,'capture-manifest.json'),'utf8'));
for (const f of manifest.files) {
  check(f.file.startsWith('raw/') && !f.file.includes('..'),'Manifest path outside assigned raw folder');
  const b = await readFile(join(privateDir,f.file));
  check(createHash('sha256').update(b).digest('hex') === f.sha256,'Private capture/inspection hash changed: '+f.file);
}
for (const h of register.held) {
  check(h.failed_attempts === 3 && h.sha256 === null,'Held source promoted or retry cap changed');
  check(h.publication_date === null,'Unretrieved original date promoted');
}
const claimIds = new Set();
for (const c of ledger.claims) {
  check(!claimIds.has(c.id),'Duplicate claim id'); claimIds.add(c.id);
  check(c.sources.every(id=>ids.has(id)),'Claim cites unknown source');
  check(c.locator && c.scope_limit && c.review_status.startsWith('pending'),'Claim missing locator, limit or pending review');
  const excerpts = [c.original_excerpt,c.parallel_excerpt,c.quoted_basis?.original_excerpt].filter(Boolean);
  check(excerpts.join(' ').split(/\s+/).length <=25,'Excerpt budget exceeded within a claim/source family');
}
for (const id of ['PK-BANURI-2018','PK-BANURI-2019']) {
  const s = register.sources.find(x=>x.id===id);
  const html = await readFile(join(privateDir,s.raw_file),'utf8');
  const c = ledger.claims.find(x=>x.sources.includes(id));
  const text = html.replace(/<[^>]+>/g,' ').replace(/\s+/g,' ').normalize('NFC');
  check(text.includes(c.original_excerpt),'Original Urdu passage absent from HTML');
  if(c.quoted_basis) check(text.includes(c.quoted_basis.original_excerpt),'Quoted Arabic basis absent from original HTML');
}
for (const image of ['PK-DUK-CULTIVATED-URDU-02.png','PK-DUK-CULTIVATED-URDU-22.png','PK-DUK-CULTIVATED-ARABIC-01.png','PK-DUK-CULTIVATED-ARABIC-14.png','IN-IFA-URDU-SEMINAR24-19.png','IN-IFA-URDU-SEMINAR33-14.png','IN-IFA-URDU-SEMINAR33-15.png']) {
  await access(join(privateDir,'raw',image)); assertions++;
}
check(signposts.publication_window_start === null && signposts.status.includes('not approved'),'Draft signposts silently preregistered');
check(signposts.certification_signposts.length === 4,'Unexpected certification signpost count');
for (const s of [...signposts.certification_signposts,...signposts.ai_observables]) check(s.evidence_basis.every(id=>ids.has(id)),'Signpost lacks checked evidence basis');
for(const s of signposts.certification_signposts) {
  check(Number.isFinite(Date.parse(s.cutoff)) && Number.isFinite(Date.parse(s.resolution_date)),'Invalid signpost dates');
  check(s.question.includes('named') && s.question.includes('valid at that cutoff'),'Insufficient certificate scope');
}
const chapter = await readFile(join(here,'CHAPTER-DRAFT.md'),'utf8');
for(const m of chapter.matchAll(/`(HALAL-[A-Z0-9-]+)`/g)) check(claimIds.has(m[1]),'Chapter cites unknown claim id');
check(chapter.includes('author-review.json') && chapter.includes('No country-wide'),'Chapter missing review/inference boundaries');
console.log(JSON.stringify({status:'pass',assertions,source_captures:register.sources.length,private_capture_and_inspection_files:manifest.files.length,claims:ledger.claims.length,held_originals:register.held.length,certification_signposts:4,translation_review:authorReview.status,author_review:authorReview,market_estimates_computed:false,policy_author_codes:'pending; not exposed'},null,2));
