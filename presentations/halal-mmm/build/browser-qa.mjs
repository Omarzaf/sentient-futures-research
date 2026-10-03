// Browser checks for presentations/halal-mmm/index.html (Chromium via Playwright).
//   PLAYWRIGHT_MODULE=/path/to/node_modules/playwright node presentations/halal-mmm/build/browser-qa.mjs [screenshot-dir]
//   QA_URL=http://127.0.0.1:8796/presentations/halal-mmm/index.html … (optional)
// Playwright is not a repository dependency; point PLAYWRIGHT_MODULE at an
// installed copy. Screenshots go to the given directory (default: none).
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';

const here=path.dirname(fileURLToPath(import.meta.url));
// QA_URL tests a served copy (for example through tools/serve.mjs); default is file://.
const page0=process.env.QA_URL||pathToFileURL(path.resolve(here,'../index.html')).href;
const origin=page0.startsWith('file:')?'file:':new URL(page0).origin;
const shots=process.argv[2]||null;
if(shots)fs.mkdirSync(shots,{recursive:true});
const req=createRequire(import.meta.url);
const {chromium}=req(process.env.PLAYWRIGHT_MODULE||'playwright');
const results=[];const fail=[];
const rec=(name,ok,detail)=>{results.push({name,ok,detail});if(!ok)fail.push(name+(detail?': '+JSON.stringify(detail):''));};
const browser=await chromium.launch(process.env.CHROMIUM_PATH?{executablePath:process.env.CHROMIUM_PATH}:{});

async function open(opts={},hash=''){
 const ctx=await browser.newContext({viewport:{width:opts.w||1280,height:opts.h||900},colorScheme:opts.scheme||'light',reducedMotion:opts.reduce?'reduce':'no-preference',javaScriptEnabled:opts.js!==false});
 const page=await ctx.newPage();
 const errors=[],requests=[];
 page.on('pageerror',e=>errors.push(e.message));
 page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
 page.on('requestfailed',r=>errors.push('failed '+r.url()));
 page.on('request',r=>{if(!r.url().startsWith(origin))requests.push(r.url());});
 await page.goto(page0+hash);await page.waitForTimeout(250);
 return {ctx,page,errors,requests};
}
const instant=p=>p.addStyleTag({content:'html{scroll-behavior:auto!important}'});
const inView=(page,sel)=>page.evaluate(s=>{const r=document.querySelector(s).getBoundingClientRect();return r.bottom>0&&r.top<innerHeight;},sel);

// 1. Widths × themes: overflow, console, offenders outside scroll containers.
for(const w of [1440,1280,1024,768,390,375])for(const scheme of ['light','dark']){
 const {ctx,page,errors,requests}=await open({w,scheme});
 const m=await page.evaluate(()=>{
  const de=document.documentElement;const off=[];
  for(const el of document.querySelectorAll('body *')){
   if(el.closest('.scroll-x,.table-wrap,.leftnav,svg,.skip,.skip-fig')||getComputedStyle(el).display==='none')continue;
   const r=el.getBoundingClientRect();if(r.width&&r.right>de.clientWidth+1)off.push(el.tagName+'.'+el.className);
  }
  const notes=[...document.querySelectorAll('.margin-note')].map(n=>getComputedStyle(n).float);
  return {scrollWidth:de.scrollWidth,clientWidth:de.clientWidth,offenders:[...new Set(off)].slice(0,5),railNotes:notes.filter(f=>f==='right').length,inlineNotes:notes.filter(f=>f==='none').length,leftnav:getComputedStyle(document.querySelector('.leftnav')).display,theme:de.getAttribute('data-theme')};
 });
 rec(`overflow ${w} ${scheme}`,m.scrollWidth===m.clientWidth&&!m.offenders.length,m);
 rec(`console ${w} ${scheme}`,!errors.length,errors);
 rec(`no network ${w} ${scheme}`,!requests.length,requests);
 rec(`theme follows preference ${w} ${scheme}`,m.theme===scheme,m.theme);
 if(shots)await page.screenshot({path:path.join(shots,`top-${w}-${scheme}.png`)});
 await ctx.close();
}

