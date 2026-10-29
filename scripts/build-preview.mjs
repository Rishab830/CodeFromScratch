import fs from 'node:fs';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
const root=process.cwd(),dist=path.resolve(root,'dist');
if(path.dirname(dist)!==root)throw new Error('Preview output must stay inside this project.');
function run(args){const result=spawnSync(process.execPath,args,{cwd:root,stdio:'inherit',windowsHide:true});if(result.error)throw result.error;if(result.status!==0)process.exit(result.status??1)}
run(['--require','./scripts/windows-links.cjs','./node_modules/@opennextjs/cloudflare/dist/cli/index.js','build']);
fs.rmSync(dist,{recursive:true,force:true});
run(['./node_modules/wrangler/bin/wrangler.js','deploy','--dry-run','--outdir','dist/server','--minify']);
fs.renameSync(path.join(dist,'server','worker.js'),path.join(dist,'server','index.js'));
fs.cpSync(path.join(root,'.open-next','assets'),path.join(dist,'client'),{recursive:true,dereference:true});
fs.mkdirSync(path.join(dist,'.openai'),{recursive:true});
fs.copyFileSync(path.join(root,'.openai','hosting.json'),path.join(dist,'.openai','hosting.json'));
fs.writeFileSync(path.join(dist,'server','wrangler.json'),JSON.stringify({name:'code-from-scratch',main:'index.js',compatibility_date:'2026-10-01',compatibility_flags:['nodejs_compat','global_fetch_strictly_public'],assets:{binding:'ASSETS',directory:'../client'}},null,2)+'\n');
console.log('Preview Worker and Pygame assets prepared in dist/.');
