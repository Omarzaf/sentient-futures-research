// Inline SVG figures for the MMM edition. Everything here is line geometry
// bound to theme tokens through CSS classes (see assets/mmm.css, "figures").
// Positions are categorical; spacing is for readability and never encodes a
// magnitude, except that one point stands for one record in Fig. 3 and R2.
import {esc,slug} from './markdown.mjs';

const r1=n=>Math.round(n*10)/10;

// Greedy line wrap by an approximate character budget.
export function wrap(text,max){
 const words=String(text).split(/\s+/);const lines=[];let cur='';
 for(const w of words){if(cur&&(cur+' '+w).length>max){lines.push(cur);cur=w;}else cur=cur?cur+' '+w:w;}
 if(cur)lines.push(cur);return lines;
}
function textLines(lines,x,y,cls,lh,anchor='start'){
 return `<text class="${cls}" x="${x}" y="${y}" text-anchor="${anchor}">`+lines.map((l,i)=>`<tspan x="${x}" dy="${i?lh:0}">${esc(l)}</tspan>`).join('')+'</text>';
}
const svgOpen=(id,w,h,role,title,desc,extra='')=>`<svg class="fig-svg" id="${id}" viewBox="0 0 ${w} ${h}" width="${w}" height="${h}" role="${role}" aria-labelledby="${id}-t ${id}-d"${extra}><title id="${id}-t">${esc(title)}</title><desc id="${id}-d">${esc(desc)}</desc>`;

// Documentary-state marks shared by Fig. 2 and Fig. 3: filled = admitted,
// hollow = held, dashed hollow = not retrieved / not located / not established.
export function mark(state,x,y,r=3.4){
 if(state==='admitted')return `<circle class="m-filled" cx="${r1(x)}" cy="${r1(y)}" r="${r}"/>`;
 if(state==='held')return `<circle class="m-hollow" cx="${r1(x)}" cy="${r1(y)}" r="${r}"/>`;
 if(state==='copper')return `<circle class="m-copper" cx="${r1(x)}" cy="${r1(y)}" r="${r+0.4}"/>`;
 return `<circle class="m-dashed" cx="${r1(x)}" cy="${r1(y)}" r="${r}"/>`;
}

// R1 — six questions as a route through sections 5–9, ending at the
// quantitative handoff that section 11.2 records as unfilled.
export function figR1(){
 const st=[
  ['01','Donor / procurement','sec-5','§5'],['02','Culture inputs','sec-6','§6'],['03','Transformation','sec-7','§7'],
  ['04','Edibility','sec-8','§8'],['05','Certification','sec-9','§9'],['06','Food authorization','sec-9-4','§9.4']];
 const W=760,H=200,y=96,x0=52,dx=108;
 const xs=st.map((_,i)=>x0+i*dx);
 let s=svgOpen('fig-r1-svg',W,H,'group','Fig. R1: six questions kept apart, as a route through sections 5 to 9',
  'Six stations on one rule, in the order the paper examines them: donor and procurement (section 5), culture inputs (section 6), transformation (section 7), edibility (section 8), certification (section 9) and food authorization (section 9.4). A bracket groups the first four as questions about the material and how it was made, and the last two as decisions by institutions. After a closed gate, a dashed segment leads to the quantitative Phase Two handoff (section 11.2), which this paper does not fill.');
 // brackets
 const br=(a,b,label)=>`<g class="f-bracket"><path class="f-struct" d="M${a} 52 V44 H${b} V52"/>`+`<rect class="f-plate" x="${r1((a+b)/2-label.length*3.9-6)}" y="36" width="${r1(label.length*7.8+12)}" height="16"/>`+textLines([label],(a+b)/2,48,'f-label',0,'middle')+'</g>';
 s+=br(xs[0]-24,xs[3]+24,'The material and how it was made');
 s+=br(xs[4]-24,xs[5]+24,'Decisions by institutions');
 s+=`<line class="f-rule" x1="${xs[0]}" y1="${y}" x2="${xs[5]}" y2="${y}"/>`;
 // gate and dashed handoff
 const gx=xs[5]+50,hx=W-50;
 s+=`<line class="f-strong" x1="${gx-2}" y1="${y-12}" x2="${gx-2}" y2="${y+12}"/><line class="f-strong" x1="${gx+2}" y1="${y-12}" x2="${gx+2}" y2="${y+12}"/>`;
 s+=`<line class="f-rule" x1="${xs[5]}" y1="${y}" x2="${gx-2}" y2="${y}"/><line class="f-dash" x1="${gx+2}" y1="${y}" x2="${hx}" y2="${y}"/>`;
 st.forEach(([n,name,href,sec],i)=>{
  const x=xs[i];
  s+=`<a class="f-link" href="#${href}" id="r1-${href}"><title>${esc(name)} — section ${sec.slice(1)}</title><rect class="f-hit" x="${x-50}" y="${y-30}" width="100" height="128"/>`;
  s+=`<circle class="f-station" cx="${x}" cy="${y}" r="6"/>`+textLines([n],x,y-18,'f-label',0,'middle');
  s+=textLines(wrap(name,13),x,y+30,'f-name',16,'middle')+textLines([sec],x,y+80,'f-label f-sec',0,'middle')+'</a>';
 });
 s+=`<a class="f-link" href="#sec-11-2" id="r1-handoff"><title>Quantitative handoff — section 11.2</title><rect class="f-hit" x="${hx-44}" y="${y-30}" width="88" height="128"/>`;
 s+=`<circle class="m-dashed f-station-d" cx="${hx}" cy="${y}" r="6"/>`+textLines(['Quantitative','handoff'],hx,y+30,'f-name',16,'middle')+textLines(['§11.2'],hx,y+80,'f-label f-sec',0,'middle')+'</a>';
 return s+'</svg>';
}

