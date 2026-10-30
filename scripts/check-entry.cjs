const {chromium}=require('@playwright/test');
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const {checkContrast}=require('./theme-contrast.cjs');
const url=process.env.TEST_URL||'http://127.0.0.1:3001',qa=path.join(__dirname,'..','artifacts','qa');
fs.mkdirSync(qa,{recursive:true});
let browser,page;
async function context(options={}){
  const ctx=await browser.newContext({viewport:{width:1440,height:1100},...options});
  await ctx.route('**/runner*/',route=>route.abort());
  await ctx.route('**/api/session',route=>route.fulfill({json:{user:null,progress:[]}}));
  return ctx;
}
async function workshop(p){await p.locator('.cm-content').waitFor();assert.equal(await p.getByRole('heading',{name:/Code\. Fix\./}).count(),0)}
(async()=>{
  browser=await chromium.launch({channel:'chrome',headless:true});
  const ctx=await context();page=await ctx.newPage();let runnerRequests=0;const errors=[];
  page.on('pageerror',e=>errors.push(e.message));page.on('request',request=>{if(/\/runner(?:-\d+)?\//.test(new URL(request.url()).pathname))runnerRequests++});
  await page.goto(url);
  await page.getByRole('heading',{name:/Code\. Fix\./}).waitFor();
  assert(await page.getByLabel('Email address',{exact:true}).isVisible());
  assert(await page.getByRole('button',{name:'Log in',exact:true}).isVisible());
  assert.equal(await page.getByRole('link',{name:'Create your account',exact:true}).getAttribute('href'),'/register');
  assert(await page.getByRole('button',{name:'Play as guest',exact:true}).isVisible());
  assert.equal(await page.locator('iframe').count(),0);assert.equal(runnerRequests,0);
  await page.screenshot({path:path.join(qa,'welcome-default.png'),fullPage:true});
  for(const theme of ['lavender','mint','peach','ocean','candy','sunshine','light']){
    await page.getByLabel('Website and avatar theme').selectOption(theme);await checkContrast(page);
  }
  await page.screenshot({path:path.join(qa,'welcome-light.png'),fullPage:true});
  for(const width of [320,390,1440]){await page.setViewportSize({width,height:1000});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,'Welcome overflow at '+width)}
  await page.getByRole('button',{name:'Play as guest',exact:true}).click();await workshop(page);
  assert.equal(await page.evaluate(()=>localStorage.getItem('cfs:guest:chosen')),'yes');
  await page.reload();await workshop(page);
  const returning=await ctx.newPage();await returning.goto(url);await workshop(returning);
  console.log('PASS: first visit shows login, signup, and guest play before loading Python; guest choice persists on reload and new tabs; seven themes and mobile layouts pass.');
  for(const route of ['/login','/register']){
    const fresh=await context(),p=await fresh.newPage();await p.goto(url+route);
    await p.getByRole('button',{name:'Play as guest',exact:true}).click();await workshop(p);
    assert.equal(new URL(p.url()).searchParams.get('guest'),'1');await fresh.close();
  }
  const blocked=await context();await blocked.addInitScript(()=>{Storage.prototype.getItem=function(){throw Error('Storage unavailable')};Storage.prototype.setItem=function(){throw Error('Storage unavailable')}});
  const p=await blocked.newPage();await p.goto(url);await p.getByRole('button',{name:'Play as guest',exact:true}).click();await workshop(p);
  await p.goto(url+'/register');await p.getByRole('button',{name:'Play as guest',exact:true}).click();await workshop(p);await p.reload();await workshop(p);
  console.log('PASS: both account pages can enter guest play; guest play remains usable when browser storage is disabled.');
  const signed=await context(),login=await signed.newPage();let authenticated=false;
  const user={id:'000000000000000000000001',name:'Workshop Learner',email:'learner@workshop.test',avatar:{design:'cat',palette:'mint'},role:'student',createdAt:new Date().toISOString(),lastLoginAt:new Date().toISOString(),preferences:{siteTheme:'mint',editorTheme:'dark'}};
  await signed.unroute('**/api/session');await signed.route('**/api/session',route=>route.fulfill({json:{user:authenticated?user:null,progress:[]}}));
  await signed.route('**/api/auth/login',async route=>{assert.deepEqual(route.request().postDataJSON(),{email:user.email,password:'workshop-password'});authenticated=true;await route.fulfill({json:{user,progress:[]}})});
  await login.goto(url);await login.getByLabel('Email address',{exact:true}).fill(user.email);await login.getByLabel('Password',{exact:true}).fill('workshop-password');await login.getByRole('button',{name:'Log in',exact:true}).click();await workshop(login);
  assert.equal(await login.locator('.site-header .pixel-avatar').getAttribute('aria-label'),'Mint Pixel Cat');
  await login.reload();await workshop(login);
  assert.equal(await login.getByRole('button',{name:'Play as guest',exact:true}).count(),0);
  assert.equal(errors.length,0,errors.join('\n'));
  console.log('PASS: login from the first-visit screen enters the workshop; returning signed-in users skip the welcome screen.');
})().catch(async error=>{console.error(error);if(page)await page.screenshot({path:path.join(qa,'entry-failure.png'),fullPage:true}).catch(()=>{});process.exitCode=1}).finally(async()=>{if(browser)await browser.close()});
