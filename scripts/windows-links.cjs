// OpenNext creates directory links without a type. Windows junctions support
// the same build layout without requiring Developer Mode or elevation.
if(process.platform==='win32'){
 const fs=require('node:fs'),path=require('node:path'),original=fs.symlinkSync;
 fs.symlinkSync=function(target,destination,type){
   try{return original(target,destination,type)}catch(error){
     const resolved=path.resolve(path.dirname(destination),target);
     if(error.code==='EPERM'&&fs.statSync(resolved).isDirectory())return original(resolved,destination,'junction');
     throw error;
   }
 };
}
