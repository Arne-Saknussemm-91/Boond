# Boond dashboard

Mobile-first, Hindi-first, read-only dashboard for one field (Live Build Spec section 9). The bot's `/link` command opens `#/f/<token>`.

```bash
npm install
npm run dev          # http://localhost:5173
npm run build        # outputs dist/ for Amplify Hosting
```

## Data
- `.env` sets `VITE_API_BASE` to the live API (API Gateway, ap-southeast-2). `src/live.ts` adapts its responses to `src/types.ts`.
  - `POST /fields` (register page) returns `field_token`; the token is saved on the phone and the home screen opens that field.
  - `GET /fields/{token}` returns the profile, `state` and `latest_advice` (the engine's advice, null until the daily job runs).
- The demo tokens (`demo`, `irrigate`, `skip`, `wait`, `heat`, `waiting`) always read `public/mock/`: real 2021-22 Ludhiana weather run through a simplified FAO-56 wheat balance in `scripts/make_mocks.py`, PAU fixed schedule as the baseline, labelled as test fields. The replay page also reads the bundled file until the backend has `GET /replay`.
- The API's CORS must allow the page's origin (dev server `http://localhost:5173`, the Amplify URL, or `*`).

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
| `#/f/<token>` | A real field from the live API |
| `#/register` | Add a field (POST /fields) |
| `#/replay` | 2021-22 season replay: Boond vs PAU fixed schedule |

Add `?lang=en` for English. Design rules are in `DESIGN.md`.
