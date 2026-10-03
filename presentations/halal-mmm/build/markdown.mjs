// Parser and inline renderer for the subset of Markdown used by the canonical
// manuscript (research/halal-cultivated/paper/paper.md): ATX headings,
// paragraphs, pipe tables, loose "- " lists, images, footnote definitions,
// footnote references, *italic* spans, bare URLs and [SOURCE-KEY] markers.
// Trace comments are kept as data on each block and removed from the text.

export const esc=s=>String(s??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');

const TRACE=/<!--\s*trace:([^|]*)\|\s*kind:\s*([a-z]+)\s*-->/g;

export function parseManuscript(text){
 const lines=text.replace(/\r\n/g,'\n').split('\n');
 const blocks=[];const notes=new Map();
 let buf=[];
 const flush=()=>{if(buf.length){blocks.push(classify(buf));buf=[];}};
 for(const line of lines){
  const def=/^\[\^([^\]]+)\]:\s(.*)$/.exec(line);
  if(def){flush();notes.set(def[1],def[2]);continue;}
  if(line.trim()===''){flush();continue;}
  buf.push(line);
 }
 flush();
 // Merge consecutive list-item blocks into one list.
 const merged=[];
 for(const b of blocks){
  const prev=merged[merged.length-1];
  if(b.type==='item'&&prev?.type==='list'){prev.items.push(b);continue;}
  if(b.type==='item'){merged.push({type:'list',items:[b]});continue;}
  merged.push(b);
 }
 return {blocks:merged,notes};
}

function takeTrace(raw){
 let trace=null,kind=null;
 const text=raw.replace(TRACE,(m,t,k)=>{trace=t.trim();kind=k;return '';}).replace(/<!--[^]*?-->/g,'').replace(/[ \t]+$/gm,'').trim();
 return {text,trace,kind};
}

function classify(lines){
 const raw=lines.join('\n');
 const {text,trace,kind}=takeTrace(raw);
 const meta={trace,kind};
 let m;
 if((m=/^(#{1,6})\s+(.*)$/.exec(text)))return {type:'heading',level:m[1].length,text:m[2].trim(),...meta};
 if((m=/^!\[([^\]]*)\]\(([^)]+)\)$/.exec(text)))return {type:'image',alt:m[1],src:m[2],...meta};
 if(text.startsWith('|'))return {type:'table',...parseTable(text.split('\n')),...meta};
 if(text.startsWith('- '))return {type:'item',text:text.slice(2).trim(),...meta};
 return {type:'para',text,...meta};
}

function splitRow(line){
 const cells=[];let cur='';
 const body=line.trim().replace(/^\|/,'').replace(/\|$/,'');
 for(const ch of body){if(ch==='|'){cells.push(cur.trim());cur='';}else cur+=ch;}
 cells.push(cur.trim());
 return cells;
}

function parseTable(rows){
 const head=splitRow(rows[0]);
 const align=splitRow(rows[1]).map(c=>c.endsWith(':')&&c.startsWith(':')?'center':c.endsWith(':')?'right':null);
 return {head,align,rows:rows.slice(2).map(splitRow)};
}

// Arabic-script runs, including spaces, digits and Arabic punctuation between
// letters. Urdu-specific letters select lang="ur"; everything else is Arabic.
const ARABIC_RUN=/[؀-ۿ](?:[؀-ۿ0-9 ’‘،؛:.–—-]*[؀-ۿ])?/g;
const URDU=/[ٹڈڑںھہیےگ]/;
export const scriptLang=s=>URDU.test(s)?'ur':'ar';
export function wrapArabic(html){
 return html.replace(ARABIC_RUN,run=>`<span lang="${scriptLang(run)}" dir="rtl">${run}</span>`);
}

const TOKEN=/(\[\^[^\]]+\])|(https?:\/\/[^\s<>"]+)|(\[[A-Z][A-Z0-9-]*\])/g;

// ctx: {noteRef(id) -> html, sourceKey(key) -> html|null, crossRef(text) -> html}
export function inline(src,ctx){
 let out='',last=0,prevNote=false;
 const text=s=>{const html=ctx.crossRef?ctx.crossRef(italics(esc(s))):italics(esc(s));return wrapArabic(html);};
 for(const m of src.matchAll(TOKEN)){
  const before=src.slice(last,m.index);
  if(before){out+=text(before);prevNote=false;}
  if(m[1]){
   const id=m[1].slice(2,-1);
   if(prevNote)out+='<sup class="nsep" aria-hidden="true">,</sup>';
   out+=ctx.noteRef(id);prevNote=true;
  }else if(m[2]){
   let url=m[2],trail='';
   while(/[.,;:)\]]$/.test(url)){trail=url.slice(-1)+trail;url=url.slice(0,-1);}
   out+=`<a class="url" href="${esc(url)}" dir="ltr" rel="noreferrer">${esc(url)}</a>`+text(trail);prevNote=false;
  }else{
   const key=m[3].slice(1,-1);const html=ctx.sourceKey?ctx.sourceKey(key):null;
   out+=html??text(m[3]);prevNote=false;
  }
  last=m.index+m[0].length;
 }
 if(last<src.length)out+=text(src.slice(last));
 return out;
}

// *italic* spans; the manuscript uses no bold, code or underscores.
function italics(s){return s.replace(/\*([^*\n]+)\*/g,'<em>$1</em>');}

// Plain text of a Markdown fragment, for preservation checks and labels.
export function plain(src){
 return src.replace(/<!--[^]*?-->/g,'').replace(/\[\^[^\]]+\]/g,'').replace(/\*([^*\n]+)\*/g,'$1').replace(/\s+/g,' ').trim();
}

export function slug(s){
 return s.normalize('NFKD').replace(/[̀-ͯ]/g,'').toLowerCase().replace(/[’'"“”]/g,'').replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
}
