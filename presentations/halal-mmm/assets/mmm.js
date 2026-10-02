/* Progressive enhancement for the MMM edition. The paper, figures, notes and
   every link work without this file; it adds the theme toggle, the active
   contents marker, the phone contents sheet, a "return" control after
   in-page detours, endnote origin marking and the optional web-font opt-in. */
(function(){
 'use strict';
 var root=document.documentElement;
 function $(id){return document.getElementById(id);}
 function each(sel,fn){Array.prototype.forEach.call(document.querySelectorAll(sel),fn);}
 function store(key,value){try{if(value===null)localStorage.removeItem(key);else localStorage.setItem(key,value);}catch(e){}}
 function stored(key){try{return localStorage.getItem(key);}catch(e){return null;}}

 /* theme */
 var themeBtn=$('themeToggle');
 function applyTheme(t){
  root.setAttribute('data-theme',t);
  themeBtn.textContent=t==='dark'?'Light':'Dark';
  themeBtn.setAttribute('aria-label',t==='dark'?'Switch to light theme':'Switch to dark theme');
 }
 if(themeBtn){
  themeBtn.hidden=false;
  applyTheme(root.getAttribute('data-theme')==='dark'?'dark':'light');
  themeBtn.addEventListener('click',function(){var next=root.getAttribute('data-theme')==='dark'?'light':'dark';applyTheme(next);store('mmm-theme',next);});
 }

 /* optional web fonts: loaded only after the reader asks */
 var FONT_URL='https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&display=swap';
 var fontBtn=$('fontToggle');
 function fontsOn(){
  if(document.getElementById('mmmWebFonts'))return;
  var l=document.createElement('link');l.rel='stylesheet';l.id='mmmWebFonts';l.href=FONT_URL;document.head.appendChild(l);
 }
 function fontsOff(){var l=$('mmmWebFonts');if(l)l.parentNode.removeChild(l);}
 function syncFontBtn(){var on=!!$('mmmWebFonts');fontBtn.textContent=on?'Stop using web fonts':'Load web fonts from Google Fonts';fontBtn.setAttribute('aria-pressed',String(on));}
 if(fontBtn){
  fontBtn.hidden=false;
  if(stored('mmm-webfonts')==='on')fontsOn();
  syncFontBtn();
  fontBtn.addEventListener('click',function(){if($('mmmWebFonts')){fontsOff();store('mmm-webfonts',null);}else{fontsOn();store('mmm-webfonts','on');}syncFontBtn();});
 }

 /* active section in the contents rail */
 var navLinks={};
 each('.leftnav a[href^="#"]',function(a){navLinks[a.getAttribute('href').slice(1)]=a;});
 if('IntersectionObserver' in window){
  var current=null;
  var io=new IntersectionObserver(function(entries){
   entries.forEach(function(en){
    if(!en.isIntersecting)return;
    var a=navLinks[en.target.id];if(!a||a===current)return;
    if(current){current.classList.remove('is-active');current.removeAttribute('aria-current');}
    a.classList.add('is-active');a.setAttribute('aria-current','location');current=a;
   });
  },{rootMargin:'-15% 0px -75% 0px'});
  Object.keys(navLinks).forEach(function(id){var el=$(id);if(el)io.observe(el);});
 }

 /* phone contents sheet: the contents rail opens over the page */
 var tocBtn=$('tocButton'),tocClose=$('tocClose'),toc=$('toc');
 function openToc(){
  root.classList.add('toc-open');tocBtn.setAttribute('aria-expanded','true');tocClose.hidden=false;
  var first=toc.querySelector('a');if(first)first.focus();
 }
 function closeToc(restore){
  if(!root.classList.contains('toc-open'))return;
  root.classList.remove('toc-open');tocBtn.setAttribute('aria-expanded','false');tocClose.hidden=true;
  if(restore)tocBtn.focus();
 }
 if(tocBtn&&toc){
  tocBtn.hidden=false;
  tocBtn.addEventListener('click',openToc);
  tocClose.addEventListener('click',function(){closeToc(true);});
  toc.addEventListener('click',function(e){if(e.target.closest&&e.target.closest('a'))closeToc(false);});
  document.addEventListener('keydown',function(e){if(e.key==='Escape')closeToc(true);});
  window.addEventListener('resize',function(){if(window.innerWidth>=980)closeToc(false);});
 }

 /* return control after an in-page detour (citation, figure point, cross-reference) */
 var chip=$('returnChip'),origin=null,watch=null,armed=false;
 function hideChip(){chip.hidden=true;origin=null;armed=false;if(watch){watch.disconnect();watch=null;}}
 function labelFor(a){
  var fig=a.closest('figure');
  if(fig){var no=fig.querySelector('.fig-no');return no?no.textContent.split(' — ')[0]:'the figure';}
  if(a.closest('.nref'))return 'note '+a.textContent;
  if(a.closest('.findings'))return 'the findings';
  if(a.closest('.hero-readout'))return 'the overview';
  return 'reading position';
 }
 function showChip(a){
  origin=a;chip.href='#'+a.id;chip.textContent='← Return to '+labelFor(a);chip.hidden=false;armed=false;
  if(watch)watch.disconnect();
  if('IntersectionObserver' in window){
   // Once the reader is back beside the origin by any route, the control is no longer needed.
   watch=new IntersectionObserver(function(entries){entries.forEach(function(en){if(en.isIntersecting&&armed)hideChip();if(!en.isIntersecting)armed=true;});});
   watch.observe(a);
  }
 }
 function goTo(el){
  el.scrollIntoView({block:'center'});
  try{el.focus({preventScroll:true});}catch(e){el.focus();}
 }
 if(chip){
  document.addEventListener('click',function(e){
   var a=e.target.closest&&e.target.closest('a[href^="#"]');
   if(!a||a===chip)return;
   if(a.closest('.leftnav')||a.closest('.toc-mobile')||a.classList.contains('skip')||a.classList.contains('skip-fig')){hideChip();return;}
   var id=a.getAttribute('href').slice(1);
   if(a.classList.contains('backref')){hideChip();markRefOrigin(id);return;}
   if(!a.id||!document.getElementById(id))return;
   showChip(a);
   if(a.closest('.nref'))markNoteOrigin(id,a.id);
  });
  chip.addEventListener('click',function(e){
   if(!origin)return;
   e.preventDefault();
   var o=origin;hideChip();
   try{history.pushState(null,'','#'+o.id);}catch(err){}
   markRefOrigin(o.id);goTo(o);
  });
 }

 /* endnotes: mark the back-link that returns to the reference just followed */
 function markNoteOrigin(noteId,refId){
  each('.backref.is-origin',function(b){b.classList.remove('is-origin');});
  var li=$(noteId);if(!li)return;
  var back=li.querySelector('a.backref[href="#'+refId+'"]');if(back)back.classList.add('is-origin');
 }
 function markRefOrigin(refId){
  each('.nref a.is-origin',function(r){r.classList.remove('is-origin');});
  var r=$(refId);if(r&&r.closest('.nref'))r.classList.add('is-origin');
 }
})();
