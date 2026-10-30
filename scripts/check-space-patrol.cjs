const {chromium}=require('@playwright/test');
const assert=require('node:assert/strict');
const path=require('node:path');
const fs=require('node:fs');
const {core}=require('./level-fixtures.cjs');
const {shipPosition,pilotSector,flyToBeacon}=require('./space-patrol-fixture.cjs');
const qa=path.join(__dirname,'..','artifacts','qa');fs.mkdirSync(qa,{recursive:true});
let browser,page;
async function enemyPositions(){
  const frame=page.frames().find(f=>/\/runner-10\/?$/.test(new URL(f.url()).pathname));
  return frame.evaluate(()=>{
    const c=document.querySelector('#canvas'),d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;
    const pixels=new Set(),scale=c.width/320,groups=[];
    for(let y=24;y<160;y++)for(let x=0;x<320;x++){
      const i=(Math.floor((y+.5)*scale)*c.width+Math.floor((x+.5)*scale))*4;
      if(d[i]===239&&d[i+1]===173&&d[i+2]===194)pixels.add(y*320+x);
    }
    while(pixels.size){
      const stack=[pixels.values().next().value],points=[];pixels.delete(stack[0]);
      while(stack.length){
        const p=stack.pop(),x=p%320,y=Math.floor(p/320);points.push([x,y]);
        for(let dy=-1;dy<=1;dy++)for(let dx=-1;dx<=1;dx++){
          const n=(y+dy)*320+x+dx;
          if(pixels.delete(n))stack.push(n);
        }
      }
      if(points.length>12)groups.push({x:points.reduce((sum,p)=>sum+p[0],0)/points.length,y:points.reduce((sum,p)=>sum+p[1],0)/points.length});
    }
    return groups;
  });
}
(async()=>{
  browser=await chromium.launch({channel:'chrome',headless:true});
  page=await browser.newPage({viewport:{width:1440,height:1100}});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.addInitScript(keys=>{try{keys.forEach(k=>localStorage.setItem(k+':complete','yes'))}catch{}},core.slice(0,5).map(l=>l.storage));
  await page.addInitScript(()=>{try{localStorage.setItem('cfs:guest:chosen','yes')}catch{}});
  await page.goto(process.env.TEST_URL||'http://127.0.0.1:3001');
  await page.locator('button[data-level-id="space-patrol"]').click();
  await page.getByRole('button',{name:'Play level',exact:true}).waitFor({timeout:180000});
  await page.getByRole('button',{name:'Play level',exact:true}).click();
  const playing=()=>page.waitForFunction(()=>document.querySelector('.status-pill').textContent==='PLAYING');
  await playing();
  const start=await shipPosition(page);assert(Math.abs(start.x-160)<2&&Math.abs(start.y-90)<2,'Ship must start at the center');
  for(const [key,axis,sign] of [['w','y',-1],['s','y',1],['a','x',-1],['d','x',1]]){
    const before=await shipPosition(page);await page.keyboard.down(key);await page.waitForTimeout(180);await page.keyboard.up(key);
    assert(((await shipPosition(page))[axis]-before[axis])*sign>7,'Movement failed: '+key);
  }
  async function compile(body){
    await page.locator('.cm-content').evaluate((n,body)=>{
      const v=n.cmTile.root.view,t=v.state.doc.toString(),m=/^[ \t]*# EDIT START\n/m.exec(t),start=m.index+m[0].length,end=start+/^[ \t]*# EDIT END/m.exec(t.slice(start)).index;
      v.dispatch({changes:{from:start,to:end,insert:body}});
    },body);
    await page.getByRole('button',{name:'Compile',exact:true}).click();await playing();
  }
  // Pause shooting so all four simultaneous enemies can be observed in the canvas.
  await compile('    for bullet in range(0):\n        shoot()\n');
  await page.keyboard.press('Space');
  let enemies=[];
  for(let i=0;i<30;i++){enemies=await enemyPositions();if(enemies.length===4)break;await page.waitForTimeout(70)}
  assert.equal(enemies.length,4,'The first wave must spawn four enemies together');
  const ship=await shipPosition(page);
  assert.equal(new Set(enemies.map(e=>`${e.x>ship.x},${e.y>ship.y}`)).size,4,'The first wave must surround the ship');
  await page.screenshot({path:path.join(qa,'space-patrol-surrounded.png'),fullPage:true});
  console.log('PASS: centered start, WASD movement, and four enemies simultaneously visible around all sides');
  await compile('    for bullet in range(30):\n        shoot()\n');await pilotSector(page,'dead');
  assert.equal(await page.getByRole('dialog',{name:'Level complete',exact:true}).count(),0);
  console.log('PASS: unconditional starter still wastes bullets and cannot clear the sector');
  for(const body of ['    while enemy_visible():\n        shoot()\n','    for bullet in range(30):\n        if enemy_visible():\n            shoot()\n']){
    await compile(body);await pilotSector(page);
    assert.equal(await page.getByRole('dialog',{name:'Level complete',exact:true}).count(),0,'Clearing enemies alone must not win');
    await flyToBeacon(page);
    assert.equal(await page.getByRole('group',{name:'Coins collected: 2 of 2',exact:true}).count(),1);
  }
  await page.setViewportSize({width:390,height:844});
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
  await page.screenshot({path:path.join(qa,'space-patrol-groups-mobile.png'),fullPage:true});
  assert.equal(errors.length,0,errors.join('\n'));
  console.log('PASS: while and for/if clear all three groups, coins persist, manual flight to the beacon wins, and mobile controls fit');
  await browser.close();
})().catch(async error=>{console.error(error);if(page)await page.screenshot({path:path.join(qa,'space-patrol-failure.png'),fullPage:true}).catch(()=>{});if(browser)await browser.close();process.exit(1)});
