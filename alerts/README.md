# Orbit Watch — Telegram background checker

This is the independent alert service for the Orbit Watch website. It is NOT deployed by publishing the website. Until this service is configured, deployed, tested, and enabled, no Telegram notifications are active.

## What you need

- A Cloudflare account with Workers, D1 and KV. The full active catalog can exceed free CPU quotas; this configuration requests 30 seconds CPU and may require a paid Workers plan. Check current pricing before enabling billing.
- Node.js 22+ and Python 3 for the optional private-chat helper.
- A dedicated Telegram bot created with @BotFather using /newbot. Open your new bot and send /start.
- The website's exact origin (scheme and hostname, with no trailing slash).

## Deploy once

Unzip the package, open a terminal in its `alerts` folder, and run:

```sh
npm install
npx wrangler login
npx wrangler d1 create orbit-alerts
npx wrangler kv namespace create CATALOG
```

Copy the returned database ID and KV namespace ID into `wrangler.jsonc`. Replace SITE_ORIGIN with your website origin. Do not put secrets in that file.

Create the database tables:

```sh
npx wrangler d1 execute orbit-alerts --remote --file=schema.sql
```

Find YOUR private Telegram chat:

```sh
python3 find-chat.py
```

The helper prompts for the bot token without displaying or saving it. It lists recent private chats only. Match your own name and username; do not guess if more than one chat is present. Send /start again if it has been over 24 hours. It does not remove or replace a webhook; use a new dedicated bot.

Store the bot token and the verified private chat ID as Worker secrets using the interactive prompts:

```sh
npx wrangler secret put TELEGRAM_BOT_TOKEN
npx wrangler secret put TELEGRAM_CHAT_ID
npx wrangler secret put ACCESS_KEY
```

For ACCESS_KEY, use a password manager to generate a unique random secret of at least 32 characters. Keep it in your password manager. Never paste the bot token into the website or ChatGPT. The website needs only ACCESS_KEY, not the bot token.

```sh
npm run deploy
```

Copy the deployed HTTPS workers.dev origin. Cron changes can take several minutes to become active. If deployment requests a billing upgrade, review the cost before accepting.

## Connect and verify

1. Open your Orbit Watch website and set your location.
2. Enter the alert service origin and ACCESS_KEY, then Connect.
3. Click Save alert location. The 45 km radius is fixed.
4. Click Send me a Telegram test. Confirm it arrives in YOUR private chat.
5. Enable notifications. Wait until Last background check advances and the status says Background monitoring active.
6. Close the website: the scheduled service continues to run.

The service runs once per minute and computes predicted ground positions in a sliding window one minute before through one minute after each check. It refines close approaches between 5-second samples, including short grazing passes. Messages can arrive up to about a minute before or after closest approach, plus provider delays; this is not an exact-to-the-second alert service. A network outage, scheduling delay, or stale orbital data can lead to missed alerts. The live radar refreshes every 2 seconds independently of this service.

The monitored center stays fixed until you explicitly save another alert location. Closing the website does not update your location. Alerts are grouped (up to 12 satellites per message) and repeat notifications for the same satellite are suppressed for 10 minutes. Rare duplicate delivery can occur if Telegram accepts a message but its response is lost. Coverage is CelesTrak's public active catalog; objects with orbital epochs older than 7 days or failed propagation are excluded. Being inside the circle does not imply naked-eye visibility.

## Pause, privacy, and maintenance

Turn off Send pass notifications in the website to pause, or disable the Cron Trigger in Cloudflare. The bot token and chat ID are Worker secrets. Coordinates and delivery status are stored in D1; orbital data are cached in KV for 2 hours. No token or location is embedded in source or public assets. The service is single-user and protected by a bearer access key; CORS permits only your configured website origin.

If a Telegram credential or recipient changes, pause the service, update secrets, reset verified with `UPDATE settings SET verified=0,enabled=0 WHERE id=1`, and repeat the test before re-enabling. Rotate a leaked token with BotFather and replace the Worker secret. Review Cloudflare logs if the website shows a stale background check. The service exposes only /status, /settings and /test; its scheduler is a Cloudflare Cron Trigger, not a public unauthenticated URL.

## Sources

- CelesTrak GP data: https://celestrak.org/NORAD/documentation/gp-data-formats.php
- CelesTrak usage policy: https://celestrak.org/usage-policy.php
- satellite.js / SGP4: https://github.com/shashwatak/satellite-js
- Telegram Bot API: https://core.telegram.org/bots/api
- Cloudflare Cron Triggers: https://developers.cloudflare.com/workers/configuration/cron-triggers/
