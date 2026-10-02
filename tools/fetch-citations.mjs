// Explicit public-source capture only. Retrieval never verifies a claim.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';
import {isIP} from 'node:net';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const args=process.argv.slice(2);
const option=(key,fallback)=>{const i=args.indexOf(key);return i<0?fallback:args[i+1];};
const run=option('--run',null);
if(!run||!/^[a-zA-Z0-9][a-zA-Z0-9._-]{0,80}$/.test(run))throw Error('Supply a unique --run name using letters, digits, dots and hyphens.');
const input=option('--input','research/halal-cultivated/paper/source-register.json');
const inputPath=path.resolve(root,input);
if(!inputPath.startsWith(root+path.sep))throw Error('Input must be inside the repository.');
const selected=option('--keys','').split(',').filter(Boolean);
const inputBytes=fs.readFileSync(inputPath);
const inputRows=JSON.parse(inputBytes.toString('utf8'));
if(!Array.isArray(inputRows))throw Error('Input must be a source array.');
const identities=new Set();
for(const row of inputRows){
 if(!row||typeof row!=='object'||!Array.isArray(row.aliases??[]))throw Error('Malformed source record.');
 for(const key of [row.key||row.id,...(row.aliases||[])]){
  if(typeof key!=='string'||!/^[A-Za-z0-9_-]+$/.test(key))throw Error('Unsafe source key');
  if(identities.has(key))throw Error('Duplicate or ambiguous source key: '+key);
  identities.add(key);
 }
 publicUrl(row.url);
}
for(const key of selected)if(!identities.has(key))throw Error('Unknown requested key: '+key);
const rows=inputRows.filter(r=>!selected.length||[r.key||r.id,...(r.aliases||[])].some(k=>selected.includes(k)));
if(!rows.length)throw Error('No source rows selected.');
const out=path.join(root,'working','citations',run);
if(fs.existsSync(out))throw Error('Run exists; choose another name to preserve its evidence.');
fs.mkdirSync(out,{recursive:true});
const sha=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
const save=(name,value)=>fs.writeFileSync(path.join(out,name),typeof value==='string'?value:JSON.stringify(value,null,2)+'\n');
fs.writeFileSync(path.join(out,'input-snapshot.json'),inputBytes);
save('selected-rows.json',rows);

