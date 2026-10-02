// Content-preservation and link checks for presentations/halal-mmm/index.html.
//   node presentations/halal-mmm/build/check.mjs
// Compares the page with the canonical manuscript and the handoff's content
// contract. Visual similarity is not evidence of preservation; these checks
// read the generated HTML as text.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {parseManuscript} from './markdown.mjs';
import {countryState,slotState} from './figures.mjs';

const here=path.dirname(fileURLToPath(import.meta.url));
const out=path.resolve(here,'..');
const root=path.resolve(out,'../..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
const json=p=>JSON.parse(read(p));
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const failures=[];let checks=0;
const check=(ok,msg)=>{checks++;if(!ok)failures.push(msg);};

const html=fs.readFileSync(process.argv[2]||path.join(out,'index.html'),'utf8');
// Link and id checks read markup only, not the inlined stylesheet and script.
const markup=html.replace(/<script\b[^>]*>[^]*?<\/script>/g,'').replace(/<style\b[^>]*>[^]*?<\/style>/g,'');
const md=read('research/halal-cultivated/paper/paper.md');
const contract=json('handoffs/claude-mmm/CONTENT-CONTRACT.json');
const prov=json('handoffs/claude-mmm/PROVENANCE.json');
const figData=json('research/halal-cultivated/paper/figure-data.json');
const appx=json('research/halal-cultivated/paper/appendices-data.json');

// 1. Supplied inputs are byte-identical to the handoff record.
for(const f of prov.canonicalInputs){const b=fs.readFileSync(path.join(root,f.path));check(b.length===f.bytes&&sha(b)===f.sha256,'Canonical input changed: '+f.path);}
for(const f of prov.copiedFiles){const b=fs.readFileSync(path.join(root,f.path));check(sha(b)===f.sha256,'Handoff file changed: '+f.path);}
check(sha(md)===contract.sourceManuscriptSha256,'Manuscript hash differs from contract');

// 2. Text normalisation shared by both sides.
const ENT={'&amp;':'&','&lt;':'<','&gt;':'>','&quot;':'"','&#39;':"'"};
const INLINE=new Set(['em','a','span','sup','b','strong','code','bdi','i']);
function htmlText(s){
 return s.replace(/<sup class="nref">[^]*?<\/sup>/g,'').replace(/<sup class="nsep"[^>]*>,<\/sup>/g,'')
  .replace(/<\/?([a-zA-Z0-9]+)\b[^>]*>/g,(m,t)=>INLINE.has(t.toLowerCase())?'':' ')
  .replace(/&(amp|lt|gt|quot|#39);/g,m=>ENT[m]).replace(/[\u2066-\u2069\u200e\u200f]/g,'').replace(/\s+/g,' ').trim();
}
const mdText=s=>s.replace(/<!--[^]*?-->/g,'').replace(/\[\^[^\]]+\]/g,'').replace(/\*([^*\n]+)\*/g,'$1').replace(/\s+/g,' ').trim();
const between=(s,a,b)=>{const i=s.indexOf(a),j=s.indexOf(b,i+1);return s.slice(i,j<0?undefined:j);};
// Remove edition-only material before comparing the paper layer.
const stripEdition=s=>s.replace(/<aside class="margin-note"[^]*?<\/aside>/g,' ').replace(/<svg[^]*?<\/svg>/g,' ')
 .replace(/<p class="edition">[^]*?<\/p>/g,' ').replace(/<p class="bib-meta">[^]*?<\/p>/g,' ').replace(/<p class="backrefs">[^]*?<\/p>/g,' ')
 .replace(/<td class="edition-col">[^]*?<\/td>/g,' ').replace(/<th scope="col" class="edition-col">[^]*?<\/th>/g,' ')
 .replace(/<span class="mono sm fig-no">[^]*?<\/span>/g,' ').replace(/<span class="mono sm">Figure description<\/span>/g,' ')
 .replace(/<a class="skip-fig"[^]*?<\/a>/g,' ').replace(/<figure class="figure-block edition-fig[^]*?<\/figure>/g,' ');
const heroHtml=between(html,'<header class="hero"','</header>');
const paperHtml=between(html,'<div class="paper-divider"','<section class="endnotes"');
const notesHtml=between(html,'<section class="endnotes"','<footer');
const paperText=htmlText(stripEdition(paperHtml));
const notesText=htmlText(stripEdition(notesHtml));

// 3. Every canonical unit appears, in order.
const {blocks,notes}=parseManuscript(md);
const units=[];
for(let i=0;i<blocks.length;i++){
 const b=blocks[i];
 if(b.type==='heading'||b.type==='para')units.push(mdText(b.text));
 // A figure renders its canonical caption first, then the original description.
 else if(b.type==='image'){units.push(mdText(blocks[i+1].text),b.alt);i++;}
 else if(b.type==='list')for(const it of b.items)units.push(mdText(it.text));
 else if(b.type==='table'){for(const c of b.head)units.push(mdText(c));for(const r of b.rows)for(const c of r)units.push(mdText(c));}
}
const heroUnits=units.slice(0,4);
const heroText=htmlText(heroHtml);
for(const u of heroUnits)check(heroText.includes(u),'Title block text missing: '+u.slice(0,80));
let pos=0,missing=0;
for(const u of units.slice(4)){
 if(!u)continue;
 const at=paperText.indexOf(u,pos);
 if(at<0){missing++;check(false,'Canonical text missing or out of order: '+u.slice(0,90));}
 else{check(true,'unit');pos=at+u.length;}
}
let npos=0;
for(const [id,text] of notes){const u=mdText(text);const at=notesText.indexOf(u,npos);check(at>=0,'Note text missing or out of order: '+id);if(at>=0)npos=at+u.length;}

// 4. Headings, notes and every reference occurrence.
const h2=[...html.matchAll(/<h2 id="[^"]+-h">([^]*?)<\/h2>/g)].map(m=>htmlText(m[1]));
const paperH2=h2.filter(t=>t!=='Notes');
check(JSON.stringify(paperH2)===JSON.stringify(contract.headings),'Headings differ from contract: '+JSON.stringify(paperH2));
const noteLis=[...html.matchAll(/<li id="n-([^"]+)" value="(\d+)"/g)];
check(noteLis.length===contract.authoredFootnoteDefinitions,'Note definition count '+noteLis.length);
check(JSON.stringify(noteLis.map(m=>m[1]))===JSON.stringify(contract.noteIds),'Note ids/order differ from contract');
const refs=[...html.matchAll(/<sup class="nref"><a href="#n-([^"]+)" id="(r-[^"]+)"/g)];
check(refs.length===contract.referenceOccurrences,'Reference occurrence count '+refs.length);
check(JSON.stringify(refs.map(m=>m[1]))===JSON.stringify(contract.noteReferenceOrder),'Reference order differs from contract');
for(const [,id,refId] of refs){
 const li=between(html,`<li id="n-${id}"`,'</li>');
 check(li.includes(`href="#${refId}"`),'No return link for '+refId);
}

// 5. Ids unique; every fragment link lands.
const ids=[...markup.matchAll(/\sid="([^"]+)"/g)].map(m=>m[1]);
const idSet=new Set(ids);
check(idSet.size===ids.length,'Duplicate ids: '+ids.filter((x,i)=>ids.indexOf(x)!==i).slice(0,5).join(', '));
const frag=[...markup.matchAll(/href="#([^"]*)"/g)].map(m=>m[1]);
for(const f of frag)check(idSet.has(decodeURIComponent(f)),'Broken fragment #'+f);
// Local asset and file links.
for(const m of markup.matchAll(/(?:href|src)="(?!#|https?:)([^"]+)"/g)){const p=path.normalize(path.join(out,decodeURIComponent(m[1].split('#')[0])));check(fs.existsSync(p)&&p.startsWith(root),'Missing local target '+m[1]);}

// 6. External sources: exactly the manuscript's 60 URLs, shown as written.
const ext=new Set([...markup.matchAll(/href="(https?:[^"]+)"/g)].map(m=>m[1].replace(/&amp;/g,'&')));
const want=new Set(contract.sourceUrls);
check(ext.size===want.size&&[...want].every(u=>ext.has(u)),'External URL set differs: extra '+[...ext].filter(u=>!want.has(u)).join(' ')+' missing '+[...want].filter(u=>!ext.has(u)).join(' '));
for(const m of html.matchAll(/<a class="url" href="([^"]+)"[^>]*>([^<]*)<\/a>/g))check(m[1]===m[2],'URL text differs from href: '+m[1]);
check(!/<(?:script|img|iframe|link)\b[^>]*(?:src|href)=["']https?:/i.test(html),'Automatic external asset load');

// 7. Figures against their data.
for(const f of contract.originalFigures)check(html.includes(f.alt.replace(/&/g,'&amp;')),'Original figure description missing: '+f.path);
for(const c of figData.countries)c.scope_labels.forEach((l,j)=>{
 check(new RegExp(`<title>${c.country.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')} · [^<]*: ${l.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')}</title>`).test(html),`Fig. 2 cell ${c.country}/${j} label`);
 const id='appx-b-'+(c.country==='UAE'?'united-arab-emirates':c.country.toLowerCase().replace(/\s+/g,'-'));
 const href=countryState(l)==='admitted'?id:id+'-gap';
 check(html.includes(`href="#${href}" id="f2-${id}-${j}"`),`Fig. 2 cell ${c.country}/${j} target`);
});
const f3=[...html.matchAll(/<a class="f-pt" href="#src-([^"]+)" id="f3-/g)].map(m=>m[1]);
check(f3.length===contract.sourceFigureCounts.canonical_records,'Fig. 3 point count '+f3.length);
check(JSON.stringify(f3)===JSON.stringify(['verified_with_note','held','not_retrieved'].flatMap(v=>appx.sources.filter(s=>s.verdict===v).map(s=>s.key))),'Fig. 3 point order differs from Appendix D');
const f3a=[...html.matchAll(/id="f3a-([^"]+)"/g)].map(m=>m[1]);
check(f3a.length===contract.sourceFigureCounts.admitted_article_reading_scopes.full_text_scoped_passages+contract.sourceFigureCounts.admitted_article_reading_scopes.abstract_only,'Fig. 3 article panel count');
check((html.match(/class="m-copper"/g)||[]).length===3,'Copper points: series mark, Fig. 3 and R3 only');
const r2=[...html.matchAll(/<a class="f-pt" href="#slot-([^"]+)" id="r2-/g)].map(m=>m[1]);
check(r2.length===45,'R2 point count '+r2.length);
for(const id of r2){const row=between(html,`<tr id="slot-${id}"`,'</tr>');const cells=[...row.matchAll(/<td[^>]*>([^]*?)<\/td>/g)].map(m=>htmlText(m[1]));const slot=appx.school_slots.find(s=>s.original_id===id);check(slot&&cells.length===2,'Slot row '+id);}

// 8. Status, review state and language markup.
check(heroText.includes('AI-assisted working draft; human verification pending'),'Draft status not near title');
check(/Final author read — pending/.test(heroText)&&/Human scholarly review — pending/.test(heroText),'Review states not shown');
const visible=html.replace(/<script[^]*?<\/script>/g,'').replace(/<title>[^]*?<\/title>/g,'').replace(/<desc>[^]*?<\/desc>/g,'')
 .replace(/<span lang="(ar|ur)" dir="rtl">[^<]*<\/span>/g,'').replace(/<a class="url"[^>]*>[^<]*<\/a>/g,'').replace(/"[^"]*"/g,'""');
check(!/[\u0600-\u06ff]/.test(visible),'Arabic-script text outside a lang/dir span');
check(/<span lang="ur" dir="rtl">/.test(html),'Urdu title not marked lang="ur"');

const result={status:failures.length?'FAIL':'PASS',checks,canonicalUnits:units.length,missingUnits:missing,notes:noteLis.length,references:refs.length,ids:ids.length,fragmentLinks:frag.length,externalUrls:ext.size,fig3Points:f3.length,r2Points:r2.length,failures:failures.slice(0,40),failureCount:failures.length};
console.log(JSON.stringify(result,null,2));
if(failures.length)process.exitCode=1;
