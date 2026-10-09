import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import type { Lang } from './types'

// Each feature keeps its own strings file shaped like { hi: {...}, en: {...} }
// and reads it with useStrings(strings). Hindi is the default (spec 9).

type Dict = Record<string, string>
export type Strings<T extends Dict> = { hi: T; en: T }

const LangContext = createContext<{ lang: Lang; setLang: (l: Lang) => void }>({
  lang: 'hi',
  setLang: () => {},
})

function initialLang(): Lang {
  const fromUrl = new URLSearchParams(window.location.search).get('lang')
  if (fromUrl === 'hi' || fromUrl === 'en') return fromUrl
  try {
    const saved = localStorage.getItem('boond.lang')
    if (saved === 'hi' || saved === 'en') return saved
  } catch {
    /* storage unavailable */
  }
  return 'hi'
}

export function LangProvider({ children }: { children: ReactNode }) {
  const [lang, setLang] = useState<Lang>(initialLang)
  useEffect(() => {
    document.documentElement.lang = lang
    try {
      localStorage.setItem('boond.lang', lang)
    } catch {
      /* storage unavailable */
    }
  }, [lang])
  return <LangContext.Provider value={{ lang, setLang }}>{children}</LangContext.Provider>
}

export function useLang() {
  return useContext(LangContext)
}

export function useStrings<T extends Dict>(strings: Strings<T>): T {
  return strings[useLang().lang]
}

// Fill "{name}" placeholders.
export function fill(template: string, values: Record<string, string | number>): string {
  return template.replace(/\{(\w+)\}/g, (_, k: string) => String(values[k] ?? `{${k}}`))
}
