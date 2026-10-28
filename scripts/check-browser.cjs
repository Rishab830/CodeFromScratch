const { chromium } = require('@playwright/test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const qa = path.join(__dirname, '..', 'artifacts', 'qa');
fs.mkdirSync(qa, {recursive:true});
let browser;

(async () => {
  browser = await chromium.launch({channel:'chrome',headless:true});
  const context = await browser.newContext({viewport:{width:1440,height:1100}});
  const page = await context.newPage();
  if (process.env.EMULATE_CLEAN_URLS === '1') {
    // Reproduce Vercel's extensionless directory-index URLs. A plain static
    // server alone will not catch a missing base URL after slash removal.
    await page.route(/\/runner(?:-2)?\/?$/, async (route) => {
      const url = new URL(route.request().url());
      if (url.pathname.endsWith('/')) {
        await route.fulfill({status:308,headers:{location:url.pathname.slice(0,-1)}});
      } else {
        const response = await route.fetch({url:url.origin + url.pathname + '/index.html'});
        await route.fulfill({response});
      }
    });
  }
  await page.addInitScript(() => {
    window.__loadingEvents = [];
    window.addEventListener('message', (event) => {
      if (event.data?.channel === 'scratch' && event.data.type === 'loading') window.__loadingEvents.push(event.data);
    });
  });
  page.on('pageerror', error => console.log('PAGE ERROR', error.message));
  await page.goto(process.env.TEST_URL || 'http://127.0.0.1:3001');
  assert.match(await page.title(), /Code From Scratch/);
  assert.equal(await page.getByRole('button',{name:/Test my fix/}).count(), 0);
  await page.waitForFunction(() => {
    const line = document.querySelector('.editable-line'), editor = document.querySelector('.editor-body');
    if (!line || !editor) return false;
    const a = line.getBoundingClientRect(), b = editor.getBoundingClientRect();
    return a.top >= b.top && a.bottom <= b.bottom;
  }, {timeout:20000});
  await page.screenshot({path:path.join(qa,'new-loading.png'),fullPage:true});
  await page.getByRole('button',{name:'Play level',exact:true}).waitFor({timeout:150000});
  const progress = await page.evaluate(() => window.__loadingEvents);
  assert(progress.some((event) => event.phase === 1 && event.loaded > 0), 'Python download never reported received bytes');
  assert(progress.some((event) => event.phase === 3 && event.loaded > 0), 'Pygame download never reported received bytes');
  assert(progress.some((event) => event.phase === 4), 'Game startup phase was missing');
  assert.equal(await page.getByRole('progressbar',{name:'Game loading progress'}).count(), 0);
  console.log('PASS: Python and Pygame report real download progress; loader clears only when ready');
  console.log('PASS: branded root app, protected editor, and actual Pygame engine load');
  await page.screenshot({path:path.join(qa,'new-desktop.png'),fullPage:true});
  const frame = page.frames().find(frame => /\/runner\/?$/.test(new URL(frame.url()).pathname));
  const editor = page.locator('.cm-content');
  const getSource = () => editor.evaluate(node => node.cmTile.root.view.state.doc.toString());
  async function setBody(body) {
    await editor.evaluate((node,body) => {
      const view = node.cmTile.root.view, text = view.state.doc.toString();
      const start = text.indexOf('    # EDIT START\n') + '    # EDIT START\n'.length;
      const end = text.indexOf('    # EDIT END',start);
      view.dispatch({changes:{from:start,to:end,insert:body}});
    }, body);
  }
  async function position() {
    return frame.evaluate(() => {
      const canvas = document.querySelector('#canvas');
      const {data,width} = canvas.getContext('2d').getImageData(0,0,canvas.width,canvas.height);
      let x = 0, y = 0, count = 0;
      for (let i = 0; i < data.length; i += 4) if (data[i] === 237 && data[i+1] === 160 && data[i+2] === 185) {
        x += (i / 4) % width; y += Math.floor((i / 4) / width); count++;
      }
      return {x:x/count,y:y/count};
    });
  }
  async function playing() { await page.waitForFunction(() => document.querySelector('.status-pill').textContent === 'PLAYING'); }
  await page.getByRole('button',{name:'Play level',exact:true}).click();
  await playing();
  const before = await position();
  await page.keyboard.down('ArrowLeft');
  await page.waitForTimeout(1100);
  await page.keyboard.up('ArrowLeft');
  await page.getByRole('dialog',{name:'Game over',exact:true}).waitFor({timeout:5000});
  assert(await page.locator('.journey-stop.next').isDisabled());
  await page.screenshot({path:path.join(qa,'new-game-over.png'),fullPage:true});
  console.log('PASS: actual manual play hits overhead spikes, game over appears, next level stays locked');
  await page.getByRole('button',{name:'Restart level',exact:true}).click();
  await playing();
  const restarted = await position();
  assert(Math.abs(restarted.x-before.x)<5);
  console.log('PASS: Restart restores the spawn position');

  const protectedSource = await getSource();
  await editor.evaluate(node => node.cmTile.root.view.dispatch({changes:{from:0,to:1,insert:'X'}}));
  assert.equal(await getSource(),protectedSource);
  await setBody('    player.move_left(\n');
  await page.getByRole('button',{name:'Compile',exact:true}).click();
  await page.waitForFunction(() => document.querySelector('.status-pill').textContent === 'CODE ERROR');
  assert.match(await page.locator('.console-message').innerText(),/Python syntax error/);
  assert(await page.locator('.journey-stop.next').isDisabled());
  console.log('PASS: Compile reports Python errors and never completes a level');

  // An alternate valid solution, with no line matching or prescribed action.
  await setBody('    pass\n');
  await page.getByRole('button',{name:'Compile',exact:true}).click();
  await playing();
  const idle = await position();
  await page.waitForTimeout(7000);
  assert(Math.abs((await position()).x-idle.x)<3);
  assert(await page.locator('.journey-stop.next').isDisabled());
  assert.equal(await page.getByRole('dialog',{name:'Level complete'}).count(),0);
  console.log('PASS: compiling and waiting cannot win; no automatic grading remains');
  await page.keyboard.down('ArrowLeft');
  await page.waitForTimeout(2300);
  await page.keyboard.down('Space');
  await page.waitForTimeout(150);
  await page.keyboard.up('Space');
  await page.waitForTimeout(2500);
  await page.keyboard.up('ArrowLeft');
  await page.getByRole('dialog',{name:'Level complete',exact:true}).waitFor({timeout:5000});
  assert(!(await page.locator('.journey-stop.next').isDisabled()));
  assert.match(await page.locator('.xp').innerText(),/100/);
  await page.screenshot({path:path.join(qa,'new-win.png'),fullPage:true});
  console.log('PASS: manually reaching the flag with alternate Python and a jump completes the level');

  await page.getByRole('button',{name:'Play again',exact:true}).click();
  await playing();
  const touchBefore = await position();
  const button = await page.getByRole('button',{name:'Move left',exact:true}).boundingBox();
  await page.mouse.move(button.x+button.width/2,button.y+button.height/2);
  await page.mouse.down();await page.waitForTimeout(350);await page.mouse.up();
  assert((await position()).x < touchBefore.x-20);
  console.log('PASS: on-screen controls move the actual Pygame character');
  await page.getByRole('button',{name:'Reset code',exact:true}).click();
  await page.waitForFunction(() => document.querySelector('.cm-content').cmTile.root.view.state.doc.toString().includes('    player.jump()\n    # EDIT END'));
  assert.match(await page.locator('.compile-state').innerText(),/Uncompiled changes/);
  await page.setViewportSize({width:390,height:844});
  await page.waitForTimeout(400);
  assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth),false);
  await page.screenshot({path:path.join(qa,'new-mobile.png'),fullPage:true});
  console.log('PASS: reset changes require Compile, and mobile layout fits');
  await page.setViewportSize({width:1440,height:1100});
  await page.locator('.journey-stop.next').click();
  await page.getByRole('heading',{name:'The Blue Leap',exact:false}).waitFor();
  await page.waitForSelector('.editable-line');
  const secondSource = await getSource();
  assert.match(secondSource,/def configure\(\):\n    # EDIT START\n    return -110/);
  assert.match(secondSource,/def on_blue\(player\):\n    player.jump\(\)/);
  await editor.evaluate(node => {
    const view=node.cmTile.root.view;
    const start=view.state.doc.toString().indexOf('    player.jump()',view.state.doc.toString().indexOf('def on_blue'));
    view.dispatch({changes:{from:start,to:start+17,insert:'    player.stop()'}});
  });
  assert.equal(await getSource(),secondSource);
  assert.match(await page.locator('.mission-story').innerText(),/blue WILL make Maya jump/);
  assert.doesNotMatch(await page.locator('.mission-story').innerText(),/distance|velocity|increase|return/i);
  assert.equal(await page.locator('.hint-section').count(),0);
  console.log('PASS: Level 2 loads its own source, locks the blue jump, and gives no solution hint');
  await page.getByRole('button',{name:'Play level',exact:true}).waitFor({timeout:150000});
  // The runner iframe changed when navigating; read the live one for Level 2.
  const secondFrame=page.frames().find(entry=>/\/runner-2\/?$/.test(new URL(entry.url()).pathname));
  async function secondPosition() {
    return secondFrame.evaluate(()=>{
      const canvas=document.querySelector('#canvas');
      const {data,width}=canvas.getContext('2d').getImageData(0,0,canvas.width,canvas.height);
      let sy=0,count=0;
      for(let i=0;i<data.length;i+=4)if(data[i]===237&&data[i+1]===160&&data[i+2]===185){sy+=Math.floor((i/4)/width);count++;}
      return sy/count;
    });
  }
  await page.getByRole('button',{name:'Play level',exact:true}).click();
  await playing();
  const secondGround=await secondPosition();
  await page.keyboard.down('ArrowLeft');await page.waitForTimeout(950);
  assert((await secondPosition()) < secondGround-7,'Blue did not force a jump');
  await page.waitForTimeout(1800);await page.keyboard.up('ArrowLeft');
  await page.getByRole('dialog',{name:'Game over',exact:true}).waitFor();
  assert.match(await page.locator('.console-message').innerText(),/solid ground/);
  console.log('PASS: blue forces an actual Pygame jump; the starter falls short of the ledge');
  await setBody('    return -300\n');
  await page.getByRole('button',{name:'Compile',exact:true}).click();
  await playing();
  await page.waitForTimeout(500);
  assert.equal(await page.getByRole('dialog',{name:'Level complete'}).count(),0);
  await page.keyboard.down('ArrowLeft');await page.waitForTimeout(5000);await page.keyboard.up('ArrowLeft');
  await page.getByRole('dialog',{name:'Level complete',exact:true}).waitFor({timeout:5000});
  assert.match(await page.locator('.xp').innerText(),/200/);
  await page.screenshot({path:path.join(qa,'level-2-win.png'),fullPage:true});
  console.log('PASS: compiled adjustment changes the jump and manual play clears Level 2');
  await page.locator('.journey-stop').first().click();
  await page.getByRole('heading',{name:'The Jumping Girl',exact:false}).waitFor();
  await page.waitForFunction(()=>document.querySelector('.cm-content')?.cmTile?.root?.view?.state.doc.toString().includes('LEVEL_NUMBER = 1'));
  assert.match(await getSource(),/def on_blue\(player\):\n    # EDIT START/);
  console.log('PASS: map navigation restores Level 1 with its own editable section');
  await browser.close();
})().catch(async error => {console.error(error);if(browser)await browser.close();process.exit(1);});
