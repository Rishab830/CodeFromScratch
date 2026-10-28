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
  console.log('PASS: branded root app, protected editor, and actual Pygame engine load');
  await page.screenshot({path:path.join(qa,'new-desktop.png'),fullPage:true});
  const frame = page.frames().find(frame => frame.url().includes('/runner/'));
  const editor = page.locator('.cm-content');
  const getSource = () => editor.evaluate(node => node.cmTile.root.view.state.doc.toString());
  async function setBody(body) {
    await editor.evaluate((node,body) => {
      const view = node.cmTile.root.view, text = view.state.doc.toString();
      const start = text.indexOf('    # EDIT START: fix the action below\n') + '    # EDIT START: fix the action below\n'.length;
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
  await browser.close();
})().catch(async error => {console.error(error);if(browser)await browser.close();process.exit(1);});
