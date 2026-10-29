import 'server-only';
import {MongoClient,type Db} from 'mongodb';
import {AsyncLocalStorage} from 'node:async_hooks';
let connection:Promise<MongoClient>|undefined;
let indexes:Promise<void>|undefined;
let workerIndexesReady=false;
const scope=new AsyncLocalStorage<{client?:MongoClient;db?:Promise<Db>}>();
const isWorker=()=>typeof navigator!=='undefined'&&navigator.userAgent==='Cloudflare-Workers';
async function ensureIndexes(db:Db){await Promise.all([
  db.collection('users').createIndex({email:1},{unique:true}),
  db.collection('sessions').createIndex({expiresAt:1},{expireAfterSeconds:0}),
  db.collection('progress').createIndex({userId:1,levelId:1},{unique:true}),
  db.collection('auth_limits').createIndex({expiresAt:1},{expireAfterSeconds:0}),
])}
export function withDatabaseScope<T>(work:()=>Promise<T>):Promise<T>{
  if(!isWorker())return work();
  return scope.run({},async()=>{try{return await work()}finally{await scope.getStore()?.client?.close()}});
}
export async function database():Promise<Db>{
  const uri=process.env.MONGODB_URI;
  if(!uri)throw new Error('DATABASE_UNAVAILABLE');
  if(isWorker()){
    const state=scope.getStore();if(!state)throw new Error('DATABASE_SCOPE_REQUIRED');
    if(!state.db){state.client=new MongoClient(uri,{maxPoolSize:1,minPoolSize:0,serverSelectionTimeoutMS:8000});state.db=state.client.connect().then(async client=>{const db=client.db(process.env.MONGODB_DB||'codefromscratch');if(!workerIndexesReady){await ensureIndexes(db);workerIndexesReady=true}return db})}
    return state.db;
  }
  if(!connection){
    const client=new MongoClient(uri,{maxPoolSize:10,minPoolSize:0,maxIdleTimeMS:60000,serverSelectionTimeoutMS:8000});
    connection=client.connect().catch(error=>{connection=undefined;indexes=undefined;throw error});
  }
  const db=(await connection).db(process.env.MONGODB_DB||'codefromscratch');
  if(!indexes)indexes=ensureIndexes(db).catch(error=>{indexes=undefined;throw error});
  await indexes;return db;
}
