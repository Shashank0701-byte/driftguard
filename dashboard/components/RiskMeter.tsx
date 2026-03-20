export function RiskMeter({ score, max = 50 }: { score: number; max?: number }) {
  const pct  = Math.min((score / max) * 100, 100)
  const color = pct > 66 ? '#EF4444' : pct > 33 ? '#F59E0B' : '#10B981'

  return (
    <div className="flex flex-col gap-1">
      <div className="flex justify-between text-xs font-mono text-gray-500">
        <span>risk score</span>
        <span style={{ color }} className="font-bold">{score}</span>
      </div>
      <div className="h-1.5 w-full bg-drift-border rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{ width: `${pct}%`, backgroundColor: color }}
        />
      </div>
    </div>
  )
}