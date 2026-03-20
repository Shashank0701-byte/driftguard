import { Severity } from '@/lib/api'
import clsx from 'clsx'

const config = {
  HIGH:   { label: 'HIGH',   cls: 'bg-red-500/10   text-red-400   border-red-500/20'   },
  MEDIUM: { label: 'MEDIUM', cls: 'bg-amber-500/10 text-amber-400 border-amber-500/20' },
  LOW:    { label: 'LOW',    cls: 'bg-blue-500/10  text-blue-400  border-blue-500/20'  },
}

export function SeverityBadge({ severity }: { severity: Severity }) {
  const { label, cls } = config[severity] ?? config.LOW
  return (
    <span className={clsx(
      'px-2 py-0.5 rounded text-xs font-mono font-bold border',
      cls
    )}>
      {label}
    </span>
  )
}