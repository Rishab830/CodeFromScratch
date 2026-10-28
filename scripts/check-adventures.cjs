const {chromium}=require('@playwright/test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const qa=path.join(__dirname,'..','artifacts','qa');
fs.mkdirSync(qa,{recursive:true});
let browser,page;
const route=['right','right','up','up','right','right','down','right','right','down','right','right'];
const fixes={
  3:'    return {"red": "green", "green": "yellow", "yellow": "red"}[current]\n',
  4:`    return ${JSON.stringify(['right','down','left','up',...route])}\n`,
  5:'    return count < 5\n',
  6:'    if password == "STAR":\n        return 2\n    return None\n',
  7:'    steps = []\n    for cell in range(3):\n        steps.append("power")\n    if len(steps) == 3:\n        steps.append("unlock")\n        steps.append("open")\n    return steps\n',
};
(async()=>{
  browser=await chromium.launch({channel:'chrome',headless:true});
  page=await browser.newPage({viewport:{width:1440,height:1100}});
  await page.addInitScript(()=>{
    localStorage.setItem('cfs:jumping-girl:v2:complete','yes');
    localStorage.setItem('cfs:blue-leap:v2:complete','yes');
  });
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.route(/\/runner(?:-[2-7])?\/?$/,async r=>{
    const url=new URL(r.request().url());
    if(url.pathname.endsWith('/')) await r.fulfill({status:308,headers:{location:url.pathname.slice(0,-1)}});
    else await r.fulfill({response:await r.fetch({url:url.origin+url.pathname+'/index.html'})});
  });
  await page.goto(process.env.TEST_URL||'http://127.0.0.1:3001');
  const stop=number=>page.locator('.journey-stop').nth(number-1);
  const playing=()=>page.waitForFunction(()=>document.querySelector('.status-pill').textContent==='PLAYING');
  const clear=()=>page.getByRole('dialog',{name:'Level complete',exact:true}).waitFor({timeout:8000});
  const screenshot=name=>page.screenshot({path:path.join(qa,name+'.png'),fullPage:true});
  async function hold(key,ms){await page.keyboard.down(key);await page.waitForTimeout(ms);await page.keyboard.up(key);}
  async function focus(){await page.locator('.game-viewport iframe').evaluate(node=>node.contentWindow.document.querySelector('#canvas').focus());}
  async function action(){await focus();await hold('Space',80);}
  async function ready(number){
    await page.waitForFunction(n=>document.querySelector('.cm-content')?.cmTile?.root?.view?.state.doc.toString().includes(`LEVEL_NUMBER = ${n}`),number);
    await page.getByRole('button',{name:'Play level',exact:true}).waitFor({timeout:150000});
    const text=await page.locator('.cm-content').evaluate(n=>n.cmTile.root.view.state.doc.toString());
    assert.equal((text.match(/# EDIT START/g)||[]).length,1);
    await page.locator('.cm-content').evaluate(n=>n.cmTile.root.view.dispatch({changes:{from:0,to:1,insert:'X'}}));
    assert.equal(await page.locator('.cm-content').evaluate(n=>n.cmTile.root.view.state.doc.toString()),text);
    const guide=await page.locator('.keyboard-guide').innerText();
    assert.doesNotMatch(guide,/Jump/);
    assert.match(guide,number===3 ? /Drive/ : number===4 ? /Step/ : /Interact/);
    assert.equal(await page.getByRole('button',{name:'Jump',exact:true}).count(),0);
  }
  async function compile(body){
    await page.locator('.cm-content').evaluate((n,body)=>{
      const view=n.cmTile.root.view,text=view.state.doc.toString();
      const match=/^[ \t]*# EDIT START\n/m.exec(text),start=match.index+match[0].length;
      const end=start+/^[ \t]*# EDIT END/m.exec(text.slice(start)).index;
      view.dispatch({changes:{from:start,to:end,insert:body}});
    },body);
    await page.getByRole('button',{name:'Compile',exact:true}).click();
  }
  async function fix(number){await compile(fixes[number]);await playing();await page.waitForTimeout(350);assert.equal(await page.getByRole('dialog',{name:'Level complete',exact:true}).count(),0);}
  await page.waitForFunction(()=>document.querySelectorAll('.journey-stop').length===7 && !document.querySelectorAll('.journey-stop')[2].disabled);
  for(let n=4;n<=7;n++) assert(await stop(n).isDisabled());
  await stop(3).click();await ready(3);
  await page.getByRole('button',{name:'Play level',exact:true}).click();await playing();
  await hold('ArrowRight',4200);
  assert.equal(await page.getByRole('dialog',{name:'Level complete',exact:true}).count(),0);
  assert(await stop(4).isDisabled());
  await screenshot('level-3-red-yellow');
  await fix(3);await hold('ArrowRight',4600);await clear();
  assert(!(await stop(4).isDisabled()));assert(await stop(5).isDisabled());
  await screenshot('level-3-complete');
  console.log('PASS: Level 3 starter waits at red/yellow; corrected Python allows manual driving and unlocks only Level 4');

  await page.getByRole('button',{name:'Next adventure',exact:true}).click();await ready(4);
  await page.getByRole('button',{name:'Play level',exact:true}).click();await playing();
  await hold('Space',1100);assert.equal(await page.getByRole('dialog',{name:'Level complete',exact:true}).count(),0);
  await screenshot('level-4-circle');
  await fix(4);await hold('Space',4500);await clear();
  assert.equal(await page.getByRole('group',{name:'Coins collected: 2 of 2',exact:true}).count(),1);
  await screenshot('level-4-complete');
  console.log('PASS: Level 4 loops in a circle until edited; manual steps and an optional detour reach the dock with both coins');

  await page.getByRole('button',{name:'Next adventure',exact:true}).click();await ready(5);
  await page.getByRole('button',{name:'Play level',exact:true}).click();await playing();
  await hold('ArrowRight',660);await action();await page.waitForTimeout(2300);
  assert.match(await page.locator('.console-message').innerText(),/Too many|still running/);
  await hold('ArrowRight',3800);assert.equal(await page.getByRole('dialog',{name:'Level complete',exact:true}).count(),0);
  await screenshot('level-5-endless');
  await fix(5);await hold('ArrowRight',660);await action();await hold('ArrowRight',3800);await clear();
  assert.equal(await page.getByRole('group',{name:'Coins collected: 5 of 5',exact:true}).count(),1);
  await screenshot('level-5-complete');
  console.log('PASS: Level 5 starter overshoots five; fixed condition stops at five, unlocks the door, and requires walking to it');

  await page.getByRole('button',{name:'Next adventure',exact:true}).click();await ready(6);
  await page.getByRole('textbox',{name:'Terminal password',exact:true}).fill('STAR');
  await page.getByRole('button',{name:'Play level',exact:true}).click();await playing();
  await action();await hold('ArrowRight',1100);
  await page.getByRole('dialog',{name:'Game over',exact:true}).waitFor();await screenshot('level-6-wrong-door');
  await fix(6);await page.getByRole('textbox',{name:'Terminal password',exact:true}).fill('WRONG');await action();
  await page.waitForTimeout(300);assert.match(await page.locator('.console-message').innerText(),/Access denied/);
  await page.getByRole('textbox',{name:'Terminal password',exact:true}).fill('STAR');await action();await hold('ArrowRight',3800);await clear();
  await screenshot('level-6-complete');
  console.log('PASS: Level 6 opens the wrong door with the starter; corrected logic rejects a wrong password and permits manual exit through STAR');

  await page.getByRole('button',{name:'Next adventure',exact:true}).click();await ready(7);
  await page.getByRole('button',{name:'Play level',exact:true}).click();await playing();
  await hold('ArrowRight',550);await action();await page.waitForTimeout(1500);await hold('ArrowRight',3800);
  assert.equal(await page.getByRole('dialog',{name:'Level complete',exact:true}).count(),0);await screenshot('level-7-locked');
  await compile('    while True:\n        pass\n');
  await page.waitForFunction(()=>document.querySelector('.status-pill').textContent==='CODE ERROR');
  assert.match(await page.locator('.console-message').innerText(),/loop did not finish/);
  await fix(7);await hold('ArrowRight',550);await action();await hold('ArrowRight',3800);await clear();
  assert.match(await page.locator('.xp').innerText(),/700/);
  assert.equal(await page.getByRole('group',{name:'Coins collected: 2 of 2',exact:true}).count(),1);
  await screenshot('level-7-complete');
  await page.setViewportSize({width:390,height:844});await page.waitForTimeout(250);
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
  await screenshot('seven-levels-mobile');
  await page.getByRole('button',{name:'Adventures complete',exact:true}).click();
  await page.getByRole('heading',{name:'Seven adventures, from scratch.',exact:true}).waitFor();
  assert.equal(errors.length,0,errors.join('\n'));
  console.log('PASS: Level 7 combines loop, condition, and sequence; infinite loops report errors; manual escape earns 700 XP and all seven levels fit mobile');
  await browser.close();
})().catch(async e=>{console.error(e);if(page)await page.screenshot({path:path.join(qa,'adventures-failure.png'),fullPage:true}).catch(()=>{});if(browser)await browser.close();process.exit(1)});
