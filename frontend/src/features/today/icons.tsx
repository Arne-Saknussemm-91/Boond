import type { Action } from '../../types'

// One plain glyph per action, drawn on a 24 grid with currentColor.
// Paired with the action word, so colour is never the only signal.
export function ActionIcon({ action, size = 32 }: { action: Action; size?: number }) {
  const common = {
    width: size,
    height: size,
    viewBox: '0 0 24 24',
    fill: 'none',
    stroke: 'currentColor',
    strokeWidth: 2,
    strokeLinecap: 'round' as const,
    strokeLinejoin: 'round' as const,
    'aria-hidden': true,
    focusable: false,
  }
  switch (action) {
    case 'IRRIGATE':
      // a drop falling onto a furrow
      return (
        <svg {...common}>
          <path d="M12 2.5c0 0-5.5 6.3-5.5 10a5.5 5.5 0 0 0 11 0c0-3.7-5.5-10-5.5-10z" fill="currentColor" stroke="none" />
          <path d="M3 21.5h18" />
        </svg>
      )
    case 'SKIP':
      // cloud with rain
      return (
        <svg {...common}>
          <path d="M7 15.5a4 4 0 0 1-.6-8 5.5 5.5 0 0 1 10.6 1.3A3.4 3.4 0 0 1 17 15.5z" />
          <path d="M8 18.5l-1 2.5M12.5 18.5l-1 2.5M17 18.5l-1 2.5" />
        </svg>
      )
    case 'WAIT':
      // clock
      return (
        <svg {...common}>
          <circle cx="12" cy="12" r="9" />
          <path d="M12 7v5.2l3.4 2" />
        </svg>
      )
    case 'HEAT_PROTECTION':
      // sun with a thermometer
      return (
        <svg {...common}>
          <path d="M15 4.5v10.2a3.5 3.5 0 1 1-4 0V4.5a2 2 0 0 1 4 0z" />
          <path d="M13 11v5.5" strokeWidth={3} />
          <path d="M3.5 6.5h3M4.5 2.8l2 2M4.5 10.2l2-2" />
        </svg>
      )
  }
}

export function SpeakerIcon({ playing }: { playing: boolean }) {
  return (
    <svg width="26" height="26" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      {playing ? (
        <rect x="6" y="6" width="12" height="12" rx="1.5" fill="currentColor" />
      ) : (
        <>
          <path d="M3.5 9.5h3.5L12 5v14l-5-4.5H3.5z" fill="currentColor" />
          <path
            d="M15.5 9a4.2 4.2 0 0 1 0 6M18.3 6.3a8 8 0 0 1 0 11.4"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
          />
        </>
      )}
    </svg>
  )
}

export function CloudOffIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true" focusable="false">
      <path d="M7 17.5a4 4 0 0 1-.6-8 5.5 5.5 0 0 1 10.6 1.3A3.4 3.4 0 0 1 17 17.5z" />
      <path d="M12 9.5v3.5M12 15.6v.1" />
    </svg>
  )
}
