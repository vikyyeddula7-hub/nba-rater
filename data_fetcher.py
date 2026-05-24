"""
Data Fetcher
Official NBA 2K26 launch ratings (top 100) sourced from nba.2k.com / Operation Sports.
2025-26 season stats sourced from Basketball-Reference / NBA.com.
"""

import time
from typing import Optional

try:
    from nba_api.stats.endpoints import playercareerstats, commonplayerinfo, leagueleaders
    from nba_api.stats.static import players as nba_players_static
    NBA_API_AVAILABLE = True
except ImportError:
    NBA_API_AVAILABLE = False

CURRENT_SEASON = "2025-26"

# ── Official NBA 2K26 OVR lookup (name → ovr) ────────────────────────────────
# Source: nba.2k.com top-100 launch ratings + Operation Sports full list
NBA_2K26_RATINGS = {
    # 98
    "Nikola Jokić": 98, "Shai Gilgeous-Alexander": 98,
    # 97
    "Giannis Antetokounmpo": 97,
    # 95
    "Luka Dončić": 95, "Luka Doncic": 95, "Anthony Edwards": 95,
    # 94
    "Stephen Curry": 94, "LeBron James": 94, "Jayson Tatum": 94,
    "Victor Wembanyama": 94,
    # 93
    "Kevin Durant": 93, "Donovan Mitchell": 93, "Anthony Davis": 93,
    "Jalen Brunson": 93, "Tyrese Haliburton": 93,
    # 92
    "Kawhi Leonard": 92, "Cade Cunningham": 92, "Joel Embiid": 92,
    "Karl-Anthony Towns": 92,
    # 91
    "Ja Morant": 91, "Devin Booker": 91,
    # 90
    "Jalen Williams": 90, "Jaylen Brown": 90, "Trae Young": 90,
    "Kyrie Irving": 90,
    # 89
    "Paolo Banchero": 89, "Evan Mobley": 89, "Pascal Siakam": 89,
    "James Harden": 89, "Jaren Jackson Jr.": 89,
    # 88
    "Bam Adebayo": 88, "Chet Holmgren": 88, "Damian Lillard": 88,
    # 87
    "Domantas Sabonis": 87, "Alperen Şengün": 87, "Alperen Sengun": 87,
    "LaMelo Ball": 87, "Darius Garland": 87, "Zion Williamson": 87,
    "Ivica Zubac": 87, "Derrick White": 87, "Jimmy Butler": 87,
    "Amen Thompson": 87,
    # 86
    "Tyler Herro": 86, "Tyrese Maxey": 86, "Jamal Murray": 86,
    "Franz Wagner": 86,
    # 85
    "Julius Randle": 85, "Zach LaVine": 85, "De'Aaron Fox": 85,
    "Austin Reaves": 85, "DeMar DeRozan": 85, "Scottie Barnes": 85,
    "OG Anunoby": 85, "Kristaps Porzingis": 85, "Kristaps Porziņģis": 85,
    # 84
    "Lauri Markkanen": 84, "Brandon Ingram": 84, "Mikal Bridges": 84,
    "Rudy Gobert": 84, "Norman Powell": 84, "Jarrett Allen": 84,
    # 83
    "Jalen Green": 83, "Desmond Bane": 83, "Myles Turner": 83,
    "Cameron Johnson": 83, "Dyson Daniels": 83, "Coby White": 83,
    # 82
    "Aaron Gordon": 82, "John Collins": 82, "Josh Giddey": 82,
    "RJ Barrett": 82, "Michael Porter Jr.": 82, "Stephon Castle": 82,
    "Brandon Miller": 82, "Deni Avdija": 82, "Naz Reid": 82,
    "Nikola Vucevic": 82, "Nikola Vučević": 82, "Jalen Duren": 82,
    "Jalen Suggs": 82, "Trey Murphy III": 82, "Cooper Flagg": 82,
    "Isaiah Hartenstein": 82, "Jaden McDaniels": 82, "Toumani Camara": 82,
    "Walker Kessler": 82,
    # 81
    "Josh Hart": 81, "Luguentz Dort": 81, "Herbert Jones": 81,
    "Jrue Holiday": 81, "Dejounte Murray": 81, "CJ McCollum": 81,
    "Anfernee Simons": 81, "Draymond Green": 81, "Paul George": 81,
    "Onyeka Okongwu": 81, "Immanuel Quickley": 81, "Andrew Nembhard": 81,
    "Jalen Johnson": 81, "Alex Sarr": 81, "Aaron Nesmith": 81,
    "Shaedon Sharpe": 81, "Bobby Portis Jr.": 81, "Bobby Portis": 81,
}