// Figure 1 — the reviewed process figure, redrawn with its labels unchanged.
export function fig1(){
 const W=760,H=470;
 const stages=[['Donor / egg','source'],['Founder cells','and bank'],['Culture','and inputs'],['Harvest / wash','formulation']];
 const qs=[
  ['1','Donor / procurement','Species, tissue, collection and slaughter history','sec-5'],
  ['2','Culture inputs','Origin, function, carryover and removal of each input','sec-6'],
  ['3','Transformation','Named authority’s criterion and relevant process evidence','sec-7'],
  ['4','Edibility','Status of the final object under the attributed dietary rule','sec-8'],
  ['5','Certification','Applicable route and an actual certificate for that product','sec-9'],
  ['6','Food authorization','Regulator, product, process, territory and effective date','sec-9-4']];
 let s=svgOpen('fig-1-svg',W,H,'group','Figure 1: from starting cells to a food product',
  'Production sequence from donor or egg source through founder cells and bank, culture and inputs, harvest and formulation; six separate analytical questions. Four manufacturing stages sit on one rule joined by arrows: donor or egg source; founder cells and bank; culture and inputs; harvest, wash and formulation. Below them, the six questions of this paper’s framework: donor and procurement, culture inputs, transformation, edibility, certification and food authorization. Arrows show manufacturing sequence only.');
 const xs=[96,286,476,666],y=58;
 s+=`<line class="f-rule" x1="${xs[0]}" y1="${y}" x2="${xs[3]}" y2="${y}"/>`;
 for(let i=0;i<3;i++){const mx=(xs[i]+xs[i+1])/2;s+=`<path class="f-struct" d="M${mx-4} ${y-5} L${mx+3} ${y} L${mx-4} ${y+5}"/>`;}
 stages.forEach((l,i)=>{s+=`<circle class="f-station" cx="${xs[i]}" cy="${y}" r="6"/>`+textLines(l,xs[i],y+30,'f-name',17,'middle');});
 s+=textLines(['Alternative sources include biopsy, post-mortem tissue and embryonic routes.','Banking, media and final formulation vary by process; this is not a universal recipe.'],40,138,'f-note',18);
 s+=`<line class="f-hair" x1="40" y1="180" x2="${W-40}" y2="180"/>`;
 qs.forEach(([n,name,detail,href],i)=>{
  const col=i<3?0:1,row=i%3,x=40+col*362,yy=222+row*70;
  s+=`<a class="f-link" href="#${href}" id="f1-${href}"><title>${n} ${esc(name)} — opens section ${href.replace('sec-','').replace('-','.')}</title><rect class="f-hit" x="${x-8}" y="${yy-22}" width="350" height="62"/>`;
  s+=textLines([n],x,yy,'f-label f-qno',0)+textLines([name],x+22,yy,'f-name f-strongname',0)+textLines(wrap(detail,46),x+22,yy+20,'f-note',16)+'</a>';
 });
 s+=textLines(['Arrows show manufacturing sequence only. The six questions are this paper’s analytical framework.'],40,448,'f-note',0);
 return s+'</svg>';
}

