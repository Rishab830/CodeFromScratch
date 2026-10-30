const assert=require('node:assert/strict');
async function checkContrast(page){
  await page.waitForTimeout(180); // Let existing button color transitions finish.
  const failures=await page.evaluate(()=>{
    const canvas=document.createElement('canvas');canvas.width=canvas.height=1;const ctx=canvas.getContext('2d',{willReadFrequently:true});
    const rgb=value=>{ctx.clearRect(0,0,1,1);ctx.fillStyle=value;ctx.fillRect(0,0,1,1);const color=[...ctx.getImageData(0,0,1,1).data];color[3]/=255;return color};
    const mix=(top,bottom)=>[0,1,2].map(i=>top[i]*top[3]+bottom[i]*(1-top[3])).concat(1);
    function background(node){if(!node)return [255,255,255,1];const color=rgb(getComputedStyle(node).backgroundColor);return color[3]===1?color:mix(color,background(node.parentElement))}
    const lum=color=>color.slice(0,3).map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4}).reduce((n,v,i)=>n+v*[.2126,.7152,.0722][i],0);
    const bad=[];
    for(const node of document.querySelectorAll('body *')){
      if(node.closest('iframe,svg,.cm-editor,button:disabled:not(.journey-stop)'))continue;
      if(![...node.childNodes].some(n=>n.nodeType===Node.TEXT_NODE&&n.textContent.trim()))continue;
      const s=getComputedStyle(node);if(s.visibility==='hidden'||s.display==='none'||!node.getClientRects().length)continue;
      const bg=background(node),color=mix(rgb(s.color),bg),a=lum(color),b=lum(bg),ratio=(Math.max(a,b)+.05)/(Math.min(a,b)+.05);
      const large=parseFloat(s.fontSize)>=24||(parseFloat(s.fontSize)>=18.66&&parseFloat(s.fontWeight)>=700);
      if(ratio<(large?3:4.5)-.01)bad.push({text:node.textContent.trim().slice(0,65),class:node.className,ratio:ratio.toFixed(2),color:s.color,bg});
    }
    return bad;
  });
  assert.deepEqual(failures,[],'Low text contrast in '+await page.locator('html').getAttribute('data-theme')+' at '+page.url()+': '+JSON.stringify(failures));
}

module.exports={checkContrast};
