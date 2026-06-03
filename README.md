# YKI Exam Sessions Dashboard

A single-page dashboard for browsing **YKI** (Yleinen kielitutkinto — the Finnish
National Certificate of Language Proficiency) exam sessions, with a tiny Python
proxy that fetches the official API and serves the page.

Live: <https://yki.asad.dev>

## What's here

| File | Purpose |
| --- | --- |
| `yki_dashboard.html` | The dashboard — editorial "schedule board" UI, filtering, sorting, and shareable filter state via URL query params. No build step, no dependencies. |
| `yki_proxy.py` | Stdlib-only HTTP server. Serves the HTML and proxies `GET /api/exam-session` to the YKI API (works around browser CORS). |

## Features

- **Filter** by level, language, date, and city; free-text search by venue/city.
- **Restricted to Finnish & Swedish** sessions.
- **Sort** by date, free spots, or how full a session is.
- **Toggles** for "open only" and "has spots".
- **Shareable links** — the active filters are encoded in the URL, so a
  pre-filtered view can be sent to someone, e.g.
  `?level=KESKI&lang=swe&open=0`.
- Animated stat counters, staggered card reveals, paper-grain styling.

## Endpoints

The proxy serves two things and nothing else.

| Path | Serves |
| --- | --- |
| `GET /` | `yki_dashboard.html`, unchanged |
| `GET /api/exam-session` | passthrough of `https://yki.opintopolku.fi/yki/api/exam-session` |

The upstream call needs a `Caller-Id` header and a matching `CSRF` header and cookie, none of which
a browser can set cross-origin, which is the real reason this proxy exists. The values in
`yki_proxy.py` are the ones the public registration page sends; they identify the caller, they do
not grant anything.

## Run locally

```bash
python3 yki_proxy.py 8080
# then open http://localhost:8080
```

The port defaults to `8080`; pass another as the first argument.

### Browser-only fallback

If you open `yki_dashboard.html` directly (no proxy), the YKI API call is blocked
by CORS. The page detects this and shows a `curl` command — run it, paste the
JSON, and the dashboard loads from that.

## Deployment

In production this runs under PM2 (`pm2 start yki_proxy.py --name yki --interpreter python3 -- 3002`)
behind Caddy, which reverse-proxies `yki.asad.dev` to `localhost:3002`.
