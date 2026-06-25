# FloraAI · Web

The frontend for FloraAI — a production-grade Next.js application that turns the
four backend services into one calm, premium product experience.

## Design language

"Organic Intelligence" — nature enhanced by technology. Built around a custom
design system (not default component-library styles):

- **Tokens** in `app/globals.css` + `tailwind.config.ts` — Deep Forest Green,
  Sage, Leaf, Warm Ivory; one editorial serif (Fraunces) for display, Geist Sans
  for UI, Geist Mono for figures.
- **Custom primitives** in `components/ui/` (Button, Card, Badge, Field, Meter,
  Spinner, Reveal) — composable, accessible, and tuned to the tokens.
- **Subtle motion** via Framer Motion (fade-up, animated meters) — improves
  rhythm, never distracts.

## Stack

Next.js 14 (App Router) · TypeScript · Tailwind CSS · Framer Motion · Recharts ·
Lucide icons. State is local React; the typed API client lives in `lib/api.ts`.

## Pages

| Route | Module | What it does |
|-------|--------|--------------|
| `/` | — | Landing: vision, the three modules, the unified flow |
| `/diagnose` | Gateway | **Flagship** — image + conditions + question → species + health + grounded advice |
| `/health` | ML | Conditions form → risk class, probabilities, SHAP drivers |
| `/vision` | DL | Image upload → species prediction with confidence + abstention |
| `/assistant` | Agent | Cited, grounded chat (Claude + local retrieval) |

## Run

```bash
npm install
npm run dev          # http://localhost:3000
```

The app talks to the FastAPI gateway via a same-origin Next.js rewrite
(`/gw/*` → `http://127.0.0.1:8000`), configured in `next.config.mjs` /
`.env.local`. Start the backend first (`make ml-serve`, `agent-serve`,
`gateway-serve`, …) or run `docker compose up`.

## Architecture notes

- **Single origin:** the browser only ever calls `/gw/*`; the gateway fans out to
  the model services. No CORS in production, one base URL to configure.
- **Typed contracts:** `lib/types.ts` mirrors the backend Pydantic schemas.
- **Honest states:** every async surface has explicit loading, empty, and error
  states; low-confidence vision results are surfaced, not hidden.
