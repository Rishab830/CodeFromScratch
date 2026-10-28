import type { Metadata } from 'next';
import './globals.css';
export const metadata: Metadata = {
  title: 'CodeQuest · The Jumping Girl',
  description: 'A little bug. A big adventure. Learn Python by fixing a real Pygame game in your browser.'
};
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
