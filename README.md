# HoopRater — Deployment Guide

A Basketball-Reference-style NBA player rating app with 2K-style OVR scores.  
Built with Python (Flask) + nba_api. No database required.

---

## Project Structure

```
nba_rater/
├── app.py              # Flask routes + template helpers
├── rating_engine.py    # 2K-style OVR formula
├── data_fetcher.py     # nba_api wrapper + fallback sample data
├── requirements.txt
├── templates/
│   ├── index.html      # Homepage: top-rated player grid
│   ├── player.html     # Per-player detail page + attribute bars
│   └── compare.html    # Side-by-side comparison tool
└── static/
    ├── css/main.css
    └── js/
        ├── search.js   # Nav autocomplete
        └── compare.js  # Compare page logic
```

---

## Quick Start (Local Dev)

### 1. Clone / place the project folder

```bash
cd ~/Desktop
# (copy the nba_rater/ folder here)
```

### 2. Create a virtual environment

```bash
cd nba_rater
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
python app.py
```

Visit → **http://localhost:5000**

> **Note:** nba_api pulls from NBA.com. If the request is rate-limited or fails,
> the app automatically falls back to curated 2024-25 sample data so the site
> always works.

---

## Deployment Options

---

### Option A — Render.com (Free tier, recommended for beginners)

1. Push your project to a GitHub repo.
2. Go to [render.com](https://render.com) → **New Web Service** → connect your repo.
3. Set:
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
4. Click **Deploy**. Render gives you a public `https://` URL for free.

---

### Option B — Railway.app (free tier, one-click)

1. Install Railway CLI: `npm install -g @railway/cli`
2. In your project folder:
   ```bash
   railway login
   railway init
   railway up
   ```
3. Railway auto-detects Flask and deploys. You'll get a public URL instantly.

---

### Option C — Fly.io (Docker-based, free tier)

1. Install Flyctl: https://fly.io/docs/hands-on/install-flyctl/
2. In your project:
   ```bash
   fly launch          # creates fly.toml automatically
   fly deploy
   ```
3. Fly wraps your app in a Docker container. Works great with gunicorn.

---

### Option D — Local network / home server

Run on your home network so any device on your WiFi can access it:

```bash
# In app.py, change the last line to:
app.run(host="0.0.0.0", port=5000, debug=False)

# Then run:
python app.py
```

Find your machine's local IP (`ipconfig` on Windows, `ifconfig` on Mac/Linux),  
then visit `http://192.168.x.x:5000` from any device on the same network.

---

### Option E — VPS (DigitalOcean Droplet, Linode, etc.)

```bash
# On the server:
git clone <your-repo>
cd nba_rater
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Run with gunicorn (production WSGI server):
gunicorn -w 2 -b 0.0.0.0:8000 app:app

# Optional: set up Nginx as a reverse proxy on port 80
```

---

## Customizing the Rating Formula

All rating logic lives in `rating_engine.py`.

- **Adjust category weights** in `compute_rating()`:
  ```python
  composite = (
      0.35 * scoring_raw +      # ← change these
      0.20 * playmaking_raw +
      0.15 * rebounding_raw +
      0.20 * defense_raw +
      0.10 * impact_raw
  ) * 100
  ```

- **Adjust league averages** (update each season):
  ```python
  LEAGUE_AVGS = {
      "pts": 12.5,   # league average points per game
      "ts_pct": 0.575,
      ...
  }
  ```

- **Add more players to the fallback list** in `data_fetcher.py`  
  under `SAMPLE_PLAYERS` — just follow the existing format.

---

## Adding Real-Time nba_api Data

The app already uses nba_api. If you want to ensure it always pulls live data:

```python
# In data_fetcher.py, CURRENT_SEASON controls which season to pull:
CURRENT_SEASON = "2024-25"   # update each season
```

nba_api has rate limits — the code already adds a 0.6s delay between calls.
If you need to pre-cache data, consider running a nightly script:

```python
# cache_players.py (run via cron)
import json
from data_fetcher import SAMPLE_PLAYERS, fetch_player_stats

cache = {}
for p in SAMPLE_PLAYERS:
    stats = fetch_player_stats(p["id"])
    if stats:
        cache[p["id"]] = stats

with open("player_cache.json", "w") as f:
    json.dump(cache, f)
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `nba_api` returns empty / errors | NBA.com is rate-limiting; wait a minute and retry. App falls back to sample data. |
| Headshots not loading | NBA CDN blocks some IPs. Add a silhouette SVG at `static/img/silhouette.svg`. |
| Flask not found | Make sure your virtualenv is activated: `source venv/bin/activate` |
| Port 5000 in use | Change `port=5000` to `port=5001` in `app.py` |

---

## Tech Stack

- **Backend:** Python 3, Flask
- **Data:** nba_api (NBA.com Stats API wrapper)
- **Frontend:** Vanilla HTML/CSS/JS (no React/Node needed)
- **Fonts:** Barlow Condensed + IBM Plex Mono (Google Fonts)
- **Production server:** gunicorn
