# Boond dashboard

Mobile-first, Hindi-first, read-only dashboard for one field (Live Build Spec section 9). The bot's `/link` command opens `#/f/<token>`.

```bash
npm install
npm run dev          # http://localhost:5173
npm run build        # outputs dist/ for Amplify Hosting
```

## Data
- With `VITE_API_BASE` unset, the app reads `public/mock/`. The mocks come from real 2021-22 Ludhiana weather (Open-Meteo archive) run through a simplified FAO-56 wheat balance in `scripts/make_mocks.py`, with the PAU fixed schedule as the baseline. They are test fields, labelled as such.
- With `VITE_API_BASE=https://<api-id>.execute-api.<region>.amazonaws.com/prod`, it calls `GET /field/{token}` and `GET /replay`. Response shapes are in `src/types.ts`; the backend must match them.

Regenerate and check the mocks (offline, uses the cached weather):
```bash
python3 -I scripts/make_mocks.py
python3 -I scripts/validate_mocks.py
```

## Routes
| Route | Shows |
|---|---|
| `#/f/demo` | Heat protection day (27 Mar 2022) |
| `#/f/irrigate`, `#/f/skip`, `#/f/wait`, `#/f/heat` | One test field per action |
| `#/f/waiting` | Field not sown yet |
| `#/replay` | 2021-22 season replay: Boond vs PAU fixed schedule |

Add `?lang=en` for English. Design rules are in `DESIGN.md`.
