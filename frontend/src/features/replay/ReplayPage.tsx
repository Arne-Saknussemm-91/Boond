import { fetchReplay } from '../../api'
import { useAsync } from '../../useAsync'
import { LoadError, Loading } from '../../components/LoadState'

// STUB: owned by the "replay" agent. Keep the default export (no props).
export default function ReplayPage() {
  const state = useAsync(fetchReplay, [])
  if (state.status === 'loading') return <Loading />
  if (state.status === 'error') return <LoadError error={state.error} />
  return (
    <section>
      <h1>2021–22 replay</h1>
      <p>{state.data.days.length} days</p>
    </section>
  )
}
