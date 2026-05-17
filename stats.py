#!/usr/bin/python3
import html
import io
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

# Force UTF-8 encoding for stdout to prevent the 'ascii' codec error
# Works on Python 3.1+
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# ── CONFIGURATION ───────────────────────────────────────────────────────────
DEFAULT_USER = "bropal404"
CACHE_SECS = 20000
GITHUB_TOKEN = ""  # PASTE TOKEN HERE

# ── THEME CONSTANTS ─────────────────────────────────────────────────────────
MONO = "ui-monospace, 'Cascadia Code', 'Fira Mono', 'Courier New', monospace"
BG, SCANLINE, PHOSPHOR, DIM, VERY_DIM = (
    "#0d1117",
    "#1a151a",
    "#f9fff0",
    "#8d8f87",
    "#5a5d56",
)
ACCENT_CYAN, ACCENT_AMB, ACCENT_RED, BAR_FULL = (
    "#7fefea",
    "#efd166",
    "#ef6b6b",
    "#39d353",
)

W, PAD = 750, 32
BARW = W - PAD * 2

LANG_COLORS = {
    "Python": "#4fa3e0",
    "JavaScript": "#f7df1e",
    "TypeScript": "#3178c6",
    "C++": "#f34b7d",
    "C": "#cccccc",
    "Java": "#ed8b00",
    "Go": "#00add8",
    "HTML": "#c97ada",
}

# ── HELPER FUNCTIONS ────────────────────────────────────────────────────────


def parse_gh_ts(ts_str):
    """Manual parsing for Python < 3.7 (replaces fromisoformat)."""
    try:
        # GitHub format: 2024-05-17T10:34:43Z
        ts = ts_str.replace("Z", "")
        # Older strptime handles this format perfectly
        dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S")
        # Python 3.2+ timezone support
        return dt.replace(tzinfo=timezone.utc)
    except:
        return datetime.now(timezone.utc)


def time_status():
    # Note: .astimezone() without args requires Python 3.6+
    try:
        now = datetime.now(timezone.utc).astimezone()
        h = now.hour
    except:
        h = datetime.now().hour  # Fallback for very old python

    statuses = {
        0: "debugging at 2 AM with chai from Damam",
        1: "praying my code compiles at 11:59 PM",
        2: "still in the SPCRC, scrolling Swiggy",
        12: "gobbling up biryani at Kadamba",
        15: "grinding GitHub instead of class",
        17: "chai + samosa at VC with the bois",
        22: "procrastinating the 11:59 deadline",
    }
    return statuses.get(h, "existing")


def gh(path):
    token = GITHUB_TOKEN or os.environ.get("GITHUB_TOKEN", "")
    headers = {"User-Agent": "readme-stats/4", "Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        req = urllib.request.Request(f"https://api.github.com{path}", headers=headers)
        with urllib.request.urlopen(req, timeout=7) as r:
            return json.loads(r.read().decode())
    except:
        return None


def get_weather(city="Hyderabad"):
    try:
        url = f"https://wttr.in/{urllib.parse.quote(city)}?format=j1"
        req = urllib.request.Request(url, headers={"User-Agent": "readme-stats/4"})
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read().decode())
            cc = data["current_condition"][0]
            desc = cc["weatherDesc"][0]["value"]
            glyphs = {
                "thunder": "&#9889;",
                "rain": "&#9974;",
                "snow": "&#10052;",
                "cloud": "&#9729;",
                "sun": "&#9728;",
            }
            glyph = next((v for k, v in glyphs.items() if k in desc.lower()), "~")
            return {"temp": cc["temp_C"], "desc": desc[:18], "glyph": glyph}
    except:
        return None


def _account_uptime():
    try:
        start = datetime(2004, 1, 20, tzinfo=timezone.utc)
        diff = datetime.now(timezone.utc) - start
        y, rem = divmod(diff.days, 365)
        m, d = divmod(rem, 30)
        return f"{y}y {m}m {d}d"
    except:
        return "unknown"


def _ascii_bar(pct, width=24):
    filled = round(pct / 100 * width)
    return "&#9619;" * filled + "&#9617;" * (width - filled)


