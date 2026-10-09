import { useEffect, useState } from 'react'
import Shell from './components/Shell'
import FieldPage from './pages/FieldPage'
import ReplayPage from './features/replay/ReplayPage'

// Hash routes keep Amplify static hosting simple (no rewrite rules needed).
//   #/f/<token>  one field's dashboard (the link the bot sends with /link)
//   #/replay     2021-22 validation replay
//   anything else -> the demo field
export type Route = { name: 'field'; token: string } | { name: 'replay' }

function parse(hash: string): Route {
  const path = hash.replace(/^#/, '')
  if (path.startsWith('/replay')) return { name: 'replay' }
  const m = path.match(/^\/f\/([^/?]+)/)
  return { name: 'field', token: m ? decodeURIComponent(m[1]) : 'demo' }
}

export default function App() {
  const [route, setRoute] = useState<Route>(() => parse(window.location.hash))
  useEffect(() => {
    const onHash = () => {
      setRoute(parse(window.location.hash))
      window.scrollTo(0, 0)
    }
    window.addEventListener('hashchange', onHash)
    return () => window.removeEventListener('hashchange', onHash)
  }, [])

  return <Shell route={route}>{route.name === 'replay' ? <ReplayPage /> : <FieldPage token={route.token} />}</Shell>
}
