#!/usr/bin/python3
"""
GitHub Stats Card -- CGI Script
Theme: Phosphor CRT / Mission-Control terminal
Deploy: place in ~/public_html/cgi-bin/stats.py
chmod +x stats.py
"""

import html
import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone

# ── CONFIGURATION ───────────────────────────────────────────────────────────
DEFAULT_USER = "bropal404"
CACHE_SECS = 20000

# ── THEME CONSTANTS ─────────────────────────────────────────────────────────
MONO = "ui-monospace, 'Cascadia Code', 'Fira Mono', 'Courier New', monospace"

BG = "#060d06"             # near-black with green tint
SCANLINE = "#0a150a"       # slightly lighter for scanline pattern
PHOSPHOR = "#b9ffb0"       # bright phosphor green — primary text
DIM = "#4d8f47"            # dimmed green
VERY_DIM = "#2a4d26"       # very dim, for decorations
ACCENT_CYAN = "#7fffea"    # cyan highlight (name, headers)
ACCENT_AMB = "#ffd166"     # amber — used sparingly for warnings/weather
ACCENT_RED = "#ff6b6b"     # red for "offline" type indicators
BAR_FULL = "#39d353"       # filled bar block
BAR_EMPTY = "#1a3318"      # empty bar block

W = 750                    # Increased width for more breathing room
PAD = 32
BARW = W - PAD * 2

LANG_COLORS = {
    "Python": "#4fa3e0", "JavaScript": "#f7df1e", "TypeScript": "#3178c6",
    "C++": "#f34b7d", "C": "#cccccc", "Java": "#ed8b00", "Go": "#00add8",
    "Rust": "#f74c00", "HTML": "#e34c26", "CSS": "#663399", "Ruby": "#cc342d",
    "Shell": "#39d353", "Kotlin": "#a97bff", "Swift": "#fa7343", "Dart": "#00b4ab",
    "Jupyter Notebook": "#f37626", "Vue": "#41b883", "PHP": "#8892bf",
    "Nix": "#7ebae4", "Makefile": "#427819", "TeX": "#3d6117",
}

# ── HELPER FUNCTIONS ────────────────────────────────────────────────────────

def time_status():
    """Return a time-aware IIIT-Hyderabad flavoured status string."""
    now = datetime.now(timezone.utc).astimezone()
    h = now.hour
    wd = now.weekday()
    is_weekend = wd >= 5

    statuses = {
        0: "debugging at 2 AM with chai from Damam",
        1: "praying my code compiles before the deadline at 11:59 PM",
        2: "still in the SPCRC, scrolling swiggy for dinner",
        3: "watching CID instead of sleeping",
        4: "waking up for the 8 AM (lol, no)",
        5: "snoozing the alarm for the 5th time",
        6: "rushing to mess for breakfast before 9:30",
        7: "sleeping through the 8:30 AM lecture",
        8: "copying friend's assignment in class",
        9: "vibing in the back bench of H105",
        10: "scrolling reels in the meeting room",
        11: "planning lunch at VC",
        12: "gobbling up biryani at Kadmaba with the bois",
        14: "napping after that kadmba biriyani",
        15: "grinding GitHub instead of attending class",
        16: "waiting for the 4 PM chai break",
        17: "chai + samosa at VC with the bois",
        18: "group project meeting that could've been an email",
        19: "dinner at mess (cuz bank balance is low)",
        21: "actually studying for tomorrow's quiz",
        22: "procrastinating the assignment due at 11:59",
        23: "rushing the 11:59 PM deadline",
    }

    if is_weekend:
        weekend_statuses = {
            0: "weekend coding session at 2 AM",
            1: "binge-watching Shinchan instead of sleeping",
            2: "late night maggi in the Devids",
            3: "gaming until sunrise",
            4: "finally going to sleep",
            5: "sleeping through the weekend morning",
            6: "brunch at VC (finally a good meal)",
            7: "weekend sleep marathon continues",
            8: "waking up for the 'important' brunch",
            9: "planning the day (doing nothing)",
            10: "still in bed, scrolling Instagram",
            11: "heading to DLF for the weekend",
            12: "lunch at Pista House",
            13: "roaming around Hitec",
            14: "back on campus, regretting the heat",
            15: "weekend 20 Hour nap session",
            16: "chai at Damam with weekend stories",
            17: "playing on ground",
            18: "getting ready for the night out",
            19: "dinner at barkaas",
            20: "movie night on lab monitor",
            21: "weekend gaming tournament",
            22: "planning to sleep early (won't happen)",
            23: "realizing Monday is tomorrow :(",
        }
        return weekend_statuses.get(h, statuses.get(h, "existing"))

    return statuses.get(h, "existing")