def render(stats, weather=None):
    svg = []

    # Calculate recency signal
    days_since = 999
    if stats["pushes"]:
        dt = parse_gh_ts(stats["pushes"][0][1])
        days_since = (datetime.now(timezone.utc) - dt).total_seconds() / 86400

    sig_map = [(1, 5), (7, 3), (30, 1)]
    f = next((v for d, v in sig_map if days_since <= d), 0)
    sig_str = "&#9646;" * f + "&#9647;" * (5 - f)
    sig_col = [ACCENT_RED, ACCENT_AMB, ACCENT_AMB, BAR_FULL, PHOSPHOR, PHOSPHOR][f]

    y = 48
    svg.append(
        f'<text x="{PAD}" y="{y - 16}" fill="{VERY_DIM}" font-family="{MONO}" font-size="9">BROPAL-STATS-CARD v4.0 :: INITIALISED</text>'
    )
    svg.append(
        f'<text x="{PAD}" y="{y + 10}" fill="{ACCENT_CYAN}" font-family="{MONO}" font-size="30" font-weight="700">{stats["name"]}</text>'
    )
    svg.append(
        f'<text x="{W - PAD}" y="{y + 10}" fill="{DIM}" font-family="{MONO}" font-size="11" text-anchor="end">@{stats["username"]}</text>'
    )

    y += 32
    svg.append(
        f'<text x="{PAD}" y="{y}" fill="{DIM}" font-family="{MONO}" font-size="11"><tspan fill="{ACCENT_AMB}">&#10095;</tspan>  {html.escape(stats["status"])}</text>'
    )
    if weather:
        svg.append(
            f'<text x="{W - PAD}" y="{y}" fill="{ACCENT_AMB}" font-family="{MONO}" font-size="11" text-anchor="end">{weather["glyph"]} {weather["temp"]}°C  {weather["desc"]}</text>'
        )

    y += 28
    svg.append(
        f'<text x="{PAD}" y="{y}" fill="{sig_col}" font-family="{MONO}" font-size="11">SIG {sig_str}</text>'
    )
    svg.append(
        f'<text x="{W - PAD}" y="{y}" fill="{VERY_DIM}" font-family="{MONO}" font-size="10" text-anchor="end">UPTIME {stats["uptime"]}</text>'
    )

    # ── SECTIONS ──
    def draw_sec(title, cy):
        l = f'<line x1="{PAD}" y1="{cy}" x2="{PAD + 12}" y2="{cy}" stroke="{DIM}" stroke-width="0.8"/>'
        l += f'<text x="{PAD + 16}" y="{cy + 4}" fill="{DIM}" font-family="{MONO}" font-size="12">[ {title} ]</text>'
        l += f'<line x1="{PAD + len(title) * 7.5 + 35}" y1="{cy}" x2="{W - PAD}" y2="{cy}" stroke="{DIM}" stroke-width="0.8"/>'
        return l, cy + 24

    y += 32
    s, y = draw_sec("LANGUAGE USAGE IN REPOS", y)
    svg.append(s)
    for lang, _, pct in stats["top_langs"]:
        svg.append(
            f'<text x="{PAD}" y="{y}" font-family="{MONO}" font-size="12"><tspan fill="{PHOSPHOR}">{lang:<14}</tspan> <tspan fill="{LANG_COLORS.get(lang, DIM)}">{_ascii_bar(pct)}</tspan> <tspan fill="{DIM}">{pct:>3}%</tspan></text>'
        )
        y += 24

    y += 12
    s, y = draw_sec("RECENT ACTIVITY", y)
    svg.append(s)
    for k, n, ts in [("PUSH", n, t) for n, t in stats["pushes"]]:
        ago = (datetime.now(timezone.utc) - parse_gh_ts(ts)).total_seconds()
        ago_s = f"{int(ago / 3600)}h" if ago < 86400 else f"{int(ago / 86400)}d"
        svg.append(
            f'<text x="{PAD}" y="{y}" font-family="{MONO}" font-size="11.5"><tspan fill="{VERY_DIM}">[</tspan><tspan fill="{PHOSPHOR}">{k}</tspan><tspan fill="{VERY_DIM}">]</tspan><tspan fill="{PHOSPHOR}"> {html.escape(n[:36])}</tspan><tspan fill="{DIM}">  +{ago_s}</tspan></text>'
        )
        y += 24

    y += 12
    s, y = draw_sec("LIFE STATS", y)
    svg.append(s)
    for k, v, c in [
        ("REPOS", stats["repos"], ACCENT_CYAN),
        ("STARS", stats["stars"], ACCENT_AMB),
        ("FOLLOWERS", stats["followers"], PHOSPHOR),
    ]:
        dots = "·" * (40 - len(k) - len(str(v)))
        svg.append(
            f'<text x="{PAD}" y="{y}" font-family="{MONO}" font-size="12"><tspan fill="{DIM}">{k} </tspan><tspan fill="{VERY_DIM}">{dots} </tspan><tspan fill="{c}" font-weight="600">{v}</tspan></text>'
        )
        y += 24

    y += 20
    svg.append(
        f'<line x1="{PAD}" y1="{y}" x2="{W - PAD}" y2="{y}" stroke="{VERY_DIM}" stroke-width="0.8"/>'
    )
    svg.append(
        f'<text x="{PAD}" y="{y + 20}" fill="{VERY_DIM}" font-family="{MONO}" font-size="9">generated {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")} UTC</text>'
    )

    return f"""<svg width="{W}" height="{y + 32}" xmlns="http://www.w3.org/2000/svg">
    <rect width="100%" height="100%" fill="{BG}"/>
    {"".join(svg)}</svg>"""


def main():
    params = urllib.parse.parse_qs(os.environ.get("QUERY_STRING", ""))
    user = params.get("user", [DEFAULT_USER])[0].strip() or DEFAULT_USER
    city = params.get("city", ["Hyderabad"])[0].strip()
    print("Content-Type: image/svg+xml\nCache-Control: public, max-age=20000\n")
    stats = get_stats(user)
    if stats:
        print(render(stats, weather=get_weather(city)))
    else:
        print(
            f'<svg width="400" height="50" xmlns="http://www.w3.org/2000/svg"><rect width="100%" height="100%" fill="#060d06"/><text x="20" y="30" fill="red" font-family="monospace">ERR: Could not fetch stats</text></svg>'
        )


def get_stats(username):
    user = gh(f"/users/{username}")
    if not user or "login" not in user:
        return None
    repos = gh(f"/users/{username}/repos?per_page=100&sort=pushed") or []
    stars = sum(r.get("stargazers_count", 0) for r in repos)
    langs = {}
    for r in repos:
        l = r.get("language")
        if l:
            langs[l] = langs.get(l, 0) + 1
    top5 = sorted(langs.items(), key=lambda x: x[1], reverse=True)[:5]
    tot = sum(c for _, c in top5) or 1
    return {
        "name": (user.get("name") or username)[:36],
        "username": user.get("login"),
        "repos": user.get("public_repos", 0),
        "followers": user.get("followers", 0),
        "stars": stars,
        "top_langs": [(l, c, round(c / tot * 100)) for l, c in top5],
        "pushes": [(r["name"], r["pushed_at"]) for r in repos if not r.get("fork")][:2],
        "prs": [],
        "status": time_status(),
        "uptime": _account_uptime(),
    }


if __name__ == "__main__":
    main()
