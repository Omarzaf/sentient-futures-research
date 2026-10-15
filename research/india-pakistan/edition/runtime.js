/* D3 7.9.0 is vendored inline. This runtime never fetches evidence or telemetry. */
(() => {
  'use strict';
  const specs = Object.fromEntries([...document.querySelectorAll('script[data-chart]')].map(node => [node.dataset.chart, JSON.parse(node.textContent)]));
  const geometry = JSON.parse(document.getElementById('edition-geography').textContent);
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const systemTheme = matchMedia('(prefers-color-scheme: dark)');
  const tip = document.getElementById('chart-tooltip');
  const css = name => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  const color = country => css(country === 'India' ? '--in' : country === 'Pakistan' ? '--pk' : '--ink-3');
  const safe = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const human = value => String(value ?? '').replaceAll('_', ' ');
  const number = value => value === '' || value === null || value === undefined ? null : Number.isFinite(Number(value)) ? Number(value) : null;
  const short = value => { const n=number(value); if(n===null)return 'Unavailable'; const a=Math.abs(n); for(const [scale,label] of [[1e9,'B'],[1e6,'M'],[1e3,'k']])if(a>=scale)return d3.format('.3~g')(n/scale)+label;return d3.format('.3~g')(n); };
  let printMode=false;
  let redrawTimer;
  let pendingAnimations=0;
  const motionObserver=new IntersectionObserver(entries=>entries.forEach(entry=>{
    if(!entry.isIntersecting)return;
    const element=entry.target;motionObserver.unobserve(element);
    if(reduced.matches||printMode||!element.isConnected)return;
    if(element.matches('path[data-draw-line]')){
      pendingAnimations++;
      d3.select(element).transition().duration(700).ease(d3.easeCubicOut).style('stroke-dashoffset','0').on('end interrupt cancel',()=>{pendingAnimations=Math.max(0,pendingAnimations-1);element.style.strokeDasharray='';element.style.strokeDashoffset='';});
    }else element.classList.add('motion-visible');
  }),{threshold:.08});
  const disputed = new Set(['Jammu and Kashmīr','Jammu and Kashmir','Ladākh','Ladakh','Azad Kashmir','Gilgit-Baltistan']);
  function hideTip(){tip.style.opacity='0';tip.setAttribute('aria-hidden','true');tip.removeAttribute('data-mark');}
  function showTip(event, content){
    tip.innerHTML=content;tip.style.opacity='1';tip.removeAttribute('aria-hidden');
    const box=event.currentTarget?.getBoundingClientRect?.();
    const px=Number.isFinite(event.clientX)?event.clientX:(box?.left??innerWidth/2)+(box?.width??0)/2;
    const py=Number.isFinite(event.clientY)?event.clientY:(box?.top??innerHeight/2);
    const w=tip.offsetWidth,h=tip.offsetHeight;
    const x=Math.max(8,Math.min(innerWidth-w-8,px+14));
    const y=Math.max(8,Math.min(innerHeight-h-8,py+14));
    tip.style.left=x+'px';tip.style.top=y+'px';
  }
  function mark(selection, describe){
    selection.attr('class', (d,i,nodes) => (nodes[i].getAttribute('class')||'')+' chart-mark')
      .on('pointerenter', (event,row)=>showTip(event,describe(row)))
      .on('pointermove',(event,row)=>showTip(event,describe(row)))
      .on('pointerleave',hideTip)
      .on('focus',(event,row)=>showTip(event,describe(row)))
      .on('blur',hideTip);
    selection.append('title').text(row=>describe(row).replace(/<[^>]*>/g,' ').replaceAll('&amp;','&'));
    return selection;
  }
  function rowTip(row, spec, fields){
    return `<span class="tip-label">${safe(row.country||row.region||row.company||row.study_id||spec.title)}</span>`+fields.filter(key=>row[key]!==undefined&&row[key]!=='').map(key=>`${safe(human(key))}: ${safe(row[key])}`).join('<br>')+`<div class="t-src">${safe(row.source_id||spec.source_ids.join('; '))} · ${safe(row.tier||'source-bound')}</div>`;
  }
  function frame(host,height=290){
    const width=Math.max(270,host.clientWidth||540);
    const svg=d3.select(host).append('svg').attr('viewBox',`0 0 ${width} ${height}`).attr('role','img').attr('aria-label',host.getAttribute('aria-label')||'Source-bound chart');
    svg.append('title').text(host.getAttribute('aria-label')||'Source-bound chart');
    return {svg,width,height};
  }
  function legend(host,countries){
    if(countries.length<2)return;
    const element=document.createElement('div');element.className='legend';
    for(const country of countries){const item=document.createElement('span');item.style.setProperty('--series-color',color(country));item.innerHTML='<i aria-hidden="true"></i>'+safe(country);element.append(item);}
    host.append(element);
  }
  function animatePath(path){
    if(reduced.matches||printMode)return;
    path.each(function(){
      if(!this.getTotalLength)return;
      const length=this.getTotalLength();if(!Number.isFinite(length)||length===0)return;
      this.style.strokeDasharray=String(length);this.style.strokeDashoffset=String(length);
      this.dataset.drawLine='true';motionObserver.observe(this);
    });
  }
  function axes(svg,x,y,width,height,margin,years=true){
    svg.append('g').attr('class','chart-grid').attr('transform',`translate(${margin.left},0)`).call(d3.axisLeft(y).ticks(4).tickSize(-(width-margin.left-margin.right)).tickFormat(''));
    svg.append('g').attr('class','chart-axis').attr('transform',`translate(0,${height-margin.bottom})`).call(d3.axisBottom(x).ticks(width<420?3:5).tickFormat(years?d3.format('d'):short).tickSizeOuter(0));
    svg.append('g').attr('class','chart-axis').attr('transform',`translate(${margin.left},0)`).call(d3.axisLeft(y).ticks(4).tickFormat(short).tickSize(0)).call(g=>g.select('.domain').remove());
  }
  function drawLine(host,spec,opt){
    const rows=spec.rows.filter(row=>number(row[opt.x||'year'])!==null&&number(row[opt.y||'value'])!==null);
    if(!rows.length){host.innerHTML='<p class="chart-empty">No source values are available in this selection.</p>';return;}
    const countries=[...new Set(rows.map(row=>row[opt.series||'country']||opt.country||''))];
    legend(host,countries);
    const {svg,width,height}=frame(host,opt.mini?155:290),margin={left:42,right:opt.mini?51:75,top:18,bottom:30};
    const years=rows.map(row=>Number(row[opt.x||'year']));let domain=d3.extent(years);if(domain[0]===domain[1])domain=[domain[0]-1,domain[1]+1];
    const x=d3.scaleLinear().domain(domain).range([margin.left,width-margin.right]);
    const y=d3.scaleLinear().domain([0,d3.max(rows,row=>Math.max(Number(row[opt.y||'value']),number(row[opt.high])??0))*1.12||1]).nice().range([height-margin.bottom,margin.top]);
    axes(svg,x,y,width,height,margin);
    countries.forEach(country=>{
      const data=rows.filter(row=>(row[opt.series||'country']||opt.country||'')===country).slice().sort((a,b)=>Number(a[opt.x||'year'])-Number(b[opt.x||'year']));
      const ink=color(country);
      if(opt.low&&opt.high){
        const area=d3.area().defined(row=>number(row[opt.low])!==null&&number(row[opt.high])!==null).x(row=>x(Number(row[opt.x||'year']))).y0(row=>y(Number(row[opt.low]))).y1(row=>y(Number(row[opt.high])));
        svg.append('path').datum(data).attr('d',area).attr('fill',ink).attr('opacity',.14);
      }
      const line=d3.line().x(row=>x(Number(row[opt.x||'year']))).y(row=>y(Number(row[opt.y||'value'])));
      if(opt.projection){
        const historical=data.filter(row=>!String(row.metric).endsWith('_projection'));
        const projected=data.filter(row=>String(row.metric).endsWith('_projection'));
        svg.append('path').datum(historical).attr('d',line).attr('fill','none').attr('stroke',ink).attr('stroke-width',2);
        svg.append('path').datum(projected).attr('d',line).attr('fill','none').attr('stroke',ink).attr('stroke-width',2).attr('stroke-dasharray','5 4');
      }else{
        const path=svg.append('path').datum(data).attr('d',line).attr('fill','none').attr('stroke',ink).attr('stroke-width',opt.mini?1.8:2.2);
        if(!opt.mini)animatePath(path);
      }
      mark(svg.append('g').selectAll('circle').data(data).join('circle').attr('cx',row=>x(Number(row[opt.x||'year']))).attr('cy',row=>y(Number(row[opt.y||'value']))).attr('r',opt.mini?2.2:3.6).attr('fill',ink).attr('stroke',css('--paper')).attr('stroke-width',1),row=>rowTip(row,spec,[opt.x||'year',opt.y||'value',opt.low,opt.high,'metric','unit'].filter(Boolean)));
      const last=data[data.length-1];
      svg.append('text').attr('class','chart-end-label').attr('x',x(Number(last[opt.x||'year']))+7).attr('y',y(Number(last[opt.y||'value']))+(country==='India'?-6:13)).attr('fill',css('--ink-2')).style('font-size',opt.mini?'10px':null).text(country);
    });
  }
  function drawPaired(host,spec,opt){
    const rows=spec.rows,{svg,width}=frame(host,25),scale=d3.scaleLinear().domain([0,d3.max(rows,row=>Number(row[opt.value]))*1.04]).range([0,width]);
    mark(svg.selectAll('rect').data(rows).join('rect').attr('x',0).attr('y',(_,i)=>i*12+2).attr('height',6).attr('rx',2).attr('width',row=>scale(Number(row[opt.value]))).attr('fill',row=>color(row.country)),row=>rowTip(row,spec,['year',opt.value,'unit']));
  }
  function drawBars(host,spec,opt){
    const rows=spec.rows.filter(row=>number(row[opt.value||'value'])!==null);
    if(!rows.length){host.innerHTML='<p class="chart-empty">No compatible values are available.</p>';return;}
    const {svg,width,height}=frame(host,Math.max(130,rows.length*33+40)),margin={left:Math.min(130,width*.39),right:50,top:16,bottom:20};
    const x=d3.scaleLinear().domain([0,d3.max(rows,row=>Number(row[opt.value||'value']))*1.08||1]).range([margin.left,width-margin.right]);
    rows.forEach((row,i)=>{
      const y=margin.top+i*33;
      const label=human(row[opt.label||'region']).replace('Islamabad Capital Territory','Islamabad').replace('Khyber Pakhtunkhwa','KP');
      svg.append('text').attr('class','chart-label').attr('x',margin.left-10).attr('y',y+11).attr('text-anchor','end').style('font-size','11px').text(label);
      mark(svg.append('rect').datum(row).attr('x',margin.left).attr('y',y).attr('width',x(Number(row[opt.value||'value']))-margin.left).attr('height',15).attr('rx',2).attr('fill',color(row.country||opt.country)),d=>rowTip(d,spec,[opt.label||'region',opt.value||'value','unit','year','residence','denominator']));
      svg.append('text').attr('class','chart-label').attr('x',x(Number(row[opt.value||'value']))+6).attr('y',y+11).style('font-size','11px').text(short(row[opt.value||'value']));
    });
  }
  function rewind(featureCollection){
    const copy=structuredClone(featureCollection);
    copy.features.forEach(feature=>{
      const multi=feature.geometry.type==='MultiPolygon';
      const polygons=multi?feature.geometry.coordinates:[feature.geometry.coordinates];
      const corrected=polygons.map(polygon=>d3.geoArea({type:'Polygon',coordinates:[polygon[0]]})>2*Math.PI?polygon.map(ring=>ring.slice().reverse()):polygon);
      feature.geometry.coordinates=multi?corrected:corrected[0];
    });return copy;
  }
  const geographies=Object.fromEntries(Object.entries(geometry).map(([country,fc])=>[country,rewind(fc)]));
  function drawMap(host,spec,opt){
    const residence=opt.residenceControl?document.getElementById(opt.residenceControl).value:'all';
    const rows=spec.rows.filter(row=>row.residence===residence);
    const values=Object.fromEntries(rows.filter(row=>row.boundary_shape_id).map(row=>[row.boundary_shape_id,row]));
    const plot=document.createElement('div');plot.className='map-plot';host.append(plot);
    const {svg,width}=frame(plot,400),fc=geographies[opt.country],proj=d3.geoMercator().fitExtent([[8,8],[width-8,392]],fc),path=d3.geoPath(proj);
    const patternId='hatch-'+host.id;
    const pattern=svg.append('defs').append('pattern').attr('id',patternId).attr('patternUnits','userSpaceOnUse').attr('width',5).attr('height',5).attr('patternTransform','rotate(45)');
    pattern.append('rect').attr('width',5).attr('height',5).attr('fill',css('--paper-2'));
    pattern.append('line').attr('x1',0).attr('x2',0).attr('y1',0).attr('y2',5).attr('stroke',css('--hatch')).attr('stroke-width',1.4);
    const numeric=rows.filter(row=>number(row.value)!==null).map(row=>Number(row.value)),extent=d3.extent(numeric);
    const ramp=d3.scaleLinear().domain(extent[0]===extent[1]?[0,extent[1]||1]:extent).range([css(opt.country==='India'?'--in-soft':'--pk-soft'),color(opt.country)]).interpolate(d3.interpolateLab);
    const paths=svg.selectAll('path').data(fc.features).join('path').attr('d',path).attr('stroke',css('--paper')).attr('stroke-width',.7).attr('fill',feature=>disputed.has(feature.properties.shapeName)?`url(#${patternId})`:values[feature.properties.shapeID]?ramp(Number(values[feature.properties.shapeID].value)):css('--paper-3'));
    mark(paths,feature=>{const row=values[feature.properties.shapeID];return `<span class="tip-label">${safe(feature.properties.shapeName)}</span>${row?`${safe(row.value)} ${safe(row.unit)}`:'No matching source observation'}${disputed.has(feature.properties.shapeName)?'<br>Hatched without data colour.':''}<div class="t-src">${safe(spec.source_ids.join('; '))}</div>`;});
    const scale=document.createElement('div');scale.className='map-ramp';scale.innerHTML=`<span>${safe(short(extent[0]))}</span><span class="ramp-fill" style="background:linear-gradient(90deg,${css(opt.country==='India'?'--in-soft':'--pk-soft')},${color(opt.country)})"></span><span>${safe(short(extent[1]))}</span><span class="hatch-key"></span><span>Hatched without data colour</span>`;host.append(scale);
    const fallback=document.createElement('div');fallback.className='ranked-fallback';
    const ranked=rows.slice().sort((a,b)=>Number(b.value)-Number(a.value));
    const maximum=d3.max(ranked,row=>Number(row.value))||1;
    fallback.innerHTML='<p class="fig-sub">Ranked source values; the complete table is below.</p><ol class="ranked-list">'+ranked.map(row=>`<li><span>${safe(row.region)}</span><span class="ranked-track"><span style="width:${Number(row.value)/maximum*100}%;background:${disputed.has(row.region)?`repeating-linear-gradient(45deg,${css('--paper-2')},${css('--paper-2')} 3px,${css('--hatch')} 3px,${css('--hatch')} 4px)`:color(opt.country)}"></span></span><span class="value" title="${safe(row.value)} ${safe(row.unit)}">${safe(short(row.value))}</span></li>`).join('')+'</ol>';
    host.append(fallback);
  }
  function drawStack(host,spec,opt){
    const residence=document.getElementById(opt.residenceControl).value;
    const rows=spec.rows.filter(row=>row.residence===residence);
    const groups=[...new Set(rows.map(row=>row.fractile))],categories=[...new Set(rows.map(row=>row.food_group))];
    const legendEl=document.createElement('div');legendEl.className='legend';
    legendEl.innerHTML=categories.map((category,i)=>`<span><span class="swatch" style="background:${color('India')};opacity:${.35+.65*i/Math.max(1,categories.length-1)}"></span>${safe(human(category))}</span>`).join('');host.append(legendEl);
    const {svg,width}=frame(host,groups.length*31+35),left=67,right=12,plotWidth=width-left-right;
    groups.forEach((group,i)=>{
      svg.append('text').attr('class','chart-label').attr('x',left-7).attr('y',i*31+17).attr('text-anchor','end').style('font-size','10px').text(group);
      let offset=0;
      categories.forEach((category,j)=>{
        const row=rows.find(r=>r.fractile===group&&r.food_group===category);if(!row||number(row.value)===null)return;
        const rect=svg.append('rect').datum(row).attr('x',left+offset/100*plotWidth).attr('y',i*31+5).attr('width',Number(row.value)/100*plotWidth).attr('height',18).attr('fill',color('India')).attr('fill-opacity',.35+.65*j/Math.max(1,categories.length-1)).attr('stroke',css('--paper')).attr('stroke-width',.5);
        mark(rect,d=>rowTip(d,spec,['residence','fractile','food_group','value','unit']));offset+=Number(row.value);
      });
    });
  }
  function drawReference(host,spec,opt){
    const reference=document.getElementById(opt.referenceControl).value,weight=document.getElementById(opt.weightControl).value,residence=document.getElementById(opt.residenceControl).value;
    const rows=spec.rows.filter(row=>row.reference_type===reference&&row.reference_weight_kg===weight&&row.residence===residence&&number(row.intake_g)!==null);
    const note=document.createElement('p');note.className='fig-sub';note.textContent=`${reference} at ${weight} kg. Solid: published consumer-unit mean. Dashed: adult reference.`;host.append(note);
    const {svg,width}=frame(host,rows.length*31+40),left=68,right=55,scale=d3.scaleLinear().domain([0,d3.max(rows,row=>Math.max(Number(row.intake_g),Number(row.requirement_g)))*1.12||1]).range([left,width-right]);
    rows.forEach((row,i)=>{
      const y=i*31+12;
      svg.append('text').attr('class','chart-label').attr('x',left-7).attr('y',y+10).attr('text-anchor','end').style('font-size','10px').text(row.fractile);
      mark(svg.append('rect').datum(row).attr('x',left).attr('y',y).attr('width',scale(Number(row.intake_g))-left).attr('height',15).attr('rx',2).attr('fill',color('India')),d=>rowTip(d,spec,['survey_group','intake_g','reference_type','reference_weight_kg','requirement_g','comparison_status']));
      svg.append('line').attr('x1',scale(Number(row.requirement_g))).attr('x2',scale(Number(row.requirement_g))).attr('y1',y-3).attr('y2',y+18).attr('stroke',css('--ink-1')).attr('stroke-width',1.2).attr('stroke-dasharray','3 2');
      svg.append('text').attr('class','chart-label').attr('x',scale(Number(row.intake_g))+5).attr('y',y+11).style('font-size','11px').text(row.intake_g);
    });
  }
  function drawRange(host,spec,opt){
    const maximum=d3.max(spec.rows,row=>Number(row[opt.high]))*1.06;
    spec.rows.forEach(row=>{
      const wrapper=document.createElement('div');wrapper.className='method-range';wrapper.innerHTML=`<h4>${safe(human(row[opt.label]))}</h4><p class="fig-sub">${safe(d3.format('.2f')(Number(row[opt.low])))} to ${safe(d3.format('.2f')(Number(row[opt.high])))} ${safe(row.unit)}</p>`;host.append(wrapper);
      const {svg,width}=frame(wrapper,60),lo=Number(row[opt.low]),hi=Number(row[opt.high]),x=d3.scaleLinear().domain([0,maximum]).range([15,width-15]);
      svg.append('line').attr('x1',15).attr('x2',width-15).attr('y1',24).attr('y2',24).attr('stroke',css('--paper-3')).attr('stroke-width',7);
      mark(svg.append('line').datum(row).attr('x1',x(lo)).attr('x2',x(hi)).attr('y1',24).attr('y2',24).attr('stroke',color(opt.country)).attr('stroke-width',7),r=>rowTip(r,spec,['scope','low','high','low_method','high_method','unit','range_type']));
      for(const value of [lo,hi])svg.append('circle').attr('cx',x(value)).attr('cy',24).attr('r',4).attr('fill',color(opt.country));
      svg.append('g').attr('class','chart-axis').attr('transform','translate(0,38)').call(d3.axisBottom(x).ticks(4).tickFormat(short).tickSizeOuter(0));
      const descriptions={bd_cuts_rohu_us_small:'Bangladesh edible-cut factors, boneless rohu fish and US small-egg portions',edible_flesh_us_jumbo:'reported meat and fish quantities treated as edible flesh, with US jumbo-egg portions'};
      const methods=document.createElement('p');methods.className='fig-sub';methods.textContent=`Lower endpoint: ${descriptions[row.low_method]||human(row.low_method)}. Upper endpoint: ${descriptions[row.high_method]||human(row.high_method)}. The method identifiers remain in Show data.`;wrapper.append(methods);
    });
  }
  function drawDots(host,spec){
    const grid=document.createElement('div');grid.className='dot-pair';host.append(grid);
    spec.rows.forEach(row=>{
      const box=document.createElement('div');box.innerHTML=`<div class="dot-number">${safe(row.value)}%</div><div class="dot-country" style="color:${color(row.country)}">${safe(row.country)}</div>`;
      const dots=document.createElement('div');dots.className='dots';dots.setAttribute('role','img');dots.setAttribute('aria-label',`${row.country}: ${row.value}%`);
      const value=Number(row.value);
      for(let i=0;i<100;i++){
        const dot=document.createElement('i'),portion=Math.max(0,Math.min(1,value-i));
        dot.style.background=portion===1?color(row.country):portion===0?css('--paper-3'):`linear-gradient(90deg,${color(row.country)} ${portion*100}%,${css('--paper-3')} ${portion*100}%)`;
        dot.style.setProperty('--dot-delay',`${i*3}ms`);
        dot.title=`${row.country}: ${row.value}% · ${row.source_id}`;dots.append(dot);
      }
      dots.addEventListener('pointermove',event=>showTip(event,rowTip(row,spec,['year','value','unit','denominator'])));dots.addEventListener('pointerleave',hideTip);box.append(dots);grid.append(box);
      if(!reduced.matches&&!printMode)motionObserver.observe(dots);
    });
  }
  function drawBenchmarkHistory(host,spec,opt){
    const grid=document.createElement('div');grid.className='two-panels';host.append(grid);
    for(const series of ['animal','total']){
      const panel=document.createElement('div');panel.innerHTML=`<p class="fig-sub">${series==='animal'?'Animal-source':'Total'} protein supply</p>`;grid.append(panel);
      drawLine(panel,{...spec,rows:spec.rows.filter(row=>row.series===series)},{...opt,series:'country'});
    }
  }
  function drawCoverage(host,spec){
    const list=document.createElement('div');list.className='coverage-list';host.append(list);
    spec.rows.forEach(row=>{
      const item=document.createElement('div');item.className='timeline-item';item.innerHTML=`<div class="timeline-date" style="color:${color(row.country)}">${safe(row.country)}<br>${safe(human(row.series))}</div><div><h4>${safe(row.covered)} / ${safe(row.n_evaluated)} evaluation cells</h4><p>Inside the nominal ${safe(row.nominal_level)}% interval · ${safe(row.split)}</p></div>`;item.addEventListener('pointermove',event=>showTip(event,rowTip(row,spec,['series','covered','n_evaluated','nominal_level','split'])));item.addEventListener('pointerleave',hideTip);list.append(item);
    });
  }
  function drawCompanies(host,spec){
    const events=document.createElement('div');events.className='company-events';host.append(events);
    const rows=spec.rows.slice().sort((a,b)=>(a.status_evidence_date||'9999').localeCompare(b.status_evidence_date||'9999'));
    rows.forEach(row=>{
      const item=document.createElement('article');item.className='timeline-item';
      const date=row.status_evidence_date||'Undated evidence';
      item.innerHTML=`<div class="timeline-date">${safe(date)}<br><span style="color:${color(row.country)}">${safe(row.country)}</span></div><div><h4>${safe(row.company)}</h4><span class="event-badge">${safe(human(row.status))}</span><p>${safe(row.category)}</p><small>${safe(human(row.inclusion_status))}</small>${row.closure_reported_date?`<small>Closure reported ${safe(row.closure_reported_date)}; event date ${safe(row.closure_effective_date||'unresolved')}.</small>`:''}${row.application_date?`<small>Application filed ${safe(row.application_date)}.</small>`:''}<small>Source: ${safe(row.source_id)} · ${safe(row.tier)}</small></div>`;
      item.addEventListener('pointermove',event=>showTip(event,rowTip(row,spec,['status_evidence_date','status','closure_reported_date','closure_effective_date','application_date'])));item.addEventListener('pointerleave',hideTip);events.append(item);
    });
  }
  function drawPolicy(host,spec){
    const events=document.createElement('div');events.className='policy-events';host.append(events);
    spec.rows.forEach(row=>{
      const item=document.createElement('article');item.className='timeline-item';
      item.innerHTML=`<div class="timeline-date">${safe(row.policy_date||'Date unresolved')}<br><span style="color:${color(row.country)}">${safe(row.country)}</span></div><div><h4>${safe(row.policy)}</h4><span class="event-badge">${safe(human(row.status))}</span><p>${safe(row.pathway)}</p>${row.publication_date?`<small>Published ${safe(row.publication_date)}.</small>`:''}${row.application_date?`<small>Filed ${safe(row.application_date)}.</small>`:''}${row.effective_date?`<small>Effective ${safe(row.effective_date)}.</small>`:''}<small>${safe(human(row.freshness))} · ${safe(row.source_id)}</small></div>`;
      item.addEventListener('pointermove',event=>showTip(event,rowTip(row,spec,['policy_date','publication_date','application_date','effective_date','status'])));item.addEventListener('pointerleave',hideTip);events.append(item);
    });
  }
  function drawOutcomes(host,spec,opt){
    const list=document.createElement('div');list.className='study-list outcome-list';host.append(list);
    for(const source of [...new Set(spec.rows.map(row=>row.source_id))]){
      const rows=spec.rows.filter(row=>row.source_id===source),first=rows[0],card=document.createElement('article');card.className='study-card';
      card.innerHTML=`<span class="status">Original outcome verified · ${safe(source)}</span><h4>${safe(opt.sourceLabels[source])}</h4><dl><div><dt>Question or reported outcome wording</dt><dd>${safe(first.question_wording)}</dd></div><div><dt>Fieldwork</dt><dd>${safe(first.fieldwork)}</dd></div><div><dt>Recruitment</dt><dd>${safe(first.recruitment)}</dd></div></dl><div class="outcome-rows">${rows.map(row=>`<div class="outcome-row"><div><b>${safe(row.geography)} · ${safe(row.protein)}</b><p>${safe(row.measure)}</p><p>Reported subgroup sample: ${opt.claims[row.record_id].sample}.</p></div><div class="outcome-value">${opt.claims[row.record_id].value}%</div></div>`).join('')}</div><p><b>Denominator:</b> ${safe(first.denominator)}</p><p><b>Limits:</b> ${safe(first.limitation)}</p><p class="scope-note">Exact source locators and row-specific notes are retained in Show data.</p>`;list.append(card);
    }
  }
  function drawStudies(host,spec,opt){
    const list=document.createElement('div');list.className='study-list';
    list.innerHTML=spec.rows.map(row=>`<article class="study-card"><span class="status">${safe(row.study_id)} · ${safe(row.country)}</span><h4>${safe(row.title)}</h4><dl><div><dt>Reported sample</dt><dd>${opt.claims[row.study_id]||'Unresolved'} respondents. ${safe(row.sample_size_basis)}</dd></div><div><dt>Fieldwork</dt><dd>${safe(row.fieldwork||'Unverified')}</dd></div><div><dt>Recruitment</dt><dd>${safe(row.method||'Unverified')}</dd></div><div><dt>Original-source check</dt><dd>${safe(human(row.original_verification_status||'extraction_only'))}. ${safe(row.original_verification_limit||'')}</dd></div></dl></article>`).join('');host.append(list);
  }
  function drawLeads(host,spec,opt){
    const list=document.createElement('div');list.className='lead-summary';
    const requests=spec.rows.filter(row=>row.priority_request==='true');
    const additional=spec.rows.filter(row=>row.additional_inspection_lead==='true');
    const requestGuidance={
      'PK-D01':['Which factors relate to willingness to try, buy or pay more for mycoprotein in Pakistan?','Request the Pakistan respondent subset, the analysed items, codebook and sharing terms. Resolve the paper’s inconsistent pooled sample totals before calculating outcomes.'],
      'IN-D01':['How do the recorded Indian respondents describe cultivated-meat acceptance?','Inspect the deposited workbook, codebook, missing cases and permission terms. A repository listing does not establish a usable analysis sample.'],
      'IN-D03':['How do Indian responses to plant-based and cultivated meat vary within this survey?','Obtain the OSF respondent files and questionnaire, identify the India subgroup and confirm reuse terms and complete outcome cases.'],
      'IN-D02':['What does this separate Indian cultivated-meat deposit actually measure?','Inspect the public deposit, provenance, instrument and permission terms before treating any row as usable respondent evidence.']
    };
    const requestCard=row=>{const [question,requirement]=requestGuidance[row.route_id]||['What can this source establish?','Read the instrument and verify access and reuse terms.'];return `<article class="study-card"><span class="status">${safe(row.route_id)} · ${safe(row.country)}</span><h4>${safe(question)}</h4><p class="source-name">${safe(row.title)}</p><p><b>Next acquisition step:</b> ${safe(requirement)}</p><p>Published candidate sample: ${opt.claims[row.route_id]||'unresolved'} · ${safe(human(row.sample_n_scope))}. Acquired usable sample: ${safe(row.acquired_sample_n||'unknown')}.</p><p>${safe(row.sample_n_interpretation||'The published candidate count is not the number of complete outcome records available for analysis.')}</p></article>`;};
    const groups=[
      ['How do people describe unfamiliar proteins?','Pakistan attitude papers and the Right to Protein perception study; Indian awareness and preference studies.','Obtain the original questions, recruitment description and response denominators. Establish whether respondent files exist and whether country-specific estimates can be reproduced.'],
      ['Does experience with a product differ from stated interest?','GFI/Kantar trial and penetration work, plant-based dairy and early-adopter reports, and Meat Your Match.','Acquire the original instrument and definitions of awareness, trial, repeat use and comparison product. Confirm the target population and access to data before estimating demand.'],
      ['How do cost and existing diets constrain choices?','India household-consumption and family-health surveys; Pakistan household surveys, price statistics and food-system sources.','Inspect compatible food categories, weights, periods and geographic coverage. These sources describe diet or expenditure context; alternative-protein adoption requires its own consumer measure.'],
      ['Which sensory or cultural questions deserve follow-up?','The meat-analogue sensory comparison, locust-acceptance studies, halal discussion and literature reviews.','Resolve study geography and product identity. Obtain the full methods and outcome wording; retain qualitative evidence in its original setting.'],
      ['What products and institutions can a local study investigate?','NUST CultMeat, company interviews, product listings, industry analysis and the BioE3 policy record.','Verify the named product or institutional activity and its current scope. Sales, repeat purchasing and respondent evidence require separate records.']
    ];
    list.innerHTML='<h4>Planned data requests</h4><div class="study-list">'+requests.map(requestCard).join('')+'</div><h4>Additional inspection lead</h4><div class="study-list">'+additional.map(requestCard).join('')+'</div><h4>Questions for the wider source register</h4><p class="fig-sub">Exact route identities and access statuses remain in Show data. The next steps below describe the evidence needed for analysis.</p><div class="study-list">'+groups.map(([question,names,requirement])=>`<article class="study-card"><h4>${safe(question)}</h4><p class="source-name">${safe(names)}</p><p><b>Acquisition requirement:</b> ${safe(requirement)}</p></article>`).join('')+'</div>';host.append(list);
  }
  function drawCulture(host,spec){
    const grid=document.createElement('div');grid.className='culture-matrix';host.append(grid);
    for(const country of ['India','Pakistan']){
      const column=document.createElement('div');column.className='culture-country';column.innerHTML=`<h4 style="color:${color(country)}">${country}</h4>`;
      spec.rows.filter(row=>row.country===country).forEach(row=>{
        const card=document.createElement('article');card.className='culture-entry';card.innerHTML=`<h5>${safe(human(row.dimension))}</h5><p>${safe(row.finding)}</p><p class="scope-note">${safe(row.evidence_scope||row.denominator)}</p><p class="scope-note">${safe(row.region)} · ${safe(row.date)} · ${safe(row.source_id)} · source tier ${safe(row.tier)}</p>`;column.append(card);
      });grid.append(column);
    }
  }
  function drawReviews(host,spec){
    const grid=document.createElement('div');grid.className='review-grid';host.append(grid);
    spec.rows.forEach(row=>{const card=document.createElement('article');card.className='review-card';card.innerHTML=`<span class="status">${safe(row.review_id)} · ${safe(row.status)}</span><h4>${safe(row.finding)}</h4><p>${safe(row.resolution)}</p>${row.limitation?`<p>${safe(row.limitation)}</p>`:''}`;grid.append(card);});
  }
  const renderers={line:drawLine,paired:drawPaired,bars:drawBars,map:drawMap,stack:drawStack,reference:drawReference,range:drawRange,dots:drawDots,forecast:drawLine,'benchmark-history':drawBenchmarkHistory,coverage:drawCoverage,companies:drawCompanies,policy:drawPolicy,studies:drawStudies,outcomes:drawOutcomes,leads:drawLeads,culture:drawCulture,reviews:drawReviews};
  function renderChart(host){
    const key=host.closest('[data-chart-container]').dataset.chartContainer,spec=specs[key],opt=JSON.parse(host.dataset.options||'{}');
    d3.select(host).selectAll('*').interrupt();host.replaceChildren();
    const renderer=renderers[host.dataset.render];if(!renderer)throw new Error('Unknown renderer '+host.dataset.render);renderer(host,spec,opt);
  }
  function drawTheory(){
    const host=document.getElementById('theory-diagram');host.replaceChildren();
    const narrow=host.clientWidth<560,{svg,width}=frame(host,narrow?660:350);
    const names=['Religious norms','Caste and class','Affordability','Cities and diaspora','Policy and certification'];
    if(narrow){
      names.forEach((name,i)=>{const y=i*62;svg.append('rect').attr('class','concept-node').attr('x',10).attr('y',y).attr('width',width-20).attr('height',46).attr('rx',3);svg.append('text').attr('x',width/2).attr('y',y+29).attr('text-anchor','middle').text(name);});
      svg.append('path').attr('class','concept-link').attr('d',`M${width/2},298 L${width/2},330`);
      svg.append('ellipse').attr('class','hub').attr('cx',width/2).attr('cy',378).attr('rx',105).attr('ry',48);
      svg.append('text').attr('class','hub-text').attr('x',width/2).attr('y',386).attr('text-anchor','middle').text('acceptability');
      ['Trial','Purchase','Habit'].forEach((name,i)=>{const y=461+i*68;svg.append('path').attr('class','concept-link').attr('d',`M${width/2},${y-34} L${width/2},${y-14}`);svg.append('text').attr('x',width/2).attr('y',y+8).attr('text-anchor','middle').text(name);});
    }else{
      const hubX=width*.56,hubY=170,leftWidth=width*.29;
      names.forEach((name,i)=>{const y=15+i*65;svg.append('rect').attr('class','concept-node').attr('x',0).attr('y',y).attr('width',leftWidth).attr('height',44).attr('rx',3);svg.append('text').attr('x',14).attr('y',y+28).text(name);const link=svg.append('path').attr('class','concept-link').attr('d',`M${leftWidth},${y+22} C${width*.4},${y+22} ${width*.4},${hubY} ${hubX-76},${hubY}`);animatePath(link);});
      svg.append('circle').attr('class','hub').attr('cx',hubX).attr('cy',hubY).attr('r',76);svg.append('text').attr('class','hub-text').attr('x',hubX).attr('y',hubY+7).attr('text-anchor','middle').text('acceptability');
      let previousRight=hubX+76;
      ['Trial','Purchase','Habit'].forEach((name,i)=>{const x=width*.74+i*width*.105,label=svg.append('text').attr('x',x).attr('y',hubY+6).attr('text-anchor','middle').text(name),bounds=label.node().getBBox(),start=previousRight+8,end=bounds.x-8;if(end>start)svg.append('path').attr('class','concept-link').attr('d',`M${start},${hubY} L${end},${hubY}`);previousRight=bounds.x+bounds.width;});
    }
  }
  function renderAll(){hideTip();motionObserver.disconnect();document.querySelectorAll('[data-render]').forEach(renderChart);drawTheory();if(!reduced.matches&&!printMode)document.querySelectorAll('.ch-head:not(.motion-visible)').forEach(element=>motionObserver.observe(element));}
  function theme(){return document.documentElement.dataset.theme||(systemTheme.matches?'dark':'light');}
  function updateThemeButton(){document.getElementById('theme-toggle').setAttribute('aria-pressed',String(theme()==='dark'));}
  document.getElementById('theme-toggle').addEventListener('click',()=>{const next=theme()==='dark'?'light':'dark';document.documentElement.dataset.theme=next;try{localStorage.setItem('sf-theme',next);}catch(error){}updateThemeButton();renderAll();});
  systemTheme.addEventListener('change',()=>{if(!document.documentElement.dataset.theme){updateThemeButton();renderAll();}});
  document.querySelectorAll('select').forEach(control=>control.addEventListener('change',()=>{document.querySelectorAll('[data-render]').forEach(host=>{if(Object.values(JSON.parse(host.dataset.options||'{}')).includes(control.id))renderChart(host);});}));
  document.getElementById('source-search').addEventListener('input',event=>{
    const query=event.target.value.trim().toLowerCase();let found=false;
    document.querySelectorAll('#source-ledger tbody tr[data-source-id]').forEach(row=>{row.hidden=!row.textContent.toLowerCase().includes(query);found ||= !row.hidden;document.querySelectorAll('#source-ledger [data-source-note-for]').forEach(note=>{if(note.dataset.sourceNoteFor===row.dataset.sourceId)note.hidden=row.hidden;});});
    document.getElementById('source-search-status').textContent=query?(found?'Matching source records are shown.':'No source records match this search.'):'The ledger contains the sources cited in this edition.';
  });
  const observer=new IntersectionObserver(entries=>entries.forEach(entry=>{if(entry.isIntersecting)document.getElementById('chapter-current').textContent=entry.target.dataset.title;}),{rootMargin:'-15% 0px -65% 0px'});
  document.querySelectorAll('[data-chapter]').forEach(section=>observer.observe(section));
  const scrolly=new IntersectionObserver(entries=>entries.forEach(entry=>entry.target.classList.toggle('is-current',entry.isIntersecting)),{rootMargin:'-20% 0px -30% 0px'});
  document.querySelectorAll('[data-scrolly-step]').forEach(step=>scrolly.observe(step));
  addEventListener('scroll',()=>{const denominator=document.documentElement.scrollHeight-innerHeight;document.getElementById('reading-progress').style.width=(denominator?Math.min(100,Math.max(0,scrollY/denominator*100)):0)+'%';},{passive:true});
  addEventListener('resize',()=>{clearTimeout(redrawTimer);redrawTimer=setTimeout(renderAll,160);});
  addEventListener('keydown',event=>{if(event.key==='Escape')hideTip();});
  reduced.addEventListener('change',()=>{d3.select(document.body).selectAll('*').interrupt();pendingAnimations=0;renderAll();});
  addEventListener('beforeprint',()=>{printMode=true;d3.select(document.body).selectAll('*').interrupt();pendingAnimations=0;renderAll();});
  addEventListener('afterprint',()=>{printMode=false;renderAll();});
  updateThemeButton();renderAll();
  document.documentElement.dataset.editionReady='true';
  window.editionChecks={specs,renderAll,activeAnimations:()=>pendingAnimations+document.getAnimations().filter(animation=>animation.playState==='running').length,theme,sourceSearch:()=>document.getElementById('source-search').value,disputed:[...disputed]};
})();
