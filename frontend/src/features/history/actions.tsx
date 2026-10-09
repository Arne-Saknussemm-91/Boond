import type { Action, Lang } from '../../types'

// Action vocabulary for the history timeline. Same words, colours and icons as
// the Today hero; the lead will merge this with the Today agent's copy.

export const actionWord: Record<Action, Record<Lang, string>> = {
  IRRIGATE: { hi: 'पानी दें', en: 'Irrigate' },
  SKIP: { hi: 'आज पानी न दें', en: 'Skip today' },
  WAIT: { hi: 'अभी रुकें', en: 'Wait' },
  HEAT_PROTECTION: { hi: 'गर्मी से बचाव', en: 'Heat protection' },
}

export const actionColor: Record<Action, string> = {
  IRRIGATE: 'var(--action-irrigate)',
  SKIP: 'var(--action-skip)',
  WAIT: 'var(--action-wait)',
  HEAT_PROTECTION: 'var(--action-heat)',
}

export const actionTint: Record<Action, string> = {
  IRRIGATE: 'var(--nehar-tint)',
  SKIP: 'var(--ok-tint)',
  WAIT: 'var(--surface)',
  HEAT_PROTECTION: 'var(--loo-tint)',
}

const DROP = 'M12 3.2c0 0-6.2 7.3-6.2 11.1a6.2 6.2 0 0 0 12.4 0C18.2 10.5 12 3.2 12 3.2z'

export function ActionIcon({ action, size = 22 }: { action: Action; size?: number }) {
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
      return (
        <svg {...common}>
          <path d={DROP} fill="currentColor" stroke="none" />
        </svg>
      )
    case 'SKIP':
      return (
        <svg {...common}>
          <path d={DROP} />
          <path d="M4 4l16 16" />
        </svg>
      )
    case 'WAIT':
      return (
        <svg {...common}>
          <path d="M7 3.5h10M7 20.5h10M8 3.5c0 4.5 8 5.5 8 8.5s-8 4-8 8.5M16 3.5c0 4.5-8 5.5-8 8.5s8 4 8 8.5" />
        </svg>
      )
    case 'HEAT_PROTECTION':
      return (
        <svg {...common}>
          <circle cx="12" cy="12" r="4.2" fill="currentColor" stroke="none" />
          <path d="M12 2.5v2.6M12 18.9v2.6M2.5 12h2.6M18.9 12h2.6M5.3 5.3l1.8 1.8M16.9 16.9l1.8 1.8M5.3 18.7l1.8-1.8M16.9 7.1l1.8-1.8" />
        </svg>
      )
  }
}
