// Build a file-only release; never deploy the research repository itself.
// Usage: node tools/build-public-paper.mjs <new-release-directory>
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
if(!process.argv[2])throw new Error('Supply a new release directory outside the repository');
const release=path.resolve(process.argv[2]);
if(release===root||release.startsWith(root+path.sep))throw new Error('Release must be outside the repository');
if(fs.existsSync(release))throw new Error('Release directory already exists; preserve it and use a new destination');
const presentation='presentations/halal-mmm/index.html';
const edition=JSON.parse(fs.readFileSync(path.join(root,'presentations/halal-mmm/edition.json'),'utf8'));
if(edition.authorApproval?.approved!==true||edition.authorApproval.scope!=='HTML edition for public sharing')throw new Error('Public sharing approval is missing');
const copies=[[presentation,'index.html']];
// Publish only the approved self-contained HTML. Its local download links would
// require additional files outside this release's authorized upload scope.
const payload=copies.map(([source,target])=>{
  const file=path.join(root,source);
  if(!fs.lstatSync(file).isFile())throw new Error('Expected a regular source file: '+source);
  const original=fs.readFileSync(file);
  const html=original.toString('utf8');
  const downloadBlock=/<div class="related">[^]*?<\/div>/g;
  if([...html.matchAll(downloadBlock)].length!==1)throw new Error('Expected exactly one local download block');
  const originalFigureLinks=/ <a href="\.\.\/\.\.\/research\/halal-cultivated\/paper\/figures\/figure-(?:1-process|2-countries|3-audit)\.svg">Reviewed original \(SVG\)<\/a>/g;
  if([...html.matchAll(originalFigureLinks)].length!==3)throw new Error('Expected exactly three original-figure download links');
  return {source,target,bytes:Buffer.from(html.replace(downloadBlock,'').replace(originalFigureLinks,'')),sourceSha256:crypto.createHash('sha256').update(original).digest('hex')};
});
const publicRoot=path.join(release,'site/public');
for(const {source,target,bytes} of payload){
  if(!target.endsWith('.html'))continue;
  const html=bytes.toString('utf8').replace(/<script\b[^>]*>[\s\S]*?<\/script>/g,'').replace(/<style\b[^>]*>[\s\S]*?<\/style>/g,'');
  for(const [,href] of html.matchAll(/(?:href|src)="([^"#]+)"/g)){
    if(/^[a-z]+:/i.test(href)||href.startsWith('//'))continue;
    const url=new URL(href,'https://static.invalid/'+target);
    const destination=decodeURIComponent(url.pathname).replace(/^\//,'')||'index.html';
    if(!payload.some(p=>p.target===destination))throw new Error(`Missing public dependency in ${source}: ${href}`);
  }
}
fs.mkdirSync(publicRoot,{recursive:true});
const manifest=[];
for(const {source,target,bytes,sourceSha256} of payload){
  const dest=path.join(publicRoot,target);
  fs.mkdirSync(path.dirname(dest),{recursive:true});
  fs.writeFileSync(dest,bytes);
  manifest.push({source,sourceSha256,path:target,bytes:bytes.length,sha256:crypto.createHash('sha256').update(bytes).digest('hex')});
}
fs.writeFileSync(path.join(release,'site/vercel.json'),JSON.stringify({
  framework:null,buildCommand:null,outputDirectory:'public',
  headers:[{source:'/(.*)',headers:[{key:'X-Content-Type-Options',value:'nosniff'}]}]
},null,2)+'\n');
fs.writeFileSync(path.join(release,'publication-manifest.json'),JSON.stringify({
  schemaVersion:1,edition,files:manifest,
  scope:'One standalone approved HTML file, including its inline styles, scripts and figures. No separate research or download files.',
  transformation:'Removed exactly one footer block of local download links and three links to original SVG downloads; all paper text, notes, citations and inline figures are preserved.'
},null,2)+'\n');
console.log(JSON.stringify({status:'PASS',publicFiles:manifest.length,publicBytes:manifest.reduce((n,f)=>n+f.bytes,0),release},null,2));
