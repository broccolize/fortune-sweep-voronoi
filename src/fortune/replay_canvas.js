/* Presentation geometry only. Python supplies every arc order and event state. */
(function (root) {
  "use strict";
  function parabolaY(p, x, d) {
    return (x-p[0])*(x-p[0])/(2*(p[1]-d))+(p[1]+d)/2;
  }
  function breakpointX(left, right, d) {
    if (left[1]===right[1]) return left[0]+(right[0]-left[0])/2;
    const dp=left[1]-d,dq=right[1]-d;
    if (dp<=0) return left[0];
    if (dq<=0) return right[0];
    const dx=right[0]-left[0],a=right[1]-left[1],b=2*dp*dx;
    const c=-dp*dx*dx-a*dp*dq;
    let discriminant=b*b-4*a*c;
    if (discriminant<0) {
      if (discriminant < -2e-14*(b*b+Math.abs(4*a*c))) throw new Error("Breakpoint precision limit");
      discriminant=0;
    }
    const q=-0.5*(b+((b<0||Object.is(b,-0))?-1:1)*Math.sqrt(discriminant));
    const r1=q?q/a:-b/(2*a),r2=q?c/q:r1;
    return left[0]+(left[1]>right[1]?Math.min(r1,r2):Math.max(r1,r2));
  }
  function stateAt(states, y) {
    let lo=0,hi=states.length;
    while (lo+1<hi) {
      const mid=(lo+hi)>>1;
      if (states[mid].y>=y) lo=mid; else hi=mid;
    }
    return lo;
  }
  if (typeof module!=="undefined" && module.exports) module.exports={parabolaY,breakpointX,stateAt};
  if (typeof document==="undefined") return;

  const D=root.FORTUNE_DATA,$=id=>document.getElementById(id);
  const canvas=$("view"),ctx=canvas.getContext("2d",{alpha:false});
  const range=$("position"),status=$("status"),queue=$("queue");
  const siteColor="#ff4962",beachColor="#f4f6fb",edgeColor="#b17cf1",circleColor="#55b4ff";
  let width=800,height=600,scale=1,xoff=0,yoff=0,dpr=1;
  let progress=0,directrix=D.view[3],index=0,manual=null,complete=!!D.special_case;
  let follow=!D.special_case,playing=false,pointerInside=false,pending=false,dirty=true,lastTime=0,lastDraw=0;
  let panelIndex=-1,frames=0,fps=0,showFPS=true,statsAt=0;
  const renderTimes=[],intervals=[];
  $("labels").checked=D.labels;
  function sx(x){return xoff+(x-D.view[0])*scale;}
  function sy(y){return height-yoff-(y-D.view[1])*scale;}
  function worldY(y){return D.world[1]+D.world[2]*y;}
  function resize() {
    const rect=canvas.getBoundingClientRect();
    width=rect.width;height=rect.height;dpr=root.devicePixelRatio||1;
    canvas.width=Math.round(width*dpr);canvas.height=Math.round(height*dpr);
    ctx.setTransform(dpr,0,0,dpr,0,0);
    scale=Math.min(width/(D.view[2]-D.view[0]),height/(D.view[3]-D.view[1]));
    xoff=(width-(D.view[2]-D.view[0])*scale)/2;
    yoff=(height-(D.view[3]-D.view[1])*scale)/2;
    dirty=true;schedule();
  }
  function segment(a,b,color,lineWidth=1.4) {
    if (!a||!b||!a.every(Number.isFinite)||!b.every(Number.isFinite)) return;
    let t0=0,t1=1;
    const dx=b[0]-a[0],dy=b[1]-a[1];
    for (const [p,q] of [[-dx,a[0]-D.view[0]],[dx,D.view[2]-a[0]],[-dy,a[1]-D.view[1]],[dy,D.view[3]-a[1]]]) {
      if (p===0) {if(q<0)return;continue;}
      const r=q/p;
      if(p<0)t0=Math.max(t0,r);else t1=Math.min(t1,r);
      if(t0>t1)return;
    }
    ctx.strokeStyle=color;ctx.lineWidth=lineWidth;
    ctx.beginPath();ctx.moveTo(sx(a[0]+t0*dx),sy(a[1]+t0*dy));ctx.lineTo(sx(a[0]+t1*dx),sy(a[1]+t1*dy));ctx.stroke();
  }
  function drawArc(focus,left,right,d) {
    const gap=focus[1]-d;
    if(gap<=0)return;
    const vertexY=(focus[1]+d)/2;
    if(vertexY>D.view[3])return;
    const outer=Math.sqrt(Math.max(0,2*gap*(D.view[3]-vertexY)));
    left=Math.max(left,focus[0]-outer,D.view[0]);right=Math.min(right,focus[0]+outer,D.view[2]);
    if(left>=right)return;
    const pieces=[];
    if(vertexY<D.view[1]) {
      const inner=Math.sqrt(2*gap*(D.view[1]-vertexY));
      if(left<focus[0]-inner)pieces.push([left,Math.min(right,focus[0]-inner)]);
      if(right>focus[0]+inner)pieces.push([Math.max(left,focus[0]+inner),right]);
    } else pieces.push([left,right]);
    ctx.strokeStyle=beachColor;ctx.lineWidth=1.7;
    for(const [a,b] of pieces) {
      if(a>=b)continue;
      const mid=(a+b)/2,ya=parabolaY(focus,a,d),yb=parabolaY(focus,b,d);
      const control=2*parabolaY(focus,mid,d)-(ya+yb)/2;
      ctx.beginPath();ctx.moveTo(sx(a),sy(ya));ctx.quadraticCurveTo(sx(mid),sy(control),sx(b),sy(yb));ctx.stroke();
    }
  }
  function eventName(e) {
    return e.kind===0?"Site "+D.sites[e.site][2]:"Circle "+e.defining.map(i=>D.sites[i][2]).join("/");
  }
  function updatePanel(state) {
    if(panelIndex===index)return;
    panelIndex=index;
    const fragment=document.createDocumentFragment();
    for(const [id,stale] of state.queue) {
      const e=D.events[id],row=document.createElement("div"),name=document.createElement("span"),value=document.createElement("span");
      row.className="event "+(stale?"stale":e.kind===0?"site":"circle");
      name.textContent=eventName(e)+(stale?" · stale":"");value.textContent=worldY(e.y).toPrecision(4);
      row.append(name,value);fragment.append(row);
    }
    if(!state.queue.length) {const row=document.createElement("p");row.textContent=D.special_case?"Collinear special case: direct bisectors.":"Queue empty.";fragment.append(row);}
    queue.replaceChildren(fragment);
    $("counts").textContent=`${state.counts[0]} site events · ${state.counts[1]} circle events · ${state.counts[2]} stale discarded · ${state.queued} queued`;
    $("order").textContent=state.arcs.map(i=>D.sites[i][2]).join(" | ")||"(empty)";
  }
  function draw() {
    const start=performance.now();
    index=complete?D.states.length-1:manual!==null?manual:stateAt(D.states,directrix);
    const state=D.states[index],done=complete||state.done;
    updatePanel(state);
    ctx.fillStyle="#06080d";ctx.fillRect(0,0,width,height);
    ctx.save();ctx.beginPath();ctx.rect(0,0,width,height);ctx.clip();
    if(done) {
      D.cells.forEach((cell,i)=>{
        if(!cell.length)return;
        ctx.beginPath();cell.forEach((p,j)=>j?ctx.lineTo(sx(p[0]),sy(p[1])):ctx.moveTo(sx(p[0]),sy(p[1])));ctx.closePath();
        ctx.fillStyle=`hsla(${(i*137.508)%360},55%,47%,.14)`;ctx.fill();ctx.strokeStyle=edgeColor;ctx.lineWidth=1.3;ctx.stroke();
      });
    } else {
      if($("markers").checked) for(const [id,invalid] of state.queue) {
        const e=D.events[id],y=sy(e.y);
        if(y<0||y>height)continue;
        ctx.strokeStyle=invalid?"#495565":e.kind===0?"#a62c44":"#23699f";ctx.lineWidth=0.8;
        ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(width,y);ctx.stroke();
      }
      const active=new Map(),breaks=[];
      for(let k=0;k+1<state.arcs.length;k++) {
        const ia=state.arcs[k],ib=state.arcs[k+1],a=D.sites[ia],b=D.sites[ib];
        const x=breakpointX(a,b,directrix),f=a[1]>directrix?a:b;
        if(f[1]<=directrix)continue;
        const p=[x,parabolaY(f,x,directrix)],key=Math.min(ia,ib)+","+Math.max(ia,ib);
        if(p.every(Number.isFinite)){if(!active.has(key))active.set(key,[]);active.get(key).push(p);breaks.push(p);}
      }
      const visibleVertices=new Set();
      for(const edge of D.edges) {
        if(edge.created>index)continue;
        const ends=edge.ends.filter(e=>e[1]<=index).map(e=>{visibleVertices.add(e[0]);return D.vertices[e[0]];});
        const moving=active.get(edge.sites.join(","))||[];
        if(ends.length>=2)segment(ends[0],ends[1],edgeColor);
        else if(ends.length)for(const p of moving)segment(ends[0],p,"#aeb9cc");
        else if(moving.length>=2)segment(moving[0],moving[1],"#aeb9cc");
        else if(moving.length&&D.sites[edge.sites[0]][1]===D.sites[edge.sites[1]][1])segment(moving[0],[moving[0][0],D.view[3]],"#aeb9cc");
      }
      for(let k=0;k<state.arcs.length;k++) {
        const f=D.sites[state.arcs[k]];
        if(f[1]===directrix) {
          let top=D.view[3];
          for(const neighbour of [state.arcs[k-1],state.arcs[k+1]])if(neighbour!==undefined&&D.sites[neighbour][1]>directrix)top=Math.min(top,parabolaY(D.sites[neighbour],f[0],directrix));
          segment([f[0],f[1]],[f[0],top],beachColor);continue;
        }
        const left=k?breakpointX(D.sites[state.arcs[k-1]],f,directrix):D.view[0];
        const right=k+1<state.arcs.length?breakpointX(f,D.sites[state.arcs[k+1]],directrix):D.view[2];
        drawArc(f,left,right,directrix);
      }
      for(const v of visibleVertices){const p=D.vertices[v];ctx.fillStyle=edgeColor;ctx.fillRect(sx(p[0])-2,sy(p[1])-2,4,4);}
      let circle=state.queue.find(([id,invalid])=>!invalid&&D.events[id].kind===1);
      if(manual!==null&&state.last!==null&&!state.discarded&&D.events[state.last].kind===1)circle=[state.last,false];
      if(circle) {
        const e=D.events[circle[0]],radius=e.centre[1]-e.y;
        if(radius>0&&radius*scale<1e7){ctx.strokeStyle=circleColor;ctx.lineWidth=1;ctx.setLineDash([5,5]);ctx.beginPath();ctx.arc(sx(e.centre[0]),sy(e.centre[1]),radius*scale,0,Math.PI*2);ctx.stroke();ctx.setLineDash([]);}
      }
      const y=sy(directrix);ctx.strokeStyle=beachColor;ctx.lineWidth=1.2;ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(width,y);ctx.stroke();
    }
    ctx.strokeStyle="#42516a";ctx.lineWidth=1;ctx.setLineDash([5,5]);ctx.strokeRect(sx(D.box[0]),sy(D.box[3]),(D.box[2]-D.box[0])*scale,(D.box[3]-D.box[1])*scale);ctx.setLineDash([]);
    ctx.font="11px Segoe UI, sans-serif";
    for(const p of D.sites) {
      ctx.fillStyle=siteColor;ctx.fillRect(sx(p[0])-3,sy(p[1])-3,6,6);
      if($("labels").checked){ctx.fillStyle="#dbe4f4";ctx.fillText(String(p[2]).slice(0,32),sx(p[0])+7,sy(p[1])-6);}
    }
    ctx.restore();
    if(showFPS){ctx.fillStyle="#72e39c";ctx.font="12px ui-monospace, monospace";ctx.fillText(fps?`${Math.round(fps)} FPS`:"Pointer-ready",12,20);}
    range.value=Math.round(progress*1000);$("positionValue").value=Math.round(progress*100)+"%";
    status.textContent=D.special_case?"Collinear sites use direct bisectors; no sweep events are needed.":done?"Completed clipped diagram. Move upward to replay.":`Sweep y = ${worldY(directrix).toPrecision(6)} · ${index} heap entries processed`;
    frames++;renderTimes.push(performance.now()-start);if(renderTimes.length>120)renderTimes.shift();
    canvas.dataset.sweepY=String(worldY(directrix));canvas.dataset.stateIndex=String(index);canvas.dataset.frameCount=String(frames);
    if(performance.now()-statsAt>250) {
      statsAt=performance.now();
      const median=[...renderTimes].sort((a,b)=>a-b)[Math.floor(renderTimes.length/2)];
      canvas.dataset.medianRenderMs=String(median);canvas.dataset.rafFps=String(fps);
      $("performance").textContent=(fps?Math.round(fps)+" fps · ":"")+median.toFixed(2)+" ms draw";
    }
  }
  function setProgress(value) {
    progress=Math.max(0,Math.min(1,value));complete=progress>=1||!!D.special_case;manual=null;
    directrix=D.view[3]+progress*(D.view[1]-D.view[3]);dirty=true;
  }
  function syncButtons() {
    $("play").textContent=playing?"Pause":"Play";$("follow").textContent="Follow pointer: "+(follow?"on":"off");
    $("hint").textContent=follow?"Move the pointer · Click to freeze · H for help":"Frozen · Click to follow · H for help";
  }
  function schedule(){if(!pending){pending=true;requestAnimationFrame(tick);}}
  function tick(now) {
    pending=false;
    const dt=lastTime?Math.min(.1,(now-lastTime)/1000):0;lastTime=now;
    if(playing){setProgress(progress+dt*Number($("speed").value)/50);if(complete){playing=false;syncButtons();}}
    if(dirty||pointerInside||playing) {
      if(lastDraw&&now-lastDraw<200){intervals.push(now-lastDraw);if(intervals.length>90)intervals.shift();fps=1000/(intervals.reduce((a,b)=>a+b,0)/intervals.length);}
      lastDraw=now;
      try{draw();}catch(error){playing=false;status.textContent="Replay drawing limit: "+error.message;syncButtons();}
      dirty=false;
    }
    if(playing||pointerInside)schedule();
  }
  function move(event) {
    if(!follow||D.special_case)return;
    playing=false;
    const rect=canvas.getBoundingClientRect(),y=D.view[1]+(height-(event.clientY-rect.top)-yoff)/scale;
    setProgress((D.view[3]-y)/(D.view[3]-D.view[1]));syncButtons();schedule();
  }
  canvas.addEventListener("pointerenter",e=>{pointerInside=true;move(e);schedule();});
  canvas.addEventListener("pointermove",move);
  canvas.addEventListener("pointerleave",()=>{pointerInside=false;});
  canvas.addEventListener("click",()=>{follow=!follow;playing=false;syncButtons();dirty=true;schedule();});
  $("follow").onclick=()=>{follow=!follow;playing=false;syncButtons();dirty=true;schedule();};
  $("play").onclick=()=>{if(complete)setProgress(0);playing=!playing;follow=false;lastTime=0;syncButtons();dirty=true;schedule();};
  range.oninput=()=>{playing=false;follow=false;setProgress(Number(range.value)/1000);syncButtons();schedule();};
  function next(){playing=false;follow=false;manual=Math.min(D.states.length-1,index+1);directrix=D.states[manual].y;progress=Math.max(0,Math.min(1,(D.view[3]-directrix)/(D.view[3]-D.view[1])));complete=manual===D.states.length-1;syncButtons();dirty=true;schedule();}
  $("next").onclick=next;
  $("reset").onclick=()=>{playing=false;follow=!D.special_case;setProgress(0);syncButtons();schedule();};
  $("finish").onclick=()=>{playing=false;follow=false;setProgress(1);syncButtons();schedule();};
  for(const name of ["labels","markers"])$(name).onchange=()=>{dirty=true;schedule();};
  $("save").onclick=()=>canvas.toBlob(blob=>{const link=document.createElement("a");link.download="fortune-replay.png";link.href=URL.createObjectURL(blob);link.click();setTimeout(()=>URL.revokeObjectURL(link.href),1000);});
  root.addEventListener("keydown",e=>{
    if(e.ctrlKey||e.metaKey||e.altKey||["INPUT","BUTTON","TEXTAREA"].includes(document.activeElement.tagName))return;
    const key=e.key.toLowerCase();
    if(key==="h")$("help").classList.toggle("visible");
    else if(key===" "){$("play").click();e.preventDefault();}
    else if(key==="arrowright"){next();e.preventDefault();}
    else if(key==="r")$("reset").click();
    else if(key==="e")$("finish").click();
    else if(key==="f"){showFPS=!showFPS;dirty=true;schedule();}
  });
  new ResizeObserver(resize).observe(canvas);
  root.fortuneReplay=Object.freeze({
    inspect:()=>({index,worldY:worldY(directrix),progress,follow,playing,frames,
      fps,medianRenderMs:renderTimes.length?[...renderTimes].sort((a,b)=>a-b)[Math.floor(renderTimes.length/2)]:0,
      eventCounts:D.states[index].counts,beach:[...D.states[index].arcs]}),
    setPosition:value=>{playing=false;follow=false;setProgress(value);syncButtons();schedule();},
    breakpointX,parabolaY
  });
  syncButtons();resize();
})(typeof window!=="undefined"?window:globalThis);
