// In-memory JavaScript rendering checks, not a browser or visual test.
const fs=require('fs'), vm=require('vm'), path=require('path'), assert=require('assert');
const directory=process.argv[2];
const html=fs.readFileSync(path.join(directory,'read.html'),'utf8');
const data=JSON.parse(html.match(/<script id="paper-data" type="application\/json">([\s\S]*?)<\/script>/)[1]);
const script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
const elements=new Map(), handlers={};
function element(id){
  if(!elements.has(id))elements.set(id,{innerHTML:'',textContent:id==='#paper-data'?JSON.stringify(data):'',value:'',style:{},clientWidth:1100,dataset:{},classList:{toggle(){}},setAttribute(){},addEventListener(name,fn){this[name]=fn;},insertAdjacentHTML(where,text){this.innerHTML+=text;},scrollIntoView(){},focus(){},showModal(){this.open=true;},close(){this.open=false;}});
  return elements.get(id);
}
const context={document:{getElementById:id=>element('#'+id),querySelector:element,querySelectorAll:()=>[],addEventListener:(name,fn)=>handlers[name]=fn},location:{hash:''},history:{replaceState(){}},URLSearchParams,innerWidth:1400};
vm.createContext(context);vm.runInContext(script,context);
const scientific=JSON.stringify(data.evidence);
assert(!/[\u3400-\u9fff]/.test(element('#sources').innerHTML),'Untranslated source labels');
for(const mode of ['B','A1','A2']){
  handlers.click({target:{closest:()=>({dataset:{mode}})}});
  for(const depth of [1,2,3]){
    element('#depth').change({target:{value:String(depth)}});
    const rendered=element('#main').innerHTML;
    assert(!rendered.includes('undefined'));
    assert(!/[\u3400-\u9fff]/.test(rendered.replaceAll('保留原文','')),'Untranslated visible UI in '+mode);
    assert(rendered.includes(mode==='B'?'Research overview':'Interpretation limits') || (mode==='A2' && depth===1));
  }
}
handlers.click({target:{closest:()=>({dataset:{proof:'e4'}})}});
assert(element('#main').innerHTML.includes('Test evidence 5'));
handlers.click({target:{closest:()=>({dataset:{mode:'A1'}})}});
assert(element('#main').innerHTML.includes('Test evidence 5'));
handlers.click({target:{closest:()=>({dataset:{zoom:'a4'}})}});
assert(element('#zoom').open);
assert(element('#zoomimg').src==='assets/test-5.svg');
assert.strictEqual(JSON.stringify(data.evidence),scientific);
handlers.click({target:{closest:()=>({dataset:{proof:'e6'}})}});
assert(element('#main').innerHTML.includes('Caption unavailable: Synthetic missing-caption test.'));
const staticHTML=html.slice(0,html.indexOf('<script id="paper-data"'));
assert(!/[\u3400-\u9fff]/.test(staticHTML),'Untranslated static HTML');
console.log(JSON.stringify({status:'passed',modes:3,depths:3,selection_preserved:true,zoom_reference:true,visible_english_labels:true,browser_test:false}));