// 2. Contrast of essential text roles in both themes.
for(const scheme of ['light','dark']){
 const {ctx,page}=await open({scheme});
 const c=await page.evaluate(()=>{
  const parse=s=>s.match(/[\d.]+/g).slice(0,3).map(Number);
  const lum=([r,g,b])=>[r,g,b].map(v=>{v/=255;return v<=0.03928?v/12.92:((v+0.055)/1.055)**2.4;}).reduce((a,v,i)=>a+v*[0.2126,0.7152,0.0722][i],0);
  const bg=parse(getComputedStyle(document.body).backgroundColor);
  const ratio=fg=>{const a=lum(fg),b=lum(bg);return Math.round(100*(Math.max(a,b)+0.05)/(Math.min(a,b)+0.05))/100;};
  const roles={'body prose':'#sec-1 > p','mono label':'.eyebrow','margin note':'.margin-note p','margin tag':'.margin-note .tag','caption':'#fig-1 .canonical-caption','edition caption':'#fig-1 .edition','note ref':'.nref a','contents link':'.leftnav a .t','table header':'table.data thead th','backref':'.backref','bib meta':'.bib-meta','readout label':'.readout-row span'};
  const out={};
  for(const [k,s] of Object.entries(roles)){const el=document.querySelector(s);out[k]=ratio(parse(getComputedStyle(el).color));}
  for(const [k,s] of Object.entries({'svg label':'.f-label','svg note':'.f-note','svg cell':'.f-cell'})){const el=document.querySelector(s);out[k]=ratio(parse(getComputedStyle(el).fill));}
  const copper=ratio(parse(getComputedStyle(document.querySelector('.m-copper')).fill));
  return {out,copper};
 });
 const low=Object.entries(c.out).filter(([,v])=>v<4.5);
 rec(`contrast ${scheme}`,!low.length,c);
 await ctx.close();
}

// 3. Citation jump and exact return (pointer).
{
 const {ctx,page,errors}=await open({w:1280});await instant(page);
 await page.click('#r-s5-01-2');await page.waitForTimeout(200);
 const a=await page.evaluate(()=>({hash:location.hash,origin:document.querySelector('#n-s5-01 .backref.is-origin')?.getAttribute('href'),chip:!document.getElementById('returnChip').hidden,chipText:document.getElementById('returnChip').textContent}));
 const noteVisible=await inView(page,'#n-s5-01');
 await page.click('#returnChip');await page.waitForTimeout(300);
 const b=await page.evaluate(()=>({hash:location.hash,focus:document.activeElement.id,chip:!document.getElementById('returnChip').hidden}));
 const back=await inView(page,'#r-s5-01-2');
 rec('citation jump and return (pointer)',a.hash==='#n-s5-01'&&noteVisible&&a.origin==='#r-s5-01-2'&&a.chip&&b.focus==='r-s5-01-2'&&back&&!b.chip,{a,b,noteVisible,back,errors});
 // Back-link path: the note's own return link for a different occurrence.
 await page.click('#r-s5-01-4');await page.waitForTimeout(150);
 await page.click('#n-s5-01 a.backref[href="#r-s5-01-4"]');await page.waitForTimeout(150);
 rec('endnote back-link lands on the cited occurrence',await page.evaluate(()=>location.hash)==='#r-s5-01-4'&&await inView(page,'#r-s5-01-4'));
 // Browser back after a jump.
 await page.goto(page0);await page.evaluate(()=>document.getElementById('r-s9-04-1').scrollIntoView({block:'center'}));
 await page.click('#r-s9-04-1');await page.waitForTimeout(150);const away=!(await inView(page,'#r-s9-04-1'));await page.goBack();await page.waitForTimeout(250);
 rec('browser Back returns from a note',away&&await inView(page,'#r-s9-04-1'),await page.evaluate(()=>location.hash));
 await ctx.close();
}

// 4. Keyboard: note reference, return chip, figure point.
{
 const {ctx,page}=await open({w:1280});await instant(page);
 await page.focus('#r-s7-01-1');
 const ring=await page.evaluate(()=>{const s=getComputedStyle(document.activeElement);return s.outlineStyle+' '+s.outlineWidth;});
 await page.keyboard.press('Enter');await page.waitForTimeout(150);
 const h1=await page.evaluate(()=>location.hash);
 await page.focus('#returnChip');await page.keyboard.press('Enter');await page.waitForTimeout(250);
 const f1=await page.evaluate(()=>document.activeElement.id);
 await page.focus('#f3-HS-006');await page.keyboard.press('Enter');await page.waitForTimeout(150);
 const h2=await page.evaluate(()=>location.hash);
 const row=await page.evaluate(()=>getComputedStyle(document.querySelector('#src-HS-006 th')).backgroundColor!==getComputedStyle(document.body).backgroundColor);
 await page.focus('#returnChip');await page.keyboard.press('Enter');await page.waitForTimeout(250);
 const f2=await page.evaluate(()=>document.activeElement.id);
 rec('keyboard citation, figure drilldown and return',h1==='#n-s7-01'&&f1==='r-s7-01-1'&&h2==='#src-HS-006'&&row&&f2==='f3-HS-006'&&!ring.startsWith('none'),{ring,h1,f1,h2,row,f2});
 // Tab order reaches the theme toggle and the skip link first.
 await page.goto(page0);await page.keyboard.press('Tab');
 rec('first Tab reaches skip link',await page.evaluate(()=>document.activeElement.className)==='skip');
 await ctx.close();
}

