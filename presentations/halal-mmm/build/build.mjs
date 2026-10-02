// Build presentations/halal-mmm/index.html from the canonical manuscript and
// its supplied data. Reads only; never writes outside presentations/halal-mmm/.
//   node presentations/halal-mmm/build/build.mjs
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {parseManuscript,inline,esc,plain,slug,wrapArabic} from './markdown.mjs';
import * as F from './figures.mjs';
import * as E from './editorial.mjs';

const here=path.dirname(fileURLToPath(import.meta.url));
const out=path.resolve(here,'..');
const root=path.resolve(out,'../..');
const rel=p=>path.relative(root,p).split(path.sep).join('/');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
const json=p=>JSON.parse(read(p));
const sha=s=>crypto.createHash('sha256').update(s).digest('hex');
const assert=(ok,msg)=>{if(!ok)throw Error(msg);};

const P='research/halal-cultivated/paper/';
const inputs=['presentations/halal-mmm/assets/mmm.css','presentations/halal-mmm/assets/mmm.js',P+'paper.md',P+'appendices-data.json',P+'source-register.json',P+'figure-data.json','handoffs/claude-mmm/CONTENT-CONTRACT.json'];
const md=read(P+'paper.md');
const appx=json(P+'appendices-data.json');
const register=json(P+'source-register.json');
const figData=json(P+'figure-data.json');
const contract=json('handoffs/claude-mmm/CONTENT-CONTRACT.json');
assert(sha(md)===contract.sourceManuscriptSha256,'paper.md differs from the content contract hash');

const {blocks,notes}=parseManuscript(md);
const noteIds=[...notes.keys()];
const noteNo=new Map(noteIds.map((id,i)=>[id,i+1]));
assert(noteIds.length===contract.authoredFootnoteDefinitions,'Unexpected note count');

// Source keys: canonical keys and aliases from the register.
const canonical=new Map();
for(const r of register){canonical.set(r.key,r.key);for(const a of r.aliases)canonical.set(a,r.key);}
const sourceByKey=new Map(appx.sources.map(s=>[s.key,s]));

// Pass 1: bibliography keys and which notes cite each key.
const bibStart=blocks.findIndex(b=>b.type==='heading'&&b.text==='Bibliography');
const bibKeys=new Set();
for(const b of blocks.slice(bibStart+1))if(b.type==='para'){const m=/\[([A-Z][A-Z0-9-]*)\]\s*$/.exec(b.text);assert(m,'Bibliography entry without key');bibKeys.add(canonical.get(m[1])??m[1]);}
const citedBy=new Map();
for(const [id,text] of notes)for(const m of text.matchAll(/\[([A-Z][A-Z0-9-]*)\]/g)){const k=canonical.get(m[1]);if(!k)continue;if(!citedBy.has(k))citedBy.set(k,[]);if(!citedBy.get(k).includes(id))citedBy.get(k).push(id);}

// Rendering state.
let section={id:'top',label:'Title'};
let figureCtx=null;
const occurrences=new Map();// note id -> [{refId,label}]
let xrefCount=0;
const ids=new Set();
const useId=id=>{assert(!ids.has(id),'Duplicate id '+id);ids.add(id);return id;};

function noteRef(id){
 assert(notes.has(id),'Unknown note '+id);
 const list=occurrences.get(id)??[];const k=list.length+1;
 const refId=useId(`r-${id}-${k}`);
 list.push({refId,label:figureCtx?figureCtx.label:section.label});occurrences.set(id,list);
 const n=noteNo.get(id);
 return `<sup class="nref"><a href="#n-${id}" id="${refId}" aria-label="Note ${n}">${n}</a></sup>`;
}
function sourceKey(key){
 const k=canonical.get(key);if(!k)return null;
 const href=bibKeys.has(k)?'#bib-'+k:'#src-'+k;
 return `<a class="srckey" href="${href}">[${esc(key)}]</a>`;
}
// Cross-references to figures, appendices and numbered sections (markup only).
function crossRef(html){
 return html.replace(/\b(Figure ([123])|Appendix ([A-E])|[Ss]ection (1[0-3]|[1-9])(?![0-9]|\.[0-9]))\b/g,(m,all,fig,app,sec)=>{
  const href=fig?'fig-'+fig:app?'appx-'+app.toLowerCase():'sec-'+sec;
  if(figureCtx&&href===figureCtx.id)return m;
  return `<a class="xref" href="#${href}" id="${useId('x-'+(++xrefCount))}">${m}</a>`;
 });
}
const ctx={noteRef,sourceKey,crossRef};
const noCtx={noteRef,sourceKey,crossRef:null};
const r=(s,c=ctx)=>inline(s,c);

