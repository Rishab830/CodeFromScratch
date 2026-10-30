'use client';
import {Gamepad2,ArrowRight} from 'lucide-react';
import {useAccount} from './AccountProvider';

export default function GuestChoice({stayHere=false}:{stayHere?:boolean}){
  const {user,playAsGuest}=useAccount();
  if(user)return null;
  return <div className="guest-choice"><button type="button" className="reset-button" onClick={()=>{playAsGuest();if(!stayHere)location.assign('/?guest=1')}}><Gamepad2 size={17}/> Play as guest <ArrowRight size={15}/></button><p>Guest progress stays on this device. Create an account to save across devices.</p></div>;
}
