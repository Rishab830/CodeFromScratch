const {chromium}=require('@playwright/test');
const assert=require('node:assert/strict');
const path=require('node:path');
const {core}=require('./level-fixtures.cjs');
const {GIFT_SOLUTION,playGifts}=require('./gift-catcher-fixture.cjs');
let browser,page;
(async()=>{
  browser=await chromium.launch({channel:'chrome',headless:true});
  page=await browser.newPage({viewport:{width:1440,height:1100}});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.addInitScript(keys=>{try{keys.forEach(key=>localStorage.setItem(key+':complete','yes'))}catch{}},core.filter(l=>l.id!=='gift-catcher').map(l=>l.storage));
  await page.route(/\/runner(?:-\d+)?\/?$/,async route=>{
    const u=new URL(route.request().url());
    if(u.pathname.endsWith('/'))await route.fulfill({status:308,headers:{location:u.pathname.slice(0,-1)}});
    else await route.fulfill({response:await route.fetch({url:u.origin+u.pathname+'/index.html'})});
  });
  await page.addInitScript(()=>{try{localStorage.setItem('cfs:guest:chosen','yes')}catch{}});
  await page.goto(process.env.TEST_URL||'http://127.0.0.1:3001');
  const playing=()=>page.waitForFunction(()=>document.querySelector('.status-pill').textContent==='PLAYING');
  async function hold(key,ms){await page.keyboard.down(key);await page.waitForTimeout(ms);await page.keyboard.up(key);}
  async function choose(id){
    await page.locator(`button[data-level-id="${id}"]`).click();
    await page.getByRole('button',{name:'Play level',exact:true}).waitFor({timeout:180000});
  }
  async function start(){await page.getByRole('button',{name:'Play level',exact:true}).click();await playing();}
  async function compile(body){
    await page.locator('.cm-content').evaluate((n,body)=>{
      const v=n.cmTile.root.view,t=v.state.doc.toString(),m=/^[ \t]*# EDIT START\n/m.exec(t),start=m.index+m[0].length,end=start+/^[ \t]*# EDIT END/m.exec(t.slice(start)).index;
      v.dispatch({changes:{from:start,to:end,insert:body}});
    },body);
    await page.getByRole('button',{name:'Compile',exact:true}).click();await playing();
  }
  await choose('gift-catcher');await start();
  assert.equal(await page.getByRole('textbox',{name:'Terminal password'}).count(),0);
  assert.equal(await page.locator('.touch-controls button').count(),2);
  assert.equal(await page.getByRole('button',{name:'Handle gift',exact:true}).count(),0);
  assert(!/SPACE/i.test(await page.locator('.keyboard-guide').innerText()));
  await compile(GIFT_SOLUTION);
  await hold('ArrowLeft',1800);
  await page.getByRole('dialog',{name:'Game over',exact:true}).waitFor({timeout:10000});
  assert.match(await page.locator('.console-message').innerText(),/one missed|every falling/i);
  assert.equal(await page.evaluate(()=>localStorage.getItem('cfs:bonus:gift-catcher:v1:complete')),null);
  await compile('    if gift_in_basket():\n        open_gift()\n        if gift_is_bomb():\n            collect()\n        else:\n            drop()\n');
  await playGifts(page,'dead');
  assert.equal(await page.evaluate(()=>localStorage.getItem('cfs:bonus:gift-catcher:v1:complete')),null);
  await compile('    if gift_in_basket():\n        if gift_is_bomb():\n            drop()\n        else:\n            collect()\n');
  await playGifts(page,'error');
  assert.match(await page.locator('.console-message').innerText(),/Open the gift before checking/);
  // The inner sensor cannot inspect a sealed gift. Opening must precede it.
  // Only movement is supplied: the nested-if handler runs automatically.
  await compile(GIFT_SOLUTION);await page.waitForTimeout(400);
  assert.equal(await page.getByRole('dialog',{name:'Level complete',exact:true}).count(),0);
  let captured=false;
  const rain=await playGifts(page,'won',async positions=>{if(!captured&&positions.gifts.length>=2){captured=true;await page.screenshot({path:path.join(__dirname,'..','artifacts','qa','gift-catcher-continuous-rain.png'),fullPage:true})}});
  assert(rain.maxFalling>=2,'Several gifts must fall at the same time');
  assert.equal(await page.getByRole('group',{name:'Coins collected: 2 of 2',exact:true}).count(),1);
  assert.equal(await page.getByRole('button',{name:'Next lesson',exact:true}).count(),1);
  console.log('PASS: continuous rain and automatic nested-if handling need only movement; one missed gift is fatal, bombs stay hidden until opened, and eggs plus saved coins are collected');

  await choose('endless-coin-collector');await start();
  await hold('ArrowRight',650);await hold('Space',180);await page.waitForTimeout(2400);await hold('ArrowRight',3500);
  assert.equal(await page.getByRole('dialog',{name:'Level complete',exact:true}).count(),0);
  assert.equal(await page.evaluate(()=>localStorage.getItem('cfs:collector:v1:complete')),null);
  await compile('    return count < 5\n');
  await page.waitForTimeout(800);
  assert.equal(await page.getByRole('dialog',{name:'Level complete',exact:true}).count(),0);
  await hold('ArrowRight',650);await hold('Space',180);await page.waitForTimeout(2200);await hold('ArrowRight',3500);
  await page.getByRole('dialog',{name:'Level complete',exact:true}).waitFor({timeout:5000});
  assert.equal(await page.getByRole('group',{name:'Coins collected: 5 of 5',exact:true}).count(),1);
  assert.equal(await page.getByRole('button',{name:'Choose another bonus',exact:true}).count(),1);
  assert.match(await page.locator('.xp').innerText(),/800/);
  assert.equal(errors.length,0,errors.join('\n'));
  console.log('PASS: Endless Coin Collector stays optional, its endless starter cannot win, and the fixed machine unlocks a manually reached exit');
  await browser.close();
})().catch(async error=>{console.error(error);if(page)await page.screenshot({path:path.join(__dirname,'..','artifacts','qa','bonus-failure.png'),fullPage:true}).catch(()=>{});if(browser)await browser.close();process.exit(1);});