// Figure 3 — one point per canonical record, in Appendix D row order.
// State rule: the record's audit verdict (verified_with_note → filled,
// held → hollow, not_retrieved → dashed). The article panel reads
// reading_scope for the admitted journal articles. The copper point is the
// single qualified record whose reading scope is "Host/index metadata only".
export function fig3(sources,counts){
 const W=760,H=356;
 const rows=[
  ['Qualified records','verified_with_note','admitted','appx-d-qualified-with-limitations-individual-records'],
  ['Held','held','held','appx-d-held-individual-records'],
  ['Not retrieved','not_retrieved','missing','appx-d-not-retrieved-individual-records']];
 const by=v=>sources.filter(s=>s.verdict===v);
 const n=sources.length;
 const art=[['Full-text passages','Selected full-text passages'],['English abstract only','English abstract only']];
 const artRows=art.map(([l,scope])=>[l,sources.filter(s=>s.verdict==='verified_with_note'&&s.reading_scope===scope)]);
 const nArt=artRows.reduce((a,[,r])=>a+r.length,0);
 const index=sources.filter(s=>s.reading_scope==='Host/index metadata only');
 if(index.length!==1)throw Error('Expected one index-metadata record');
 let s=svgOpen('fig-3-svg',W,H,'group','Figure 3: evidence available to this paper',
  `Audit counts: ${by('verified_with_note').length} qualified records, ${by('held').length} held, ${by('not_retrieved').length} not retrieved; among ${nArt} admitted journal articles, ${artRows[0][1].length} have full-text scoped readings and ${artRows[1][1].length} English-abstract-only readings. One point per canonical record (n = ${n}); five aliases are folded into canonical records. Each point opens its row in Appendix D.`);
 s+=textLines([`Canonical records · n = ${n}`],0,22,'f-label',0);
 const px=218,pitch=8.15;
 let y=62;
 for(const [label,verdict,state,href] of rows){
  const list=by(verdict);
  s+=`<a class="f-link" href="#${href}" id="f3-row-${verdict}"><title>${esc(label)}: ${list.length} records — open the Appendix D table</title><rect class="f-hit" x="0" y="${y-18}" width="200" height="28"/>`+textLines([label],0,y+4,'f-name',0)+textLines([String(list.length)],196,y+5,'f-count',0,'end')+'</a>';
  s+=`<line class="f-hair" x1="${px-6}" y1="${y+16}" x2="${W}" y2="${y+16}"/>`;
  list.forEach((src,i)=>{
   const x=px+i*pitch,cop=src.reading_scope==='Host/index metadata only';
   s+=`<a class="f-pt" href="#src-${esc(src.key)}" id="f3-${esc(src.key)}" data-key="${esc(src.key)}"><title>${esc(src.title)} (${esc(src.key)}) · ${esc(label)}</title><circle class="f-hit" cx="${r1(x)}" cy="${y}" r="5"/>${mark(cop?'copper':state,x,y,2.9)}</a>`;
   if(cop)s+=`<line class="f-struct" x1="${r1(x)}" y1="${y-6}" x2="${r1(x)}" y2="${y-18}"/>`+textLines(['index metadata only'],r1(x)+4,y-20,'f-label',0,'start');
  });
  y+=40;
 }
 y+=26;
 s+=textLines([`Admitted journal articles · n = ${nArt}`],0,y,'f-label',0);
 y+=36;
 for(const [label,list] of artRows){
  s+=textLines([label],0,y+4,'f-name',0)+textLines([String(list.length)],196,y+5,'f-count',0,'end');
  s+=`<line class="f-hair" x1="${px-6}" y1="${y+16}" x2="${W}" y2="${y+16}"/>`;
  list.forEach((src,i)=>{const x=px+i*14;s+=`<a class="f-pt" href="#src-${esc(src.key)}" id="f3a-${esc(src.key)}" data-key="${esc(src.key)}"><title>${esc(src.title)} (${esc(src.key)}) · ${esc(label)}</title><circle class="f-hit" cx="${x}" cy="${y}" r="6"/>${mark('admitted',x,y,2.9)}</a>`;});
  y+=36;
 }
 s+=textLines(['Counts measure research availability, not independent authorities, agreement or legal validity.','Five aliases are folded into canonical records; one qualified record supplies index metadata only.'],0,y+8,'f-note',17);
 if(by('verified_with_note').length!==counts.verdicts.verified_with_note||by('held').length!==counts.verdicts.held||by('not_retrieved').length!==counts.verdicts.not_retrieved)throw Error('Figure 3 counts differ from figure-data.json');
 return s+'</svg>';
}

