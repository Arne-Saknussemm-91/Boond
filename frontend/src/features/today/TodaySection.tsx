import type { FieldProfile, Today } from '../../types'

// STUB: owned by the "today" agent. Keep the default export and props.
export default function TodaySection({ field, today }: { field: FieldProfile; today: Today }) {
  return (
    <section aria-labelledby="today-h">
      <h1 id="today-h">{today.action}</h1>
      <p>
        {field.label}: {today.depth_mm} mm, wallet {today.water_wallet_pct}%
      </p>
    </section>
  )
}
