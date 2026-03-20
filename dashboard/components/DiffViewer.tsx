import { Snapshot } from '@/lib/api'

function ServiceRow({
  name, desired, actual
}: {
  name: string
  desired: any
  actual: any
}) {
  const drifted = JSON.stringify(desired) !== JSON.stringify(actual)

  return (
    <div className={`rounded border p-3 ${
      drifted ? 'border-red-500/20 bg-red-500/5' : 'border-drift-border'
    }`}>
      <div className="flex items-center gap-2 mb-2">
        <span className="text-xs font-mono font-bold text-white">{name}</span>
        {drifted
          ? <span className="text-xs text-drift-red font-mono">DRIFT</span>
          : <span className="text-xs text-drift-green font-mono">OK</span>
        }
      </div>
      {drifted && (
        <div className="grid grid-cols-2 gap-2 text-xs font-mono">
          <div className="bg-drift-bg rounded p-2">
            <div className="text-gray-600 mb-1">desired</div>
            <pre className="text-drift-green text-[10px] overflow-auto max-h-24 whitespace-pre-wrap">
              {JSON.stringify(desired, null, 2)}
            </pre>
          </div>
          <div className="bg-drift-bg rounded p-2">
            <div className="text-gray-600 mb-1">actual</div>
            <pre className="text-drift-red text-[10px] overflow-auto max-h-24 whitespace-pre-wrap">
              {JSON.stringify(actual, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  )
}

export function DiffViewer({ snapshot }: { snapshot: Snapshot }) {
  const allServices = new Set([
    ...Object.keys(snapshot.desired),
    ...Object.keys(snapshot.actual),
  ])

  return (
    <div className="space-y-2">
      {[...allServices].map(name => (
        <ServiceRow
          key={name}
          name={name}
          desired={snapshot.desired[name]}
          actual={snapshot.actual[name]}
        />
      ))}
    </div>
  )
}