from flask import Flask, render_template, request, jsonify
import rating_engine
from rating_engine import compute_rating, get_rating_breakdown, rating_tier
from data_fetcher import fetch_player_stats, search_players, get_season_leaders, _resolve_ovr
from colleges import get_college
from tennis_data import ATP_PLAYERS, ATP_BY_RANK, ATP_BY_NAME

app = Flask(__name__)

TEAM_COLORS = {
    "Atlanta Hawks": "#E03A3E", "Boston Celtics": "#007A33",
    "Brooklyn Nets": "#000000", "Charlotte Hornets": "#1D1160",
    "Chicago Bulls": "#CE1141", "Cleveland Cavaliers": "#860038",
    "Dallas Mavericks": "#00538C", "Denver Nuggets": "#0E2240",
    "Detroit Pistons": "#C8102E", "Golden State Warriors": "#1D428A",
    "Houston Rockets": "#CE1141", "Indiana Pacers": "#002D62",
    "LA Clippers": "#C8102E", "Los Angeles Clippers": "#C8102E",
    "Los Angeles Lakers": "#552583", "Memphis Grizzlies": "#5D76A9",
    "Miami Heat": "#98002E", "Milwaukee Bucks": "#00471B",
    "Minnesota Timberwolves": "#0C2340", "New Orleans Pelicans": "#0C2340",
    "New York Knicks": "#006BB6", "Oklahoma City Thunder": "#007AC1",
    "Orlando Magic": "#0077C0", "Philadelphia 76ers": "#006BB6",
    "Phoenix Suns": "#1D1160", "Portland Trail Blazers": "#E03A3E",
    "Sacramento Kings": "#5A2D81", "San Antonio Spurs": "#C4CED4",
    "Toronto Raptors": "#CE1141", "Utah Jazz": "#002B5C",
    "Washington Wizards": "#002B5C",
}

# ── Template globals ──────────────────────────────────────────────────────

@app.context_processor
def inject_globals():
    return {"rating_engine": rating_engine}

@app.template_global()
def team_color(team_name: str) -> str:
    return TEAM_COLORS.get(team_name, "#e8523a")

@app.template_global()
def context_note(value: float, stat_key: str, invert: bool = False) -> str:
    from rating_engine import LEAGUE_AVGS, z as zscore
    avg = LEAGUE_AVGS.get(stat_key)
    if avg is None:
        return "–"
    zv = zscore(stat_key, value)
    if invert:
        zv = -zv
    if zv >= 2.0:    return "Elite"
    elif zv >= 1.2:  return "Above avg"
    elif zv >= 0.3:  return "Solid"
    elif zv >= -0.3: return f"Avg (~{avg:.1f})"
    elif zv >= -1.2: return "Below avg"
    else:            return "Well below avg"

@app.template_global()
def bar_color(val: int) -> str:
    if val >= 90:   return "#FFD700"
    elif val >= 80: return "#4FC3F7"
    elif val >= 70: return "#81C784"
    elif val >= 60: return "#FFA726"
    else:           return "#EF5350"

# ── Basketball routes ─────────────────────────────────────────────────────

@app.route("/")
def index():
    leaders = get_season_leaders()
    return render_template("index.html", leaders=leaders)

@app.route("/player/<int:player_id>")
def player_detail(player_id):
    stats = fetch_player_stats(player_id)
    if not stats:
        return "Player not found", 404
    rating    = _resolve_ovr(stats["name"], stats)
    breakdown = get_rating_breakdown(stats)
    college   = get_college(stats["name"])
    return render_template("player.html", stats=stats, rating=rating,
                           breakdown=breakdown, college=college)

@app.route("/teams")
def teams():
    from teams_data import get_all_teams
    return render_template("teams.html", teams=get_all_teams())

@app.route("/api/search")
def api_search():
    query = request.args.get("q", "").strip()
    if len(query) < 2:
        return jsonify([])
    return jsonify(search_players(query))

@app.route("/api/player/<int:player_id>")
def api_player(player_id):
    stats = fetch_player_stats(player_id)
    if not stats:
        return jsonify({"error": "Player not found"}), 404
    rating    = _resolve_ovr(stats["name"], stats)
    breakdown = get_rating_breakdown(stats)
    tier      = rating_tier(rating)
    return jsonify({"stats": stats, "rating": rating, "breakdown": breakdown, "tier": tier})

@app.route("/compare")
def compare():
    return render_template("compare.html")

# ── Tennis routes ─────────────────────────────────────────────────────────

@app.route("/tennis")
def tennis_index():
    return render_template("tennis_index.html", players=ATP_PLAYERS)

@app.route("/tennis/player/<int:rank>")
def tennis_player(rank):
    player = ATP_BY_RANK.get(rank)
    if not player:
        return "Player not found", 404
    return render_template("tennis_player.html", player=player)

@app.route("/tennis/rankings")
def tennis_rankings():
    return render_template("tennis_rankings.html", players=ATP_PLAYERS)

@app.route("/tennis/compare")
def tennis_compare():
    return render_template("tennis_compare.html")

@app.route("/tennis/api/search")
def tennis_api_search():
    q = request.args.get("q", "").strip().lower()
    if len(q) < 2:
        return jsonify([])
    results = [
        {"rank": p["rank"], "name": p["name"], "country": p["country"], "flag": p["flag"]}
        for p in ATP_PLAYERS if q in p["name"].lower()
    ][:10]
    return jsonify(results)

@app.route("/tennis/api/player/<int:rank>")
def tennis_api_player(rank):
    player = ATP_BY_RANK.get(rank)
    if not player:
        return jsonify({"error": "Not found"}), 404
    return jsonify(player)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
