"""
Minecraft memory watcher for a BisectHosting (Starbase / Pterodactyl) server.

Checks the server's RAM use. If it's over the limit, it warns players in chat,
saves the world, and restarts the server. Designed to run on a GitHub Actions
schedule (see .github/workflows/memory-watch.yml) but also works on any computer:

    BISECT_API_KEY=xxxx python watcher.py
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request

PANEL = os.environ.get("PANEL_URL", "https://games.bisecthosting.com")
SERVER_ID = os.environ.get("SERVER_ID", "41f2bcb2")
API_KEY = os.environ.get("BISECT_API_KEY", "")

# Your plan is 6 GB (6144 MB). Restarting a bit *before* the cap avoids the
# server getting killed for running out of memory mid-game.
LIMIT_GB = float(os.environ.get("MEMORY_LIMIT_GB", "5.7"))
# Don't restart again if the server came up less than this long ago.
MIN_UPTIME_MIN = int(os.environ.get("MIN_UPTIME_MIN", "30"))
WARNING_SECONDS = int(os.environ.get("WARNING_SECONDS", "60"))


def api(method, path, body=None):
    req = urllib.request.Request(
        f"{PANEL}/api/client/servers/{SERVER_ID}{path}",
        method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            # The panel's firewall blocks Python's default "Python-urllib" user agent.
            "User-Agent": "Mozilla/5.0 (mc-memory-watcher; +https://github.com/TomaHawk2005/mc-memory-watcher)",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")[:500]
        sys.exit(f"Panel returned HTTP {e.code} for {method} {path}: {body}")


def say(msg):
    api("POST", "/command", {"command": f"say {msg}"})


def main():
    if not API_KEY:
        sys.exit("BISECT_API_KEY is not set")

    stats = api("GET", "/resources")["attributes"]
    state = stats["current_state"]
    mem_gb = stats["resources"]["memory_bytes"] / 1024**3
    uptime_min = stats["resources"]["uptime"] / 60000  # uptime is in ms

    print(f"state={state} memory={mem_gb:.2f} GB uptime={uptime_min:.0f} min limit={LIMIT_GB} GB")

    if state != "running" or stats.get("is_sleeping"):
        print("Server isn't running, nothing to do.")
        return
    if mem_gb < LIMIT_GB:
        print("Memory OK.")
        return
    if uptime_min < MIN_UPTIME_MIN:
        print("Over the limit, but the server just started. Skipping this time.")
        return

    print("Memory too high, restarting.")
    say(f"Memory is high ({mem_gb:.1f} GB). Restarting in {WARNING_SECONDS} seconds!")
    time.sleep(max(WARNING_SECONDS - 10, 0))
    api("POST", "/command", {"command": "save-all"})
    time.sleep(10)
    api("POST", "/power", {"signal": "restart"})
    print("Restart sent.")


if __name__ == "__main__":
    main()
