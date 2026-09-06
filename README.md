# Orbit Watch

Private satellite ground-track monitor with a fixed 45 km radius, device/manual coordinates, live CelesTrak active catalog and SGP4 propagation.

The site builds with npm run build. The tracker runs in a browser worker. Telegram background monitoring is a separate deployable Cloudflare service in alerts/; see alerts/README.md. It is not active until credentials, storage and scheduling are configured in the user’s Cloudflare account.

No bot credentials are embedded or stored in the site. The service access key remains in tab memory.

## Setup

Requires Node.js 22.13 or later. Install with `npm ci`, then run `npm run build`. For local development run `npm run dev`.

The existing hosted website is https://orbit-watch-45.hffuh.chatgpt.site. Uploading this source to GitHub does not redeploy or stop that Site.

The satellite calculation is in `lib/orbit/core.js`; the browser worker is `public/tracker-worker.js`. The fixed boundary is a 45 km ground-distance circle.

## Telegram

The intended bot is **@PassPredictor_bot**. Alerts are not configured or enabled. Follow `alerts/README.md` to deploy the background checker and securely configure its bot token, verified private chat ID, and access key. Never commit these values.
