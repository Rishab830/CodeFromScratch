const {chromium}=require('@playwright/test');
const assert=require('node:assert/strict');
const path=require('node:path');
const fs=require('node:fs');
const {core,bonus}=require('./level-fixtures.cjs');
const qa=path.join(__dirname,'..','artifacts','qa');fs.mkdirSync(qa,{recursive:true});
let browser,page;
const fixes={
 'confused-traffic-signal':'    if current == "red":\n        next_color = "green"\n    elif current == "green":\n        next_color = "yellow"\n    else:\n        next_color = "red"\n',
 'parcel-sorter':'    if parcel_colour() == "red":\n        send_left()\n    elif parcel_colour() == "blue":\n        send_middle()\n    else:\n        send_right()\n',
 'bridge-builder':'    for i in range(3):\n        place_plank()\n    cross_bridge()\n',
 'lost-robot':'    for i in range(3):\n        move_left()\n    for i in range(2):\n        move_up()\n    for i in range(3):\n        move_left()\n',
 'charging-station':'    while not battery_full():\n        charge()\n    open_exit()\n',
 'foggy-tunnel':'    while not exit_detected():\n        move_forward()\n    open_exit()\n',
 'rocket-launch':'    if power_on():\n        if fuel_ready():\n            launch()\n        else:\n            refuel()\n    else:\n        wait_for_power()\n',
 'greenhouse-grid':'    for row in range(3):\n        for column in range(3):\n            water_cell(row, column)\n    open_exit()\n',
 'final-escape':'    for row in range(2):\n        for column in range(3):\n            power_cell(row, column)\n    if all_powered():\n        unlock_exit()\n        open_exit()\n',
};
(async()=>{
  assert.deepEqual(Array.from(core,l=>l.id),['confused-traffic-signal','parcel-sorter','bridge-builder','lost-robot','charging-station','foggy-tunnel']);
  browser=await chromium.launch({channel:'chrome',headless:true});
  page=await browser.newPage({viewport:{width:1440,height:1100}});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.route(/\/runner(?:-\d+)?\/?$/,async route=>{
    const u=new URL(route.request().url());
    if(u.pathname.endsWith('/'))await route.fulfill({status:308,headers:{location:u.pathname.slice(0,-1)}});
    else await route.fulfill({response:await route.fetch({url:u.origin+u.pathname+'/index.html'})});
  });
  await page.goto(process.env.TEST_URL||'http://127.0.0.1:3001');
  const stop=id=>page.locator(`button[data-level-id="${id}"]`);
  const playing=()=>page.waitForFunction(()=>document.querySelector('.status-pill').textContent==='PLAYING');
  const won=()=>page.getByRole('dialog',{name:'Level complete',exact:true}).waitFor({timeout:8000});
  const dead=()=>page.getByRole('dialog',{name:'Game over',exact:true}).waitFor({timeout:8000});
  async function hold(key,ms){await page.keyboard.down(key);await page.waitForTimeout(ms);await page.keyboard.up(key);}
  async function ready(id){
    const entry=[...core,...bonus].find(l=>l.id===id);
    await page.waitForFunction(n=>document.querySelector('.cm-content')?.cmTile?.root?.view?.state.doc.toString().includes(`LEVEL_NUMBER = ${n}\n`),entry.number);
    await page.getByRole('button',{name:'Play level',exact:true}).waitFor({timeout:180000});
    const source=await page.locator('.cm-content').evaluate(n=>n.cmTile.root.view.state.doc.toString());
    await page.locator('.cm-content').evaluate(n=>n.cmTile.root.view.dispatch({changes:{from:0,to:1,insert:'X'}}));
    assert.equal(await page.locator('.cm-content').evaluate(n=>n.cmTile.root.view.state.doc.toString()),source);
    if(entry.exercise==='build'){
      assert.equal(source.split('# EDIT START\n')[1].split('    # EDIT END')[0].trim(),'pass');
      assert(await page.getByRole('region',{name:'Python code editor'}).getByLabel('Available lesson functions').isVisible());
    }
  }
  async function compile(body){
    await page.locator('.cm-content').evaluate((n,body)=>{
      const v=n.cmTile.root.view,t=v.state.doc.toString(),m=/^[ \t]*# EDIT START\n/m.exec(t),start=m.index+m[0].length,end=start+/^[ \t]*# EDIT END/m.exec(t.slice(start)).index;
      v.dispatch({changes:{from:start,to:end,insert:body}});
    },body);
    await page.getByRole('button',{name:'Compile',exact:true}).click();
  }
  async function fixed(id){await compile(fixes[id]);await playing();await page.waitForTimeout(350);assert.equal(await page.getByRole('dialog',{name:'Level complete',exact:true}).count(),0);}
  async function start(){await page.getByRole('button',{name:'Play level',exact:true}).click();await playing();}
  async function next(id){await page.getByRole('button',{name:'Next lesson',exact:true}).click();await ready(id);}
  async function screenshot(name){await page.screenshot({path:path.join(qa,name+'.png'),fullPage:true});}
  await ready(core[0].id);
  for(const l of [...core.slice(1),...bonus])assert(await stop(l.id).isDisabled());
  await start();await hold('ArrowRight',3600);assert(await stop('parcel-sorter').isDisabled());
  await fixed('confused-traffic-signal');await hold('ArrowRight',4600);await won();
  console.log('PASS: core 1 debugs if/elif/else; only the next core lesson unlocks');

  await next('parcel-sorter');await start();await hold('Space',500);assert.equal(await page.getByRole('dialog',{name:'Level complete',exact:true}).count(),0);
  await screenshot('workshop-parcel-blank');
  await compile('    if parcel_colour() != "":\n        send_left()\n');await playing();await hold('Space',4500);await dead();
  await fixed('parcel-sorter');await hold('Space',11000);await won();
  console.log('PASS: core 2 starts blank, exposes supplied functions, and requires routing all colours correctly');

  await next('bridge-builder');await start();await hold('Space',1000);await dead();
  await fixed('bridge-builder');await hold('Space',4100);await won();
  console.log('PASS: core 3 teaches counted repetition through a real bridge-building bug');

  await next('lost-robot');await start();await hold('Space',400);assert.equal(await page.getByRole('dialog',{name:'Level complete',exact:true}).count(),0);
  await screenshot('workshop-robot-blank');
  await compile('    move_left()\n');await page.waitForFunction(()=>document.querySelector('.status-pill').textContent==='CODE ERROR');
  await fixed('lost-robot');await hold('Space',2800);await won();
  console.log('PASS: core 4 is a blank for-loop route, with no instruction lists');

  await next('charging-station');await start();await hold('Space',350);await dead();
  await fixed('charging-station');await hold('Space',1500);await won();
  console.log('PASS: core 5 debugs while using a sensor that updates after each manual action');

  await next('foggy-tunnel');await start();await hold('Space',350);assert.equal(await page.getByRole('dialog',{name:'Level complete',exact:true}).count(),0);
  await screenshot('workshop-foggy-blank');
  await compile('    for i in range(6):\n        move_forward()\n    open_exit()\n');
  await page.waitForFunction(()=>document.querySelector('.status-pill').textContent==='CODE ERROR');assert.match(await page.locator('.console-message').innerText(),/while/);
  await compile('    while True:\n        pass\n');await playing();await hold('Space',150);
  await page.waitForFunction(()=>document.querySelector('.status-pill').textContent==='CODE ERROR');assert.match(await page.locator('.console-message').innerText(),/not making progress/);
  await fixed('foggy-tunnel');await hold('Space',8200);await won();
  assert.match(await page.locator('.xp').innerText(),/600/);
  assert.equal(await page.getByRole('group',{name:'Coins collected: 3 of 3',exact:true}).count(),1);
  for(const l of bonus)assert(!(await stop(l.id).isDisabled()));
  assert.equal(await page.evaluate(keys=>keys.some(k=>localStorage.getItem(k+':complete')==='yes'),bonus.map(l=>l.storage)),false);
  await screenshot('workshop-complete');
  await page.getByRole('button',{name:'Workshop complete',exact:true}).click();await page.getByRole('heading',{name:'Workshop complete!',exact:true}).waitFor();
  await page.getByRole('button',{name:'Close',exact:true}).click();
  console.log('PASS: core 6 requires while, handles three hidden lengths, and completes the workshop without any bonus');

  for(const [id,duration] of [['rocket-launch',1100],['greenhouse-grid',3000],['final-escape',2600]]){
    await stop(id).click();await ready(id);await fixed(id);await hold('Space',duration);await won();
    assert.equal(await page.getByRole('button',{name:'Choose another bonus',exact:true}).count(),1);
  }
  assert.equal(await page.evaluate(()=>localStorage.getItem('cfs:doors:v1:complete')),null);
  await page.setViewportSize({width:390,height:844});await page.waitForTimeout(200);
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
  await screenshot('workshop-bonuses-mobile');
  assert.equal(errors.length,0,errors.join('\n'));
  console.log('PASS: planned bonuses work independently, blank nested challenges expose helpers, and mobile layout fits');
  await browser.close();
})().catch(async error=>{console.error(error);if(page)await page.screenshot({path:path.join(qa,'workshop-failure.png'),fullPage:true}).catch(()=>{});if(browser)await browser.close();process.exit(1)});
