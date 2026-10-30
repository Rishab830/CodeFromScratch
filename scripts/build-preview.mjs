import fs from 'node:fs';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {pathToFileURL} from 'node:url';
const root=process.cwd(),dist=path.resolve(root,'dist');
if(path.dirname(dist)!==root)throw new Error('Preview output must stay inside this project.');
function run(args){const result=spawnSync(process.execPath,args,{cwd:root,stdio:'inherit',windowsHide:true});if(result.error)throw result.error;if(result.status!==0)process.exit(result.status??1)}
run(['--require','./scripts/windows-links.cjs','./node_modules/@opennextjs/cloudflare/dist/cli/index.js','build']);
// OpenNext copies .env files into this module. Keep private settings in the
// host's runtime bindings instead of embedding local credentials in the Worker.
const envModule=path.join(root,'.open-next','cloudflare','next-env.mjs');
const compiledEnv=await import(pathToFileURL(envModule).href);
fs.writeFileSync(envModule,['production','development','test'].map(mode=>{
  const publicEnv=Object.fromEntries(Object.entries(compiledEnv[mode]).filter(([key])=>key.startsWith('NEXT_PUBLIC_')));
  return `export const ${mode} = ${JSON.stringify(publicEnv)};\n`;
}).join(''));
fs.rmSync(dist,{recursive:true,force:true});
run(['./node_modules/wrangler/bin/wrangler.js','deploy','--dry-run','--outdir','dist/server','--minify']);
fs.renameSync(path.join(dist,'server','worker.js'),path.join(dist,'server','index.js'));
fs.cpSync(path.join(root,'.open-next','assets'),path.join(dist,'client'),{recursive:true,dereference:true});
fs.mkdirSync(path.join(dist,'.openai'),{recursive:true});
fs.copyFileSync(path.join(root,'.openai','hosting.json'),path.join(dist,'.openai','hosting.json'));
fs.writeFileSync(path.join(dist,'server','wrangler.json'),JSON.stringify({name:'code-from-scratch',main:'index.js',compatibility_date:'2026-10-01',compatibility_flags:['nodejs_compat','global_fetch_strictly_public'],assets:{binding:'ASSETS',directory:'../client'}},null,2)+'\n');
console.log('Preview Worker and Pygame assets prepared in dist/.');
