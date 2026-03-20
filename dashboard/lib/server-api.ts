import 'server-only'

import type { DriftEvent, Snapshot } from '@/lib/api'

const BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const API_KEY = process.env.DRIFTGUARD_API_KEY

function authHeaders() {
  if (!API_KEY) {
    throw new Error('DRIFTGUARD_API_KEY is not set for the dashboard server')
  }

  return {
    'X-API-Key': API_KEY,
  }
}

export const serverApi = {
  async getDrifts(severity?: string): Promise<DriftEvent[]> {
    const url = severity ? `${BASE}/drifts/?severity=${severity}` : `${BASE}/drifts/`
    const res = await fetch(url, {
      headers: authHeaders(),
      next: { revalidate: 30 },
    })

    if (!res.ok) {
      throw new Error('Failed to fetch drifts')
    }

    return res.json()
  },

  async getLatestSnapshot(): Promise<Snapshot | null> {
    const res = await fetch(`${BASE}/drifts/latest-snapshot`, {
      headers: authHeaders(),
      next: { revalidate: 30 },
    })

    if (!res.ok) {
      return null
    }

    return res.json()
  },
}