// Heading ids.
let h2id=null;
function headingId(level,text){
 let m;
 if(level===2){
  if(text==='Abstract')return 'sec-abstract';
  if((m=/^(\d+)\.\s/.exec(text)))return 'sec-'+m[1];
  if((m=/^Appendix ([A-E])\./.exec(text)))return 'appx-'+m[1].toLowerCase();
  return slug(text);
 }
 if((m=/^(\d+)\.(\d+)\s/.exec(text)))return `sec-${m[1]}-${m[2]}`;
 return h2id+'-'+slug(text);
}
function sectionLabel(level,text,id){
 let m;
 if(text==='Abstract')return 'Abstract';
 if((m=/^(\d+(?:\.\d+)?)\.?\s/.exec(text)))return '§'+m[1];
 if((m=/^Appendix ([A-E])\./.exec(text)))return 'App. '+m[1];
 if(level===3&&section.label.startsWith('App.'))return section.label.split(' ').slice(0,2).join(' ');
 return text;
}

// Appendix row maps.
const slotPrefix={'Hanafi sources':'HN','Maliki sources':'M','Shafii sources':'S','Hanbali sources':'HB','Sistani: a named Jafari authority':'J'};
const slotsById=new Map(appx.school_slots.map(s=>[s.original_id,s]));
const verdictTables={'Held — individual records':'held','Not retrieved — individual records':'not_retrieved','Qualified with limitations — individual records':'verified_with_note'};
const countryIds={};
for(const c of figData.countries)countryIds[c.country]='appx-b-'+slug(c.country==='UAE'?'United Arab Emirates':c.country);
const slotTraditions=[];// for Fig. R2
const hostOf=u=>{try{return new URL(u).hostname.replace(/^www\./,'');}catch{return '';}};

function renderTable(b,h3){
 const tradition=h2id==='appx-a'?h3:null;
 const verdict=h2id==='appx-d'?verdictTables[h3]:null;
 const cols=b.head.length;
 const wide=cols>=3;
 let head=b.head.map((c,i)=>`<th scope="col"${b.align[i]?` class="a-${b.align[i]}"`:''}>${r(c)}</th>`).join('');
 if(verdict)head+='<th scope="col" class="edition-col">Record <span class="mono sm">(edition)</span></th>';
 let rows='';
 const list=verdict?appx.sources.filter(s=>s.verdict===verdict):null;
 if(verdict)assert(list.length===b.rows.length,'Appendix D row count differs for '+h3);
 const slotList=[];
 b.rows.forEach((cells,i)=>{
  let rowId='';
  if(tradition){
   const id=`${slotPrefix[tradition]}-Q${i+1}`;const slot=slotsById.get(id);
   assert(slot&&cells[0]===`${slot.question_number}. ${slot.question}`,'Appendix A row mismatch '+id);
   rowId=useId('slot-'+id);slotList.push({id,state:F.slotState(cells[2])});
  }
  let extra='';
  if(verdict){
   const s=list[i];
   const title=(s.key==='SG-LIST'?'SFA novel-food process list':s.title);
   const squash=t=>t.replace(/\s+/g,'');
   assert(squash(cells[0]).startsWith(squash(title).slice(0,20)),'Appendix D row mismatch '+s.key);
   rowId=useId('src-'+s.key);
   const alias=s.aliases.length?` <span class="mono sm">alias ${s.aliases.map(esc).join(', ')}</span>`:'';
   const cite=bibKeys.has(s.key)?`<a href="#bib-${s.key}">Bibliography entry</a>`:`<span class="host" dir="ltr">${esc(hostOf(s.url))}</span><span class="uncited">not cited in the notes</span>`;
   extra=`<td class="edition-col"><span class="mono sm rowkey">${esc(s.key)}</span>${alias}<br>${cite}</td>`;
  }
  const tds=cells.map((c,j)=>j===0?`<th scope="row">${r(c)}</th>`:`<td${b.align[j]?` class="a-${b.align[j]}"`:''}>${r(c)}</td>`).join('');
  rows+=`<tr${rowId?` id="${rowId}"`:''}>${tds}${extra}</tr>`;
 });
 if(tradition)slotTraditions.push({name:tradition==='Sistani: a named Jafari authority'?'Sistani':tradition.replace(' sources',''),short:tradition==='Sistani: a named Jafari authority'?'Sistani':tradition.replace(' sources',''),anchor:h2id+'-'+slug(h3),slots:slotList});
 const label=(h3&&h2id!=='sec-9'&&h2id!=='sec-10'?h3:b.head.join(', '));
 return (wide?'<p class="scroll-hint" aria-hidden="true">Scroll sideways for every column →</p>':'')+`<div class="table-wrap${wide?' span-rail':''}" role="region" aria-label="${esc('Table: '+plain(label))}" tabindex="0"><table class="data"><thead><tr>${head}</tr></thead><tbody>${rows}</tbody></table></div>`;
}

