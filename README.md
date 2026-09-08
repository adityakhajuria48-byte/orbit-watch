# Orbit Watch

Private satellite ground-track monitor with an adjustable 10–1,000 km radius (45 km default), device/manual coordinates, live CelesTrak active catalog and SGP4 propagation.

The site builds with npm run build. The tracker runs in a browser worker. Telegram background monitoring is a separate deployable Cloudflare service in alerts/; see alerts/README.md. It is not active until credentials, storage and scheduling are configured in the user’s Cloudflare account.

No bot credentials are embedded or stored in the site. The service access key remains in tab memory.

Satellite details include orbital elements, speed, observer-relative elevation and slant distance, and an interactive 10-minute forecast. Forecast samples do not imply guaranteed visibility or schedule notifications. See alerts/upgrade-radius.sql for upgrading older standalone alert databases.

## Map, profiles, favorites and Python passes

The world map renders all valid satellite subpoints and the selected satellite's next 90 minutes of ground track. Search the full catalog or open a curated mission profile. Verified descriptions currently cover ISS, Hubble and Landsat 9, with source links and review dates; other profiles explicitly report unverified metadata. Favorites are device-local.

`python/orbit_engine.py` computes passes in a separate browser worker using Pyodide and sgp4. It also runs under CPython; see `python/README.md`. No Python server is needed for the published timeline. Full-catalog calculations can take several minutes; featured or favorite selections are faster. The first calculation needs internet access to download the pinned Pyodide runtime.

Telegram API v3 supports selected NORAD IDs; apply the documented schema migration when upgrading an existing checker. Local favorites never alter the running alert service until saved. Alerts are still unconfigured for @PassPredictor_bot.

The catalog endpoint retains its last in-memory successful result for up to 24 hours during upstream failures and labels fallback data. Browser downloads have a 30-second timeout, exponential retry up to five-minute intervals, and reconnect recovery. Invalid/stale orbital records are excluded independently of download timestamps.

`npm run build` now includes an actual server-rendered homepage smoke test, preventing the initial null-data regression from passing the build. Python numerical tests: `python -m unittest discover -s python`.

## Setup

Requires Node.js 22.13 or later. Install with `npm ci`, then run `npm run build`. For local development run `npm run dev`.

The existing hosted website is https://orbit-watch-45.hffuh.chatgpt.site. Uploading this source to GitHub does not redeploy or stop that Site.

The satellite calculation is in `lib/orbit/core.js`; the browser worker is `public/tracker-worker.js`. The adjustable boundary is a 10–1,000 km ground-distance circle (45 km default).

## Telegram

The intended bot is **@PassPredictor_bot**. Alerts are not configured or enabled. Follow `alerts/README.md` to deploy the background checker and securely configure its bot token, verified private chat ID, and access key. Never commit these values.

## Focused observatory layout

Map, Passes, Satellites and Radar now use accessible persistent tabs. Changing views preserves prediction jobs and current selections. Location/radius controls sit beside the workspace on desktop and remain available through the overview shortcuts on mobile. Telegram configuration is collapsible. The map supports hover labels, keyboard panning/zoom, and pauses drawing when its tab is hidden. Catalog filtering is memoized; no new packages or fonts were added. Reduced-motion preferences disable decorative transitions.
