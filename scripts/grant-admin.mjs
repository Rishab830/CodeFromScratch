import {MongoClient} from 'mongodb';
const email=process.argv[2]?.trim().toLowerCase();
if(!process.env.MONGODB_URI||!email){console.error('Set MONGODB_URI and run npm run admin:grant -- your@email.com after creating your account.');process.exit(1)}
const client=new MongoClient(process.env.MONGODB_URI);
try{
 await client.connect();
 const result=await client.db(process.env.MONGODB_DB||'codefromscratch').collection('users').updateOne({email},{$set:{role:'admin',updatedAt:new Date()}});
 if(!result.matchedCount)throw new Error('No account has this email. Create your account first.');
 console.log('Admin access granted to the selected account. Log out and back in to refresh your profile.');
}catch(error){console.error(error.message==='No account has this email. Create your account first.'?error.message:'Admin setup could not connect. Check your server environment and Atlas access settings.');process.exitCode=1}finally{await client.close()}