def get_2k26_rating(name: str) -> Optional[int]:
    """Return official 2K26 OVR for a player name, or None if not in the database."""
    from teams_data import NBA_2K26
    return NBA_2K26.get(name)


# ── Curated 2025-26 season stats for the homepage ────────────────────────────
SAMPLE_PLAYERS = [
    {
        "id": 203999,  "name": "Nikola Jokić",            "team": "Denver Nuggets",
        "position": "C",  "age": 30,
        "pts": 28.6, "reb": 12.9, "ast": 11.1, "stl": 1.4, "blk": 0.8,
        "tov": 3.7,  "fga": 18.9, "fgm": 11.7, "fg_pct": 0.619,
        "fg3a": 3.1, "fg3m": 1.3, "fg3_pct": 0.419, "fta": 6.2, "ftm": 5.2,
        "ft_pct": 0.839, "min": 34.8, "gp": 65, "plus_minus": 9.8, "ts_pct": 0.672, "usg_pct": 29.5,
        "headshot_url": "https://cdn.nba.com/headshots/nba/latest/1040x760/203999.png",
    },
    {
        "id": 1628983, "name": "Shai Gilgeous-Alexander", "team": "Oklahoma City Thunder",
        "position": "PG", "age": 27,
        "pts": 31.1, "reb": 5.5, "ast": 6.2, "stl": 2.1, "blk": 1.0,
        "tov": 2.6,  "fga": 21.8, "fgm": 11.1, "fg_pct": 0.509,
        "fg3a": 4.5, "fg3m": 1.6, "fg3_pct": 0.356, "fta": 9.5, "ftm": 8.4,
        "ft_pct": 0.884, "min": 34.6, "gp": 68, "plus_minus": 8.9, "ts_pct": 0.631, "usg_pct": 33.8,
        "headshot_url": "https://cdn.nba.com/headshots/nba/latest/1040x760/1628983.png",
    },
    {
        "id": 203507,  "name": "Giannis Antetokounmpo",   "team": "Milwaukee Bucks",
        "position": "PF", "age": 31,
        "pts": 31.8, "reb": 11.5, "ast": 6.1, "stl": 1.1, "blk": 1.2,
        "tov": 3.3,  "fga": 20.9, "fgm": 13.0, "fg_pct": 0.622,
        "fg3a": 1.4, "fg3m": 0.4, "fg3_pct": 0.286, "fta": 11.2, "ftm": 8.1,
        "ft_pct": 0.723, "min": 35.0, "gp": 70, "plus_minus": 7.1, "ts_pct": 0.638, "usg_pct": 34.2,
        "headshot_url": "https://cdn.nba.com/headshots/nba/latest/1040x760/203507.png",
    },
    {
        "id": 1629029, "name": "Luka Dončić",             "team": "Los Angeles Lakers",
        "position": "PG", "age": 26,
        "pts": 33.5, "reb": 8.8, "ast": 9.4, "stl": 1.4, "blk": 0.5,
        "tov": 4.0,  "fga": 24.0, "fgm": 11.8, "fg_pct": 0.492,
        "fg3a": 8.2, "fg3m": 3.3, "fg3_pct": 0.402, "fta": 9.8, "ftm": 8.2,
        "ft_pct": 0.837, "min": 36.5, "gp": 64, "plus_minus": 5.8, "ts_pct": 0.609, "usg_pct": 36.5,
        "headshot_url": "https://cdn.nba.com/headshots/nba/latest/1040x760/1629029.png",
    },
    {
        "id": 1630162, "name": "Anthony Edwards",         "team": "Minnesota Timberwolves",
        "position": "SG", "age": 24,
        "pts": 29.6, "reb": 5.8, "ast": 5.9, "stl": 1.5, "blk": 0.6,
        "tov": 2.9,  "fga": 22.5, "fgm": 10.5, "fg_pct": 0.467,
        "fg3a": 8.1, "fg3m": 3.4, "fg3_pct": 0.420, "fta": 6.0, "ftm": 5.1,
        "ft_pct": 0.850, "min": 36.0, "gp": 76, "plus_minus": 5.2, "ts_pct": 0.582, "usg_pct": 33.5,
        "headshot_url": "https://cdn.nba.com/headshots/nba/latest/1040x760/1630162.png",
    },
    {
        "id": 201939,  "name": "Stephen Curry",           "team": "Golden State Warriors",
        "position": "PG", "age": 37,
        "pts": 24.1, "reb": 4.6, "ast": 6.5, "stl": 1.3, "blk": 0.4,
        "tov": 2.8,  "fga": 18.4, "fgm": 8.4, "fg_pct": 0.457,
        "fg3a": 9.0, "fg3m": 3.8, "fg3_pct": 0.422, "fta": 4.5, "ftm": 4.0,
        "ft_pct": 0.889, "min": 33.5, "gp": 60, "plus_minus": 4.5, "ts_pct": 0.613, "usg_pct": 29.0,
        "headshot_url": "https://cdn.nba.com/headshots/nba/latest/1040x760/201939.png",
    },
    {
        "id": 2544,    "name": "LeBron James",            "team": "Los Angeles Lakers",
        "position": "SF", "age": 41,
        "pts": 23.5, "reb": 7.6, "ast": 8.8, "stl": 1.0, "blk": 0.5,
        "tov": 3.3,  "fga": 18.0, "fgm": 9.2, "fg_pct": 0.511,
        "fg3a": 4.5, "fg3m": 1.7, "fg3_pct": 0.378, "fta": 4.2, "ftm": 3.5,
        "ft_pct": 0.833, "min": 33.8, "gp": 67, "plus_minus": 3.8, "ts_pct": 0.601, "usg_pct": 28.0,
        "headshot_url": "https://cdn.nba.com/headshots/nba/latest/1040x760/2544.png",
    },
    {
        "id": 1628369, "name": "Jayson Tatum",            "team": "Boston Celtics",
        "position": "SF", "age": 27,
        "pts": 27.5, "reb": 8.6, "ast": 5.0, "stl": 1.1, "blk": 0.7,
        "tov": 2.9,  "fga": 21.2, "fgm": 10.3, "fg_pct": 0.486,
        "fg3a": 8.0, "fg3m": 3.4, "fg3_pct": 0.425, "fta": 5.0, "ftm": 4.2,
        "ft_pct": 0.840, "min": 36.0, "gp": 71, "plus_minus": 5.8, "ts_pct": 0.603, "usg_pct": 31.5,
        "headshot_url": "https://cdn.nba.com/headshots/nba/latest/1040x760/1628369.png",
    },
    {
        "id": 1641705, "name": "Victor Wembanyama",       "team": "San Antonio Spurs",
        "position": "C",  "age": 21,
        "pts": 30.9, "reb": 10.5, "ast": 4.0, "stl": 1.6, "blk": 3.6,
        "tov": 2.9,  "fga": 22.0, "fgm": 10.8, "fg_pct": 0.491,
        "fg3a": 7.0, "fg3m": 2.8, "fg3_pct": 0.400, "fta": 8.0, "ftm": 7.0,
        "ft_pct": 0.875, "min": 34.2, "gp": 73, "plus_minus": 4.1, "ts_pct": 0.617, "usg_pct": 33.0,
        "headshot_url": "https://cdn.nba.com/headshots/nba/latest/1040x760/1641705.png",
    },
    {
        "id": 201142,  "name": "Kevin Durant",            "team": "Houston Rockets",
        "position": "SF", "age": 36,
        "pts": 25.7, "reb": 6.7, "ast": 4.0, "stl": 0.8, "blk": 1.1,
        "tov": 3.0,  "fga": 18.8, "fgm": 10.0, "fg_pct": 0.532,
        "fg3a": 4.5, "fg3m": 1.9, "fg3_pct": 0.422, "fta": 5.0, "ftm": 4.6,
        "ft_pct": 0.920, "min": 35.5, "gp": 72, "plus_minus": 3.2, "ts_pct": 0.635, "usg_pct": 28.5,
        "headshot_url": "https://cdn.nba.com/headshots/nba/latest/1040x760/201142.png",
    },
    {
        "id": 1626164, "name": "Donovan Mitchell",        "team": "Cleveland Cavaliers",
        "position": "SG", "age": 28,
        "pts": 30.0, "reb": 4.5, "ast": 5.1, "stl": 1.5, "blk": 0.5,
        "tov": 2.6,  "fga": 22.5, "fgm": 10.9, "fg_pct": 0.485,
        "fg3a": 6.5, "fg3m": 2.6, "fg3_pct": 0.400, "fta": 7.3, "ftm": 6.3,
        "ft_pct": 0.863, "min": 34.5, "gp": 68, "plus_minus": 5.0, "ts_pct": 0.598, "usg_pct": 31.5,
        "headshot_url": "https://cdn.nba.com/headshots/nba/latest/1040x760/1626164.png",
    },
    {
        "id": 203076,  "name": "Anthony Davis",           "team": "Dallas Mavericks",
        "position": "C",  "age": 32,
        "pts": 24.8, "reb": 11.2, "ast": 3.2, "stl": 1.2, "blk": 2.0,
        "tov": 2.2,  "fga": 17.5, "fgm": 10.0, "fg_pct": 0.571,
        "fg3a": 1.5, "fg3m": 0.5, "fg3_pct": 0.333, "fta": 6.5, "ftm": 5.2,
        "ft_pct": 0.800, "min": 34.8, "gp": 65, "plus_minus": 4.5, "ts_pct": 0.622, "usg_pct": 27.0,
        "headshot_url": "https://cdn.nba.com/headshots/nba/latest/1040x760/203076.png",
    },
    {
        "id": 1628973, "name": "Jalen Brunson",           "team": "New York Knicks",
        "position": "PG", "age": 28,
        "pts": 26.8, "reb": 3.5, "ast": 7.0, "stl": 0.9, "blk": 0.3,
        "tov": 2.3,  "fga": 20.8, "fgm": 10.2, "fg_pct": 0.490,
        "fg3a": 5.8, "fg3m": 2.3, "fg3_pct": 0.397, "fta": 5.5, "ftm": 4.7,
        "ft_pct": 0.855, "min": 35.0, "gp": 72, "plus_minus": 4.8, "ts_pct": 0.591, "usg_pct": 30.5,
        "headshot_url": "https://cdn.nba.com/headshots/nba/latest/1040x760/1628973.png",
    },
    {
        "id": 1628386, "name": "Ja Morant",               "team": "Memphis Grizzlies",
        "position": "PG", "age": 25,
        "pts": 23.8, "reb": 5.8, "ast": 8.8, "stl": 1.1, "blk": 0.6,
        "tov": 3.0,  "fga": 18.5, "fgm": 8.8, "fg_pct": 0.476,
        "fg3a": 3.2, "fg3m": 1.0, "fg3_pct": 0.313, "fta": 7.5, "ftm": 6.2,
        "ft_pct": 0.827, "min": 31.5, "gp": 60, "plus_minus": 1.8, "ts_pct": 0.582, "usg_pct": 30.0,
        "headshot_url": "https://cdn.nba.com/headshots/nba/latest/1040x760/1629630.png",
    },
    {
        "id": 1628384, "name": "Bam Adebayo",             "team": "Miami Heat",
        "position": "C",  "age": 28,
        "pts": 21.2, "reb": 10.2, "ast": 4.2, "stl": 1.2, "blk": 0.9,
        "tov": 2.4,  "fga": 15.5, "fgm": 8.6, "fg_pct": 0.555,
        "fg3a": 0.5, "fg3m": 0.1, "fg3_pct": 0.200, "fta": 5.5, "ftm": 4.1,
        "ft_pct": 0.745, "min": 34.5, "gp": 73, "plus_minus": 3.5, "ts_pct": 0.594, "usg_pct": 23.5,
        "headshot_url": "https://cdn.nba.com/headshots/nba/latest/1040x760/1628384.png",
    },
    {
        "id": 1626156, "name": "Jaylen Brown",            "team": "Boston Celtics",
        "position": "SG", "age": 28,
        "pts": 30.0, "reb": 5.5, "ast": 4.0, "stl": 1.2, "blk": 0.5,
        "tov": 3.0,  "fga": 22.0, "fgm": 10.8, "fg_pct": 0.491,
        "fg3a": 5.5, "fg3m": 2.2, "fg3_pct": 0.400, "fta": 7.2, "ftm": 6.3,
        "ft_pct": 0.875, "min": 34.4, "gp": 74, "plus_minus": 4.2, "ts_pct": 0.596, "usg_pct": 30.5,
        "headshot_url": "https://cdn.nba.com/headshots/nba/latest/1040x760/1626156.png",
    },
    {
        "id": 1628384, "name": "Devin Booker",            "team": "Phoenix Suns",
        "position": "SG", "age": 28,
        "pts": 28.0, "reb": 4.8, "ast": 6.5, "stl": 1.0, "blk": 0.4,
        "tov": 2.8,  "fga": 21.0, "fgm": 10.2, "fg_pct": 0.486,
        "fg3a": 6.5, "fg3m": 2.5, "fg3_pct": 0.385, "fta": 6.0, "ftm": 5.4,
        "ft_pct": 0.900, "min": 33.5, "gp": 70, "plus_minus": 1.5, "ts_pct": 0.592, "usg_pct": 30.0,
        "headshot_url": "https://cdn.nba.com/headshots/nba/latest/1040x760/1626164.png",
    },
]

