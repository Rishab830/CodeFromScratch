'use client';
import {createContext,useContext,useEffect,useRef,useState,type ReactNode} from 'react';
import {LEVELS} from '../lib/levels';
import {siteThemeFrom,type Avatar,type SiteTheme} from '../lib/avatars';
import type {AccountUser,LevelPatch,Preferences,SavedLevel,SessionData} from '../lib/account-types';
type Job={revision:string;patch:LevelPatch&{preferences?:Partial<Preferences>}};
type Queue=Record<string,Job>;
declare global {interface Window {cfsReadCoins?:(runtimeId:number,accountId:string)=>string}}
type ContextValue={ready:boolean;user:AccountUser|null;guestMode:boolean;playAsGuest:()=>void;progress:SavedLevel[];syncState:string;siteTheme:SiteTheme;storageKey:(key:string)=>string;saveLevel:(id:string,patch:LevelPatch)=>void;savePreferences:(preferences:Partial<Preferences>)=>void;login:(email:string,password:string)=>Promise<void>;register:(name:string,email:string,password:string,avatar:Avatar,importGuest:boolean)=>Promise<void>;logout:()=>Promise<void>;updateProfile:(name:string,avatar:Avatar)=>Promise<void>;importGuest:()=>Promise<void>};
const AccountContext=createContext<ContextValue|null>(null);
const prefix=(user:AccountUser|null)=>user?`cfs:user:${user.id}:`:'';
function read<T>(key:string,fallback:T):T{try{const raw=localStorage.getItem(key);return raw===null?fallback:JSON.parse(raw)}catch{return fallback}}
function put(key:string,value:string){try{localStorage.setItem(key,value)}catch{}}
function remove(key:string){try{localStorage.removeItem(key)}catch{}}
const emptyLevel=(id:string):SavedLevel=>({levelId:id,completed:false,coins:[],attempts:0,updatedAt:new Date().toISOString()});
function mergeLevel(row:SavedLevel,patch:LevelPatch):SavedLevel{if(!Object.keys(patch).length)return row;return {...row,...(patch.code!==undefined?{code:patch.code,codeVersion:patch.codeVersion}:{}),...(patch.hint!==undefined?{hint:patch.hint}:{}),completed:row.completed||!!patch.completed,coins:Array.from(new Set([...row.coins,...patch.coins??[]])).sort(),attempts:row.attempts+(patch.attemptIds?.length??0),updatedAt:new Date().toISOString()}}
function cacheLevel(user:AccountUser|null,row:SavedLevel){
  const level=LEVELS.find(l=>l.id===row.levelId);if(!level)return;
  const scope=prefix(user);put(scope+level.storage+':snapshot',JSON.stringify(row));
  if(row.completed)put(scope+level.storage+':complete','yes');else remove(scope+level.storage+':complete');
  put(scope+`cfs:coins:level-${level.runtimeId}:v1`,JSON.stringify([...row.coins].sort()));
  if(row.code!==undefined&&row.codeVersion===(level.codeVersion??0))put(scope+level.storage+':body'+(level.codeVersion?':'+level.codeVersion:''),row.code);
  if(row.hint!==undefined)put(scope+level.storage+':hint',JSON.stringify(row.hint));
}
async function api<T>(path:string,method='GET',body?:unknown):Promise<T>{const response=await fetch(path,{method,credentials:'same-origin',cache:'no-store',headers:body?{'Content-Type':'application/json'}:undefined,body:body?JSON.stringify(body):undefined,keepalive:method==='PATCH'});const data=await response.json();if(!response.ok)throw new Error(data.error||'The request failed. Please try again.');return data}
export function AccountProvider({children}:{children:ReactNode}){
  const [ready,setReady]=useState(false),[user,setUser]=useState<AccountUser|null>(null),[progress,setProgress]=useState<SavedLevel[]>([]),[syncState,setSyncState]=useState('local');
  const [siteTheme,setSiteTheme]=useState<SiteTheme>('lavender');
  const [guestMode,setGuestMode]=useState(false);
  function playAsGuest(){setGuestMode(true);put('cfs:guest:chosen','yes')}
  function applyTheme(theme:SiteTheme){setSiteTheme(theme);document.documentElement.dataset.theme=theme;put('cfs:theme:active',theme)}
  const current=useRef<AccountUser|null>(null),queue=useRef<Queue>({}),memory=useRef<Record<string,SavedLevel>>({}),busy=useRef(false),timer=useRef<ReturnType<typeof setTimeout>|undefined>(undefined);
  const queueKey=(u:AccountUser)=>prefix(u)+'outbox';
  function publish(){setProgress(Object.values(memory.current))}
  function persist(){const u=current.current;if(u)put(queueKey(u),JSON.stringify(queue.current))}
  function schedule(){if(timer.current)clearTimeout(timer.current);timer.current=setTimeout(()=>{void flush()},600)}
  function enqueue(id:string,patch:Job['patch']){
    if(!current.current)return;
    const old=queue.current[id]?.patch??{};
    queue.current[id]={revision:crypto.randomUUID(),patch:{...old,...patch,...(old.coins||patch.coins?{coins:Array.from(new Set([...old.coins??[],...patch.coins??[]]))}:{}),...(old.attemptIds||patch.attemptIds?{attemptIds:Array.from(new Set([...old.attemptIds??[],...patch.attemptIds??[]]))}:{}),...(old.preferences||patch.preferences?{preferences:{...old.preferences,...patch.preferences}}:{})}};
    persist();setSyncState('saving');schedule();
  }
  async function flush(){
    const owner=current.current;if(!owner||busy.current)return;
    busy.current=true;
    try{
      while(current.current?.id===owner.id){
        const entry=Object.entries(queue.current)[0];if(!entry)break;
        const [id,job]=entry,patch={...job.patch};
        if(patch.attemptIds)patch.attemptIds=patch.attemptIds.slice(0,50);
        const result=await api<{user?:AccountUser;progress?:SavedLevel}>(id==='preferences'?'/api/profile':'/api/progress/'+encodeURIComponent(id),'PATCH',{accountId:owner.id,...patch});
        if(current.current?.id!==owner.id)return;
        const pending=queue.current[id],sentAttempts=new Set(patch.attemptIds??[]);
        if(pending?.revision===job.revision&&!(job.patch.attemptIds&&job.patch.attemptIds.length>50))delete queue.current[id];
        else if(pending?.patch.attemptIds){pending.patch.attemptIds=pending.patch.attemptIds.filter(v=>!sentAttempts.has(v));if(pending.revision===job.revision){pending.revision=crypto.randomUUID()}}
        if(result.progress){const row=mergeLevel(result.progress,queue.current[id]?.patch??{});memory.current[id]=row;cacheLevel(owner,row);publish()}
        persist();
      }
      if(current.current?.id===owner.id)setSyncState(Object.keys(queue.current).length?'saving':'saved');
    }catch{if(current.current?.id===owner.id){setSyncState('offline');timer.current=setTimeout(()=>{void flush()},15000)}}finally{busy.current=false;if(current.current?.id!==owner.id&&Object.keys(queue.current).length)schedule()}
  }
  function applySession(data:SessionData){
    current.current=data.user;setUser(data.user);memory.current={};queue.current=data.user?read<Queue>(queueKey(data.user),{}):{};
    if(!data.user){
      let theme:SiteTheme='lavender';try{theme=siteThemeFrom(localStorage.getItem('cfs:theme:site'))}catch{}applyTheme(theme);
      for(const level of LEVELS){
        const row=read<SavedLevel>(level.storage+':snapshot',emptyLevel(level.id));
        try{row.completed=localStorage.getItem(level.storage+':complete')==='yes';const code=localStorage.getItem(level.storage+':body'+(level.codeVersion?':'+level.codeVersion:''));if(code!==null){row.code=code;row.codeVersion=level.codeVersion??0}}catch{}
        const rawCoins=read<unknown>(`cfs:coins:level-${level.runtimeId}:v1`,[]);row.coins=Array.isArray(rawCoins)?rawCoins.filter(v=>typeof v==='string'&&level.coins.includes(v)):[];
        memory.current[level.id]=row;
      }
    }
    if(data.user){
      for(const level of LEVELS){const row=data.progress.find(p=>p.levelId===level.id)??emptyLevel(level.id);const merged=mergeLevel(row,queue.current[level.id]?.patch??{});memory.current[level.id]=merged;cacheLevel(data.user,merged)}
      const prefs={...data.user.preferences,...queue.current.preferences?.patch.preferences};
      prefs.siteTheme=siteThemeFrom(prefs.siteTheme,data.user.avatar);
      current.current={...data.user,avatar:{...data.user.avatar,palette:prefs.siteTheme},preferences:prefs};setUser(current.current);
      put(prefix(data.user)+'cfs:theme:site',prefs.siteTheme);put(prefix(data.user)+'cfs:theme:editor',prefs.editorTheme);applyTheme(prefs.siteTheme);
    }
    window.cfsReadCoins=(runtimeId,accountId)=>{if(accountId!==(current.current?.id??''))return '[]';const level=LEVELS.find(l=>l.runtimeId===runtimeId);return JSON.stringify([...(level?memory.current[level.id]?.coins??[]:[])].sort())};
    publish();setSyncState(data.user?(Object.keys(queue.current).length?'saving':'saved'):'local');setReady(true);if(data.user)schedule();
  }
  useEffect(()=>{
    let guest=new URLSearchParams(location.search).get('guest')==='1';
    try{guest=guest||localStorage.getItem('cfs:guest:chosen')==='yes'}catch{}
    if(guest)playAsGuest();
    let alive=true;api<SessionData>('/api/session').then(data=>{if(alive)applySession(data)}).catch(()=>{if(alive){applySession({user:null,progress:[]});setSyncState('offline')}});
    const online=()=>{void flush()},hidden=()=>{if(document.visibilityState==='hidden')void flush()};
    window.addEventListener('online',online);window.addEventListener('pagehide',online);document.addEventListener('visibilitychange',hidden);
    return()=>{alive=false;if(timer.current)clearTimeout(timer.current);window.removeEventListener('online',online);window.removeEventListener('pagehide',online);document.removeEventListener('visibilitychange',hidden)};
  },[]);
  function saveLevel(id:string,patch:LevelPatch){
    const level=LEVELS.find(l=>l.id===id);if(!level)return;
    const row=memory.current[id]??read<SavedLevel>(prefix(current.current)+level.storage+':snapshot',emptyLevel(id));
    const next=mergeLevel(row,patch);memory.current[id]=next;cacheLevel(current.current,next);publish();enqueue(id,patch);
  }
  function savePreferences(preferences:Partial<Preferences>){
    const owner=current.current;
    if(owner){const updated={...owner,avatar:preferences.siteTheme?{...owner.avatar,palette:preferences.siteTheme}:owner.avatar,preferences:{...owner.preferences,...preferences}};current.current=updated;setUser(updated);enqueue('preferences',{preferences})}
    if(preferences.siteTheme){put(prefix(owner)+'cfs:theme:site',preferences.siteTheme);applyTheme(preferences.siteTheme)}
    if(preferences.editorTheme)put(prefix(owner)+'cfs:theme:editor',preferences.editorTheme);
  }
  async function importGuest(){
    if(!current.current)return;
    for(const level of LEVELS){
      const codeKey=level.storage+':body'+(level.codeVersion?':'+level.codeVersion:''),patch:LevelPatch={};
      try{if(localStorage.getItem(level.storage+':complete')==='yes')patch.completed=true;const code=localStorage.getItem(codeKey);if(code){patch.code=code;patch.codeVersion=level.codeVersion??0}}catch{}
      const coins=read<unknown>(`cfs:coins:level-${level.runtimeId}:v1`,[]);if(Array.isArray(coins))patch.coins=coins.filter(c=>typeof c==='string'&&level.coins.includes(c));
      if(Object.keys(patch).length)saveLevel(level.id,patch);
    }
    await flush();
  }
  async function login(email:string,password:string){applySession(await api<SessionData>('/api/auth/login','POST',{email,password}))}
  async function register(name:string,email:string,password:string,avatar:Avatar,bringGuest:boolean){applySession(await api<SessionData>('/api/auth/register','POST',{name,email,password,avatar}));if(bringGuest)await importGuest()}
  async function logout(){await flush();await api('/api/auth/logout','POST',{});applySession({user:null,progress:[]})}
  async function updateProfile(name:string,avatar:Avatar){const owner=current.current;if(!owner)return;await flush();const result=await api<{user:AccountUser}>('/api/profile','PATCH',{accountId:owner.id,name,avatar});if(current.current?.id===owner.id){const updated={...result.user,preferences:{...result.user.preferences,...queue.current.preferences?.patch.preferences}};current.current=updated;setUser(updated);applyTheme(updated.preferences.siteTheme)}}
  return <AccountContext.Provider value={{ready,user,guestMode,playAsGuest,progress,syncState,siteTheme,storageKey:key=>prefix(user)+key,saveLevel,savePreferences,login,register,logout,updateProfile,importGuest}}>{children}</AccountContext.Provider>;
}
export function useAccount(){const value=useContext(AccountContext);if(!value)throw new Error('AccountProvider is required');return value}
