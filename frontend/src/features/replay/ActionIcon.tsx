import type { Action } from '../../types'

// Small line icons so an action is never shown by colour alone.
export default function ActionIcon({ action, size = 22 }: { action: Action; size?: number }) {
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
  }
  switch (action) {
    case 'IRRIGATE':
      return (
        <svg {...common}>
          <path d="M12 3s-6 7.2-6 11a6 6 0 0 0 12 0c0-3.8-6-11-6-11z" fill="currentColor" stroke="none" />
        </svg>
      )
    case 'SKIP':
      return (
        <svg {...common}>
          <path d="M7 15a4.5 4.5 0 0 1-.6-8.96A5.5 5.5 0 0 1 17 7a4 4 0 0 1 .5 8" />
          <path d="M9 18l-1 2.5M13 18l-1 2.5M17 18l-1 2.5" />
        </svg>
      )
    case 'WAIT':
      return (
        <svg {...common}>
          <circle cx="12" cy="12" r="8.5" />
          <path d="M12 7.5V12l3 2" />
        </svg>
      )
    case 'HEAT_PROTECTION':
      return (
        <svg {...common}>
          <circle cx="12" cy="12" r="4" fill="currentColor" stroke="none" />
          <path d="M12 2.5v2.5M12 19v2.5M2.5 12H5M19 12h2.5M5.3 5.3l1.8 1.8M16.9 16.9l1.8 1.8M5.3 18.7l1.8-1.8M16.9 7.1l1.8-1.8" />
        </svg>
      )
  }
}