def gh(path):
    token = os.environ.get("GITHUB_TOKEN", "")
    headers = {
        "User-Agent": "readme-stats/4",
        "Accept": "application/vnd.github+json",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        req = urllib.request.Request(
            f"https://api.github.com{path}",
            headers=headers,
        )
        with urllib.request.urlopen(req, timeout=7) as response:
            return json.loads(response.read().decode())
    except Exception as e :
        print(e)
        print("problem")
        return None

def get_weather(city="Hyderabad"):
    """Fetch current weather from wttr.in (no API key needed)."""
    try:
        url = f"https://wttr.in/{urllib.parse.quote(city)}?format=j1"
        req = urllib.request.Request(url, headers={"User-Agent": "readme-stats/4"})
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read().decode())
            cc = data["current_condition"][0]
            temp = cc["temp_C"]
            desc = cc["weatherDesc"][0]["value"]
            feels = cc["FeelsLikeC"]
            
            # pick a simple weather glyph
            dl = desc.lower()
            if "thunder" in dl: glyph = "⚡"
            elif "rain" in dl or "drizzle" in dl: glyph = "⛆"
            elif "snow" in dl: glyph = "❄"
            elif "fog" in dl or "mist" in dl: glyph = "≋"
            elif "overcast" in dl or "cloud" in dl: glyph = "☁"
            elif "sunny" in dl or "clear" in dl: glyph = "☀"
            else: glyph = "~"
            
            return {
                "temp": temp,
                "feels": feels,
                "desc": desc[:18],
                "glyph": glyph,
                "city": city,
            }
    except Exception:
        return None

def _fmt(n):
    return f"{n/1000:.1f}k" if n >= 1000 else str(n)

def _ago(s):
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        diff = (datetime.now(timezone.utc) - dt).total_seconds()
        if diff < 3600: return f"{int(diff/60)}m"
        if diff < 86400: return f"{int(diff/3600)}h"
        if diff < 604800: return f"{int(diff/86400)}d"
        return f"{int(diff/604800)}w"
    except Exception:
        return "?"

def _signal_blocks(days_since_push):
    """5-block signal strength based on recency."""
    if days_since_push <= 1: filled = 5
    elif days_since_push <= 3: filled = 4
    elif days_since_push <= 7: filled = 3
    elif days_since_push <= 14: filled = 2
    elif days_since_push <= 30: filled = 1
    else: filled = 0
    return "▮" * filled + "▯" * (5 - filled), filled

def _account_uptime():
    """Years/months/days since Jan 20, 2004."""
    try:
        dt = datetime(2004, 1, 20, tzinfo=timezone.utc)
        diff = datetime.now(timezone.utc) - dt
        days = diff.days
        y, rem = divmod(days, 365)
        m, d = divmod(rem, 30)
        return f"{y}y {m}m {d}d"
    except Exception:
        return "unknown"

def _ascii_bar(pct, width=24):
    """Render an ASCII ▓░ progress bar."""
    filled = round(pct / 100 * width)
    return "▓" * filled + "░" * (width - filled)

def _t(x, y, content, fill, size=12, weight="normal", anchor="start", spacing=None, mono=True):
    fam = MONO if mono else "sans-serif"
    sp = f' letter-spacing="{spacing}"' if spacing else ""
    an = f' text-anchor="{anchor}"' if anchor != "start" else ""
    return (
        f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" '
        f'font-weight="{weight}" font-family="{fam}"{sp}{an}>{content}</text>\n'
    )

