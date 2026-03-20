import type { Metadata } from 'next'
import type { ReactNode } from 'react'
import './globals.css'
import { StatusBar } from '@/components/StatusBar'

export const metadata: Metadata = {
  title: 'DriftGuard',
  description: 'Infrastructure drift detection engine',
}

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="bg-drift-bg text-gray-100 min-h-screen">
        <header className="border-b border-drift-border bg-drift-surface">
          <div className="max-w-6xl mx-auto px-6 py-4 flex items-center gap-3">
            <div className="w-6 h-6 rounded bg-drift-green flex items-center justify-center">
              <span className="text-black text-xs font-black">D</span>
            </div>
            <span className="font-mono font-bold text-white">DriftGuard</span>
            <span className="text-drift-muted font-mono text-xs">v1.0</span>
          </div>
        </header>
        <StatusBar />
        <main className="max-w-6xl mx-auto px-6 py-8">
          {children}
        </main>
      </body>
    </html>
  )
}