// 5. Figure drilldowns: Fig. 2 cell, R2 slot, R1 station, readout.
{
 const {ctx,page}=await open({w:1440});await instant(page);
 const checks=[['#f2-appx-b-singapore-4','#appx-b-singapore'],['#f2-appx-b-india-2','#appx-b-india-gap'],['#r2-J-Q1','#slot-J-Q1'],['#r1-sec-9-4','#sec-9-4'],['#ro-fig-r2','#fig-r2'],['#x-1',null]];
 const outc=[];
 for(const [src,dest] of checks){
  await page.goto(page0);await instant(page);await page.click(src);await page.waitForTimeout(150);
  const hash=await page.evaluate(()=>location.hash);const target=dest||hash;
  const ok=(!dest||hash===dest)&&await inView(page,target);
  await page.click('#returnChip');await page.waitForTimeout(250);
  const ret=await inView(page,src);
  outc.push({src,hash,ok,ret});
 }
 rec('figure and cross-reference drilldown with return',outc.every(o=>o.ok&&o.ret),outc);
 await ctx.close();
}

// 6. Deep link after reload.
{
 const {ctx,page}=await open({w:1280},'#n-abd-23');
 await page.reload();await page.waitForTimeout(250);
 rec('deep link survives reload',await inView(page,'#n-abd-23'));
 await ctx.close();
}

// 7. Phone contents sheet.
{
 const {ctx,page}=await open({w:390,h:844});await instant(page);
 await page.click('#tocButton');await page.waitForTimeout(100);
 const o=await page.evaluate(()=>({open:document.documentElement.classList.contains('toc-open'),nav:getComputedStyle(document.querySelector('.leftnav')).display,focus:document.activeElement.closest('.leftnav')!==null,expanded:document.getElementById('tocButton').getAttribute('aria-expanded')}));
 await page.keyboard.press('Escape');await page.waitForTimeout(100);
 const c=await page.evaluate(()=>({open:document.documentElement.classList.contains('toc-open'),focus:document.activeElement.id}));
 await page.click('#tocButton');await page.click('.leftnav a[href="#appx-b"]');await page.waitForTimeout(250);
 const n=await page.evaluate(()=>({hash:location.hash,open:document.documentElement.classList.contains('toc-open')}));
 rec('phone contents sheet opens, closes, navigates',o.open&&o.nav==='block'&&o.focus&&o.expanded==='true'&&!c.open&&c.focus==='tocButton'&&n.hash==='#appx-b'&&!n.open&&await inView(page,'#appx-b'),{o,c,n});
 // Dense tables and wide figures scroll inside their own containers.
 const sc=await page.evaluate(()=>{const t=document.querySelector('#appx-d .table-wrap.span-rail');const f=document.querySelector('#fig-2 .scroll-x');return {table:[t.scrollWidth,t.clientWidth],fig:[f.scrollWidth,f.clientWidth],doc:[document.documentElement.scrollWidth,document.documentElement.clientWidth]};});
 rec('phone: tables and figures scroll internally, page does not',sc.table[0]>sc.table[1]&&sc.fig[0]>sc.fig[1]&&sc.doc[0]===sc.doc[1],sc);
 if(shots){await page.goto(page0+'#fig-2');await page.waitForTimeout(200);await page.screenshot({path:path.join(shots,'fig2-390-light.png')});await page.click('#tocButton');await page.screenshot({path:path.join(shots,'contents-390-light.png')});}
 await ctx.close();
}

// 8. Theme toggle persists across reload.
{
 const {ctx,page}=await open({w:1280,scheme:'light'});
 await page.click('#themeToggle');
 const t1=await page.evaluate(()=>[document.documentElement.getAttribute('data-theme'),getComputedStyle(document.body).backgroundColor,document.getElementById('themeToggle').textContent]);
 await page.reload();await page.waitForTimeout(150);
 const t2=await page.evaluate(()=>document.documentElement.getAttribute('data-theme'));
 const copper=await page.evaluate(()=>getComputedStyle(document.querySelector('.m-copper')).fill);
 rec('theme toggle and persistence; copper fixed',t1[0]==='dark'&&t1[1]==='rgb(28, 24, 21)'&&t1[2]==='Light'&&t2==='dark'&&copper==='rgb(138, 90, 59)',{t1,t2,copper});
 await ctx.close();
}

// 9. Reduced motion stops the drift; normal motion keeps it.
for(const reduce of [false,true]){
 const {ctx,page}=await open({reduce});
 const a=await page.evaluate(()=>getComputedStyle(document.querySelector('.drift')).animationName);
 rec(`drift animation ${reduce?'stopped under reduced motion':'present by default'}`,reduce?a==='none':a==='mmm-spin',a);
 await ctx.close();
}

