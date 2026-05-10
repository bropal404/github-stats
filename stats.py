#!/usr/bin/python3
"""
GitHub Stats Card -- CGI Script (Dark Theme, v4)

Deploy:
    place in ~/public_html/cgi-bin/stats.py
    chmod +x stats.py

"""

import html
import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone


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


DEFAULT_USER = "bropal404"

W = 600
PAD = 36
BARW = W - PAD * 2

CACHE_SECS = 3600

LANG_COLORS = {
    "Python": "#3572A5",
    "JavaScript": "#f1e05a",
    "TypeScript": "#3178c6",
    "C++": "#f34b7d",
    "C": "#555555",
    "Java": "#b07219",
    "Go": "#00ADD8",
    "Rust": "#dea584",
    "HTML": "#e34c26",
    "CSS": "#563d7c",
    "Ruby": "#701516",
    "Shell": "#89e051",
    "Kotlin": "#A97BFF",
    "Swift": "#F05138",
    "Dart": "#00B4AB",
    "Lua": "#000080",
    "Haskell": "#5e5086",
    "Scala": "#c22d40",
    "R": "#198CE7",
    "MATLAB": "#e16737",
    "Jupyter Notebook": "#DA5B0B",
    "Vue": "#41b883",
    "PHP": "#4F5D95",
    "Elixir": "#6e4a7e",
    "Clojure": "#db5855",
}



def gh(path):
    token = os.environ.get("GITHUB_TOKEN", "")

    headers = {
        "User-Agent": "readme-stats/3",
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

    except Exception:
        return None


def time_ago(s):
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))

        diff = (datetime.now(timezone.utc) - dt).total_seconds()

        if diff < 3600:
            return f"{int(diff / 60)}m ago"

        if diff < 86400:
            return f"{int(diff / 3600)}h ago"

        if diff < 604800:
            return f"{int(diff / 86400)}d ago"

        return f"{int(diff / 604800)}w ago"

    except Exception:
        return ""


def fmt(n):
    return f"{n / 1000:.1f}k" if n >= 1000 else str(n)



def get_stats(username):
    user = gh(f"/users/{username}")

    if not user or "login" not in user:
        return None

    repos = gh(f"/users/{username}/repos?per_page=100&type=owner&sort=pushed") or []

    stars = 0
    forks = 0

    langs = {}

    pushes = []

    for repo in repos:
        stars += repo.get("stargazers_count", 0)
        forks += repo.get("forks_count", 0)

        language = repo.get("language")

        if language:
            langs[language] = langs.get(language, 0) + 1

        if not repo.get("fork") and repo.get("pushed_at"):
            pushes.append(
                (
                    html.escape(repo["name"][:32]),
                    repo["pushed_at"],
                )
            )

    prs_raw = gh(
        f"/search/issues?q=author:{username}+type:pr&sort=created&order=desc&per_page=3"
    )

    prs = []

    if prs_raw and "items" in prs_raw:
        for pr in prs_raw["items"]:
            title = html.escape(pr.get("title", "")[:38])

            prs.append(
                (
                    f"#{pr.get('number')} {title}",
                    pr.get("created_at", ""),
                )
            )

    top5 = sorted(
        langs.items(),
        key=lambda x: x[1],
        reverse=True,
    )[:5]

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
    }



