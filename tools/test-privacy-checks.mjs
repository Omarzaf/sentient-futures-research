import assertStrict from 'node:assert/strict';
import {isExcludedPath, privacyHazards, privacyHazardNames} from './privacy-checks.mjs';

let cases=0;
const assert=(...args)=>{cases++;assertStrict(...args);};

assert(privacyHazardNames.includes('absolute home path'));
const slash='/';
const at='@';
const user='omar';
const usersPath=slash+'Users/'+user+'/';
const homePath=slash+'home/'+user+'/';

const safeUrls=[
 'https://www.thermofisher.com/us/en/home/references/gibco-cell-culture-basics/cell-culture-environment/culture-media.html',
 'https://example.org/home/references/report.pdf',
 'http://localhost:9000/home/references/index.html',
 'A public page can contain the word /home/references after a hostname.'
];
for(const text of safeUrls)assert(!privacyHazards(text).includes('absolute home path'),text);

const unsafeHomePaths=[
 usersPath+'Downloads/private-note.md',
 'source='+homePath+'project/.env',
 'Open (`'+usersPath+'Documents/report.md`) before packaging.',
 'file://'+usersPath+'Desktop/private-note.md',
 '<a>'+usersPath+'Desktop/private-note.md</a>',
 '['+usersPath+'Desktop/private-note.md]',
 'path:'+usersPath+'Desktop/private-note.md',
 '`https://example.org/home/references/index.html`'+usersPath+'Desktop/private-note.md',
 'https://example.org/download?path='+homePath+'project',
 'https://example.org/#'+homePath+'project'
];
for(const text of unsafeHomePaths)assert(privacyHazards(text).includes('absolute home path'),text);

assert(privacyHazards('https://'+'docs.google.com/document/d/example/edit').includes('private document URL'));
assert(privacyHazards('contact '+['researcher','example.org'].join(at)).includes('email address'));
assert(privacyHazards('-----BEGIN '+'PRIVATE KEY-----\nabc').includes('private key'));
assert(privacyHazards('token '+'ghp_'+'abcdefghijklmnopqrstuvwxyz').includes('credential-like token'));
assert(privacyHazards('background:'+'data:'+'image/png;'+'base64,AAAA').includes('embedded raster'));

for(const path of ['.env','.env.local','.env.production.local','config/.env.local','nested/.env','notes/private/file.md','paper.pdf','bundle.zip','secret.pem','run.log'])assert(isExcludedPath(path),path);
// These paths would enter the all-files manifest if accidentally copied into the
// library; verify.mjs uses this same gate on every manifest/repository path.
for(const path of [
 '.agents/skills/paper-lookup/SKILL.md',
 'nested/.agents/skills/tool/source.mjs',
 '.codex/config.toml',
 '.tools/paper-lookup/package.json',
 'vendor/paper-lookup/README.md',
 'tool-cache/candidate/manifest.json',
 '.venv-stats/lib/package.py',
 'OUTPUTS/Research Loop Working/audit/actions.jsonl',
 'private/retrieval.md',
 'working/review-packet.json',
])assert(isExcludedPath(path),path);
for(const path of ['research/protein-survey-data/README.md','sources/catalog.json','research/ai-protein/index.html'])assert(!isExcludedPath(path),path);

// Paper exports stay outside the repository, whatever their name.
for(const path of ['research/halal-cultivated/paper/exports/cultivated-chicken-halal-working-paper.pdf','research/halal-cultivated/paper/exports/cultivated-chicken-halal-working-paper.docx'])assert(isExcludedPath(path),path);

console.log(JSON.stringify({status:'PASS',cases,failed:0}));
