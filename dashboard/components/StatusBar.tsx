'use client'

import { useEffect, useState } from 'react'
import clsx from 'clsx'

import { api } from '@/lib/api'

export function StatusBar() {
  const [status, setStatus] = useState<'ok' | 'error' | 'loading'>('loading')
  const [scanning, setScanning] = useState(false)
  const [lastScan, setLastScan] = useState<string | null>(null)
  const [scanError, setScanError] = useState<string | null>(null)

  useEffect(() => {
    api.getHealth()
      .then(() => setStatus('ok'))
      .catch(() => setStatus('error'))
  }, [])

  async function handleScan() {
    setScanning(true)
    setScanError(null)
    try {
      await api.triggerScan()
      setLastScan(new Date().toLocaleTimeString())
    } catch (error) {
      setScanError(error instanceof Error ? error.message : 'Scan failed')
    } finally {
      setScanning(false)
      window.location.reload()
    }
  }

  return (
    <div className="border-b border-drift-border bg-drift-surface px-6 py-3">
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div
            className={clsx(
              'h-2 w-2 rounded-full',
              status === 'ok' && 'bg-drift-green animate-pulse-slow',
              status === 'error' && 'bg-drift-red',
              status === 'loading' && 'bg-drift-muted',
            )}
          />
          <span className="font-mono text-xs text-gray-400">
            API {status === 'ok' ? 'connected' : status === 'error' ? 'unreachable' : 'connecting...'}
          </span>
          {lastScan && (
            <span className="font-mono text-xs text-gray-600">
              last scan {lastScan}
            </span>
          )}
        </div>
        <button
          onClick={handleScan}
          disabled={scanning}
          className="rounded border border-drift-border px-3 py-1.5 text-xs font-mono font-bold text-gray-300 transition-colors hover:border-drift-green hover:text-drift-green disabled:opacity-40"
        >
          {scanning ? 'scanning...' : 'scan now'}
        </button>
      </div>
      {scanError && (
        <div className="mt-2 font-mono text-xs text-drift-red">
          {scanError}
        </div>
      )}
    </div>
  )
}