def render(stats):
    BG = "#0d1117"
    BORDER = "#30363d"

    TEXT_PRIMARY = "#c9d1d9"
    TEXT_SECONDARY = "#8b949e"
    TEXT_MUTED = "#6e7681"
    ACCENT = "#58a6ff"

    DIVIDER = "#21262d"
    BAR_BG = "#161b22"


    name_y = 44
    user_y = name_y + 18

    bio_line = ""
    status_y = user_y + 22

    if stats["bio"]:
        bio_line = f"""
        <text
            x="{PAD}"
            y="{user_y + 18}"
            fill="{TEXT_SECONDARY}"
            font-size="12.5"
            font-family="Segoe UI, sans-serif"
        >
            {stats["bio"]}
        </text>
        """
        status_y = user_y + 38

    status_line = f"""
    <text
        x="{PAD}"
        y="{status_y}"
        fill="{TEXT_MUTED}"
        font-size="11"
        font-family="Segoe UI, sans-serif"
    >
        <tspan fill="#f0883e" font-size="12">&#9679;</tspan>  {html.escape(stats["status"])}
    </text>
    """

    div1_y = status_y + 20


    lang_header_y = div1_y + 20
    bar_y = lang_header_y + 14
    bar_h = 11

    bar_rects = ""
    bx = PAD

    for lang, _, pct in stats["top_langs"]:
        width = BARW * pct / 100
        color = LANG_COLORS.get(lang, "#8b949e")
        bar_rects += f"""
        <rect
            x="{bx:.2f}"
            y="{bar_y}"
            width="{width:.2f}"
            height="{bar_h}"
            fill="{color}"
        />
        """
        bx += width

    col_width = BARW // 3
    leg_y0 = bar_y + bar_h + 22
    leg_svg = ""

    for i, (lang, _, pct) in enumerate(stats["top_langs"]):
        col = i % 3
        row = i // 3
        lx = PAD + col * col_width
        ly = leg_y0 + row * 20
        color = LANG_COLORS.get(lang, "#8b949e")
        leg_svg += f"""
        <circle cx="{lx + 5}" cy="{ly - 5}" r="5" fill="{color}"/>
        <text
            x="{lx + 16}"
            y="{ly}"
            fill="{TEXT_PRIMARY}"
            font-size="11.5"
            font-family="Segoe UI, sans-serif"
        >
            {lang}<tspan fill="{TEXT_MUTED}" font-size="10.5"> {pct}%</tspan>
        </text>
        """

    rows = (len(stats["top_langs"]) + 2) // 3
    div2_y = leg_y0 + rows * 20 + 14


    events = []
    events.extend([("push", name, ts) for name, ts in stats["pushes"]])
    events.extend([("pr", label, ts) for label, ts in stats["prs"]])

    act_header_y = div2_y + 20
    act_y = act_header_y + 20

    act_svg = f"""
    <text
        x="{PAD}"
        y="{act_header_y}"
        fill="{TEXT_MUTED}"
        font-size="10"
        letter-spacing="0.7"
        font-family="Segoe UI, sans-serif"
    >
        RECENT ACTIVITY
    </text>
    """

    for kind, label, ts in events[:3]:
        is_push = kind == "push"
        color = "#58a6ff" if is_push else "#a371f7"
        icon = "&#8593;" if is_push else "&#10548;"
        verb = "pushed to" if is_push else "opened PR"
        ago = time_ago(ts)
        act_svg += f"""
        <text x="{PAD}" y="{act_y}" fill="{color}" font-size="13" font-family="monospace">{icon}</text>
        <text x="{PAD + 18}" y="{act_y}" fill="{TEXT_SECONDARY}" font-size="12" font-family="Segoe UI, sans-serif">
            {verb}<tspan fill="{TEXT_PRIMARY}" font-weight="600"> {label}</tspan><tspan fill="{TEXT_MUTED}" font-size="11">  {ago}</tspan>
        </text>
        """
        act_y += 21


    div3_y = act_y + 12

    slots = [
        ("REPOS", fmt(stats["repos"]), "#58a6ff", 0),
        ("STARS", fmt(stats["stars"]), "#e3b341", 1),
        ("FORKS", fmt(stats["forks"]), "#3fb950", 2),
        ("FOLLOWERS", fmt(stats["followers"]), "#a371f7", 3),
    ]

    slot_w = (W - PAD * 2) / 4
    slabel_y = div3_y + 24
    sval_y = div3_y + 50

    stats_svg = ""
    for label, val, color, idx in slots:
        sx = PAD + idx * slot_w
        stats_svg += f"""
        <text
            x="{sx:.1f}"
            y="{slabel_y}"
            fill="{TEXT_MUTED}"
            font-size="10"
            letter-spacing="0.7"
            font-family="Segoe UI, sans-serif"
        >{label}</text>
        <text
            x="{sx:.1f}"
            y="{sval_y}"
            fill="{color}"
            font-size="27"
            font-weight="700"
            font-family="Courier New, monospace"
        >{val}</text>
        """

    H = sval_y + PAD


    return f"""<svg
    width="{W}"
    height="{H}"
    viewBox="0 0 {W} {H}"
    xmlns="http://www.w3.org/2000/svg"
>
    <defs>
        <clipPath id="bc">
            <rect x="{PAD}" y="{bar_y}" width="{BARW}" height="{bar_h}" rx="4"/>
        </clipPath>
    </defs>

    <!-- Card background -->
    <rect width="{W}" height="{H}" rx="12" fill="{BG}" stroke="{BORDER}" stroke-width="1"/>

    <!-- Name -->
    <text x="{PAD}" y="{name_y}" fill="{TEXT_PRIMARY}" font-size="21" font-weight="700" font-family="Segoe UI, sans-serif">
        {stats["name"]}
    </text>

    <!-- @username -->
    <text x="{PAD}" y="{user_y}" fill="{ACCENT}" font-size="12" font-family="Courier New, monospace">
        @{stats["username"]}
    </text>

    {bio_line}

    {status_line}

    <!-- Divider 1 -->
    <line x1="{PAD}" y1="{div1_y}" x2="{W - PAD}" y2="{div1_y}" stroke="{DIVIDER}" stroke-width="1"/>

    <!-- Languages header -->
    <text x="{PAD}" y="{lang_header_y}" fill="{TEXT_MUTED}" font-size="10" letter-spacing="0.7" font-family="Segoe UI, sans-serif">
        TOP LANGUAGES
    </text>

    <!-- Language bar background -->
    <rect x="{PAD}" y="{bar_y}" width="{BARW}" height="{bar_h}" rx="4" fill="{BAR_BG}"/>

    <!-- Language bar fill -->
    <g clip-path="url(#bc)">{bar_rects}</g>

    <!-- Language bar border -->
    <rect x="{PAD}" y="{bar_y}" width="{BARW}" height="{bar_h}" rx="4" fill="none" stroke="{BORDER}" stroke-width="0.6"/>

    {leg_svg}

    <!-- Divider 2 -->
    <line x1="{PAD}" y1="{div2_y}" x2="{W - PAD}" y2="{div2_y}" stroke="{DIVIDER}" stroke-width="1"/>

    {act_svg}

    <!-- Divider 3 -->
    <line x1="{PAD}" y1="{div3_y}" x2="{W - PAD}" y2="{div3_y}" stroke="{DIVIDER}" stroke-width="1"/>

    {stats_svg}
</svg>"""



def error_svg(msg):
    return f"""
    <svg width="420" height="56" xmlns="http://www.w3.org/2000/svg">
        <rect width="420" height="56" rx="8" fill="#0d1117" stroke="#f85149" stroke-width="1"/>
        <text x="16" y="33" fill="#f85149" font-size="13" font-family="Segoe UI, sans-serif">
            {html.escape(msg)}
        </text>
    </svg>
    """



def main():
    params = urllib.parse.parse_qs(os.environ.get("QUERY_STRING", ""))

    user = params.get("user", [DEFAULT_USER])[0].strip()

    if not user:
        user = DEFAULT_USER

    print("Content-Type: image/svg+xml")
    print(f"Cache-Control: public, max-age={CACHE_SECS}")
    print()

    stats = get_stats(user)

    if stats:
        print(render(stats))
    else:
        print(error_svg(f"Could not fetch GitHub stats for: {user}"))


if __name__ == "__main__":
    main()
