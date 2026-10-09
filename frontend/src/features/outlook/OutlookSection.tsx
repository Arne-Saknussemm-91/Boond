import type { OutlookDay, Today } from '../../types'

// STUB: owned by the "outlook + history" agent. Keep the default export and props.
export default function OutlookSection({ outlook }: { today: Today; outlook: OutlookDay[] }) {
  return (
    <section aria-labelledby="outlook-h">
      <h2 id="outlook-h">16-day outlook</h2>
      <p>{outlook.length} days</p>
    </section>
  )
}