_SAMPLE_BY_ID   = {p["id"]: p for p in SAMPLE_PLAYERS}
_SAMPLE_BY_NAME = {p["name"]: p for p in SAMPLE_PLAYERS}


def _resolve_ovr(name: str, stats: dict) -> int:
    """Return 2K26 OVR if in database, else compute from stats (fallback only)."""
    official = get_2k26_rating(name)
    if official:
        return official
    # Fallback for players not in the top-100 list: estimate as sub-81
    from rating_engine import compute_rating
    raw = compute_rating(stats)
    # Cap at 80 since anyone in the official list is ≥81; unranked are below that
    return min(80, raw)


def fetch_player_stats(player_id: int) -> Optional[dict]:
    if NBA_API_AVAILABLE:
        try:
            return _fetch_live(player_id)
        except Exception as e:
            print(f"[nba_api] Error fetching {player_id}: {e}")
    return _SAMPLE_BY_ID.get(player_id)


def search_players(query: str) -> list:
    query_lower = query.lower()
    if NBA_API_AVAILABLE:
        try:
            all_players = nba_players_static.get_active_players()
            return [
                {"id": p["id"], "name": p["full_name"], "team": ""}
                for p in all_players
                if query_lower in p["full_name"].lower()
            ][:10]
        except Exception:
            pass
    return [
        {"id": p["id"], "name": p["name"], "team": p["team"]}
        for p in SAMPLE_PLAYERS
        if query_lower in p["name"].lower()
    ]


