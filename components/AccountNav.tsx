'use client';
import {Cloud,CloudOff} from 'lucide-react';
import {useAccount} from './AccountProvider';
import PixelAvatar from './PixelAvatar';
import {DEFAULT_AVATAR} from '../lib/avatars';
export default function AccountNav(){const {user,syncState}=useAccount();return <><span className={'account-sync '+syncState} title={user?(syncState==='saved'?'Saved to your account':syncState==='offline'?'Offline. Changes are saved on this device until sync resumes.':'Saving your progress'):'Log in to save across devices'}>{syncState==='offline'?<CloudOff size={14}/>:<Cloud size={14}/>}</span>{!user&&<a href="/login" className="header-login">Log in</a>}<a href="/profile" className="avatar account-avatar" aria-label="Open profile" title={user?`${user.name} · Your profile`:'Your profile · Sign in to save'}><PixelAvatar avatar={user?.avatar??DEFAULT_AVATAR} size={36}/></a></>}
