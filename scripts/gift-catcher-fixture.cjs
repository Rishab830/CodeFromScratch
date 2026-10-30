const assert=require('node:assert/strict');
const GIFT_SOLUTION='    if gift_in_basket():\n        open_gift()\n        if gift_is_bomb():\n            drop()\n        else:\n            collect()\n';
async function giftPositions(page){
  const frame=page.frames().find(f=>/\/runner-6\/?$/.test(new URL(f.url()).pathname));
  return frame.evaluate(()=>{
    const c=document.querySelector('#canvas'),d=c.getContext('2d').getImageData(0,0,c.width,c.height).data,s=c.width/320;
    let bx=0,bn=0;
    for(let i=0;i<d.length;i+=4){
      if(d[i]===237&&d[i+1]===160&&d[i+2]===185){bx+=(i/4)%c.width;bn++}
    }
    const groups=[];
    for(let y=50;y<137;y++)for(let x=0;x<320;x++){
      const i=(Math.floor((y+.5)*s)*c.width+Math.floor((x+.5)*s))*4;
      if(d[i]!==238||d[i+1]!==174||d[i+2]!==199)continue;
      let group=groups.find(g=>Math.abs(g.x/g.n-x)<16&&Math.abs(g.y/g.n-y)<16);
      if(!group){group={x:0,y:0,n:0};groups.push(group)}
      group.x+=x;group.y+=y;group.n++;
    }
    const gifts=groups.filter(g=>g.n>20).map(g=>({x:g.x/g.n,y:g.y/g.n})).filter(g=>g.y<127.5).sort((a,b)=>b.y-a.y);
    return {basket:bx/bn/s,gifts,gift:gifts[0]??null};
  });
}
async function playGifts(page,expected='won',onRain){
  let held=null,maxFalling=0;
  const deadline=Date.now()+120000;
  try{
    while(Date.now()<deadline){
      if(await page.getByRole('dialog',{name:'Game over',exact:true}).count()){
        assert.equal(expected,'dead',await page.locator('.console-message').innerText());return {maxFalling};
      }
      if(await page.getByRole('dialog',{name:'Level complete',exact:true}).count()){
        assert.equal(expected,'won');return {maxFalling};
      }
      if(await page.locator('.status-pill').innerText()==='CODE ERROR'){
        assert.equal(expected,'error',await page.locator('.console-message').innerText());return {maxFalling};
      }
      const p=await giftPositions(page);
      maxFalling=Math.max(maxFalling,p.gifts.length);
      if(onRain)await onRain(p);
      let next=null;
      if(p.gift){
        if(p.gift.x-p.basket>5)next='ArrowRight';
        if(p.gift.x-p.basket < -5)next='ArrowLeft';
      }
      if(next!==held){if(held)await page.keyboard.up(held);held=next;if(held)await page.keyboard.down(held)}
      await page.waitForTimeout(50);
    }
    throw Error('Gift Catcher timed out: '+await page.locator('.console-message').innerText());
  } finally {if(held)await page.keyboard.up(held)}
}
module.exports={GIFT_SOLUTION,giftPositions,playGifts};
