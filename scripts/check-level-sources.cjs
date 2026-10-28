const {chromium}=require('@playwright/test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const slugs=['jumping-girl','blue-leap','confused-traffic-signal','lost-robot','endless-coin-collector','wrong-door','final-escape'];
const keys=['cfs:jumping-girl:v2','cfs:blue-leap:v2','cfs:traffic:v1','cfs:robot:v1','cfs:collector:v1','cfs:doors:v1','cfs:escape:v1'];
let browser;
(async()=>{
  browser=await chromium.launch({channel:'chrome',headless:true});
  const page=await browser.newPage({viewport:{width:390,height:844}});
  await page.addInitScript(keys=>keys.forEach(key=>localStorage.setItem(key+':complete','yes')),keys);
  await page.goto(process.env.TEST_URL||'http://127.0.0.1:3001');
  for(let index=0;index<slugs.length;index++){
    if(index) await page.locator('.journey-stop').nth(index).click();
    await page.waitForFunction(n=>document.querySelector('.cm-content')?.cmTile?.root?.view?.state.doc.toString().includes(`LEVEL_NUMBER = ${n}`),index+1);
    const name=slugs[index]+'.py';
    assert.equal(await page.locator('.editor-titlebar>div>span').first().innerText(),name);
    const visibleSource=await page.locator('.cm-content').evaluate(node=>node.cmTile.root.view.state.doc.toString());
    assert.equal(visibleSource,fs.readFileSync(path.join(__dirname,'..','game','levels',name),'utf8').replace(/\r\n?/g,'\n'));
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,'Filename causes mobile overflow: '+name);
  }
  console.log('PASS: all seven editor filenames and complete sources match their dedicated Pygame files, including mobile layout');
  await browser.close();
})().catch(async error=>{console.error(error);if(browser)await browser.close();process.exit(1)});
