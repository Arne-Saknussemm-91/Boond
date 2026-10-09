import type { HistoryDay } from '../../types'

// STUB: owned by the "outlook + history" agent. Keep the default export and props.
export default function HistorySection({ history }: { history: HistoryDay[] }) {
  return (
    <section aria-labelledby="history-h">
      <h2 id="history-h">History</h2>
      <p>{history.length} days</p>
    </section>
  )
}
