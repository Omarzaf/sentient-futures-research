const forbiddenPath=/(^|\/)(?:\.env(?:\.[^/]*)?|node_modules|\.venv(?:-[^/]+)?|\.playwright-mcp|\.agents|\.codex|\.tools|vendor|tool-cache|private|working|Research Loop Working|AGENTS\.md|\.DS_Store)(\/|$)|\.(?:docx?|xlsx?|pptx?|pdf|zip|pem|key|log)$/i;

const localHomePath=/\/(?:Users|home)\/[A-Za-z0-9._-]+\//g;
const httpUrlPrefix=/https?:\/\/[^\s"'`<>?#]*$/i;

function insideHttpUrlPath(text,index) {
 const before=text.slice(0,index);
 const boundary=Math.max(
  before.lastIndexOf(' '),
  before.lastIndexOf('\n'),
  before.lastIndexOf('\t'),
  before.lastIndexOf('"'),
  before.lastIndexOf("'"),
  before.lastIndexOf('`'),
  before.lastIndexOf('<'),
  before.lastIndexOf('>')
 );
 const tokenPrefix=before.slice(boundary+1);
 return httpUrlPrefix.test(tokenPrefix);
}

export function hasLocalHomePath(text) {
 localHomePath.lastIndex=0;
 for(const match of text.matchAll(localHomePath)) {
  if(!insideHttpUrlPath(text,match.index))return true;
 }
 return false;
}

const hazards=[
 ['absolute home path',hasLocalHomePath],
 ['private document URL',text=>/https?:\/\/(?:docs|drive)\.google\.com\//i.test(text)],
 ['email address',text=>/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/i.test(text)],
 ['private key',text=>/-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----/.test(text)],
 ['credential-like token',text=>/\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{25,}|sk-[A-Za-z0-9_-]{24,})\b/.test(text)],
 ['embedded raster',text=>/data:image\/(?:jpeg|png|webp);base64,/i.test(text)]
];

export function isExcludedPath(path) {
 return !Object.hasOwn(reviewedBinaryExports,path)&&forbiddenPath.test(path);
}

export function privacyHazards(text) {
 return hazards.filter(([,check])=>check(text)).map(([name])=>name);
}

export const privacyHazardNames=hazards.map(([name])=>name);
import crypto from 'node:crypto';

// Exact bytes reviewed for layout, metadata and source-link preservation, then
// explicitly approved by the author for feature-branch sharing on 2 October 2026.
export const reviewedBinaryExports=Object.freeze({
 'research/halal-cultivated/paper/exports/cultivated-chicken-halal-working-paper.pdf':'c0fcc56d198202520379d2c7a80fdc42e85751ee6c5285cf6c8604dc830ef50a',
 'research/halal-cultivated/paper/exports/cultivated-chicken-halal-working-paper.docx':'66a314d164d3d55d49ed8e5b9685bf9ea1b9dde66282680f142c3474c81d4458'
});

export function isReviewedBinaryExport(path,bytes) {
 return Object.hasOwn(reviewedBinaryExports,path)&&crypto.createHash('sha256').update(bytes).digest('hex')===reviewedBinaryExports[path];
}
