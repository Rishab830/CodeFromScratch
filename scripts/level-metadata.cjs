// Read the app's lesson registry when packaging or checking games.
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const ts=require('typescript');
const code=ts.transpileModule(fs.readFileSync(path.join(__dirname,'..','lib','levels.ts'),'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS}}).outputText;
const context={exports:{}};vm.runInNewContext(code,context);
module.exports={levels:context.exports.LEVELS,core:context.exports.CORE_LEVELS,bonus:context.exports.BONUS_LEVELS};
if(require.main===module) process.stdout.write(JSON.stringify(module.exports.levels));
