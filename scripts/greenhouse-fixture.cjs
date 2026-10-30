const assert=require('node:assert/strict');
const GREENHOUSE_SOLUTION='    for plant in range(3):\n        for stage in range(3):\n            water_plant(plant)\n';
async function greenhousePixels(page){
  const frame=page.frames().find(f=>/^\/runner-13\/?$/.test(new URL(f.url()).pathname));
  return frame.evaluate(()=>{
    const c=document.querySelector('#canvas'),ctx=c.getContext('2d'),d=ctx.getImageData(0,0,c.width,c.height).data,s=c.width/320;
    const sample=(x,y)=>{const i=(Math.floor((y+.5)*s)*c.width+Math.floor((x+.5)*s))*4;return [d[i],d[i+1],d[i+2]]};
    let sum=0,n=0,water=0;const plants=[0,0,0];
    for(let y=78;y<161;y++)for(let x=0;x<320;x++){
      const p=sample(x,y);
      if(p[0]===237&&p[1]===160&&p[2]===185){sum+=x;n++}
      if(p[0]===112&&p[1]===178&&p[2]===213)water++;
      if(p[0]===121&&p[1]===176&&p[2]===120||p[0]===152&&p[1]===198&&p[2]===135){const index=[110,174,238].findIndex(cx=>Math.abs(cx-x)<15);if(index>=0)plants[index]++}
    }
    return {girl:sum/n,plants,water};
  });
}
async function moveGreenhouseGirl(page,target){
  let held=null;
  try{
    for(let i=0;i<300;i++){
      const {girl}=await greenhousePixels(page);
      assert(Number.isFinite(girl),'Girl must be visible');
      if(Math.abs(target-girl)<2.6)return;
      const next=target>girl?'ArrowRight':'ArrowLeft';
      if(next!==held){if(held)await page.keyboard.up(held);held=next;await page.keyboard.down(held)}
      await page.waitForTimeout(25);
    }
    throw Error('Could not walk to '+target);
  }finally{if(held)await page.keyboard.up(held)}
}
async function runGreenhouse(page,onAnimation){
  await moveGreenhouseGirl(page,49);
  await page.keyboard.press('Space');
  const deadline=Date.now()+25000;
  while(Date.now()<deadline){
    assert.equal(await page.getByRole('dialog',{name:'Game over',exact:true}).count(),0,await page.locator('.console-message').innerText());
    if((await page.locator('.console-message').innerText()).includes('All three plants are fully grown'))return;
    if(onAnimation)await onAnimation(await greenhousePixels(page));
    await page.waitForTimeout(50);
  }
  throw Error('Watering machine did not finish');
}
async function exitGreenhouse(page){
  await moveGreenhouseGirl(page,247);
  await page.waitForFunction(()=>document.querySelector('.console-message').textContent.includes('Key collected!'));
  await moveGreenhouseGirl(page,293);
  await page.keyboard.press('Space');
  await page.waitForFunction(()=>document.querySelector('.console-message').textContent.includes('Door open!'));
  await moveGreenhouseGirl(page,304);
  await page.getByRole('dialog',{name:'Level complete',exact:true}).waitFor();
}
module.exports={GREENHOUSE_SOLUTION,greenhousePixels,moveGreenhouseGirl,runGreenhouse,exitGreenhouse};
