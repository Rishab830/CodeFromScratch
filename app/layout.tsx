import type { Metadata } from 'next';
import './globals.css';
export const metadata: Metadata = {
  title: 'Code From Scratch · Learn, compile, play',
  description: 'Tiny bugs. Big adventures. Edit real Python, compile your changes, and play your way through pastel pixel worlds.'
};
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
