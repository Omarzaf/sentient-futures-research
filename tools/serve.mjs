import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import {fileURLToPath} from 'node:url';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const manifest=JSON.parse(fs.readFileSync(path.join(root,'provenance/file-manifest.json'),'utf8'));
const allowed=new Set(manifest.files.map(f=>f.path).filter(p=>!p.split('/').some(s=>s.startsWith('.'))&&!p.startsWith('tools/')));
allowed.add('provenance/file-manifest.json');
const types={'.html':'text/html; charset=utf-8','.md':'text/plain; charset=utf-8','.json':'application/json; charset=utf-8','.csv':'text/csv; charset=utf-8','.ris':'application/x-research-info-systems','.svg':'image/svg+xml'};
const port=Number(process.env.RESEARCH_PORT||8796);
if(!Number.isInteger(port)||port<1024||port>65535)throw Error('RESEARCH_PORT must be an integer from 1024 to 65535');
const server=http.createServer((req,res)=>{
 if(!['GET','HEAD'].includes(req.method)){res.writeHead(405,{'Allow':'GET, HEAD'});res.end();return;}
 let name;try{name=decodeURIComponent(new URL(req.url,'http://localhost').pathname).replace(/^\//,'');}catch{res.writeHead(400);res.end();return;}
 if(!name||name.endsWith('/'))name+='index.html';
 if(!allowed.has(name)){res.writeHead(404);res.end('Not found');return;}
 const file=path.join(root,name);
 if(!fs.existsSync(file)||fs.lstatSync(file).isSymbolicLink()){res.writeHead(404);res.end('Not found');return;}
 const real=fs.realpathSync(file);if(!real.startsWith(root+path.sep)){res.writeHead(404);res.end('Not found');return;}
 res.writeHead(200,{'Content-Type':types[path.extname(name)]||'application/octet-stream','X-Content-Type-Options':'nosniff','Cache-Control':'no-store'});
 if(req.method==='HEAD')res.end();else fs.createReadStream(file).pipe(res);
});
server.on('error',err=>{console.error('Could not start local preview: '+err.code+'. Check RESEARCH_PORT and permission to bind to loopback.');process.exitCode=1;});
server.listen(port,'127.0.0.1',()=>console.log('Research library: http://127.0.0.1:'+port+'/'));
