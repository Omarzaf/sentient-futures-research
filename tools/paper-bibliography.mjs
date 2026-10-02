/** Format the checked identity without inventing missing edition metadata. */
export function bibliographyEntry(source) {
 const b=source.bibliographic;
 const names=b.author.split(/;\s*/);
 if(b.journal&&names.length){const words=names[0].split(' ');if(words.length>1)names[0]=words.pop()+', '+words.join(' ');}
 const author=names.length>2?names.slice(0,-1).join(', ')+', and '+names.at(-1):names.join(', and ');
 const book=/classical|manual|book|dossier/.test(source.source_type??'')||/Islamic Laws|Radd al-|al-Mughni|Bidayat|al-Dhakhira|Hashiyat/.test(b.title);
 const parts=[author+'.',book?`*${b.title}*.`:`“${b.title}.”`];
 if(b.journal)parts.push(`*${b.journal}* ${b.volume??''}${b.issue?`, no. ${b.issue}`:''} (${b.year??'n.d.'})${b.page?`: ${b.page}`:''}.`);
 else {
  if(b.translator)parts.push(`Translated by ${b.translator}.`);
  if(b.editor)parts.push(`Edited by ${b.editor}.`);
  if(b.volume)parts.push(`Vol. ${b.volume}.`);
  if(b.publisher&&b.publisher!==b.author)parts.push(`${b.place?b.place+': ':''}${b.publisher}, ${b.year??'n.d.'}.`);
  else parts.push(`${b.year??'n.d.'}.`);
 }
 if(source.locator)parts.push('Cited location: '+source.locator+'.');
 parts.push(source.doi?`https://doi.org/${source.doi}.`:`${source.url}.`);
 parts.push(`Accessed ${source.accessed??'2026-10-02'}.`);
 if(b.year===null)parts.push('Publication year unestablished; cited digital version and locator retained.');
 return parts.filter(Boolean).join(' ').replaceAll('n.d..','n.d.').replaceAll('.. ','. ')+' ['+source.key+']';
}

/** Return only keys present at the end of footnote definitions. */
export function citedSourceKeys(markdown) {
 const keys=new Set();
 for(const line of markdown.split('\n'))if(/^\[\^[^\]]+\]:/.test(line)) {
  const suffix=line.match(/((?:\s*\[[A-Z][A-Z0-9-]*(?:\s*[;,]\s*[A-Z][A-Z0-9-]*)*\])+)[\s.]*$/);
  for(const match of (suffix?.[1]??'').matchAll(/\[([^\]]+)\]/g))for(const key of match[1].split(/[;,]/))keys.add(key.trim());
 }
 return [...keys];
}