def get_season_leaders() -> list:
    from rating_engine import rating_tier
    if NBA_API_AVAILABLE:
        try:
            return _fetch_live_leaders()
        except Exception as e:
            print(f"[nba_api] Leaders error: {e}")

    result = []
    for p in SAMPLE_PLAYERS:
        ovr  = _resolve_ovr(p["name"], p)
        tier = rating_tier(ovr)
        result.append({**p, "ovr": ovr, "tier": tier})
    result.sort(key=lambda x: x["ovr"], reverse=True)
    return result


def _fetch_live(player_id: int) -> Optional[dict]:
    time.sleep(0.6)
    career  = playercareerstats.PlayerCareerStats(player_id=player_id, per_mode36="PerGame")
    df      = career.get_data_frames()[0]
    season_row = df[df["SEASON_ID"] == CURRENT_SEASON]
    if season_row.empty:
        season_row = df.tail(1)
    row = season_row.iloc[0]

    info     = commonplayerinfo.CommonPlayerInfo(player_id=player_id)
    info_row = info.get_data_frames()[0].iloc[0]
    name     = info_row.get("DISPLAY_FIRST_LAST", "Unknown")

    fga = float(row.get("FGA", 0))
    fta = float(row.get("FTA", 0))
    pts = float(row.get("PTS", 0))
    ts_denom = 2 * (fga + 0.44 * fta)
    ts_pct   = pts / ts_denom if ts_denom else 0

    return {
        "id":         player_id,
        "name":       name,
        "team":       info_row.get("TEAM_NAME", ""),
        "position":   info_row.get("POSITION", ""),
        "age":        int(info_row.get("SEASON_EXP", 0)),
        "pts":        pts,
        "reb":        float(row.get("REB", 0)),
        "ast":        float(row.get("AST", 0)),
        "stl":        float(row.get("STL", 0)),
        "blk":        float(row.get("BLK", 0)),
        "tov":        float(row.get("TOV", 0)),
        "fga":        fga,
        "fgm":        float(row.get("FGM", 0)),
        "fg_pct":     float(row.get("FG_PCT", 0)),
        "fg3a":       float(row.get("FG3A", 0)),
        "fg3m":       float(row.get("FG3M", 0)),
        "fg3_pct":    float(row.get("FG3_PCT", 0)),
        "fta":        fta,
        "ftm":        float(row.get("FTM", 0)),
        "ft_pct":     float(row.get("FT_PCT", 0)),
        "min":        float(row.get("MIN", 0)),
        "gp":         int(row.get("GP", 0)),
        "plus_minus": float(row.get("PLUS_MINUS", 0)),
        "ts_pct":     ts_pct,
        "usg_pct":    0.0,
        "headshot_url": f"https://cdn.nba.com/headshots/nba/latest/1040x760/{player_id}.png",
    }