// Figures placed at the canonical image positions.
const figByImage={'figures/figure-1-process.png':{id:'fig-1',label:'Fig. 1 — From starting cells to a food product',svg:()=>F.fig1(),cls:'',legend:E.captions.fig1},
 'figures/figure-3-audit.png':{id:'fig-3',label:'Fig. 3 — Evidence available to this paper',svg:()=>F.fig3(appx.sources,figData.counts),cls:'',legend:E.captions.fig3,skip:true},
 'figures/figure-2-countries.png':{id:'fig-2',label:'Fig. 2 — Documentary scope by jurisdiction',svg:()=>F.fig2(figData.countries,countryIds).svg,cls:' full',legend:E.captions.fig2,skip:true}};
for(const f of contract.originalFigures)assert(Object.keys(figByImage).some(k=>f.path.endsWith(k.replace('figures/','figures/'))),'Unmapped figure '+f.path);

function figureBlock({id,label,svg,cls,legend,skip},captionHtml,alt){
 useId(id);
 const skipLink=skip?`<a class="skip-fig" href="#${id}-end">Skip the record links in ${esc(label.split(' — ')[0])}</a>`:'';
 return `<figure class="figure-block${cls}" id="${id}" aria-labelledby="${id}-cap">${skipLink}<div class="fig-body scroll-x" tabindex="-1">${svg()}</div><p class="scroll-hint" aria-hidden="true">Scroll sideways for the full figure →</p><figcaption id="${id}-cap"><span class="mono sm fig-no">${esc(label)}</span>${captionHtml}${legend??''}<p class="alt-text"><span class="mono sm">Figure description</span> ${esc(alt)}</p></figcaption><span id="${id}-end" class="fig-end"></span></figure>`;
}
function editionFigure(id,cap,svg,cls=''){
 useId(id);
 return `<figure class="figure-block edition-fig${cls}" id="${id}" aria-labelledby="${id}-cap"><div class="fig-body scroll-x" tabindex="-1">${svg}</div><p class="scroll-hint" aria-hidden="true">Scroll sideways for the full figure →</p><figcaption id="${id}-cap"><span class="mono sm fig-no">${esc(cap.label)}</span>${cap.html}</figcaption></figure>`;
}

// Rail notes keyed by the start of the paragraph they gloss.
const pendingRail=new Map(E.railNotes.map(n=>[n.before,n]));
function railFor(text){
 for(const [k,n] of pendingRail)if(text.startsWith(k)){pendingRail.delete(k);return `<aside class="margin-note" aria-label="${esc(n.tag)}"><span class="mono sm tag">${esc(n.tag)}</span><p>${n.html}</p></aside>`;}
 return '';
}

