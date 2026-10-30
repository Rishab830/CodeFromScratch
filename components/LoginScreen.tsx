'use client';
import {useState,type FormEvent} from 'react';
import {ArrowRight,KeyRound,Sparkles} from 'lucide-react';
import {useAccount} from './AccountProvider';
import AccountShell from './AccountShell';
import PixelAvatar from './PixelAvatar';
import GuestChoice from './GuestChoice';

function destination(){const next=new URLSearchParams(location.search).get('next');return next&&['/','/profile','/admin'].includes(next)?next:'/'}
export default function LoginScreen({firstVisit=false}:{firstVisit?:boolean}){
 const {login,user,ready}=useAccount();
 const [email,setEmail]=useState(''),[password,setPassword]=useState(''),[error,setError]=useState(''),[busy,setBusy]=useState(false);
 async function submit(event:FormEvent){event.preventDefault();setBusy(true);setError('');try{await login(email,password);if(!firstVisit)location.assign(destination())}catch(e){setError((e as Error).message);setBusy(false)}}
 return <AccountShell showBackLink={!firstVisit}><div className="auth-layout"><section className="account-card auth-form-card"><span className="account-eyebrow"><KeyRound size={14}/>{firstVisit?'LITTLE BUGS. BIG ADVENTURES.':'PICK UP WHERE YOU LEFT OFF'}</span><h1>{firstVisit?<>Code. Fix.<br/>Play.</>:<>Welcome back,<br/>adventurer.</>}</h1><p>{firstVisit?'Create an account to save your adventures, log in to continue, or jump in as a guest.':'Your code, coins, and next little breakthrough are waiting.'}</p>{ready&&user?<div className="signed-in-note"><p>You’re logged in as {user.name}.</p><a className="compile-button" href="/">Continue playing <ArrowRight size={16}/></a></div>:<form onSubmit={submit}><label>Email address<input type="email" autoComplete="email" value={email} onChange={e=>setEmail(e.target.value)} required maxLength={254}/></label><label>Password<input type="password" autoComplete="current-password" value={password} onChange={e=>setPassword(e.target.value)} required/></label>{error&&<p className="form-error" role="alert">{error}</p>}<button className="compile-button" disabled={busy||!ready}>{busy?'Logging in…':'Log in'}<ArrowRight size={16}/></button></form>}{!user&&<><div className="signup-choice"><span>New here?</span><a className="reset-button" href="/register">Create your account <ArrowRight size={15}/></a></div><GuestChoice stayHere={firstVisit}/></>}</section><aside className="auth-story"><div className="avatar-party"><PixelAvatar avatar={{design:'cat',palette:'peach'}} size={86}/><PixelAvatar avatar={{design:'robot',palette:'lavender'}} size={126}/><PixelAvatar avatar={{design:'frog',palette:'mint'}} size={86}/></div><span className="account-eyebrow"><Sparkles size={14}/> YOUR ADVENTURE GOES WITH YOU</span><h2>A new device.<br/>The same little hero.</h2><p>Keep your level progress, coin collection, and code drafts together in your account.</p><div className="auth-perks"><span>✦ Saved code</span><span>✦ Collected coins</span><span>✦ Your pixel persona</span></div></aside></div></AccountShell>;
}
