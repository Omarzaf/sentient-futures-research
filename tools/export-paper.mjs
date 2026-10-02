/** Export the canonical manuscript using the already-installed Pandoc. */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const paper=path.join(root,'research/halal-cultivated/paper');
const out=path.join(root,'working/paper-release');
const state=JSON.parse(fs.readFileSync(path.join(paper,'execution-state.json')));
if(!state.outlineApproved||!state.manuscriptDrafted)throw Error('A completed, authorized manuscript is required.');
const original=fs.readFileSync(path.join(paper,'paper.md'),'utf8');
if(state.review?.status!=='pass_with_limits'||state.review.manuscriptSha256!==crypto.createHash('sha256').update(original).digest('hex'))throw Error('The current manuscript must match the completed review checkpoint.');
const sources=JSON.parse(fs.readFileSync(path.join(paper,'source-register.json')));
const keys=new Set(sources.flatMap(s=>[s.key,...s.aliases]));
// Trace and source-key markup remains in the canonical text for auditing.
const clean=original.replace(/<!--[^]*?-->/g,'').replace(/\[([A-Z][A-Z0-9-]*)\]/g,(full,key)=>keys.has(key)?'':full).replace(/[ \t]+\n/g,'\n').replace(/\n{3,}/g,'\n\n');
fs.mkdirSync(out,{recursive:true});
fs.writeFileSync(path.join(out,'paper.md'),clean);
const args=['--from=markdown+footnotes+pipe_tables+auto_identifiers-implicit_figures','--resource-path='+paper];
const body=execFileSync('pandoc',[...args,'--to=html5','--toc','--toc-depth=2','--standalone','--metadata','pagetitle=Cultivated Chicken and Halal Market Access'],{input:clean,encoding:'utf8',maxBuffer:20e6});
let main=body.match(/<body[^>]*>([^]*?)<\/body>/)?.[1];
if(!main)throw Error('Pandoc did not return an HTML body.');
// Keep the title and abstract first, with direct links to each major section.
main=main.replace(/<nav id="TOC"[^]*?<\/nav>/,'');
const sections=[...main.matchAll(/<h2 id="([^"]+)">([^]*?)<\/h2>/g)].filter(m=>m[1]!=='abstract');
const toc='<nav id="TOC" aria-label="Contents"><strong>Contents</strong><ul>'+sections.map(m=>'<li><a href="#'+m[1]+'">'+m[2]+'</a></li>').join('')+'</ul></nav>';
main=main.replace(/<h2 id="([^"]+)">1\./,toc+'<h2 id="$1">1.');
main=main.replace(/<table([^>]*)>/g,'<div class="table-scroll" tabindex="0"><table$1>').replace(/<\/table>/g,'</table></div>');
main=main.replace(/(src="figures\/figure-[^"]+)\.png"/g,'$1.svg"');
main=main.replace(/<p>(<img src="(figures\/[^\"]+)"[^>]*>)<\/p>/g,'<div class="figure-scroll" tabindex="0" role="group" aria-label="Scrollable figure"><a href="$2" aria-label="Open figure at full size">$1</a></div><p class="caption"><a href="$2">Open figure at full size</a></p>');
const css=`:root{color-scheme:light;--ink:#172c29;--muted:#53625e;--line:#d5dfdb}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#fff;color:var(--ink);font:18px/1.7 Georgia,serif}.reader{max-width:980px;margin:auto;padding:24px 32px 90px}.top{font:14px/1.5 system-ui,sans-serif;display:flex;justify-content:space-between;gap:20px;flex-wrap:wrap;padding-bottom:22px;border-bottom:1px solid var(--line)}a{color:#245f56;text-underline-offset:3px;overflow-wrap:anywhere}a:focus-visible,div:focus-visible{outline:3px solid #9c742b;outline-offset:4px}h1,h2,h3,h4{color:#000;line-height:1.2;scroll-margin-top:20px}h1{font-size:clamp(34px,5vw,52px);font-weight:500;letter-spacing:-.025em;margin:48px 0 20px}h2{font-size:29px;font-weight:500;margin:60px 0 22px}h3{font-size:22px;margin:35px 0 16px}p{margin:0 0 20px}p,li{max-width:78ch}#TOC{font:14px/1.7 system-ui,sans-serif;background:#f5f8f6;padding:20px 26px;margin:28px 0 40px;columns:2;column-gap:38px}#TOC ul{margin:0;padding-left:17px}#TOC li{break-inside:avoid;margin:5px 0}figure{margin:35px 0}.figure-scroll{overflow-x:auto;margin:28px 0 8px}.figure-scroll img{min-width:760px}img{display:block;width:100%;height:auto;max-width:100%;margin:22px auto}figcaption,.caption{font:14px/1.5 system-ui,sans-serif;color:var(--muted)}table{border-collapse:collapse;width:100%;font:14px/1.5 system-ui,sans-serif;margin:12px 0 25px}th,td{border:1px solid var(--line);padding:11px 12px;text-align:left;vertical-align:top}th{background:#e8f0ec;font-weight:600}th:first-child,td:first-child{min-width:110px}td{min-width:150px}.table-scroll{overflow-x:auto;max-width:100%;margin-bottom:24px}.footnotes{font-size:14px;line-height:1.6;margin-top:65px}.footnotes li{margin-bottom:14px}.footnote-ref{font:12px system-ui,sans-serif}blockquote{margin:22px 0;padding-left:22px;border-left:2px solid #bdcbc5}footer{font:13px/1.6 system-ui,sans-serif;margin-top:50px;border-top:1px solid var(--line);padding-top:20px}@media(max-width:600px){.reader{padding:20px 20px 60px}body{font-size:17px}#TOC{columns:1}h2{font-size:26px;margin-top:42px}table{font-size:13px}}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}@media print{.reader{max-width:none;padding:0}#TOC{columns:2}.top{display:none}a{color:inherit}.table-scroll{overflow:visible}h2,h3{break-after:avoid}figure{break-inside:avoid}}`;
const html='<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content="A source-bounded working paper on cultivated chicken, religious conditions, certification and food authorization."><title>Cultivated Chicken and Halal Market Access</title><style>'+css+'</style></head><body><div class="reader"><nav class="top" aria-label="Research navigation"><a href="../../../index.html">Research library</a><span>Working paper · 2 October 2026 · <a href="paper.md">Auditable Markdown</a></span></nav><main>'+main+'</main><footer>AI-assisted working draft; human verification pending. Local review edition. No institutional or mentor endorsement is implied.</footer></div></body></html>\n';
fs.writeFileSync(path.join(paper,'index.html'),html);
const hash=s=>crypto.createHash('sha256').update(s).digest('hex');
fs.writeFileSync(path.join(paper,'reader-build.json'),JSON.stringify({generator:'tools/export-paper.mjs',pandoc:execFileSync('pandoc',['--version'],{encoding:'utf8'}).split('\n')[0],manuscript_sha256:hash(original),reader_sha256:hash(html),human_review:'pending',published:false},null,2)+'\n');
if(process.argv.includes('--docx')){
 // Static internal links work immediately, without asking Word to update a field.
 const contents='## Contents\n\n'+sections.map(m=>'- ['+m[2].replace(/<[^>]+>/g,'')+'](#'+m[1]+')').join('\n')+'\n\n';
 const docxText=clean.replace(/^## 1\./m,contents+'## 1.');
 execFileSync('pandoc',[...args,'--to=docx','--output='+path.join(out,'cultivated-chicken-halal-working-paper.docx')],{input:docxText,stdio:['pipe','inherit','inherit']});
}
console.log(JSON.stringify({reader:'research/halal-cultivated/paper/index.html',markdown:'working/paper-release/paper.md',docx:process.argv.includes('--docx')}));
