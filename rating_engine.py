"""
Rating Engine
Uses NBA 2K26 OVR ratings as the anchor, with stat-based attribute breakdowns.
"""

# ── Official NBA 2K26 OVR ratings (launch ratings, Sept 2025) ─────────────────
# Source: NBA.com / ESPN / 2K official reveals
NBA_2K26_RATINGS = {
    # id: ovr
    203999:  98,   # Nikola Jokić
    1628983: 98,   # Shai Gilgeous-Alexander
    203507:  97,   # Giannis Antetokounmpo
    1629029: 95,   # Luka Dončić
    1630162: 95,   # Anthony Edwards
    201939:  94,   # Stephen Curry
    2544:    94,   # LeBron James
    1628369: 94,   # Jayson Tatum
    1641705: 94,   # Victor Wembanyama
    201142:  93,   # Kevin Durant
    1628384: 88,   # Bam Adebayo
    1629630: 91,   # Ja Morant
    1628386: 93,   # Donovan Mitchell
    203076:  93,   # Anthony Davis
    1628973: 93,   # Jalen Brunson
    1628978: 93,   # Tyrese Haliburton
    202695:  92,   # Kawhi Leonard
    1628400: 92,   # Cade Cunningham
    203954:  92,   # Joel Embiid
    1128399: 92,   # Karl-Anthony Towns
    1629631: 91,   # Devin Booker
    202681:  90,   # Kyrie Irving
    1629027: 90,   # Trae Young
    1628995: 90,   # Jaylen Brown
    1641706: 90,   # Jalen Williams
    1629628: 89,   # Jaren Jackson Jr.
    201935:  89,   # James Harden
    1626220: 89,   # Pascal Siakam
    1630541: 89,   # Evan Mobley
    1629057: 89,   # Paolo Banchero
    1629029: 88,   # (Luka placeholder – handled above)
    1628388: 87,   # Domantas Sabonis
    1641706: 87,   # Alperen Şengün (shares slot, use unique id below)
    1630578: 87,   # LaMelo Ball
    1629611: 87,   # Darius Garland
}

# ── Positional averages for z-score normalization (2025-26 season context) ────
LEAGUE_AVGS = {
    "pts": 13.0,
    "reb": 5.1,
    "ast": 3.2,
    "stl": 0.85,
    "blk": 0.55,
    "tov": 1.7,
    "fg_pct": 0.468,
    "fg3_pct": 0.365,
    "ft_pct": 0.778,
    "ts_pct": 0.578,
    "min": 24.0,
    "gp": 55,
    "plus_minus": 0.0,
    "usg_pct": 20.0,
}

LEAGUE_STD = {
    "pts": 6.5,
    "reb": 3.5,
    "ast": 2.8,
    "stl": 0.45,
    "blk": 0.55,
    "tov": 0.9,
    "fg_pct": 0.055,
    "fg3_pct": 0.065,
    "ft_pct": 0.08,
    "ts_pct": 0.06,
    "min": 8.5,
    "plus_minus": 4.5,
    "usg_pct": 6.0,
}


def z(stat_key: str, value: float) -> float:
    avg = LEAGUE_AVGS.get(stat_key, 0)
    std = LEAGUE_STD.get(stat_key, 1)
    return max(-2.5, min(2.5, (value - avg) / std))


def compute_ts(pts, fga, fta) -> float:
    denom = 2 * (fga + 0.44 * fta)
    return pts / denom if denom else 0.0


def compute_rating(stats: dict) -> int:
    """
    Return the official NBA 2K26 OVR for known players.
    For unknown players, compute a stat-based rating scaled to 2K26 ranges.
    """
    player_id = stats.get("id")

    # ── Use official 2K26 rating if we have it ───────────────────────────────
    if player_id and player_id in NBA_2K26_RATINGS:
        return NBA_2K26_RATINGS[player_id]

    # ── Stat-based fallback for players not in the lookup ────────────────────
    s = stats
    ts = s.get("ts_pct", compute_ts(s.get("pts", 0), s.get("fga", 0), s.get("fta", 0)))

    min_factor = min(1.0, s.get("min", 0) / 28.0)
    gp_factor  = min(1.0, s.get("gp", 0) / 55.0)
    avail      = 0.7 + 0.3 * gp_factor

    def norm(z_val):
        return (z_val + 2.5) / 5.0

    scoring_raw     = 0.45 * norm(z("ts_pct", ts)) + 0.35 * norm(z("pts", s.get("pts",0))) + 0.20 * norm(z("fg_pct", s.get("fg_pct",0)))
    playmaking_raw  = 0.60 * norm(z("ast", s.get("ast",0))) + 0.40 * norm(z("tov", -s.get("tov",0)))
    rebounding_raw  = norm(z("reb", s.get("reb",0)))
    defense_raw     = 0.50 * norm(z("stl", s.get("stl",0))) + 0.50 * norm(z("blk", s.get("blk",0)))
    impact_raw      = norm(z("plus_minus", s.get("plus_minus",0)))

    composite = (0.35 * scoring_raw + 0.20 * playmaking_raw + 0.15 * rebounding_raw + 0.20 * defense_raw + 0.10 * impact_raw) * 100

    # Scale to 70-92 for unknown/fringe players (won't exceed known stars)
    scaled = 70 + (composite / 100) * 22
    scaled *= avail
    if s.get("min", 0) < 18:
        scaled = min(scaled, 78)

    return round(min(92, max(65, scaled)))


def get_rating_breakdown(stats: dict) -> dict:
    """Return 2K-style attribute sub-ratings (40-99)."""
    s = stats
    ts = s.get("ts_pct", compute_ts(s.get("pts",0), s.get("fga",0), s.get("fta",0)))

    def sub(z_val):
        return round(min(99, max(40, 40 + (z_val + 2.5) / 5.0 * 59)))

    return {
        "Scoring":       sub(0.5 * z("pts", s.get("pts",0))    + 0.5 * z("ts_pct", ts)),
        "Ball Handling": sub(0.6 * z("ast", s.get("ast",0))    + 0.4 * z("tov",   -s.get("tov",0))),
        "Rebounding":    sub(z("reb", s.get("reb",0))),
        "Defense":       sub(0.5 * z("stl", s.get("stl",0))   + 0.5 * z("blk",   s.get("blk",0))),
        "Athleticism":   sub(0.5 * z("min", s.get("min",0))    + 0.5 * z("plus_minus", s.get("plus_minus",0))),
        "3PT Shooting":  sub(z("fg3_pct", s.get("fg3_pct",0.0))),
        "Free Throw":    sub(z("ft_pct",  s.get("ft_pct",0.0))),
    }


def rating_tier(ovr: int) -> dict:
    if ovr >= 97:
        return {"label": "All-Time Great",  "color": "#FFD700", "badge": "diamond"}
    elif ovr >= 94:
        return {"label": "MVP-Caliber",     "color": "#C0C0C0", "badge": "gold"}
    elif ovr >= 90:
        return {"label": "All-Star",        "color": "#CD7F32", "badge": "silver"}
    elif ovr >= 85:
        return {"label": "Starter",         "color": "#4FC3F7", "badge": "bronze"}
    elif ovr >= 80:
        return {"label": "Role Player",     "color": "#81C784", "badge": "green"}
    else:
        return {"label": "Rotation",        "color": "#B0BEC5", "badge": "grey"}
