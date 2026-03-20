import { DriftCard } from '@/components/DriftCard'
import { DiffViewer } from '@/components/DiffViewer'
import { RiskMeter } from '@/components/RiskMeter'
import { serverApi } from '@/lib/server-api'

export const revalidate = 30

export default async function Home() {
  const [drifts, snapshot] = await Promise.all([
    serverApi.getDrifts().catch(() => []),
    serverApi.getLatestSnapshot().catch(() => null),
  ])

  const open = drifts.filter(d => d.resolved === 'false')
  const resolved = drifts.filter(d => d.resolved === 'true')
  const high = open.filter(d => d.severity === 'HIGH').length
  const medium = open.filter(d => d.severity === 'MEDIUM').length

  return (
    <div className="space-y-8">
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        {[
          { label: 'open drifts', value: open.length, color: open.length > 0 ? 'text-drift-red' : 'text-drift-green' },
          { label: 'high severity', value: high, color: high > 0 ? 'text-drift-red' : 'text-gray-400' },
          { label: 'medium', value: medium, color: medium > 0 ? 'text-drift-amber' : 'text-gray-400' },
          { label: 'resolved today', value: resolved.length, color: 'text-drift-green' },
        ].map(({ label, value, color }) => (
          <div key={label} className="rounded-lg border border-drift-border bg-drift-surface p-4">
            <div className="mb-1 font-mono text-xs text-gray-500">{label}</div>
            <div className={`text-3xl font-mono font-bold ${color}`}>{value}</div>
          </div>
        ))}
      </div>

      {snapshot && (
        <div className="rounded-lg border border-drift-border bg-drift-surface p-4">
          <RiskMeter score={snapshot.risk_score} />
        </div>
      )}

      <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
        <div>
          <h2 className="mb-4 text-sm font-mono font-bold uppercase tracking-wider text-gray-400">
            Active Drifts ({open.length})
          </h2>
          {open.length === 0 ? (
            <div className="rounded-lg border border-drift-border p-8 text-center">
              <div className="mb-1 text-sm font-mono text-drift-green">all clear</div>
              <div className="text-xs font-mono text-gray-600">
                No drift detected. Infrastructure matches source of truth.
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              {open.map(d => <DriftCard key={d.id} drift={d} />)}
            </div>
          )}
        </div>

        <div>
          <h2 className="mb-4 text-sm font-mono font-bold uppercase tracking-wider text-gray-400">
            Latest Snapshot
          </h2>
          {snapshot ? (
            <DiffViewer snapshot={snapshot} />
          ) : (
            <div className="rounded-lg border border-drift-border p-8 text-center">
              <div className="text-xs font-mono text-gray-600">
                No snapshot yet. Trigger a scan to begin.
              </div>
            </div>
          )}
        </div>
      </div>

      {resolved.length > 0 && (
        <div>
          <h2 className="mb-4 text-sm font-mono font-bold uppercase tracking-wider text-gray-400">
            Resolved ({resolved.length})
          </h2>
          <div className="space-y-2">
            {resolved.slice(0, 5).map(d => <DriftCard key={d.id} drift={d} />)}
          </div>
        </div>
      )}
    </div>
  )
}
