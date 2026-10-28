import type { Metadata } from 'next';
import './globals.css';
import './themes.css';
export const metadata: Metadata = {
  title: 'Code From Scratch · Learn, compile, play',
  description: 'Tiny bugs. Big adventures. Edit real Python, compile your changes, and play your way through pastel pixel worlds.'
};
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en" data-theme="dark" suppressHydrationWarning><head><script dangerouslySetInnerHTML={{__html:"try{document.documentElement.dataset.theme=localStorage.getItem('cfs:theme:site')==='light'?'light':'dark'}catch{}"}}/></head><body>{children}</body></html>;
}
