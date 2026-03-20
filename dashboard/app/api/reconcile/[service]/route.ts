import { NextRequest, NextResponse } from 'next/server'

const BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const API_KEY = process.env.DRIFTGUARD_API_KEY

export async function POST(
  request: NextRequest,
  context: { params: Promise<{ service: string }> }
) {
  if (!API_KEY) {
    return NextResponse.json(
      { error: 'Dashboard server is missing DRIFTGUARD_API_KEY' },
      { status: 500 }
    )
  }

  const { service } = await context.params
  const dryRun = request.nextUrl.searchParams.get('dry_run') ?? 'false'

  const res = await fetch(
    `${BASE}/reconcile/${encodeURIComponent(service)}?dry_run=${dryRun}`,
    {
      method: 'POST',
      headers: {
        'X-API-Key': API_KEY,
      },
      cache: 'no-store',
    }
  )

  const data = await res.json()
  return NextResponse.json(data, { status: res.status })
}
