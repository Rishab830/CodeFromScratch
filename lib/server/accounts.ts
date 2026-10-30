import 'server-only';
import {createHash,randomBytes} from 'node:crypto';
import {hash,compare} from 'bcryptjs';
import {ObjectId,type Document} from 'mongodb';
import {database,withDatabaseScope} from './database';
import {LEVELS} from '../levels';
import {DEFAULT_AVATAR,validAvatar,validSiteTheme,siteThemeFrom} from '../avatars';
import type {AccountUser,SavedLevel,Preferences} from '../account-types';

const COOKIE='cfs_session',SESSION_SECONDS=60*60*24*30;
const digest=(text:string)=>createHash('sha256').update(text).digest('hex');
const admin=(user:Document)=>user.role==='admin';
class ApiError extends Error{constructor(public status:number,message:string){super(message)}}
function userDto(user:Document):AccountUser{
  const avatar=validAvatar(user.avatar)?user.avatar:DEFAULT_AVATAR;
  const siteTheme=siteThemeFrom(user.preferences?.siteTheme,avatar);
  return {id:String(user._id),name:user.name,email:user.email,avatar:{...avatar,palette:siteTheme},role:admin(user)?'admin':'student',createdAt:user.createdAt.toISOString(),lastLoginAt:user.lastLoginAt.toISOString(),preferences:{...user.preferences,siteTheme,editorTheme:user.preferences?.editorTheme==='light'?'light':'dark'}};
}
function progressDto(row:Document):SavedLevel{return {levelId:row.levelId,completed:!!row.completed,coins:[...(row.coins??[])].sort(),...(typeof row.code==='string'?{code:row.code,codeVersion:row.codeVersion}:{}),hint:row.hint??-1,attempts:row.attemptIds?.length??0,updatedAt:row.updatedAt.toISOString(),...(row.completedAt?{completedAt:row.completedAt.toISOString()}: {})}}
function json(data:unknown,status=200){return Response.json(data,{status,headers:{'Cache-Control':'private, no-store','X-Content-Type-Options':'nosniff'}})}
function cookie(token:string,request:Request,clear=false){return `${COOKIE}=${token}; Path=/; HttpOnly; SameSite=Lax; Max-Age=${clear?0:SESSION_SECONDS}${new URL(request.url).protocol==='https:'?'; Secure':''}`}
function tokenFrom(request:Request){const raw=request.headers.get('cookie')?.split(';').map(v=>v.trim()).find(v=>v.startsWith(COOKIE+'='))?.slice(COOKIE.length+1);return raw&&/^[\w-]{43}$/.test(raw)?raw:null}
async function currentUser(request:Request){const token=tokenFrom(request);if(!token)return null;const db=await database();const session=await db.collection('sessions').findOne({_id:digest(token) as never,expiresAt:{$gt:new Date()}});return session?db.collection('users').findOne({_id:session.userId}):null}
async function requireUser(request:Request){const user=await currentUser(request);if(!user)throw new ApiError(401,'Please log in to continue.');return user}
async function progress(userId:ObjectId){return (await (await database()).collection('progress').find({userId}).toArray()).map(progressDto)}
async function input(request:Request){
  const protocol=(request.headers.get('x-forwarded-proto')??new URL(request.url).protocol.slice(0,-1)).split(',')[0].trim();
  const host=request.headers.get('host');
  const expected=process.env.APP_ORIGIN||(host?`${protocol}://${host}`:new URL(request.url).origin);
  if(!['http','https'].includes(protocol)||request.headers.get('origin')!==expected)throw new ApiError(403,'This request could not be verified. Refresh and try again.');
  if(!request.headers.get('content-type')?.startsWith('application/json'))throw new ApiError(415,'Send this request as JSON.');
  const text=await request.text();if(Buffer.byteLength(text)>20000)throw new ApiError(413,'This update is too large.');
  try{const body=JSON.parse(text);if(!body||typeof body!=='object'||Array.isArray(body))throw Error();return body as Record<string,unknown>}catch{throw new ApiError(400,'The request could not be read.')}
}
function emailFrom(value:unknown){if(typeof value!=='string'||value.length>254||!/^\S+@\S+\.\S+$/.test(value.trim()))throw new ApiError(400,'Enter a valid email address.');return value.trim().toLowerCase()}
function nameFrom(value:unknown){if(typeof value!=='string'||value.trim().length<2||value.trim().length>50)throw new ApiError(400,'Your name needs 2–50 characters.');return value.trim()}
function passwordFrom(value:unknown){if(typeof value!=='string'||value.length<10||Buffer.byteLength(value)>72)throw new ApiError(400,'Use a password of at least 10 characters and no more than 72 bytes.');return value}
async function limit(request:Request,email:string,action:string){
  const db=await database(),bucket=Math.floor(Date.now()/900000);
  const ip=request.headers.get('x-forwarded-for')?.split(',')[0]?.trim()||'unknown';
  for(const [key,max] of [[`${action}:email:${email}`,10],[`${action}:ip:${ip}`,300]] as const){
    const row=await db.collection('auth_limits').findOneAndUpdate({_id:digest(key+':'+bucket) as never},{$inc:{count:1},$setOnInsert:{expiresAt:new Date((bucket+2)*900000)}},{upsert:true,returnDocument:'after'});
    if((row?.count??0)>max)throw new ApiError(429,'Too many attempts. Please try again in 15 minutes.');
  }
}
async function issueSession(user:Document,request:Request){
  const db=await database(),token=randomBytes(32).toString('base64url');
  const old=tokenFrom(request);if(old)await db.collection('sessions').deleteOne({_id:digest(old) as never});
  await db.collection('sessions').insertOne({_id:digest(token) as never,userId:user._id,createdAt:new Date(),expiresAt:new Date(Date.now()+SESSION_SECONDS*1000)});
  const response=json({user:userDto(user),progress:await progress(user._id)});response.headers.set('Set-Cookie',cookie(token,request));return response;
}
function preferencesFrom(value:unknown):Partial<Preferences>{
  if(!value||typeof value!=='object'||Array.isArray(value))throw new ApiError(400,'Choose valid preferences.');
  const raw=value as Record<string,unknown>,result:Partial<Preferences>={};
  if(raw.siteTheme!==undefined){if(raw.siteTheme!=='dark'&&!validSiteTheme(raw.siteTheme))throw new ApiError(400,'Choose a valid website theme.');result.siteTheme=siteThemeFrom(raw.siteTheme)}
  if(raw.editorTheme!==undefined){if(raw.editorTheme!=='dark'&&raw.editorTheme!=='light')throw new ApiError(400,'Choose a valid code theme.');result.editorTheme=raw.editorTheme}
  if(raw.lastLevel!==undefined){if(typeof raw.lastLevel!=='string'||!LEVELS.some(l=>l.id===raw.lastLevel))throw new ApiError(400,'Choose a valid lesson.');result.lastLevel=raw.lastLevel}
  return result;
}
async function routeRequest(request:Request):Promise<Response>{
  try{
    const url=new URL(request.url),path=url.pathname.replace(/\/$/,''),method=request.method;
    if(path==='/api/session'&&method==='GET'){
      const user=await currentUser(request);return json({user:user?userDto(user):null,progress:user?await progress(user._id):[]});
    }
    if(path==='/api/auth/register'&&method==='POST'){
      const body=await input(request),email=emailFrom(body.email),name=nameFrom(body.name),password=passwordFrom(body.password);
      if(!validAvatar(body.avatar))throw new ApiError(400,'Choose one of the available avatars.');
      await limit(request,email,'register');const db=await database();
      const now=new Date(),user={_id:new ObjectId(),email,name,role:'student',passwordHash:await hash(password,12),avatar:body.avatar,createdAt:now,lastLoginAt:now,updatedAt:now,preferences:{siteTheme:body.avatar.palette,editorTheme:'dark'}};
      try{await db.collection('users').insertOne(user)}catch(error){if((error as {code?:number}).code===11000)throw new ApiError(409,'An account with that email already exists. Try logging in.');throw error}
      return issueSession(user,request);
    }
    if(path==='/api/auth/login'&&method==='POST'){
      const body=await input(request),email=emailFrom(body.email);
      if(typeof body.password!=='string'||Buffer.byteLength(body.password)>72)throw new ApiError(401,'Email or password is incorrect.');
      await limit(request,email,'login');const db=await database(),user=await db.collection('users').findOne({email});
      // Still perform an expensive comparison for an unknown account.
      const dummy='$2b$12$R9h/cIPz0gi.URNNX3kh2OPST9/PgBkqquzi.Ss7KIUgO2t0jWMUW';
      const correct=await compare(body.password,user?.passwordHash??dummy);
      if(!user||!correct)throw new ApiError(401,'Email or password is incorrect.');
      user.lastLoginAt=new Date();await db.collection('users').updateOne({_id:user._id},{$set:{lastLoginAt:user.lastLoginAt}});return issueSession(user,request);
    }
    if(path==='/api/auth/logout'&&method==='POST'){
      await input(request);const token=tokenFrom(request);if(token)await (await database()).collection('sessions').deleteOne({_id:digest(token) as never});
      const response=json({ok:true});response.headers.set('Set-Cookie',cookie('',request,true));return response;
    }
    if(path==='/api/profile'&&method==='PATCH'){
      const body=await input(request),user=await requireUser(request);
      if(body.accountId!==String(user._id))throw new ApiError(409,'Your account changed. Reload before saving.');
      const changes:Document={updatedAt:new Date()};
      if(body.name!==undefined)changes.name=nameFrom(body.name);
      if(body.avatar!==undefined){if(!validAvatar(body.avatar))throw new ApiError(400,'Choose a valid avatar.');changes.avatar=body.avatar}
      if(body.preferences!==undefined)for(const [key,value] of Object.entries(preferencesFrom(body.preferences)))changes['preferences.'+key]=value;
      // One palette controls both the website and the profile icon, in one write.
      if(changes.avatar)changes['preferences.siteTheme']=changes.avatar.palette;
      else if(changes['preferences.siteTheme']){
        if(validAvatar(user.avatar))changes['avatar.palette']=changes['preferences.siteTheme'];
        else changes.avatar={...DEFAULT_AVATAR,palette:changes['preferences.siteTheme']};
      }
      const updated=await (await database()).collection('users').findOneAndUpdate({_id:user._id},{$set:changes},{returnDocument:'after'});return json({user:userDto(updated!)});
    }
    if(path.startsWith('/api/progress/')&&method==='PATCH'){
      const body=await input(request),user=await requireUser(request),levelId=path.slice('/api/progress/'.length),level=LEVELS.find(l=>l.id===levelId);
      if(!level)throw new ApiError(404,'This lesson does not exist.');
      if(body.accountId!==String(user._id))throw new ApiError(409,'Your account changed. Reload before saving.');
      const changes:Document={updatedAt:new Date()},add:Document={};
      if(body.completed!==undefined){if(typeof body.completed!=='boolean')throw new ApiError(400,'Invalid completion.');if(body.completed){changes.completed=true}}
      if(body.coins!==undefined){if(!Array.isArray(body.coins)||body.coins.length>level.coins.length||body.coins.some(c=>typeof c!=='string'||!level.coins.includes(c)))throw new ApiError(400,'Invalid coins for this lesson.');add.coins={$each:body.coins}}
      if(body.code!==undefined){if(typeof body.code!=='string'||body.code.length>8000||body.code.includes('# EDIT END'))throw new ApiError(400,'Keep your code within the editable section and under 8,000 characters.');if(body.codeVersion!==(level.codeVersion??0))throw new ApiError(409,'This lesson was updated. Reload before saving your code.');changes.code=body.code;changes.codeVersion=body.codeVersion}
      if(body.hint!==undefined){if(!Number.isInteger(body.hint)||(body.hint as number)<-1||(body.hint as number)>2)throw new ApiError(400,'Invalid hint.');changes.hint=body.hint}
      if(body.attemptIds!==undefined){if(!Array.isArray(body.attemptIds)||body.attemptIds.length>50||body.attemptIds.some(v=>typeof v!=='string'||!/^[a-f0-9-]{36}$/.test(v)))throw new ApiError(400,'Invalid attempt update.');add.attemptIds={$each:body.attemptIds}}
      const db=await database(),update:Document={$set:changes,$setOnInsert:{userId:user._id,levelId,createdAt:new Date()}};
      if(Object.keys(add).length)update.$addToSet=add;
      const saved=await db.collection('progress').findOneAndUpdate({userId:user._id,levelId},update,{upsert:true,returnDocument:'after'});
      if(body.completed)await db.collection('progress').updateOne({_id:saved!._id,completedAt:{$exists:false}},{$set:{completedAt:new Date()}});
      return json({progress:progressDto(saved!)});
    }
    if(path.startsWith('/api/admin/')&&method==='GET'){
      const user=await requireUser(request);if(!admin(user))throw new ApiError(403,'Admin access is required.');
      const db=await database();
      if(path==='/api/admin/users'){
        const query=(url.searchParams.get('q')??'').slice(0,80),page=Math.max(1,Math.min(100000,Math.trunc(Number(url.searchParams.get('page'))||1)));
        const filter=query?{$or:[{name:{$regex:query.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'),$options:'i'}},{email:{$regex:query.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'),$options:'i'}}]}:{};
        const [users,total,totalUsers]=await Promise.all([db.collection('users').find(filter,{projection:{passwordHash:0}}).sort({createdAt:-1}).skip((page-1)*20).limit(20).toArray(),db.collection('users').countDocuments(filter),db.collection('users').countDocuments()]);
        const rows=await Promise.all(users.map(async account=>{const saved=await progress(account._id);return {...userDto(account),completed:saved.filter(p=>p.completed).length,coins:saved.reduce((n,p)=>n+p.coins.length,0),attempts:saved.reduce((n,p)=>n+p.attempts,0)}}));
        return json({users:rows,total,totalUsers,page,pages:Math.ceil(total/20)});
      }
      const match=/^\/api\/admin\/users\/([a-f0-9]{24})$/.exec(path);
      if(match){const account=await db.collection('users').findOne({_id:new ObjectId(match[1])});if(!account)throw new ApiError(404,'This account was not found.');return json({user:userDto(account),progress:await progress(account._id)})}
    }
    return json({error:'This endpoint was not found.'},404);
  }catch(error){
    if(error instanceof ApiError)return json({error:error.message},error.status);
    console.error('Account request failed:',error instanceof Error?error.name:'UnknownError');
    return json({error:'Account saving is temporarily unavailable. Please try again shortly.'},503);
  }
}
export function handleAccountRequest(request:Request){return withDatabaseScope(()=>routeRequest(request))}
