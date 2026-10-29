const assert=require('node:assert/strict');
async function shipPosition(page){
  const frame=page.frames().find(f=>/\/runner-10\/?$/.test(new URL(f.url()).pathname));
  return frame.evaluate(()=>{
    const c=document.querySelector('#canvas'),d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;
    let x=0,y=0,n=0;
    for(let i=0;i<d.length;i+=4)if(d[i]===153&&d[i+1]===215&&d[i+2]===229){x+=(i/4)%c.width;y+=Math.floor(i/4/c.width);n++}
    return n?{x:x/n/(c.width/320),y:y/n/(c.height/180)}:null;
  });
}
async function pilotSector(page,expected='clear'){
  await page.keyboard.press('Space');
  let held='ArrowRight';await page.keyboard.down(held);
  try{
    const deadline=Date.now()+90000;
    while(Date.now()<deadline){
      if(await page.getByRole('dialog',{name:'Game over',exact:true}).count()){
        assert.equal(expected,'dead',await page.locator('.console-message').innerText());return;
      }
      if(/Sector clear!/.test(await page.locator('.console-message').innerText())){
        assert.equal(expected,'clear');return;
      }
      const position=await shipPosition(page);
      const next=position?.x>275?'ArrowLeft':position?.x<45?'ArrowRight':held;
      if(next!==held){await page.keyboard.up(held);held=next;await page.keyboard.down(held)}
      await page.waitForTimeout(160);
    }
    throw Error('Space Patrol did not finish: '+await page.locator('.console-message').innerText());
  } finally {await page.keyboard.up(held)}
}
async function flyToBeacon(page){
  let position;
  for(let i=0;i<20&&!position;i++){position=await shipPosition(page);if(!position)await page.waitForTimeout(80)}
  assert(position,'Ship is missing');
  const key=position.x>160?'ArrowLeft':'ArrowRight';
  await page.keyboard.down(key);await page.waitForTimeout(Math.abs(position.x-160)/88*1000);await page.keyboard.up(key);
  await page.keyboard.down('ArrowUp');await page.waitForTimeout(1600);await page.keyboard.up('ArrowUp');
  await page.getByRole('dialog',{name:'Level complete',exact:true}).waitFor({timeout:5000});
}
module.exports={shipPosition,pilotSector,flyToBeacon};