function publicUrl(value){
 const u=new URL(value);
 if(!['https:','http:'].includes(u.protocol)||u.username||u.password||u.port&&!['80','443'].includes(u.port))throw Error('Unsupported public-source URL');
 if(!u.hostname.includes('.')||isIP(u.hostname)||u.hostname.startsWith('[')||/\.(?:local|internal|test|localhost)$/i.test(u.hostname))throw Error('Non-public host rejected');
 return u.href;
}
function htmlText(raw){
 const common={amp:'&',lt:'<',gt:'>',quot:'"',apos:"'",nbsp:' ',ndash:'–',mdash:'—',lsquo:'‘',rsquo:'’',ldquo:'“',rdquo:'”'};
 return raw.replace(/<(script|style|noscript)\b[^>]*>[\s\S]*?<\/\1>/gi,' ').replace(/<\/(?:p|div|li|h[1-6]|tr)>/gi,'\n').replace(/<[^>]*>/g,' ').replace(/&(#x[0-9a-f]+|#\d+|[a-z]+);/gi,(all,s)=>{if(!s.startsWith('#'))return common[s.toLowerCase()]??all;const n=s[1].toLowerCase()==='x'?parseInt(s.slice(2),16):parseInt(s.slice(1),10);return n>0&&n<=0x10ffff?String.fromCodePoint(n):all;}).replace(/[\t ]+/g,' ').replace(/\n\s*\n/g,'\n').trim();
}
async function capture(row){
 const key=row.key||row.id;
 if(!/^[A-Za-z0-9_-]+$/.test(key))throw Error('Unsafe source key');
 const receipt={key,aliases:row.aliases||[],url_checked:row.url,final_url:null,http_status:null,content_type:null,retrieved_at:new Date().toISOString(),redirects:[],bytes:0,sha256:null,text_sha256:null,capture_status:'not_retrieved',audit_verdict:'pending',error:null};
 try{
  let url=publicUrl(row.url),response;
  const signal=AbortSignal.timeout(30000);
  for(let hop=0;hop<=6;hop++){
   response=await fetch(url,{redirect:'manual',signal,headers:{'User-Agent':'SentientFutures-CitationAudit/1.0','Accept':'text/html,application/pdf,application/json,text/plain;q=0.9,*/*;q=0.5'}});
   receipt.final_url=url;receipt.http_status=response.status;receipt.content_type=response.headers.get('content-type')||'';
   if([301,302,303,307,308].includes(response.status)&&response.headers.get('location')){
    const next=publicUrl(new URL(response.headers.get('location'),url).href);
    receipt.redirects.push({status:response.status,from:url,to:next});
    await response.body?.cancel();url=next;if(hop===6)throw Error('Redirect limit reached');continue;
   }
   break;
  }
  const chunks=[];let size=0;
  for await(const chunk of response.body){size+=chunk.length;if(size>40*1024*1024){throw Error('Source exceeds 40 MiB capture limit');}chunks.push(chunk);}
  const bytes=Buffer.concat(chunks);receipt.bytes=bytes.length;receipt.sha256=sha(bytes);
  const pdf=bytes.subarray(0,5).toString()==='%PDF-';
  const ext=pdf?'pdf':/json/i.test(receipt.content_type)?'json':/html/i.test(receipt.content_type)?'html':'bin';
  fs.writeFileSync(path.join(out,key+'.'+ext),bytes);
  let plain='';
  if(pdf){try{plain=execFileSync('pdftotext',['-layout',path.join(out,key+'.pdf'),'-'],{encoding:'utf8',maxBuffer:32*1024*1024,timeout:30000});}catch(e){receipt.extraction_error=e.code||e.message.slice(0,180);}}
  else if(/html|text|json|xml/i.test(receipt.content_type)){
   const encoding=/charset\s*=\s*["']?([^;\s"']+)/i.exec(receipt.content_type)?.[1]||'utf-8';
   receipt.text_encoding=encoding;
   try{const decoded=new TextDecoder(encoding,{fatal:true}).decode(bytes);plain=/html|xml/i.test(receipt.content_type)?htmlText(decoded):decoded;}
   catch{receipt.extraction_error='Unsupported or invalid text encoding: '+encoding;}
  }
  if(plain){save(key+'.txt',plain);receipt.text_sha256=sha(plain);receipt.text_characters=plain.length;}
  const blocked=/access denied|request blocked|verify you are human|enable javascript|client challenge|just a moment|captcha/i.test(plain.slice(0,1600));
  receipt.capture_status=response.ok&&bytes.length&&plain.length>120&&!blocked?'retrieved_candidate':'not_retrieved';
  receipt.note='Candidate means bytes and extractable text only. Identity, locator, exact passage, context and bibliography require a separate review.';
 }catch(error){receipt.error={name:error.name,message:error.message,cause:error.cause?.code||null};}
 save(key+'.receipt.json',receipt);
 process.stdout.write(JSON.stringify({key,status:receipt.capture_status,http:receipt.http_status,bytes:receipt.bytes,error:receipt.error})+'\n');
 return receipt;
}
const receipts=[];
// Bounded batches limit concurrent requests; every request has a timeout.
for(let i=0;i<rows.length;i+=3){receipts.push(...await Promise.all(rows.slice(i,i+3).map(capture)));}
save('manifest.json',{run,input,input_sha256:sha(inputBytes),selected_rows_sha256:sha(JSON.stringify(rows,null,2)+'\n'),captured_at:new Date().toISOString(),count:receipts.length,receipts});
