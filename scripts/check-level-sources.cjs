const {chromium}=require('@playwright/test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {levels,core}=require('./level-fixtures.cjs');
let browser;
(async()=>{
  browser=await chromium.launch({channel:'chrome',headless:true});
  const page=await browser.newPage({viewport:{width:390,height:844}});
  await page.addInitScript(keys=>{try{keys.forEach(key=>localStorage.setItem(key+':complete','yes'))}catch{}},core.map(l=>l.storage));
  await page.route('**/runner*/',route=>route.abort());
  await page.addInitScript(()=>{try{localStorage.setItem('cfs:guest:chosen','yes')}catch{}});
  await page.goto(process.env.TEST_URL||'http://127.0.0.1:3001');
  for(const level of levels){
    await page.locator(`button[data-level-id="${level.id}"]`).click();
    await page.waitForFunction(n=>document.querySelector('.cm-content')?.cmTile?.root?.view?.state.doc.toString().includes(`LEVEL_NUMBER = ${n}\n`),level.number);
    const name=level.id+'.py';
    assert.equal(await page.locator('.editor-titlebar>div>span').first().innerText(),name);
    const source=await page.locator('.cm-content').evaluate(n=>n.cmTile.root.view.state.doc.toString());
    assert.equal(source,fs.readFileSync(path.join(__dirname,'..','game','levels',name),'utf8').replace(/\r\n?/g,'\n'));
    assert((await page.locator('h1').innerText()).startsWith(level.title));
    const displayNumber=(level.group==='bonus'?'B':'')+String(level.group==='bonus'?level.number-core.length:level.number).padStart(2,'0');
    assert((await page.locator('.game-heading>span').innerText()).endsWith(displayNumber),'Wrong game number: '+name);
    assert.equal(await page.locator('.mission-story h2').innerText(),level.missionTitle);
    assert.equal(await page.locator('.mission-story p').innerText(),level.mission);
    assert.equal(await page.locator('.mission-steps>div').nth(2).locator('p').innerText(),level.playInstruction);
    assert.equal(await page.locator('.level-reward strong').innerText(),level.goal);
    assert.deepEqual(await page.locator('.keyboard-guide kbd').allInnerTexts(),Array.from(level.keyboardGuide,([keys])=>keys));
    assert.deepEqual(await page.locator('.touch-controls button').evaluateAll(nodes=>nodes.map(n=>n.getAttribute('aria-label'))),Array.from(level.controls,([,label])=>label));
    const html=await (await page.request.get(new URL(level.runtime+'index.html',page.url()).href)).text();
    assert(html.includes(`<title>${level.title} · Pygame runner</title>`),'Wrong runner title: '+name);
    assert(!html.includes('lessonReadInput'),'Obsolete password input: '+name);
    for(const hint of level.hints){
      await page.locator('.hint-section button').click();
      assert.equal(await page.locator('#level-hint').innerText(),hint);
    }
    await page.getByRole('button',{name:'Player actions',exact:true}).click();
    assert.equal(await page.locator('.reference-content>p').innerText(),level.reference);
    assert.deepEqual(await page.locator('.api-grid code').allInnerTexts(),Array.from(level.actions,([name])=>name));
    await page.setViewportSize({width:1440,height:900});
    await page.getByRole('button',{name:'How to play',exact:true}).click();
    assert((await page.getByRole('dialog').innerText()).includes(level.playInstruction));
    await page.getByRole('button',{name:'Close',exact:true}).click();
    await page.setViewportSize({width:390,height:844});
    await page.evaluate(()=>{
      const frame=document.querySelector('iframe');
      window.dispatchEvent(new MessageEvent('message',{source:frame.contentWindow,data:{channel:'scratch',type:'ready'}}));
    });
    assert.equal(await page.locator('.console-message p').innerText(),level.intro);
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,'Mobile overflow: '+name);
    for(const width of [320,1440]){
      await page.setViewportSize({width,height:900});
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,`Overflow at ${width}: ${name}`);
    }
    await page.setViewportSize({width:390,height:844});
  }
  console.log('PASS: all 13 levels have matching titles, missions, objectives, controls, references, three hints, ready/help messages, and dedicated source; no overflow at 320/390/1440px');
  await browser.close();
})().catch(async e=>{console.error(e);if(browser)await browser.close();process.exit(1)});