// Pass 2: render the paper.
assert(blocks[0].type==='heading'&&blocks[0].level===1,'Title expected');
const title=blocks[0].text,statusLine=blocks[1].text,subtitle=blocks[2].text,byline=blocks[3].text;
assert(statusLine==='AI-assisted working draft; human verification pending','Status line changed');
let body='',open=false,h3text=null,figR2placed=false,figR3placed=false;
const nav=[];
for(let i=4;i<blocks.length;i++){
 const b=blocks[i];
 if(b.type==='heading'){
  const id=headingId(b.level,b.text);
  if(b.level===2){
   if(open)body+='</section>';
   h2id=id;h3text=null;
   section={id,label:sectionLabel(2,b.text,id)};
   const cls=id.startsWith('appx')?'appendix':id==='bibliography'?'bibliography':'paper-sec';
   body+=`<section class="${cls}" id="${useId(id)}" aria-labelledby="${id}-h"><h2 id="${useId(id+'-h')}">${secNumber(b.text)}</h2>`;
   open=true;nav.push({id,text:b.text});
  }else{
   h3text=b.text;
   section={id,label:sectionLabel(3,b.text,id)};
   body+=`<h3 id="${useId(id)}">${esc(b.text)}</h3>`;
  }
  continue;
 }
 if(b.type==='image'){
  const f=figByImage[b.src];assert(f,'Unknown image '+b.src);
  const cap=blocks[i+1];assert(cap?.type==='para'&&cap.text.startsWith('Figure '),'Figure caption expected');
  figureCtx={id:f.id,label:f.label.split(' — ')[0]};
  body+=figureBlock(f,`<p class="canonical-caption" data-kind="${cap.kind??''}">${r(cap.text)}</p>`,b.alt);
  figureCtx=null;i++;continue;
 }
 if(b.type==='table'){body+=renderTable(b,h3text);continue;}
 if(b.type==='list'){body+='<ul class="gap-list">'+b.items.map(it=>`<li data-kind="${it.kind??''}">${r(it.text)}</li>`).join('')+'</ul>';continue;}
 if(b.type==='para'){
  if(section.id==='bibliography'){body+=bibEntry(b);continue;}
  body+=railFor(b.text);
  let pid='';
  if(h2id==='appx-b'&&b.text.startsWith('Bounded gap:'))pid=` id="${useId(countryIds[Object.keys(countryIds).find(c=>section.id===countryIds[c])]+'-gap')}"`;
  body+=`<p${pid} data-kind="${b.kind??''}">${r(b.text)}</p>`;
  // Edition figures after their anchoring paragraphs.
  if(!figR2placed&&b.text.startsWith('The research frame comprises nine questions')){body+='%%FIG-R2%%';figR2placed=true;}
  if(!figR3placed&&b.text.startsWith('The quantitative handoff remains blocked by missing compatible inputs.')&&h2id==='sec-11'){body+=editionFigure('fig-r3',E.captions.r3,F.figR3(),' full');figR3placed=true;}
  continue;
 }
 throw Error('Unhandled block '+b.type);
}
if(open)body+='</section>';
assert(figR2placed&&figR3placed,'Edition figures not placed');
assert(pendingRail.size===0,'Unplaced rail notes: '+[...pendingRail.keys()].join(' | '));

function secNumber(text){
 const m=/^(\d+\.|Appendix [A-E]\.)\s(.*)$/.exec(text);
 return m?`<span class="secno">${esc(m[1])}</span> ${esc(m[2])}`:esc(text);
}
function bibEntry(b){
 const m=/\[([A-Z][A-Z0-9-]*)\]\s*$/.exec(b.text);const key=canonical.get(m[1])??m[1];
 const s=sourceByKey.get(key);
 const cites=(citedBy.get(key)??[]).map(id=>`<a href="#n-${id}">${noteNo.get(id)}</a>`).join(', ');
 const state=s?{verified_with_note:'Qualified with limitations',held:'Held',not_retrieved:'Not retrieved'}[s.verdict]+' · '+esc(s.reading_scope):'';
 const meta=`<p class="bib-meta"><span class="mono sm">Register</span> ${state}${cites?` · cited in notes ${cites}`:''}${s?` · <a href="#src-${key}">Appendix D record</a>`:''}</p>`;
 const own={noteRef,crossRef:null,sourceKey:k=>canonical.get(k)===key?`<span class="srckey">[${esc(k)}]</span>`:sourceKey(k)};
 return railFor(b.text)+`<div class="bib" id="${useId('bib-'+key)}"><p>${r(b.text,own)}</p>${meta}</div>`;
}

// Fig. R2 needs the Appendix A tables, which render later in the document.
const questions=appx.school_slots.filter(s=>s.tradition==='Hanafi sources').map(s=>`${s.question_number}. ${s.question}`);
const r2=F.figR2(slotTraditions,questions);
assert(r2.totals.attributed+r2.totals.inference+r2.totals.none+r2.totals.open===45,'Slot total');
body=body.replace('%%FIG-R2%%',editionFigure('fig-r2',E.captions.r2,r2.svg,' full'));