// Figure 2 — documentary scope by jurisdiction, every cell label kept.
// Cell-state rule, unchanged from tools/build_paper_figures.py (first match wins):
//   1. label starts with "Not " or "Unretrieved"  → missing in this review
//   2. label is "Language hold"                   → held lead
//   3. anything else                              → admitted, bounded document
export const countryState=label=>label.startsWith('Not ')||label.startsWith('Unretrieved')?'missing':label==='Language hold'?'held':'admitted';
export function fig2(countries,countryIds){
 const W=760,H=436;
 const heads=[['Religious','position'],['Certification','mechanism'],['Product','certificate'],['Food','route'],['Product food','listing'],['Authority /','community']];
 const lx=0,c0=116,cw=107;
 const tally={admitted:0,held:0,missing:0};
 for(const c of countries)for(const l of c.scope_labels)tally[countryState(l)]++;
 let s=svgOpen('fig-2-svg',W,H,'group','Figure 2: documentary scope by jurisdiction',
  `Seven-country matrix separating religious positions, certification mechanisms, product certificates, food routes, product food listings and authority context; unavailable or held evidence stays visible. Of 42 cells, ${tally.admitted} hold a bounded admitted document, ${tally.held} a language-held lead and ${tally.missing} record evidence not located, not established or unretrieved in this review. No country has an established product certificate. `+countries.map(c=>c.country+': '+c.scope_labels.join(', ')).join('. ')+'.');
 heads.forEach((h,j)=>{s+=textLines(h,c0+j*cw+10,22,'f-label',13);});
 s+=`<line class="f-struct" x1="0" y1="46" x2="${W}" y2="46"/>`;
 countries.forEach((c,i)=>{
  const y=78+i*42,id=countryIds[c.country];
  s+=`<a class="f-link" href="#${id}" id="f2-${id}"><title>${esc(c.country)} — open Appendix B</title><rect class="f-hit" x="0" y="${y-20}" width="${c0-6}" height="38"/>`+textLines([c.country],lx,y+4,'f-name f-strongname',0)+'</a>';
  c.scope_labels.forEach((label,j)=>{
   const st=countryState(label),x=c0+j*cw;
   const href=st==='admitted'?id:id+'-gap';
   const lines=wrap(label,12);
   s+=`<a class="f-link" href="#${href}" id="f2-${id}-${j}"><title>${esc(c.country)} · ${esc(heads[j].join(' '))}: ${esc(label)}</title><rect class="f-hit" x="${x}" y="${y-20}" width="${cw-4}" height="38"/>`+mark(st,x+5,y-1,3.4)+textLines(lines,x+16,y+(lines.length>1?-4:4),'f-cell',15)+'</a>';
  });
  s+=`<line class="f-hair" x1="0" y1="${y+21}" x2="${W}" y2="${y+21}"/>`;
 });
 const ly=384;
 s+=mark('admitted',6,ly-4)+textLines(['Admitted, bounded document'],16,ly,'f-note',0);
 s+=mark('held',226,ly-4)+textLines(['Language hold'],236,ly,'f-note',0);
 s+=mark('missing',370,ly-4)+textLines(['Missing in this review'],380,ly,'f-note',0);
 s+=textLines(['Evidence checked 2 October 2026. A document is not a national verdict. Detailed scope and citations: §9 and Appendix B.'],0,ly+30,'f-note',0);
 return {svg:s+'</svg>',tally};
}

