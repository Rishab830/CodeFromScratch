const { chromium } = require('@playwright/test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const qa = path.join(__dirname, '..', 'artifacts', 'qa');
fs.mkdirSync(qa, {recursive:true});
let browser, page;

(async () => {
  browser = await chromium.launch({channel:'chrome',headless:true});
  const context = await browser.newContext({viewport:{width:1440,height:1100}});
  page = await context.newPage();
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
      const marker = /^[ \t]*# EDIT START\n/m.exec(text);
      const start = marker.index + marker[0].length;
      const end = start + /^[ \t]*# EDIT END/m.exec(text.slice(start)).index;
      view.dispatch({changes:{from:start,to:end,insert:body}});
    }, body);
  }
  async function position(activeFrame = frame) {
    return activeFrame.evaluate(() => {
      const canvas = document.querySelector('#canvas');
      const {data,width} = canvas.getContext('2d').getImageData(0,0,canvas.width,canvas.height);
      let x = 0, y = 0, count = 0;
      for (let i = 0; i < data.length; i += 4) if (data[i] === 237 && data[i+1] === 160 && data[i+2] === 185) {
        x += (i / 4) % width; y += Math.floor((i / 4) / width); count++;
      }
      return {x:x/count,y:y/count};
    });
  }
  // Use visible sprite pixels to time the jump, so runtime speed and screenshot
  // capture time cannot move the player past the edge between test actions.
  async function jumpAt(x, activeFrame = frame) {
    await activeFrame.waitForFunction(target => {
      const canvas = document.querySelector('#canvas');
      const {data,width} = canvas.getContext('2d').getImageData(0,0,canvas.width,canvas.height);
      let sum = 0, count = 0;
      for (let i = 0; i < data.length; i += 4) if (data[i] === 237 && data[i+1] === 160 && data[i+2] === 185) {
        sum += (i / 4) % width; count++;
      }
      return count > 0 && sum / count <= target * width / 320;
    }, x, {timeout:7000,polling:'raf'});
    await page.keyboard.down('Space');await page.waitForTimeout(80);await page.keyboard.up('Space');
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
  await page.waitForTimeout(3700);
  await page.keyboard.up('ArrowLeft');
  await page.getByRole('dialog',{name:'Game over',exact:true}).waitFor({timeout:5000});
  await page.screenshot({path:path.join(qa,'level-1-gap-fall.png'),fullPage:true});
  assert(await page.locator('.journey-stop.next').isDisabled());
  await page.getByRole('button',{name:'Restart level',exact:true}).click();
  await playing();
  console.log('PASS: fixed Level 1 code still falls into the gap without a manual jump; Restart works');
  await page.keyboard.down('ArrowLeft');
  await jumpAt(160);
  await page.waitForTimeout(2500);
  await page.keyboard.up('ArrowLeft');
  await page.getByRole('dialog',{name:'Level complete',exact:true}).waitFor({timeout:5000});
  assert(!(await page.locator('.journey-stop.next').isDisabled()));
  assert.match(await page.locator('.xp').innerText(),/100/);
  await page.screenshot({path:path.join(qa,'new-win.png'),fullPage:true});
  console.log('PASS: manually jumping the gap and reaching the flag completes Level 1');

  await page.getByRole('button',{name:'Play again',exact:true}).click();
  await playing();
  const touchBefore = await position();
  await page.getByRole('button',{name:'Move left',exact:true}).scrollIntoViewIfNeeded();
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
  assert.match(secondSource,/# EDIT START\nclass Girl:/);
  assert.doesNotMatch(secondSource,/configure/);
  assert.match(secondSource,/GAP = pygame.Rect\(132, FLOOR, 12, HEIGHT - FLOOR\)/);
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
  const classSource=secondSource.split('# EDIT START\n')[1].split('# EDIT END')[0];
  assert.match(classSource,/def __init__/);
  assert.match(classSource,/def stop/);
  await page.getByRole('button',{name:'Play level',exact:true}).click();
  await playing();
  await page.keyboard.down('ArrowLeft');await page.waitForTimeout(1100);await page.keyboard.up('ArrowLeft');
  await page.getByRole('dialog',{name:'Game over',exact:true}).waitFor();
  assert.match(await page.locator('.console-message').innerText(),/spikes/);
  console.log('PASS: Level 2 uses the original spike map; starter jump hits the spikes');
  await setBody(classSource.replace('self.vy = -178','self.vy = -80'));
  await page.getByRole('button',{name:'Compile',exact:true}).click();
  await playing();
  await page.waitForTimeout(500);
  assert.equal(await page.getByRole('dialog',{name:'Level complete'}).count(),0);
  await page.keyboard.down('ArrowLeft');await page.waitForTimeout(3700);await page.keyboard.up('ArrowLeft');
  await page.getByRole('dialog',{name:'Game over',exact:true}).waitFor({timeout:5000});
  await page.getByRole('button',{name:'Restart level',exact:true}).click();
  await playing();
  console.log('PASS: Level 2 also falls into the gap if the player does not jump');
  await page.keyboard.down('ArrowLeft');await jumpAt(148,secondFrame);
  await page.waitForTimeout(2600);await page.keyboard.up('ArrowLeft');
  await page.getByRole('dialog',{name:'Level complete',exact:true}).waitFor({timeout:5000});
  assert.match(await page.locator('.xp').innerText(),/200/);
  await page.screenshot({path:path.join(qa,'level-2-small-jump-win.png'),fullPage:true});
  console.log('PASS: full class compiles; small jumps pass beneath the spikes and clear the floor gap');
  await setBody(classSource.replace('self.vy = -178','self.vy = -420'));
  await page.getByRole('button',{name:'Compile',exact:true}).click();
  await playing();
  await page.keyboard.down('ArrowLeft');await page.waitForTimeout(190);
  await page.keyboard.down('Space');await page.waitForTimeout(80);await page.keyboard.up('Space');
  await page.waitForTimeout(300);
  await page.screenshot({path:path.join(qa,'level-2-high-jump.png'),fullPage:true});
  await jumpAt(148,secondFrame);
  await page.waitForTimeout(2600);await page.keyboard.up('ArrowLeft');
  await page.getByRole('dialog',{name:'Level complete',exact:true}).waitFor({timeout:5000});
  console.log('PASS: a high manual jump clears the spikes and a second manual jump clears the gap');
  await setBody(classSource.replace('self.vy = -178','self.vy = -300'));
  await page.getByRole('button',{name:'Compile',exact:true}).click();
  await playing();
  await page.keyboard.down('ArrowLeft');
  await page.keyboard.down('Space');await page.waitForTimeout(80);await page.keyboard.up('Space');
  await page.waitForTimeout(1100);await page.keyboard.up('ArrowLeft');
  const onTop = await position(secondFrame);
  assert(onTop.y / 2.5 > 60 && onTop.y / 2.5 < 72, 'Maya did not land on the spike platform');
  await page.waitForTimeout(500);
  assert(Math.abs((await position(secondFrame)).y-onTop.y)<3, 'Standing above blue should not cause another jump');
  await page.keyboard.down('ArrowRight');await page.waitForTimeout(200);await page.keyboard.up('ArrowRight');
  const walkedRight = await position(secondFrame);
  assert(walkedRight.x>onTop.x+15);
  assert(Math.abs(walkedRight.y-onTop.y)<3);
  await page.keyboard.down('ArrowLeft');await page.waitForTimeout(200);await page.keyboard.up('ArrowLeft');
  const walkedLeft = await position(secondFrame);
  assert(walkedLeft.x<walkedRight.x-15);
  assert(Math.abs(walkedLeft.y-onTop.y)<3);
  await page.screenshot({path:path.join(qa,'level-2-walkable-top.png'),fullPage:true});
  await page.keyboard.down('Space');await page.waitForTimeout(80);await page.keyboard.up('Space');
  await page.waitForTimeout(100);
  assert((await position(secondFrame)).y<onTop.y-20);
  await page.waitForTimeout(1500);
  assert(Math.abs((await position(secondFrame)).y-onTop.y)<3);
  await page.keyboard.down('ArrowLeft');await jumpAt(148,secondFrame);
  await page.waitForTimeout(2600);await page.keyboard.up('ArrowLeft');
  await page.getByRole('dialog',{name:'Level complete',exact:true}).waitFor({timeout:5000});
  console.log('PASS: Maya lands on the spike platform, stays still, walks both ways, jumps, and can finish the level');
  await page.locator('.journey-stop').first().click();
  await page.getByRole('heading',{name:'The Jumping Girl',exact:false}).waitFor();
  await page.waitForFunction(()=>document.querySelector('.cm-content')?.cmTile?.root?.view?.state.doc.toString().includes('LEVEL_NUMBER = 1'));
  assert.match(await getSource(),/def on_blue\(player\):\n    # EDIT START/);
  console.log('PASS: map navigation restores Level 1 with its own editable section');
  await browser.close();
})().catch(async error => {console.error(error);if(page)await page.screenshot({path:path.join(qa,'failure.png'),fullPage:true}).catch(()=>{});if(browser)await browser.close();process.exit(1);});
