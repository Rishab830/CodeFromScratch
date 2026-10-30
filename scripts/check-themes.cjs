const {checkContrast}=require('./theme-contrast.cjs');
const {chromium}=require('@playwright/test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const qa=path.join(__dirname,'..','artifacts','qa');
fs.mkdirSync(qa,{recursive:true});
let browser;
(async()=>{
  browser=await chromium.launch({channel:'chrome',headless:true});
  const context=await browser.newContext({viewport:{width:1440,height:1100},colorScheme:'light'});
  const page=await context.newPage();
  const errors=[];
  page.on('pageerror',error=>errors.push(error.message));
  await page.addInitScript(()=>{try{localStorage.setItem('cfs:traffic:v1:complete','yes')}catch{}});
  await page.route('**/runner*/',route=>route.abort());
  const url=process.env.TEST_URL || 'http://127.0.0.1:3001';
  await page.addInitScript(()=>{try{localStorage.setItem('cfs:guest:chosen','yes')}catch{}});
  await page.goto(url);
  await page.locator('.editable-line').first().waitFor();
  const site=()=>page.getByLabel('Website and avatar theme',{exact:true});
  const code=(mode)=>page.getByRole('button',{name:`Use ${mode} code editor theme`,exact:true});
  const getSource=()=>page.locator('.cm-content').evaluate(node=>node.cmTile.root.view.state.doc.toString());
  async function check(siteTheme,editorTheme){
    await page.waitForFunction(([site,code])=>document.documentElement.dataset.theme===site&&document.querySelector('.editor-panel').dataset.codeTheme===code,[siteTheme,editorTheme]);
    assert.equal(await site().inputValue(),siteTheme);
    const name={lavender:'Lavender',mint:'Mint',peach:'Peach',ocean:'Ocean',candy:'Candy',sunshine:'Sunshine',light:'Light'}[siteTheme];
    assert.match(await page.locator('.site-header .pixel-avatar').getAttribute('aria-label'),new RegExp('^'+name+' '));
    assert.equal(await code(editorTheme).getAttribute('aria-pressed'),'true');
  }
  await check('lavender','dark');
  assert.equal(await page.getByRole('group',{name:'website theme',exact:true}).count(),0);
  assert.equal(await site().locator('option').count(),7);
  console.log('PASS: dark Lavender and dark code are default; Light is one of seven website/avatar themes.');
  await page.locator('.editable-line').first().click();
  await page.keyboard.press('Home');await page.keyboard.press('Shift+End');await page.keyboard.insertText('    pass');
  const edited=await getSource();
  await page.locator('.cm-content').evaluate(node=>window.__themeTestView=node.cmTile.root.view);
  const backgrounds=new Set();
  for(const palette of ['lavender','mint','peach','ocean','candy','sunshine','light']){
    await site().selectOption(palette);await check(palette,'dark');
    backgrounds.add(await page.locator('body').evaluate(node=>getComputedStyle(node).backgroundColor));
    await checkContrast(page);
    assert.equal(await getSource(),edited);
  }
  assert.equal(backgrounds.size,7,'Every palette must change the website background.');
  await site().selectOption('light');await check('light','dark');
  assert.equal(await getSource(),edited);
  await page.screenshot({path:path.join(qa,'light-site-dark-code.png'),fullPage:true});
  await code('light').click();await check('light','light');
  await checkContrast(page);
  const lightBackground=await page.locator('.cm-editor').evaluate(node=>getComputedStyle(node).backgroundColor);
  assert.notEqual(lightBackground,'rgb(40, 44, 52)');
  await page.screenshot({path:path.join(qa,'light-site-light-code.png'),fullPage:true});
  await site().selectOption('ocean');await check('ocean','light');
  await checkContrast(page);
  await page.screenshot({path:path.join(qa,'dark-site-light-code.png'),fullPage:true});
  assert.equal(await getSource(),edited);
  assert(await page.locator('.cm-content').evaluate(node=>node.cmTile.root.view===window.__themeTestView),'Theme switching recreated the editor and its history');
  console.log('PASS: all site/editor combinations work independently without replacing edited code or editor history');
  await page.locator('.editable-line').first().click();await page.keyboard.press('Home');await page.keyboard.press('Shift+End');
  await page.waitForTimeout(100);
  assert(await page.locator('.cm-selectionBackground').count()>0);
  await code('dark').click();await check('ocean','dark');
  await site().selectOption('light');await code('light').click();
  await page.reload();await page.locator('.editable-line').first().waitFor();await check('light','light');
  assert.equal(await getSource(),edited);
  console.log('PASS: separate theme preferences and edited code persist after reload');
  await page.locator('button[data-level-id="parcel-sorter"]').click();
  await page.getByRole('heading',{name:'The Parcel Sorter',exact:false}).waitFor();
  await check('light','light');
  await page.waitForFunction(()=>document.querySelector('.cm-content')?.cmTile?.root?.view?.state.doc.toString().includes('LEVEL_NUMBER = 2'));
  await page.setViewportSize({width:390,height:844});await page.waitForTimeout(150);
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
  assert(await site().isVisible());assert(await code('dark').isVisible());
  await page.screenshot({path:path.join(qa,'light-mode-mobile.png'),fullPage:true});
  await site().selectOption('lavender');await check('lavender','light');
  for(const width of [320,390,1440]){await page.setViewportSize({width,height:1000});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,'Workshop overflow at '+width)}
  for(const route of ['/register','/login','/profile','/admin']){
    await page.goto(url+route);await site().waitFor();
    for(const palette of ['lavender','mint','peach','ocean','candy','sunshine','light']){
      await site().selectOption(palette);await page.waitForFunction(t=>document.documentElement.dataset.theme===t,palette);
      await checkContrast(page);
    }
    for(const width of [320,390,1440]){await page.setViewportSize({width,height:1000});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,route+' overflow at '+width)}
    if(route==='/register'){
      await page.getByRole('button',{name:'Choose Mint palette',exact:true}).click();
      assert.equal(await site().inputValue(),'mint');
      await checkContrast(page);
      await page.screenshot({path:path.join(qa,'mint-registration.png'),fullPage:true});
      await page.getByRole('button',{name:'Choose Light palette',exact:true}).click();
      assert.equal(await site().inputValue(),'light');
      await checkContrast(page);
      await page.screenshot({path:path.join(qa,'light-registration.png'),fullPage:true});
    }
  }
  assert.equal(errors.length,0,errors.join('\n'));
  console.log('PASS: preferences survive level navigation; both controls remain accessible on mobile');
  await browser.close();
})().catch(async error=>{console.error(error);if(browser)await browser.close();process.exit(1);});
