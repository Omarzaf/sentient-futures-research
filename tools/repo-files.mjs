// Helpers shared by verify.mjs and build-library.mjs.
import fs from 'node:fs';
import path from 'node:path';
import {execFileSync} from 'node:child_process';

// Files Git tracks plus new files it does not ignore. Gitignored local material
// (drive-archive/, uploads/, .env, .DS_Store) never reaches the manifest or the checks.
export function repoFiles(root) {
 const out=execFileSync('git',['ls-files','-z','--cached','--others','--exclude-standard'],{cwd:root,encoding:'utf8',maxBuffer:1<<26});
 return [...new Set(out.split('\0'))].filter(p=>p&&fs.lstatSync(path.join(root,p),{throwIfNoEntry:false})).sort();
}
export const unescapeEntities=s=>s.replaceAll('&amp;','&').replaceAll('&quot;','"').replaceAll('&#39;',"'");
