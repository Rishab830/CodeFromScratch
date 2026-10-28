'use client';

import { Moon, Sun } from 'lucide-react';

export type Theme = 'dark' | 'light';

export default function ThemeSwitch({value,onChange,scope}: {
  value: Theme;
  onChange: (theme:Theme) => void;
  scope: 'website' | 'code editor';
}) {
  return <div className="theme-switch" role="group" aria-label={`${scope} theme`}>
    <span className="theme-switch-label">{scope === 'website' ? 'Site' : 'Code'}</span>
    <div className="theme-switch-options">
      <button type="button" aria-label={`Use dark ${scope} theme`} title={`Dark ${scope}`} aria-pressed={value === 'dark'} onClick={() => onChange('dark')}><Moon size={13}/></button>
      <button type="button" aria-label={`Use light ${scope} theme`} title={`Light ${scope}`} aria-pressed={value === 'light'} onClick={() => onChange('light')}><Sun size={13}/></button>
    </div>
  </div>;
}
