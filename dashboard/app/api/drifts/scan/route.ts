import { NextResponse } from 'next/server'

const BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const API_KEY = process.env.DRIFTGUARD_API_KEY

export async function POST() {
  if (!API_KEY) {
    return NextResponse.json(
      { error: 'Dashboard server is missing DRIFTGUARD_API_KEY' },
      { status: 500 }
    )
  }

  try {
    const res = await fetch(`${BASE}/drifts/scan`, {
      method: 'POST',
      headers: {
        'X-API-Key': API_KEY,
      },
      cache: 'no-store',
    })

    const raw = await res.text()
    let data: unknown

    try {
      data = raw ? JSON.parse(raw) : {}
    } catch {
      data = { error: raw || 'Backend returned a non-JSON response' }
    }

    return NextResponse.json(data, { status: res.status })
  } catch (error) {
    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : 'Failed to reach backend API',
      },
      { status: 500 }
    )
  }
}
