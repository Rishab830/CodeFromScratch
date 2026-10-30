import type { Metadata } from 'next';
import './globals.css';
import './accounts.css';
import './site-themes.css';
import './themes.css';
import {AccountProvider} from '../components/AccountProvider';
export const metadata: Metadata = {
  title: 'Code From Scratch · Learn, compile, play',
  description: 'Tiny bugs. Big adventures. Edit real Python, compile your changes, and play your way through pastel pixel worlds.'
};
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en" data-theme="lavender" suppressHydrationWarning><head><script dangerouslySetInnerHTML={{__html:"try{var t=localStorage.getItem('cfs:theme:active')||localStorage.getItem('cfs:theme:site');document.documentElement.dataset.theme=['lavender','mint','peach','ocean','candy','sunshine','light'].includes(t)?t:'lavender'}catch{}"}}/></head><body><AccountProvider>{children}</AccountProvider></body></html>;
}
