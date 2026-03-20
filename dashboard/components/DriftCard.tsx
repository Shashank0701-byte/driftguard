'use client'

import { useState } from 'react'
import { formatDistanceToNow } from 'date-fns'

import { api, DriftEvent } from '@/lib/api'
import { SeverityBadge } from './SeverityBadge'

export function DriftCard({ drift }: { drift: DriftEvent }) {
  const [reconciling, setReconciling] = useState(false)
  const [done, setDone] = useState(drift.resolved === 'true')

  async function handleReconcile() {
    setReconciling(true)
    try {
      await api.reconcile(drift.service)
      setDone(true)
    } finally {
      setReconciling(false)
    }
  }

  return (
    <div
      className={`rounded-lg border p-4 transition-all ${
        done
          ? 'border-drift-border opacity-50'
          : drift.severity === 'HIGH'
            ? 'border-red-500/30 bg-red-500/5'
            : drift.severity === 'MEDIUM'
              ? 'border-amber-500/30 bg-amber-500/5'
              : 'border-drift-border bg-drift-surface'
      }`}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          <div className="mb-2 flex items-center gap-2">
            <SeverityBadge severity={drift.severity} />
            <span className="font-mono text-xs text-gray-500">
              {formatDistanceToNow(new Date(drift.created_at), { addSuffix: true })}
            </span>
            {done && (
              <span className="font-mono text-xs text-drift-green">resolved</span>
            )}
          </div>

          <div className="mb-3 flex items-center gap-2">
            <span className="text-sm font-mono font-bold text-white">
              {drift.service}
            </span>
            <span className="text-drift-muted">/</span>
            <span className="text-sm font-mono text-gray-400">
              {drift.field}
            </span>
          </div>

          <div className="grid grid-cols-2 gap-2 text-xs font-mono">
            <div className="rounded border border-drift-border bg-drift-bg p-2">
              <div className="mb-1 text-gray-600">expected</div>
              <div className="truncate text-drift-green">
                {drift.expected ?? '-'}
              </div>
            </div>
            <div className="rounded border border-drift-border bg-drift-bg p-2">
              <div className="mb-1 text-gray-600">actual</div>
              <div className="truncate text-drift-red">
                {drift.actual ?? '-'}
              </div>
            </div>
          </div>
        </div>

        {!done && (
          <button
            onClick={handleReconcile}
            disabled={reconciling}
            className="shrink-0 rounded border border-drift-green/30 px-3 py-1.5 text-xs font-mono font-bold text-drift-green transition-all hover:bg-drift-green hover:text-black disabled:opacity-40"
          >
            {reconciling ? 'fixing...' : 'reconcile'}
          </button>
        )}
      </div>
    </div>
  )
}
