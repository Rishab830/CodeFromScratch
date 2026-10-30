'use client';
import {Braces,ArrowLeft,ShieldCheck} from 'lucide-react';
import type {ReactNode} from 'react';
import {useAccount} from './AccountProvider';
import AccountNav from './AccountNav';
import ThemeSelector from './ThemeSelector';
export default function AccountShell({children}:{children:ReactNode}){
 const {user}=useAccount();
 return <div className="account-shell"><header className="site-header"><a className="brand" href="/" aria-label="Code From Scratch home"><span className="brand-icon"><Braces size={23}/></span><span>code<span className="brand-middle">from</span>scratch<span className="brand-period">.</span></span></a><nav aria-label="Account navigation"><a href="/">Workshop</a>{user?.role==='admin'&&<a href="/admin"><ShieldCheck size={15}/> Admin</a>}</nav><div className="profile"><ThemeSelector/><AccountNav/></div></header><main className="account-main"><a className="back-to-workshop" href="/"><ArrowLeft size={14}/> Back to the workshop</a>{children}</main><footer className="account-footer">Small steps. Big adventures. Code from scratch.</footer></div>;
}
