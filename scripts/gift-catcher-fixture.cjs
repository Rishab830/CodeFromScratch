const assert=require('node:assert/strict');
const GIFT_SOLUTION='    if gift_in_basket():\n        open_gift()\n        if gift_is_bomb():\n            drop()\n        else:\n            collect()\n';
async function giftPositions(page){
  const frame=page.frames().find(f=>/\/runner-6\/?$/.test(new URL(f.url()).pathname));
  return frame.evaluate(()=>{
    const c=document.querySelector('#canvas'),d=c.getContext('2d').getImageData(0,0,c.width,c.height).data,s=c.width/320;
    let bx=0,bn=0,gx=0,gy=0,gn=0;
    for(let i=0;i<d.length;i+=4){
      if(d[i]===237&&d[i+1]===160&&d[i+2]===185){bx+=(i/4)%c.width;bn++}
      if(d[i]===238&&d[i+1]===174&&d[i+2]===199){gx+=(i/4)%c.width;gy+=Math.floor(i/4/c.width);gn++}
    }
    return {basket:bx/bn/s,gift:gn?{x:gx/gn/s,y:gy/gn/s}:null};
  });
}
async function playGifts(page,expected='won'){
  let held=null,handled=false;
  const deadline=Date.now()+120000;
  try{
    while(Date.now()<deadline){
      if(await page.getByRole('dialog',{name:'Game over',exact:true}).count()){
        assert.equal(expected,'dead',await page.locator('.console-message').innerText());return;
      }
      if(await page.getByRole('dialog',{name:'Level complete',exact:true}).count()){
        assert.equal(expected,'won');return;
      }
      if(await page.locator('.status-pill').innerText()==='CODE ERROR'){
        assert.equal(expected,'error',await page.locator('.console-message').innerText());return;
      }
      const p=await giftPositions(page);
      let next=null;
      if(p.gift&&p.gift.y<122){
        handled=false;
        if(p.gift.x-p.basket>5)next='ArrowRight';
        if(p.gift.x-p.basket < -5)next='ArrowLeft';
      }
      if(next!==held){if(held)await page.keyboard.up(held);held=next;if(held)await page.keyboard.down(held)}
      if(/Gift in the basket!/.test(await page.locator('.console-message').innerText())&&!handled){
        await page.keyboard.down('Space');await page.waitForTimeout(70);await page.keyboard.up('Space');handled=true;
      }
      await page.waitForTimeout(70);
    }
    throw Error('Gift Catcher timed out: '+await page.locator('.console-message').innerText());
  } finally {if(held)await page.keyboard.up(held)}
}
module.exports={GIFT_SOLUTION,giftPositions,playGifts};