def _fetch_live_leaders() -> list:
    from rating_engine import rating_tier
    time.sleep(0.6)
    leaders_ep = leagueleaders.LeagueLeaders(
        season=CURRENT_SEASON, per_mode48="PerGame", stat_category_abbreviation="PTS"
    )
    df = leaders_ep.get_data_frames()[0].head(25)
    result = []
    for _, row in df.iterrows():
        pid  = int(row["PLAYER_ID"])
        name = row["PLAYER"]
        fga  = float(row.get("FGA", 0))
        fta  = float(row.get("FTA", 0))
        pts  = float(row.get("PTS", 0))
        ts_d = 2 * (fga + 0.44 * fta)
        ts   = pts / ts_d if ts_d else 0.55
        stats = {
            "id": pid, "name": name,
            "team": row.get("TEAM", ""), "position": row.get("POS", ""),
            "age": int(row.get("AGE", 0)),
            "pts": pts, "reb": float(row.get("REB", 0)), "ast": float(row.get("AST", 0)),
            "stl": float(row.get("STL", 0)), "blk": float(row.get("BLK", 0)),
            "tov": float(row.get("TOV", 0)), "fga": fga, "fgm": float(row.get("FGM", 0)),
            "fg_pct": float(row.get("FG_PCT", 0)), "fg3a": float(row.get("FG3A", 0)),
            "fg3m": float(row.get("FG3M", 0)), "fg3_pct": float(row.get("FG3_PCT", 0)),
            "fta": fta, "ftm": float(row.get("FTM", 0)), "ft_pct": float(row.get("FT_PCT", 0)),
            "min": float(row.get("MIN", 0)), "gp": int(row.get("GP", 0)),
            "plus_minus": float(row.get("PLUS_MINUS", 0)),
            "ts_pct": ts, "usg_pct": 0.0,
            "headshot_url": f"https://cdn.nba.com/headshots/nba/latest/1040x760/{pid}.png",
        }
        ovr  = _resolve_ovr(name, stats)
        tier = rating_tier(ovr)
        result.append({**stats, "ovr": ovr, "tier": tier})
    result.sort(key=lambda x: x["ovr"], reverse=True)
    return result