// R2 — the 45 comparison slots of Appendix A. Slot-state rule, read from the
// verbatim "Currently admitted answer" cell (first match wins):
//   1. starts with "Open"               → recorded as open (dashed ring)
//   2. starts with "No answer admitted" → no admitted answer (em-rule)
//   3. starts with "Inference:"         → the paper's labeled inference (hollow)
//   4. anything else                    → attributed answer (filled)
export const slotState=answer=>/^Open\b/.test(answer)?'open':/^No answer admitted/.test(answer)?'none':/^Inference:/.test(answer)?'inference':'attributed';
export function figR2(traditions,questions){
 // traditions: [{name, short, slots:[{id, state}]}] ; questions: ['1. Who decides…', …]
 const W=760,H=446,c0=432,cw=66,top=58,rh=30;
 const tot=traditions.map(t=>({attributed:0,inference:0,none:0,open:0}));
 traditions.forEach((t,j)=>t.slots.forEach(sl=>tot[j][sl.state]++));
 const all={attributed:0,inference:0,none:0,open:0};tot.forEach(t=>{for(const k in t)all[k]+=t[k];});
 let s=svgOpen('fig-r2-svg',W,H,'group','Fig. R2: the 45 comparison slots, nine questions by five traditions',
  `Nine questions in rows and five traditions in columns; one point per slot, read from Appendix A. ${all.attributed} slots have an attributed answer, ${all.inference} the paper’s labeled inference, ${all.none} no admitted answer and ${all.open} is recorded as open. `+traditions.map((t,j)=>`${t.name}: ${tot[j].attributed} attributed, ${tot[j].inference} inference, ${tot[j].none} none${tot[j].open?', '+tot[j].open+' open':''}`).join('; ')+'. Each point opens its Appendix A row.');
 traditions.forEach((t,j)=>{s+=`<a class="f-link" href="#${t.anchor}" id="r2-${t.anchor}"><title>${esc(t.name)} — open the Appendix A table</title><rect class="f-hit" x="${c0+j*cw-30}" y="12" width="60" height="26"/>`+textLines([t.short],c0+j*cw,30,'f-label',0,'middle')+'</a>';});
 s+=`<line class="f-struct" x1="0" y1="${top-16}" x2="${W}" y2="${top-16}"/>`;
 questions.forEach((q,i)=>{
  const y=top+i*rh;
  s+=textLines([q],0,y+4,'f-cell',0);
  s+=`<line class="f-hair" x1="0" y1="${y+14}" x2="${W}" y2="${y+14}"/>`;
  traditions.forEach((t,j)=>{
   const sl=t.slots[i],x=c0+j*cw;
   const name={attributed:'attributed answer',inference:'labeled inference',none:'no answer admitted',open:'open question'}[sl.state];
   let m;
   if(sl.state==='attributed')m=`<circle class="m-filled" cx="${x}" cy="${y}" r="3.6"/>`;
   else if(sl.state==='inference')m=`<circle class="m-hollow" cx="${x}" cy="${y}" r="3.6"/>`;
   else if(sl.state==='open')m=`<circle class="m-dashed" cx="${x}" cy="${y}" r="4.4"/>`;
   else m=`<line class="f-struct" x1="${x-6}" y1="${y}" x2="${x+6}" y2="${y}"/>`;
   s+=`<a class="f-pt" href="#slot-${sl.id}" id="r2-${sl.id}"><title>${esc(t.name)} · question ${i+1}: ${name}</title><rect class="f-hit" x="${x-24}" y="${y-13}" width="48" height="26"/>${m}</a>`;
  });
 });
 const ty=top+questions.length*rh+18;
 s+=textLines(['Attributed · inference · none'],0,ty,'f-label',0);
 traditions.forEach((t,j)=>{s+=textLines([`${tot[j].attributed} · ${tot[j].inference} · ${tot[j].none}`].concat(tot[j].open?[`${tot[j].open} open`]:[]),c0+j*cw,ty,'f-cell',16,'middle');});
 const ly=ty+48;
 s+=`<circle class="m-filled" cx="6" cy="${ly-4}" r="3.6"/>`+textLines(['Attributed answer'],16,ly,'f-note',0);
 s+=`<circle class="m-hollow" cx="166" cy="${ly-4}" r="3.6"/>`+textLines(['The paper’s inference'],176,ly,'f-note',0);
 s+=`<line class="f-struct" x1="342" y1="${ly-4}" x2="354" y2="${ly-4}"/>`+textLines(['No answer admitted'],362,ly,'f-note',0);
 s+=`<circle class="m-dashed" cx="526" cy="${ly-4}" r="4.4"/>`+textLines(['Open'],538,ly,'f-note',0);
 return {svg:s+'</svg>',totals:all};
}

