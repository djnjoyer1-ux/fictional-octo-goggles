'use strict';
const api = typeof browser !== 'undefined' ? browser : chrome;
const ids = ['enabled','blur','threshold','maskScale'];
const defaults = { enabled:true, blur:18, threshold:0.45, maskScale:1.35 };
async function broadcast(settings){
  const tabs = await api.tabs.query({active:true,currentWindow:true});
  if(tabs[0]?.id) api.tabs.sendMessage(tabs[0].id,{type:'FACEBLUR_SETTINGS',settings}).catch(()=>{});
}
async function init(){
  const settings = await api.storage.local.get(defaults);
  for(const id of ids) document.getElementById(id)[id==='enabled'?'checked':'value']=settings[id];
  updateOutputs();
}
function updateOutputs(){
  blurOut.value=`${blur.value}px`; thresholdOut.value=Number(threshold.value).toFixed(2); maskOut.value=`${Number(maskScale.value).toFixed(2)}×`;
}
for(const id of ids) document.addEventListener('change',async e=>{
  if(e.target.id!==id)return;
  const value=id==='enabled'?e.target.checked:Number(e.target.value);
  await api.storage.local.set({[id]:value}); updateOutputs(); broadcast({[id]:value});
});
document.addEventListener('input',updateOutputs);
rescan.addEventListener('click',async()=>{const [tab]=await api.tabs.query({active:true,currentWindow:true});if(tab?.id)api.tabs.sendMessage(tab.id,{type:'FACEBLUR_RESCAN'}).catch(()=>{});});
init();
