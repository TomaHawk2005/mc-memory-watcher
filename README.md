# Minecraft memory watcher

Restarts our BisectHosting Minecraft server when its RAM goes over 5.7 GB (the plan caps at 6 GB).
GitHub runs it about every 5 minutes for free, so nothing has to stay on at home.

## What's in here

- `watcher.py`: the bot. Checks RAM; if it's too high, warns players in chat, saves, and restarts.
- `.github/workflows/memory-watch.yml`: tells GitHub to run the bot every 5 minutes.

## The API key

The bot logs into the panel with an API key stored as the repo secret `BISECT_API_KEY`
(Settings > Secrets and variables > Actions). Never paste the key into the code.
If it ever leaks, delete it in the Starbase panel (Account > API Credentials) and make a new one.

## Settings

Change these in `.github/workflows/memory-watch.yml` (under `env:`):

- `MEMORY_LIMIT_GB`: when to restart (default 5.7)
- `MIN_UPTIME_MIN`: won't restart a server that started less than this many minutes ago (default 30)
- `WARNING_SECONDS`: how much warning players get in chat (default 60)

## Notes

- To test it: Actions tab > *Minecraft memory watcher* > **Run workflow**. The log shows the current RAM.
- GitHub pauses scheduled workflows after 60 days with no repo activity. If that happens, click "Enable workflow" in the Actions tab.
- The separate every-6-hours restart lives in the Starbase panel under Schedules.
