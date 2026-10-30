'use client';
import {AVATAR_PALETTES,type SiteTheme} from '../lib/avatars';
import {useAccount} from './AccountProvider';

export default function ThemeSelector(){
  const {siteTheme,savePreferences}=useAccount();
  const palette=AVATAR_PALETTES.find(p=>p.id===siteTheme)!;
  return <label className="site-theme-picker"><span className="theme-swatch" style={{background:palette.primary}} aria-hidden="true"/><span className="theme-picker-label">Theme</span><select aria-label="Website and avatar theme" value={siteTheme} onChange={event=>savePreferences({siteTheme:event.target.value as SiteTheme})}>{AVATAR_PALETTES.map(p=><option key={p.id} value={p.id}>{p.id==='light'?'Light · White & orange':p.name}</option>)}</select></label>;
}
