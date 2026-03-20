const BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export type Severity = 'HIGH' | 'MEDIUM' | 'LOW'

export interface DriftEvent {
  id: number
  service: string
  field: string
  expected: string | null
  actual: string | null
  severity: Severity
  risk_score: number
  resolved: string
  created_at: string
}

export interface Snapshot {
  id: number
  desired: Record<string, any>
  actual: Record<string, any>
  drift_count: number
  risk_score: number
  created_at: string
}

export const api = {
  async triggerScan(): Promise<any> {
    const res = await fetch('/api/drifts/scan', { method: 'POST' })
    const data = await res.json()
    if (!res.ok) {
      throw new Error(data?.detail || data?.error || 'Failed to trigger scan')
    }
    return data
  },

  async reconcile(service: string, dryRun = false): Promise<any> {
    const res = await fetch(
      `/api/reconcile/${encodeURIComponent(service)}?dry_run=${dryRun}`,
      { method: 'POST' }
    )
    const data = await res.json()
    if (!res.ok) {
      throw new Error(data?.detail || data?.error || 'Failed to reconcile service')
    }
    return data
  },

  async getHealth(): Promise<any> {
    const res = await fetch(`${BASE}/health`)
    return res.json()
  }
}