// 10. JavaScript disabled: the paper, notes and inline contents remain.
for(const w of [1280,390]){
 const {ctx,page}=await open({w,js:false});
 const r=await page.evaluate(()=>({h2:document.querySelectorAll('h2').length,notes:document.querySelectorAll('.notes li').length,refs:document.querySelectorAll('.nref a').length,tocInline:getComputedStyle(document.querySelector('.toc-mobile')).display,toggle:document.getElementById('themeToggle').hidden,overflow:document.documentElement.scrollWidth-document.documentElement.clientWidth}));
 rec(`no-JS reading ${w}`,r.h2>=21&&r.notes===177&&r.refs===251&&r.toggle&&r.overflow===0&&(w>=980||r.tocInline==='block'),r);
 await page.click('a[href="#n-s1-01"]');await page.waitForTimeout(150);
 rec(`no-JS citation link ${w}`,await page.evaluate(()=>location.hash)==='#n-s1-01');
 await ctx.close();
}

// 11. Language and direction markup; SVG accessibility.
{
 const {ctx,page}=await open({w:1440});
 const l=await page.evaluate(()=>({ar:[...document.querySelectorAll('[lang=ar]')].map(e=>getComputedStyle(e).direction),ur:[...document.querySelectorAll('[lang=ur]')].map(e=>getComputedStyle(e).direction),urUpper:[...document.querySelectorAll('[lang=ur],[lang=ar]')].some(e=>getComputedStyle(e).textTransform==='uppercase'),urls:[...document.querySelectorAll('a.url')].every(a=>getComputedStyle(a).direction==='ltr')}));
 rec('Arabic and Urdu marked rtl, URLs ltr, no uppercasing',l.ar.length>0&&l.ar.every(d=>d==='rtl')&&l.ur.length>0&&l.ur.every(d=>d==='rtl')&&!l.urUpper&&l.urls,{ar:l.ar.length,ur:l.ur.length});
 const s=await page.evaluate(()=>[...document.querySelectorAll('svg.fig-svg')].map(v=>({id:v.id,role:v.getAttribute('role'),title:!!v.querySelector('title')?.textContent.trim(),desc:(v.querySelector('desc')?.textContent||'').length,links:v.querySelectorAll('a').length})));
 rec('every figure has role, title and description',s.length===6&&s.every(x=>x.title&&x.desc>80&&(x.links?x.role==='group':x.role==='img')),s);
 if(shots){await page.goto(page0+'#src-P-BANURI-2019');await page.waitForTimeout(200);await page.screenshot({path:path.join(shots,'urdu-row-1440.png')});}
 await ctx.close();
}

// 12. Print media.
{
 const {ctx,page}=await open({w:1280,scheme:'dark'});
 await page.emulateMedia({media:'print'});
 const p=await page.evaluate(()=>({nav:getComputedStyle(document.querySelector('.leftnav')).display,toggle:getComputedStyle(document.getElementById('themeToggle')).display,bg:getComputedStyle(document.body).backgroundColor,notes:getComputedStyle(document.querySelector('.margin-note')).float}));
 let pages=null;
 if(shots){const pdf=await page.pdf({path:path.join(shots,'print.pdf'),format:'A4',printBackground:false});pages=(pdf.toString('latin1').match(/\/Type\s*\/Page[^s]/g)||[]).length;}
 rec('print styles: chrome hidden, light ground, notes inline',p.nav==='none'&&p.toggle==='none'&&p.bg==='rgb(255, 255, 255)'&&p.notes==='none',{...p,pdfPages:pages});
 await ctx.close();
}

// 13. Optional web fonts load only after the reader asks.
{
 const {ctx,page,requests}=await open({w:1280});
 const before=requests.length;
 await page.click('#fontToggle');
 let loaded=false;
 try{await page.waitForFunction(()=>document.fonts.check('18px Newsreader')&&document.fonts.check('11px "IBM Plex Mono"'),null,{timeout:15000});loaded=true;}catch{}
 rec('no font request until opt-in; fonts load after opt-in (network)',before===0&&requests.some(u=>u.includes('fonts.googleapis.com')),{before,after:requests.length,loaded});
 if(shots&&loaded){await page.evaluate(()=>scrollTo(0,0));await page.waitForTimeout(300);await page.screenshot({path:path.join(shots,'top-1440-webfonts.png')});}
 await page.click('#fontToggle');
 await ctx.close();
}

await browser.close();
const summary={status:fail.length?'FAIL':'PASS',checks:results.length,failed:fail.length,failures:fail,results};
console.log(JSON.stringify(summary,null,1));
if(fail.length)process.exitCode=1;