// R3 — section 11.2 as a corridor: the manufacturing dossier, five separate
// determinations (none populated in the present record) and the closed gate
// to the quantitative handoff, whose four inputs are missing.
export function figR3(){
 const W=760,H=476;
 const dossier=['Donor and procurement procedure','Original material and founder line','Relevant cell-bank history','Ingredients used at each stage','Enzyme source and production route, with its function','Removed or transformed input: operation, resulting material, residual evidence','Any claimed change of legal identity, stated for review'];
 const det=[['Religious position','The authority, and how the disclosed facts meet its conditions'],['Certification route','The applicable route'],['Product certificate','The product covered by the resulting document'],['Food authorization','Its own product and process match'],['Import access','Additional evidence; a domestic decision does not travel automatically']];
 const missing=['Accepted versioned baseline','Compatible finished-product reference market','Product-specific access evidence','Allocated capacity'];
 let s=svgOpen('fig-r3-svg',W,H,'img','Fig. R3: from a manufacturing dossier to separate decisions',
  'Left, seven items the manufacturing dossier would document, from donor and procurement procedure to any claimed change of legal identity. Centre, five separate determinations: religious position, certification route, product certificate, food authorization and import access, each needing its own evidence, scope and date; the present production record contains no populated assessment for any of them. Right, past a closed gate, the quantitative handoff and its four missing inputs: an accepted versioned baseline, a compatible finished-product reference market, product-specific access evidence and allocated capacity. No numerical input or gate is filled by this paper.');
 s+=textLines(['Manufacturing dossier'],0,22,'f-label',0)+textLines(['Separate determinations'],330,22,'f-label',0)+textLines(['Quantitative handoff'],604,22,'f-label',0);
 s+=`<line class="f-struct" x1="6" y1="48" x2="6" y2="412"/>`;
 let y=58;const dy=[];
 dossier.forEach(d=>{const lines=wrap(d,34);s+=`<line class="f-struct" x1="2" y1="${y-4}" x2="10" y2="${y-4}"/>`+textLines(lines,22,y,'f-cell',15);dy.push(y);y+=Math.max(46,lines.length*15+28);});
 const midY=232;
 s+=`<line class="f-rule" x1="270" y1="${midY}" x2="300" y2="${midY}"/>`;
 det.forEach(([name,need],i)=>{
  const yy=62+i*74;
  s+=`<path class="f-rule" d="M300 ${midY} C 316 ${midY}, 316 ${yy-4}, 332 ${yy-4}"/>`;
  s+=`<circle class="m-hollow" cx="340" cy="${yy-4}" r="5"/>`+textLines([name],354,yy,'f-name f-strongname',0)+textLines(wrap(need,32),354,yy+18,'f-note',15);
 });
 s+=textLines(['Each with its own scope and date'],330,436,'f-label',0)+textLines(['Hollow rings: no populated assessment in the present record'],330,456,'f-note',0);
 // closed gate with the one copper point
 const gx=584;
 s+=`<line class="f-strong" x1="${gx-2}" y1="48" x2="${gx-2}" y2="412"/><line class="f-strong" x1="${gx+2}" y1="48" x2="${gx+2}" y2="412"/>`;
 s+=`<rect class="f-plate" x="${gx-8}" y="${midY-8}" width="16" height="16"/><circle class="m-copper" cx="${gx}" cy="${midY}" r="3.8"/>`;
 s+=`<line class="f-dash" x1="612" y1="48" x2="612" y2="412"/>`;
 missing.forEach((m,i)=>{const yy=70+i*84;s+=`<circle class="m-dashed" cx="612" cy="${yy-4}" r="5"/>`+textLines(wrap(m,18),626,yy,'f-cell',15);});
 s+=textLines(['No numerical input or gate','is filled by this paper.'],604,436,'f-note',16);
 return s+'</svg>';
}

// Series mark, after assets/series-mark.svg, bound to theme tokens; the
// outer tick ring drifts once per 180 s and stops under reduced motion.
export function seriesMark(size=44){
 let ticks='';
 for(let i=0;i<24;i++){const a=i*Math.PI/12,inner=i%6===0?53:58,outer=64;ticks+=`<line x1="${r1(70+inner*Math.cos(a))}" y1="${r1(70+inner*Math.sin(a))}" x2="${r1(70+outer*Math.cos(a))}" y2="${r1(70+outer*Math.sin(a))}"/>`;}
 return `<svg class="series-mark" width="${size}" height="${size}" viewBox="0 0 140 140" aria-hidden="true" focusable="false"><circle class="sm-outer" cx="70" cy="70" r="64"/><g class="sm-ticks drift">${ticks}</g><circle class="sm-ring" cx="70" cy="70" r="46"/><circle class="sm-inner" cx="70" cy="70" r="29"/><ellipse class="sm-orbit" cx="70" cy="70" rx="46" ry="17"/><circle class="sm-core" cx="70" cy="70" r="6"/><circle class="m-copper" cx="116" cy="70" r="2.6"/><circle class="sm-moon" cx="70" cy="41" r="1.8"/></svg>`;
}

export {slug};
