const {chromium}=require('@playwright/test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {levels,core}=require('./level-fixtures.cjs');
let browser;
(async()=>{
  browser=await chromium.launch({channel:'chrome',headless:true});
  const page=await browser.newPage({viewport:{width:390,height:844}});
  await page.addInitScript(keys=>keys.forEach(key=>localStorage.setItem(key+':complete','yes')),core.map(l=>l.storage));
  await page.route('**/runner*/',route=>route.abort());
  await page.goto(process.env.TEST_URL||'http://127.0.0.1:3001');
  for(const level of levels){
    await page.locator(`button[data-level-id="${level.id}"]`).click();
    await page.waitForFunction(n=>document.querySelector('.cm-content')?.cmTile?.root?.view?.state.doc.toString().includes(`LEVEL_NUMBER = ${n}\n`),level.number);
    const name=level.id+'.py';
    assert.equal(await page.locator('.editor-titlebar>div>span').first().innerText(),name);
    const source=await page.locator('.cm-content').evaluate(n=>n.cmTile.root.view.state.doc.toString());
    assert.equal(source,fs.readFileSync(path.join(__dirname,'..','game','levels',name),'utf8').replace(/\r\n?/g,'\n'));
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,'Mobile overflow: '+name);
  }
  console.log('PASS: all six core and seven bonus editors show their own dedicated source and filename without mobile overflow');
  await browser.close();
})().catch(async e=>{console.error(e);if(browser)await browser.close();process.exit(1)});
