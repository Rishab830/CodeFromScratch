const {MongoMemoryServer}=require('mongodb-memory-server');
const {MongoClient}=require('mongodb');
const {chromium,request}=require('@playwright/test');
const {spawn,spawnSync}=require('node:child_process');
const assert=require('node:assert/strict');
const crypto=require('node:crypto');
const fs=require('node:fs'),path=require('node:path');
const {levels}=require('./level-fixtures.cjs');
const {checkContrast}=require('./theme-contrast.cjs');
const url='http://127.0.0.1:3010',qa=path.join(__dirname,'..','artifacts','qa');fs.mkdirSync(qa,{recursive:true});
let mongo,client,server,browser,activePage,logs='';
const pause=ms=>new Promise(r=>setTimeout(r,ms));
async function expectStatus(response,status){assert.equal(response.status(),status,await response.text());return response.json()}
(async()=>{
 mongo=await MongoMemoryServer.create();client=new MongoClient(mongo.getUri());await client.connect();const db=client.db('account_test');
 server=spawn(process.execPath,[require.resolve('next/dist/bin/next'),'start','--hostname','127.0.0.1','--port','3010'],{cwd:path.join(__dirname,'..'),env:{...process.env,MONGODB_URI:mongo.getUri(),MONGODB_DB:'account_test'},stdio:['ignore','pipe','pipe'],windowsHide:true});
 server.stdout.on('data',d=>logs+=d);server.stderr.on('data',d=>logs+=d);
 for(let i=0;i<120;i++){try{if((await fetch(url+'/api/session')).ok)break}catch{}if(i===119)throw Error('Server did not start: '+logs);await pause(250)}
 const guest=await request.newContext({baseURL:url,extraHTTPHeaders:{Origin:url}});
 await expectStatus(await guest.get('/api/admin/users'),401);
 await expectStatus(await guest.patch('/api/progress/confused-traffic-signal',{data:{accountId:'x',completed:true}}),401);
 await expectStatus(await guest.post('/api/auth/register',{data:{name:'Invalid',email:'bad',password:'short'}}),400);
 await expectStatus(await guest.post('/api/auth/register',{headers:{Origin:'https://unrelated.example'},data:{}}),403);
 const runner=await guest.get('/runner-3/?account=000000000000000000000000');assert.equal(runner.status(),200,'Server routes must serve the Pygame runner');assert((await runner.text()).includes('id="canvas"'));
 browser=await chromium.launch({channel:'chrome',headless:true});
 const context=await browser.newContext({viewport:{width:1440,height:1100}}),page=await context.newPage();activePage=page;const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.addInitScript(()=>{try{localStorage.setItem('cfs:jumping-girl:v2:complete','yes');localStorage.setItem('cfs:coins:level-1:v1','["below"]')}catch{}});
 await page.goto(url+'/register');await page.getByLabel('Your name',{exact:true}).fill('Ada Pixel');await page.getByLabel('Email address',{exact:true}).fill('ada@workshop.test');await page.getByLabel('Password',{exact:true}).fill('A-long-test-password-42');await page.getByLabel('Confirm password',{exact:true}).fill('A-long-test-password-42');
 await page.getByRole('button',{name:'Choose Froggy',exact:true}).click();await page.getByRole('button',{name:'Choose Ocean palette',exact:true}).click();
 for(const width of [320,390,1440]){await page.setViewportSize({width,height:1000});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,'Registration overflow at '+width)}
 await page.screenshot({path:path.join(qa,'account-register.png'),fullPage:true});
 await page.getByRole('button',{name:'Create my account',exact:true}).click();await page.waitForURL(url+'/');await page.locator('.cm-content').waitFor();
 assert.equal(await page.locator('.site-header .pixel-avatar').getAttribute('aria-label'),'Ocean Froggy');
 let session=await (await context.request.get(url+'/api/session')).json();const ada=session.user;
 assert.equal(ada.preferences.siteTheme,'ocean');assert.equal(await page.locator('html').getAttribute('data-theme'),'ocean');
 assert.equal(session.progress.length,0,'Guest progress must not be silently imported');assert.equal(ada.role,'student');assert(!JSON.stringify(session).includes('passwordHash'));
 const cookies=await context.cookies();const sessionCookie=cookies.find(c=>c.name==='cfs_session');assert(sessionCookie.httpOnly);assert.equal(sessionCookie.sameSite,'Lax');
 const stored=await db.collection('users').findOne({email:ada.email});assert(stored.passwordHash.startsWith('$2'));assert.notEqual(stored.passwordHash,'A-long-test-password-42');assert(!await db.collection('sessions').findOne({_id:sessionCookie.value}));
 console.log('PASS: registration, avatar palettes, protected cookies, hashed passwords and tokens, CSRF rejection, and isolated guest progress.');
 const base={accountId:ada.id},attemptId=crypto.randomUUID();
 for(const theme of ['lavender','mint','peach','ocean','candy','sunshine','light']){
   const result=await expectStatus(await context.request.patch(url+'/api/profile',{headers:{Origin:url},data:{...base,preferences:{siteTheme:theme}}}),200);
   assert.equal(result.user.avatar.palette,theme);assert.equal(result.user.preferences.siteTheme,theme);
   const saved=await db.collection('users').findOne({_id:stored._id});assert.equal(saved.avatar.palette,theme);assert.equal(saved.preferences.siteTheme,theme);
 }
 await expectStatus(await context.request.patch(url+'/api/profile',{headers:{Origin:url},data:{...base,preferences:{siteTheme:'unknown'}}}),400);
 await expectStatus(await context.request.patch(url+'/api/profile',{headers:{Origin:url},data:{...base,preferences:{siteTheme:'ocean'}}}),200);
 await expectStatus(await context.request.patch(url+'/api/profile',{headers:{Origin:url},data:{...base,role:'admin',email:'changed@workshop.test'}}),200);
 await expectStatus(await context.request.get(url+'/api/admin/users'),403);
 await expectStatus(await guest.post('/api/auth/register',{data:{name:'Duplicate',email:'ADA@WORKSHOP.TEST',password:'A-second-valid-password',avatar:{design:'robot',palette:'mint'}}}),409);
 await expectStatus(await context.request.patch(url+'/api/progress/confused-traffic-signal',{headers:{Origin:url},data:{accountId:'000000000000000000000000',completed:true}}),409);
 await expectStatus(await context.request.patch(url+'/api/progress/confused-traffic-signal',{headers:{Origin:url},data:{...base,coins:['other-level-coin']}}),400);
 const traffic=levels.find(l=>l.id==='confused-traffic-signal');
 const patch=data=>context.request.patch(url+'/api/progress/'+traffic.id,{headers:{Origin:url},data:{...base,...data}});
 await expectStatus(await patch({attemptIds:[attemptId]}),200);await expectStatus(await patch({attemptIds:[attemptId]}),200);
 assert.equal((await db.collection('progress').findOne({levelId:traffic.id})).attemptIds.length,1);
 await expectStatus(await patch({code:'    pass\n',codeVersion:999}),409);
 await db.collection('progress').deleteMany({});
 await page.reload();await page.getByRole('button',{name:'Play level',exact:true}).waitFor({timeout:180000});await page.getByRole('button',{name:'Play level',exact:true}).click();await page.waitForFunction(()=>document.querySelector('.status-pill').textContent==='PLAYING');
 await page.keyboard.down('ArrowRight');await page.waitForTimeout(1700);await page.keyboard.up('ArrowRight');
 for(let i=0;i<30;i++){session=await (await context.request.get(url+'/api/session')).json();if(session.progress.find(p=>p.levelId===traffic.id)?.coins.includes('first'))break;await pause(200)}
 assert(session.progress.find(p=>p.levelId===traffic.id)?.coins.includes('first'),'A coin must sync immediately, before finishing the level');assert(!session.progress.find(p=>p.levelId===traffic.id)?.completed);
 const solution='    if current == "red":\n        next_color = "green"\n    elif current == "green":\n        next_color = "yellow"\n    else:\n        next_color = "red"\n';
 async function edit(body){await page.locator('.cm-content').evaluate((node,body)=>{const v=node.cmTile.root.view,t=v.state.doc.toString(),m=/^[ \t]*# EDIT START\n/m.exec(t),start=m.index+m[0].length,end=start+/^[ \t]*# EDIT END/m.exec(t.slice(start)).index;v.dispatch({changes:{from:start,to:end,insert:body}})},body)}
 await edit(solution);await page.getByRole('button',{name:'Compile',exact:true}).click();await page.waitForFunction(()=>document.querySelector('.status-pill').textContent==='PLAYING');await page.keyboard.down('ArrowRight');await page.getByRole('dialog',{name:'Level complete',exact:true}).waitFor({timeout:20000});await page.keyboard.up('ArrowRight');
 for(let i=0;i<30;i++){session=await (await context.request.get(url+'/api/session')).json();if(session.progress.find(p=>p.levelId===traffic.id)?.completed)break;await pause(200)}
 assert(session.progress.find(p=>p.levelId===traffic.id).completed);assert.equal(session.progress.find(p=>p.levelId===traffic.id).coins.length,2);assert.equal(session.progress.find(p=>p.levelId===traffic.id).code,solution);
 await expectStatus(await patch({completed:false,coins:[]}),200);const merged=await (await context.request.get(url+'/api/session')).json();assert(merged.progress.find(p=>p.levelId===traffic.id).completed);assert.equal(merged.progress.find(p=>p.levelId===traffic.id).coins.length,2);
 await page.getByRole('link',{name:'Open profile',exact:true}).click();await page.getByLabel('Display name',{exact:true}).fill('Ada Starlight');await page.getByRole('button',{name:'Choose Byte Ghost',exact:true}).click();await page.getByRole('button',{name:'Choose Candy palette',exact:true}).click();await page.getByRole('button',{name:'Save profile',exact:true}).click();await page.getByText('Your new look is saved.',{exact:true}).waitFor();
 assert.equal(await page.locator('.site-header .pixel-avatar').getAttribute('aria-label'),'Candy Byte Ghost');
 assert.equal(await page.locator('html').getAttribute('data-theme'),'candy');
 for(const theme of ['lavender','mint','peach','ocean','sunshine','light','candy']){await page.getByLabel('Website and avatar theme').selectOption(theme);await checkContrast(page)}
 for(const width of [320,390,1440]){await page.setViewportSize({width,height:1000});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,'Profile overflow at '+width)}
 await page.screenshot({path:path.join(qa,'account-profile.png'),fullPage:true});
 console.log('PASS: real Pygame coin pickups, code drafts, attempts, and completed levels reach MongoDB; profile edits update the header.');
 const second=await browser.newContext({viewport:{width:1440,height:1100}}),otherPage=await second.newPage();await otherPage.goto(url+'/login');await otherPage.getByLabel('Email address',{exact:true}).fill(ada.email);await otherPage.getByLabel('Password',{exact:true}).fill('A-long-test-password-42');await otherPage.getByRole('button',{name:'Log in',exact:true}).click();await otherPage.waitForURL(url+'/');await otherPage.locator('.cm-content').waitFor();
 assert.equal(await otherPage.locator('.site-header .pixel-avatar').getAttribute('aria-label'),'Candy Byte Ghost');assert.match(await otherPage.locator('.xp').innerText(),/100/);
 assert.equal(await otherPage.locator('html').getAttribute('data-theme'),'candy');
 const scope='cfs:user:'+ada.id+':';assert.equal(await otherPage.evaluate(k=>localStorage.getItem(k),scope+'cfs:coins:level-3:v1'),'["first","second"]');
 await otherPage.route('**/api/progress/**',route=>route.abort());
 const offlineCode=solution+'    # My offline draft\n';await otherPage.locator('.cm-content').evaluate((node,body)=>{const v=node.cmTile.root.view,t=v.state.doc.toString(),m=/^[ \t]*# EDIT START\n/m.exec(t),start=m.index+m[0].length,end=start+/^[ \t]*# EDIT END/m.exec(t.slice(start)).index;v.dispatch({changes:{from:start,to:end,insert:body}})},offlineCode);
 await otherPage.waitForTimeout(1200);await otherPage.reload();await otherPage.locator('.cm-content').waitFor();assert((await otherPage.locator('.cm-content').evaluate(n=>n.cmTile.root.view.state.doc.toString())).includes('My offline draft'));
 await otherPage.unroute('**/api/progress/**');await otherPage.evaluate(()=>window.dispatchEvent(new Event('online')));
 for(let i=0;i<30;i++){session=await (await second.request.get(url+'/api/session')).json();if(session.progress.find(p=>p.levelId===traffic.id)?.code.includes('My offline draft'))break;await pause(200)}
 assert(session.progress.find(p=>p.levelId===traffic.id).code.includes('My offline draft'));
 const blocked=await browser.newContext();await blocked.addCookies(await context.cookies());const blockedPage=await blocked.newPage();
 await blockedPage.addInitScript(()=>{Storage.prototype.getItem=function(){throw new Error('Storage disabled')};Storage.prototype.setItem=function(){throw new Error('Storage disabled')}});
 await blockedPage.goto(url+'/?level='+traffic.id);await blockedPage.locator('.cm-content').waitFor();assert((await blockedPage.locator('.cm-content').evaluate(n=>n.cmTile.root.view.state.doc.toString())).includes('My offline draft'));assert.match(await blockedPage.locator('.xp').innerText(),/100/);
 const blockedFrame=blockedPage.frames().find(f=>new URL(f.url()).pathname.startsWith('/runner-3'));await blockedFrame.waitForFunction(()=>typeof window.lessonReadCoins==='function');assert.deepEqual(JSON.parse(await blockedFrame.evaluate(()=>window.lessonReadCoins(3))),['first','second']);await blocked.close();
 const contextB=await request.newContext({baseURL:url,extraHTTPHeaders:{Origin:url}});
 const bob=await expectStatus(await contextB.post('/api/auth/register',{data:{name:'Bob Byte',email:'bob@workshop.test',password:'Another-strong-test-password',avatar:{design:'pilot',palette:'mint'},role:'admin'}}),200);
 assert.equal(bob.user.role,'student');assert.equal(bob.progress.length,0);await expectStatus(await contextB.get('/api/admin/users'),403);await expectStatus(await contextB.get('/api/admin/users/'+ada.id),403);
 await expectStatus(await contextB.patch('/api/progress/'+traffic.id,{data:{accountId:ada.id,completed:true}}),409);
 await expectStatus(await context.request.post(url+'/api/auth/login',{headers:{Origin:url},data:{email:ada.email,password:'wrong-password'}}),401);
 console.log('PASS: a second device restores the account; offline drafts survive reload and sync later; accounts cannot read or write each other’s progress or grant themselves admin.');
 const grant=spawnSync(process.execPath,['scripts/grant-admin.mjs',ada.email],{cwd:path.join(__dirname,'..'),env:{...process.env,MONGODB_URI:mongo.getUri(),MONGODB_DB:'account_test'},windowsHide:true,encoding:'utf8'});assert.equal(grant.status,0,grant.stderr);
 await page.goto(url+'/admin');await page.getByRole('heading',{name:'A little progress, everywhere.',exact:true}).waitFor();await page.getByRole('button',{name:'View profile',exact:true}).first().waitFor();
 let directory=await expectStatus(await context.request.get(url+'/api/admin/users'),200);assert.equal(directory.totalUsers,2);assert(!JSON.stringify(directory).includes('passwordHash'));
 for(const theme of ['lavender','mint','peach','ocean','sunshine','light','candy']){await page.getByLabel('Website and avatar theme').selectOption(theme);await checkContrast(page)}
 await db.collection('users').insertMany(Array.from({length:21},(_,i)=>({name:'Workshop Student '+i,email:`student${i}@qa.test`,role:'student',createdAt:new Date(),lastLoginAt:new Date(),preferences:{siteTheme:'dark',editorTheme:'dark'}})));
 directory=await expectStatus(await context.request.get(url+'/api/admin/users?page=2'),200);assert.equal(directory.users.length,3);assert.equal(directory.totalUsers,23);assert.equal(directory.pages,2);
 await page.getByRole('textbox',{name:'Search students',exact:true}).fill('Ada Starlight');await page.waitForTimeout(700);await page.getByRole('button',{name:'View profile',exact:true}).click();await page.getByRole('dialog',{name:'Student details',exact:true}).waitFor();await page.getByText('View saved student code',{exact:true}).click();assert((await page.getByRole('dialog').innerText()).includes('My offline draft'));await page.screenshot({path:path.join(qa,'account-admin-details.png'),fullPage:true});
 await page.getByRole('button',{name:'Close student details',exact:true}).click();await page.setViewportSize({width:390,height:844});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);await page.screenshot({path:path.join(qa,'account-admin-mobile.png'),fullPage:true});
 const adminDetail=await expectStatus(await context.request.get(url+'/api/admin/users/'+ada.id),200);assert.equal(adminDetail.progress.find(p=>p.levelId===traffic.id).coins.length,2);assert(!JSON.stringify(adminDetail).includes('passwordHash'));
 await otherPage.goto(url+'/profile');await otherPage.getByRole('button',{name:'Log out',exact:true}).click();await otherPage.waitForURL(url+'/');await expectStatus(await second.request.get(url+'/api/admin/users'),401);assert.equal((await (await second.request.get(url+'/api/session')).json()).user,null);
 await otherPage.goto(url+'/login');await otherPage.getByLabel('Email address',{exact:true}).fill('bob@workshop.test');await otherPage.getByLabel('Password',{exact:true}).fill('Another-strong-test-password');await otherPage.getByRole('button',{name:'Log in',exact:true}).click();await otherPage.waitForURL(url+'/');await otherPage.locator('.cm-content').waitFor();assert.match(await otherPage.locator('.xp').innerText(),/^0 XP$/);assert.equal(await otherPage.locator('.site-header .pixel-avatar').getAttribute('aria-label'),'Mint Star Pilot');
 const expiry=await db.collection('sessions').findOne({userId:stored._id});if(expiry){await db.collection('sessions').updateOne({_id:expiry._id},{$set:{expiresAt:new Date(0)}});assert.equal((await (await context.request.get(url+'/api/session')).json()).user,null)}
 assert.equal(errors.length,0,errors.join('\n'));console.log('PASS: admin directory and saved code access, student-role rejection, mobile layout, logout revocation, and session expiry.');
 await guest.dispose();await contextB.dispose();
})().catch(async error=>{if(activePage)await activePage.screenshot({path:path.join(qa,'account-failure.png'),fullPage:true}).catch(()=>{});console.error(error);console.error(logs.slice(-2500));process.exitCode=1}).finally(async()=>{if(browser)await browser.close();if(server)server.kill();if(client)await client.close();if(mongo)await mongo.stop()});