def _line(x1, y1, x2, y2, stroke=VERY_DIM, sw=0.8, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
        f'stroke="{stroke}" stroke-width="{sw}"{d}/>\n'
    )

def _rect(x, y, w, h, fill="none", stroke="none", sw=1, rx=0):
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n'
    )

def _section(label, y):
    """Draw a section header like ── [ ACTIVITY ] ────────────────"""
    bracket = f"[ {label} ]"
    blen = len(bracket) * 7.2 + 8  # approx pixel width
    svg = _line(PAD, y, PAD + 12, y, stroke=DIM)
    svg += _t(PAD + 16, y + 4, bracket, fill=DIM, size=12)
    svg += _line(PAD + 24 + blen, y, W - PAD, y, stroke=DIM)
    return svg, y + 24

def error_svg(msg):
    return f'''<svg width="{W}" height="100" viewBox="0 0 {W} 100" xmlns="http://www.w3.org/2000/svg">
        <rect width="{W}" height="100" fill="{BG}"/>
        <text x="{PAD}" y="50" fill="{ACCENT_RED}" font-family="{MONO}" font-size="14">ERR: {html.escape(msg)}</text>
    </svg>'''

# ── DATA GATHERING ──────────────────────────────────────────────────────────

def get_stats(username):
    user = gh(f"/users/{username}")
    if not user or "login" not in user:
        return None

    repos = gh(f"/users/{username}/repos?per_page=100&type=owner&sort=pushed") or []

    stars = 0
    forks = 0
    langs = {}
    pushes = []
    
    top_repo = ""
    top_stars = -1

    for repo in repos:
        s = repo.get("stargazers_count", 0)
        stars += s
        forks += repo.get("forks_count", 0)

        if s > top_stars:
            top_stars = s
            top_repo = html.escape(repo["name"][:40])

        language = repo.get("language")
        if language:
            langs[language] = langs.get(language, 0) + 1

        if not repo.get("fork") and repo.get("pushed_at"):
            pushes.append((
                html.escape(repo["name"][:32]),
                repo["pushed_at"],
            ))

    prs_raw = gh(f"/search/issues?q=author:{username}+type:pr&sort=created&order=desc&per_page=3")
    prs = []

    if prs_raw and "items" in prs_raw:
        for pr in prs_raw["items"]:
            title = html.escape(pr.get("title", "")[:38])
            prs.append((
                f"#{pr.get('number')} {title}",
                pr.get("created_at", ""),
            ))

    top5 = sorted(langs.items(), key=lambda x: x[1], reverse=True)[:5]
    total = sum(count for _, count in top5) or 1
    top5_pct = [(lang, count, round(count / total * 100)) for lang, count in top5]

    return {
        "name": html.escape((user.get("name") or username)[:36]),
        "username": html.escape(user.get("login", username)),
        "bio": html.escape((user.get("bio") or "")[:68]),
        "repos": user.get("public_repos", 0),
        "followers": user.get("followers", 0),
        "stars": stars,
        "forks": forks,
        "top_langs": top5_pct,
        "pushes": pushes[:2],
        "prs": prs[:1],
        "status": time_status(),
        "top_repo": top_repo,
        "uptime": _account_uptime(),
    }

# ── RENDERING ENGINE ────────────────────────────────────────────────────────

