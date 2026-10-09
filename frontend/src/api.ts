import type { FieldResponse, ReplayResponse } from './types'

// When VITE_API_BASE is unset the dashboard reads the mock files in public/mock,
// so the UI can be built and recorded before the backend is deployed.
const API_BASE = (import.meta.env.VITE_API_BASE as string | undefined)?.replace(/\/$/, '')

export const usingMocks = !API_BASE

async function getJson<T>(url: string): Promise<T> {
  const res = await fetch(url)
  if (!res.ok) throw new Error(`${res.status} ${res.statusText} for ${url}`)
  return (await res.json()) as T
}

export function fetchField(token: string): Promise<FieldResponse> {
  // Mock mode has a single demo field, whatever the token.
  if (!API_BASE) return getJson(`${import.meta.env.BASE_URL}mock/field-demo.json`)
  return getJson(`${API_BASE}/field/${encodeURIComponent(token)}`)
}

export function fetchReplay(): Promise<ReplayResponse> {
  if (!API_BASE) return getJson(`${import.meta.env.BASE_URL}mock/replay.json`)
  return getJson(`${API_BASE}/replay`)
}