// Endnotes, grouped by the part of the paper they serve.
const groupOf=id=>id.startsWith('a-')?['notes-abstract','Abstract']:/^s(\d+)-/.test(id)?['notes-s'+/^s(\d+)-/.exec(id)[1],'Section '+/^s(\d+)-/.exec(id)[1]]:id==='fig2'?['notes-fig2','Figure 2']:id.startsWith('abd-')?['notes-abd','Appendices A, B and D']:['notes-gl','Appendix E'];
let notesHtml='',curGroup=null,refTotal=0;
for(const id of noteIds){
 const [gid,glabel]=groupOf(id);
 if(gid!==curGroup){if(curGroup)notesHtml+='</ol>';notesHtml+=`<h3 id="${useId(gid)}">${esc(glabel)}</h3><ol class="notes" start="${noteNo.get(id)}">`;curGroup=gid;}
 const occ=occurrences.get(id)??[];assert(occ.length,'Note never referenced: '+id);refTotal+=occ.length;
 const back=occ.map((o,k)=>`<a class="backref" href="#${o.refId}" aria-label="Back to reference ${k+1} of ${occ.length}, ${esc(o.label)}">${esc(o.label)} ↩</a>`).join(' ');
 notesHtml+=`<li id="${useId('n-'+id)}" value="${noteNo.get(id)}" data-note="${id}"><p>${r(notes.get(id),noCtx)}</p><p class="backrefs"><span class="mono sm">Cited at</span> ${back}</p></li>`;
}
notesHtml+='</ol>';
assert(refTotal===contract.referenceOccurrences,`Reference occurrences ${refTotal} ≠ ${contract.referenceOccurrences}`);

// Hero, guide and contents.
const c=figData.counts;
const slotEmpty=r2.totals.none+r2.totals.open;
const noCert=figData.countries.filter(x=>F.countryState(x.scope_labels[2])==='missing').length;
const readout=[['6',E.readoutLabels.questions(6),'#fig-r1'],[String(c.canonical_records),E.readoutLabels.records(c.canonical_records,c.verdicts.verified_with_note,c.verdicts.held,c.verdicts.not_retrieved),'#fig-3'],['45',E.readoutLabels.slots(45,slotEmpty),'#fig-r2'],[String(figData.countries.length),E.readoutLabels.countries(figData.countries.length,noCert),'#fig-2']];
const hero=`<header class="hero" id="${useId('top')}">
<div class="masthead">${F.seriesMark(48)}<span class="wordmark">Meaning, Man and Model</span></div>
<p class="mono eyebrow">Research working paper — 2 October 2026</p>
<h1>${esc(title)}</h1>
<p class="status"><span class="status-mark" aria-hidden="true"></span>${esc(statusLine)}</p>
<p class="thesis">${esc(subtitle)}</p>
<div class="meta-row"><span class="byline">${esc(byline)}</span><span class="mono sm">Final author read — pending</span><span class="mono sm">Human scholarly review — pending</span></div>
</header>`;
const guide=`<section class="guide" id="${useId('overview')}" aria-labelledby="guide-label">
<p class="mono lg guide-label" id="guide-label">${esc(E.guideLabel)}</p>
<p class="lead">${esc(E.lead)}</p>
<aside class="hero-readout" aria-label="The record at a glance">${readout.map(([n,t,h])=>`<a class="readout-row" href="${h}" id="${useId('ro-'+h.slice(1))}"><b>${n}</b><span>${esc(t)}</span></a>`).join('')}</aside>
<div class="tldr"><h2 class="mono lg" id="${useId('findings')}">Findings</h2><ol class="findings">${E.findings.map(f=>`<li><span class="mono sm layer">${esc(f.layer)}</span> ${f.html} <span class="refs">${f.refs.map(([h,l])=>`<a href="#${h}" id="${useId('fd-'+h+'-'+slug(f.layer))}">${esc(l)}</a>`).join(' · ')}</span></li>`).join('')}</ol></div>
${editionFigure('fig-r1',E.captions.r1,F.figR1())}
</section>`;
const divider=`<div class="paper-divider" id="${useId('paper')}"><p class="mono lg">${esc(E.dividerLabel)}</p><p>${esc(E.dividerText)}</p></div>`;
const navLabel=t=>{let m;if(t==='Abstract')return ['·','Abstract'];if((m=/^(\d+)\.\s(.*)$/.exec(t)))return [m[1],m[2]];if((m=/^Appendix ([A-E])\.\s(.*)$/.exec(t)))return [m[1],m[2]];return ['·',t];};
const navItems=[...nav.map(n=>[n.id,...navLabel(n.text)]),['notes','·','Notes']];
const navList=navItems.map(([id,n,t])=>`<li><a href="#${id}"><span class="mono sm">${esc(n)}</span><span class="t">${esc(t)}</span></a></li>`).join('');
const leftnav=`<nav class="leftnav" id="toc" aria-label="Contents"><div class="leftnav-inner"><div class="toc-head"><span class="mono sm">Contents</span><button type="button" class="toc-close" id="tocClose" hidden>Close</button></div><a class="start-link" href="#top"><span class="mono sm">Start</span><span class="t">Overview and findings</span></a><ol>${navList}</ol></div></nav>`;
const tocMobile=`<details class="toc-mobile" id="contents"><summary><span class="mono">Contents</span></summary><ol>${navItems.map(([id,n,t])=>`<li><a href="#${id}"><span class="mono sm">${esc(n)}</span> ${esc(t)}</a></li>`).join('')}</ol></details>`;