def render(stats, weather=None):
    svg = []

    # ── scanline pattern ──────────────────────────────────────────────────
    defs = f"""
    <defs>
      <pattern id="scan" x="0" y="0" width="{W}" height="3" patternUnits="userSpaceOnUse">
        <rect x="0" y="0" width="{W}" height="1" fill="{SCANLINE}" opacity="0.55"/>
      </pattern>
      <filter id="glow" x="-10%" y="-10%" width="120%" height="120%">
        <feGaussianBlur in="SourceGraphic" stdDeviation="1.5" result="blur"/>
        <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
      </filter>
    </defs>
    """

    # ── derive extra stats ────────────────────────────────────────────────
    days_since = 999
    if stats["pushes"]:
        try:
            last_ts = stats["pushes"][0][1]
            dt = datetime.fromisoformat(last_ts.replace("Z", "+00:00"))
            days_since = (datetime.now(timezone.utc) - dt).total_seconds() / 86400
        except Exception:
            pass

    signal_str, signal_lvl = _signal_blocks(days_since)
    signal_color = [ACCENT_RED, ACCENT_AMB, ACCENT_AMB, BAR_FULL, PHOSPHOR, PHOSPHOR][signal_lvl]
    
    uptime = stats.get("uptime", "")
    top_repo = stats.get("top_repo", "")

    # ── TOP BAR (name + weather) ──────────────────────────────────────────
    cur_y = 48  # Increased initial Y padding

    # boot line
    svg.append(_t(PAD, cur_y - 16, "BROPAL-STATS-CARD v4.0 :: INITIALISED", VERY_DIM, size=9, spacing=0.8))

    # name — big, cyan, glowing
    svg.append(
        f'<text x="{PAD}" y="{cur_y + 10}" fill="{ACCENT_CYAN}" font-size="30" '
        f'font-weight="700" font-family="{MONO}" filter="url(#glow)" letter-spacing="2">'
        f'{stats["name"]}</text>\n'
    )

    # @handle right-aligned
    svg.append(_t(W - PAD, cur_y + 10, f"@{stats['username']}", DIM, size=11, anchor="end"))

    cur_y += 32  # Spaced out from name

    # status row
    svg.append(
        f'<text x="{PAD}" y="{cur_y}" fill="{DIM}" font-size="11" font-family="{MONO}">'
        f'<tspan fill="{ACCENT_AMB}">❯</tspan>  {html.escape(stats["status"])}'
        f'</text>\n'
    )

    # weather — top right, same row
    if weather:
        wx_str = f'{weather["glyph"]} {weather["temp"]}°C  {weather["desc"]}'
        svg.append(
            f'<text x="{W - PAD}" y="{cur_y}" fill="{ACCENT_AMB}" font-size="11" '
            f'font-family="{MONO}" text-anchor="end">{html.escape(wx_str)}</text>\n'
        )

    cur_y += 28  # Spaced out

    # signal + uptime row
    svg.append(
        f'<text x="{PAD}" y="{cur_y}" fill="{signal_color}" font-size="11" font-family="{MONO}">'
        f'SIG {signal_str}</text>\n'
    )
    if uptime:
        svg.append(_t(W - PAD, cur_y, f"UPTIME {uptime}", VERY_DIM, size=10, anchor="end"))

    cur_y += 32  # Spaced out

    # ── SECTION: LANGUAGES ────────────────────────────────────────────────
    hdr, cur_y = _section("LANGUAGE USAGE IN REPOS", cur_y)
    svg.append(hdr)

    for lang, _, pct in stats["top_langs"]:
        color = LANG_COLORS.get(lang, DIM)
        bar = _ascii_bar(pct, width=24) # wider bar
        name_col = f"{lang:<14}"
        pct_col = f"{pct:>3}%"

        svg.append(
            f'<text x="{PAD}" y="{cur_y}" font-size="12" font-family="{MONO}">'
            f'<tspan fill="{PHOSPHOR}">{name_col}</tspan>'
            f'<tspan fill="{color}"> {bar} </tspan>'
            f'<tspan fill="{DIM}">{pct_col}</tspan>'
            f'</text>\n'
        )
        cur_y += 24 # Spaced out rows

    cur_y += 12

    # ── SECTION: ACTIVITY ─────────────────────────────────────────────────
    hdr, cur_y = _section("RECENT ACTIVITY", cur_y)
    svg.append(hdr)

    events = []
    events.extend([("push", name, ts) for name, ts in stats["pushes"]])
    events.extend([("pr", label, ts) for label, ts in stats["prs"]])

    for kind, label, ts in events[:3]:
        is_push = kind == "push"
        badge = "PUSH" if is_push else "PR  "
        color = PHOSPHOR if is_push else ACCENT_CYAN
        ago = _ago(ts)
        
        svg.append(
            f'<text x="{PAD}" y="{cur_y}" font-size="11.5" font-family="{MONO}">'
            f'<tspan fill="{VERY_DIM}">[</tspan>'
            f'<tspan fill="{color}">{badge}</tspan>'
            f'<tspan fill="{VERY_DIM}">]</tspan>'
            f'<tspan fill="{PHOSPHOR}"> {html.escape(label[:36])}</tspan>'
            f'<tspan fill="{DIM}">  +{ago}</tspan>'
            f'</text>\n'
        )
        cur_y += 24 # Spaced out rows

    if top_repo:
        cur_y += 6
        svg.append(
            f'<text x="{PAD}" y="{cur_y}" font-size="11" font-family="{MONO}">'
            f'<tspan fill="{VERY_DIM}">★ TOP REPO </tspan>'
            f'<tspan fill="{ACCENT_AMB}" font-weight="600">{html.escape(top_repo[:40])}</tspan>'
            f'</text>\n'
        )
        cur_y += 24 # Spaced out rows

    cur_y += 12

    # ── SECTION: STATS ────────────────────────────────────────────────────
    hdr, cur_y = _section("LIFE STATS", cur_y)
    svg.append(hdr)

    def _stat_row(key, val, val_color=PHOSPHOR):
        total = 48 # Increased to spread dots more widely across wider screen
        dots = "·" * max(2, total - len(key) - len(str(val)) - 2)
        return (
            f'<text x="{PAD}" y="{cur_y}" font-size="12" font-family="{MONO}">'
            f'<tspan fill="{DIM}">{key} </tspan>'
            f'<tspan fill="{VERY_DIM}">{dots} </tspan>'
            f'<tspan fill="{val_color}" font-weight="600">{val}</tspan>'
            f'</text>\n'
        )

    rows_data = [
        ("REPOS", _fmt(stats["repos"]), ACCENT_CYAN),
        ("STARS", _fmt(stats["stars"]), ACCENT_AMB),
        ("FOLLOWERS", _fmt(stats["followers"]), PHOSPHOR),
    ]
    
    for key, val, col in rows_data:
        svg.append(_stat_row(key, val, col))
        cur_y += 24 # Spaced out rows

    cur_y += 16

    # ── FOOTER ────────────────────────────────────────────────────────────
    svg.append(_line(PAD, cur_y, W - PAD, cur_y, stroke=VERY_DIM))
    cur_y += 20
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M UTC")
    svg.append(
        f'<text x="{PAD}" y="{cur_y}" fill="{VERY_DIM}" font-size="9" font-family="{MONO}" letter-spacing="0.5">'
        f'generated {now_str}  //  bropal404.github.io'
        f'</text>\n'
    )

    H = cur_y + 28

    # ── ASSEMBLE ──────────────────────────────────────────────────────────
    body = "".join(svg)
    return f"""<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">
    <rect width="{W}" height="{H}" fill="{BG}"/>
    {defs}
    <rect width="{W}" height="{H}" fill="url(#scan)"/>
    {body}
    </svg>"""

# ── MAIN CGI EXECUTABLE ─────────────────────────────────────────────────────

def main():
    params = urllib.parse.parse_qs(os.environ.get("QUERY_STRING", ""))
    user = params.get("user", [DEFAULT_USER])[0].strip() or DEFAULT_USER
    city = params.get("city", ["Hyderabad"])[0].strip()

    print("Content-Type: image/svg+xml")
    print(f"Cache-Control: public, max-age={CACHE_SECS}")
    print()

    stats = get_stats(user)
    weather = get_weather(city)

    if stats:
        print(render(stats, weather=weather))
    else:
        print(error_svg(f"Could not fetch GitHub stats for: {user}"))

if __name__ == "__main__":
    main()