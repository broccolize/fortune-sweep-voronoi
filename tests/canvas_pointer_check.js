// Source-level event test: pointer movement must work without a pressed button.
const fs=require('fs');
const input=JSON.parse(fs.readFileSync(0,'utf8'));
let pending=null;
const noop=()=>{};
const context=new Proxy({}, {get:(target,key)=>target[key]||noop});
function element(){return {
  events:{},dataset:{},value:'0',checked:false,children:[],tagName:'DIV',
  classList:{toggle:noop},
  addEventListener(name,fn){this.events[name]=fn;},
  getBoundingClientRect(){return {left:0,top:0,width:800,height:600};},
  getContext(){return context;},
  append(...children){this.children.push(...children);},
  replaceChildren(...children){this.children=children;}
};}
const nodes=new Map();
global.window=global;
global.FORTUNE_DATA=input.payload;
global.devicePixelRatio=1;
global.addEventListener=noop;
global.requestAnimationFrame=fn=>{pending=fn;return 1;};
global.ResizeObserver=class {constructor(fn){this.fn=fn;}observe(){this.fn();}};
global.document={
  getElementById(id){if(!nodes.has(id))nodes.set(id,element());return nodes.get(id);},
  createElement:element,createDocumentFragment:element,activeElement:{tagName:'BODY'}
};
require(input.script);
function pump(time){const fn=pending;pending=null;if(fn)fn(time);}
pump(0);
const view=nodes.get('view');
view.events.pointerenter({clientY:100});pump(16);
const first=global.fortuneReplay.inspect();
view.events.pointermove({clientY:450});pump(32);
const second=global.fortuneReplay.inspect();
process.stdout.write(JSON.stringify({first,second}));