const notesSection=`<section class="endnotes" id="${useId('notes')}" aria-labelledby="notes-h"><h2 id="${useId('notes-h')}">Notes</h2><p class="notes-intro">The ${noteIds.length} notes of the manuscript, numbered in order of definition. Notes cited more than once appear once here, with a return link to each of the ${refTotal} places they are cited.</p>${notesHtml}</section>`;

const pdf='../../research/halal-cultivated/paper/exports/cultivated-chicken-halal-working-paper.pdf';
const colophon=`<footer class="colophon-wrap"><div class="related"><span class="mono sm">The paper in other forms</span><a href="../../research/halal-cultivated/paper/paper.md">Canonical Markdown</a><a href="../../research/halal-cultivated/paper/index.html">Plain reader</a><a href="${pdf}">Reviewed PDF</a><a href="../../research/halal-cultivated/paper/exports/cultivated-chicken-halal-working-paper.docx">Word</a><a href="../../research/halal-cultivated/paper/source-register.json">Source register (JSON)</a></div>
<div class="colophon"><span class="mono sm">${esc(E.colophon.series)}</span><span class="mono sm">${esc(E.colophon.status)}</span><span class="mono sm">No institutional or mentor endorsement is implied</span><span class="fonts">${esc(E.colophon.fonts)} <button type="button" class="link-button" id="fontToggle" hidden aria-pressed="false">Load web fonts from Google Fonts</button></span><span class="mono sm faint">${E.colophon.year}</span></div></footer>`;

// Stylesheet and script are inlined so the page works from file://, from
// tools/serve.mjs (which serves only listed MIME types) and as a single file.
const css=fs.readFileSync(path.join(out,'assets/mmm.css'),'utf8');
const js=fs.readFileSync(path.join(out,'assets/mmm.js'),'utf8');
assert(!css.includes('</style')&&!js.includes('</script'),'Asset would close its inline element');
const html=`<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="color-scheme" content="light dark">
<title>${esc(title)} — Meaning, Man and Model</title>
<meta name="description" content="${esc(subtitle)}. AI-assisted working draft; human verification pending.">
<script>(function(){var d=document.documentElement,t=null;try{t=localStorage.getItem('mmm-theme');}catch(e){}if(t!=='dark'&&t!=='light'){t=window.matchMedia&&window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';}d.setAttribute('data-theme',t);d.className+=' js';})();</script>
<style>
${css}</style>
</head>
<body>
<a class="skip" href="#main">Skip to the paper</a>
<button class="theme-toggle" id="themeToggle" type="button" aria-pressed="false" hidden>Dark</button>
<button class="toc-button" id="tocButton" type="button" aria-controls="toc" aria-expanded="false" hidden>Contents</button>
<a class="return-chip" id="returnChip" href="#top" hidden>← Return</a>
<div class="page"><div class="frame">
${leftnav}
<main class="content" id="main" tabindex="-1">
${hero}
${tocMobile}
${guide}
${divider}
${body}
${notesSection}
${colophon}
</main>
</div></div>
<script>
${js}</script>
</body></html>
`;
fs.writeFileSync(path.join(out,'index.html'),html);
const record={generator:'presentations/halal-mmm/build/build.mjs',inputs:Object.fromEntries(inputs.map(p=>[p,sha(read(p))])),output:{'presentations/halal-mmm/index.html':sha(html)},notes:noteIds.length,referenceOccurrences:refTotal,figures:{original:['fig-1','fig-3','fig-2'],edition:['fig-r1','fig-r2','fig-r3']},fig2Cells:F.fig2(figData.countries,countryIds).tally,slots:r2.totals,humanReview:'pending',published:false};
fs.writeFileSync(path.join(out,'build-record.json'),JSON.stringify(record,null,2)+'\n');
console.log(JSON.stringify({output:rel(path.join(out,'index.html')),bytes:Buffer.byteLength(html),notes:noteIds.length,references:refTotal,ids:ids.size,slots:r2.totals}));
