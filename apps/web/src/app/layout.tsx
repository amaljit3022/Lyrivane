import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'LyricFlow Studio | Automated Lyrical Video Generator',
  description: 'Let every word move with the music. Local-first automated lyrical video generator by Krittika Labs.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-background text-gray-100 min-h-screen flex flex-col">
        {children}
      </body>
    </html>
  );
}
