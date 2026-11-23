#!/usr/bin/env python3
"""
Generate animated New-Chinese calligraphy brush GitHub contribution SVGs
(light Xuan-paper & dark inkstone themes) using pure CSS keyframes (zero JS).

A mineral-green-dipped calligraphy brush glides chronologically across every
active contribution day, pressing down and lingering longer on darker days as
green ink blooms into the paper.
"""

from __future__ import annotations

import datetime as dt
import json
import math
import os
import re
import sys
import urllib.request
from pathlib import Path

USERNAME = os.environ.get("GITHUB_USERNAME", "says693")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "").strip()

MONTH_ZH = {
    1: "一月", 2: "二月", 3: "三月", 4: "四月",
    5: "五月", 6: "六月", 7: "七月", 8: "八月",
    9: "九月", 10: "十月", 11: "十一月", 12: "十二月",
}

LEVEL_MAP = {
    "NONE": 0,
    "FIRST_QUARTILE": 1,
    "SECOND_QUARTILE": 2,
    "THIRD_QUARTILE": 3,
    "FOURTH_QUARTILE": 4,
}

THEMES = {
    "light": {
        "card_bg": "#FAF8F4",
        "card_border": "#1E4D45",
        "card_border_op": "0.16",
        "inner_border_op": "0.07",
        "corner": "#1E4D45",
        "title": "#1C2321",
        "muted": "#5E746F",
        "cinnabar": "#B83B32",
        "cell_stroke": "#E2DDD2",
        "levels": [
            "#EFECE4",  # 0: blank Xuan paper
            "#BCE3D3",  # 1: pale celadon
            "#7AC4A8",  # 2: bamboo green
            "#379474",  # 3: pine emerald
            "#165A46",  # 4: deep mineral teal-green
        ],
        "halo": "#2E9E76",
        "shaft_a": "#8D6A4B",
        "shaft_b": "#5C402A",
        "shaft_node": "#3D2919",
        "ferrule_a": "#ECE5D7",
        "ferrule_b": "#C8BFA9",
        "hair_top": "#F1ECE2",
        "hair_mid": "#35A37B",
        "hair_tip": "#13523D",
        "hair_gloss": "#B7F5DD",
        "shadow": "#102822",
    },
    "dark": {
        "card_bg": "#121820",
        "card_border": "#69AEA2",
        "card_border_op": "0.20",
        "inner_border_op": "0.09",
        "corner": "#69AEA2",
        "title": "#E5ECE9",
        "muted": "#7C9892",
        "cinnabar": "#D65A4F",
        "cell_stroke": "#24303B",
        "levels": [
            "#1B232C",  # 0: inkstone blank
            "#1B493D",  # 1: subtle jade ink
            "#28735E",  # 2: misty bamboo
            "#3FA686",  # 3: bright mineral emerald
            "#6BE0B8",  # 4: luminous malachite
        ],
        "halo": "#56D4A8",
        "shaft_a": "#B48E6A",
        "shaft_b": "#75553A",
        "shaft_node": "#4B3522",
        "ferrule_a": "#3B4C48",
        "ferrule_b": "#253230",
        "hair_top": "#DCE4E0",
        "hair_mid": "#44B890",
        "hair_tip": "#7BF0C6",
        "hair_gloss": "#D8FFF0",
        "shadow": "#000000",
    },
}


def fetch_via_graphql(username: str, token: str):
    query = """
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                date
                contributionCount
                contributionLevel
                weekday
              }
            }
          }
        }
      }
    }
    """
    body = json.dumps({"query": query, "variables": {"login": username}}).encode("utf-8")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "says693-ink-brush-generator",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    cal = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    weeks = []
    for w_idx, week in enumerate(cal["weeks"]):
        week_days = []
        for d in week["contributionDays"]:
            week_days.append({
                "date": d["date"],
                "level": LEVEL_MAP.get(d["contributionLevel"], 0),
                "count": int(d["contributionCount"]),
                "week": w_idx,
                "weekday": int(d["weekday"]),
            })
        weeks.append(week_days)
    return int(cal["totalContributions"]), weeks


def fetch_via_public_html(username: str):
    url = f"https://github.com/users/{username}/contributions"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        html = resp.read().decode("utf-8", errors="ignore")

    m_total = re.search(r"([\d,]+)\s+contributions?\s+in\s+the\s+last\s+year", html)
    total = int(m_total.group(1).replace(",", "")) if m_total else 0

    raw_days = []
    for tag in re.findall(r'<td[^>]*class="ContributionCalendar-day"[^>]*>', html):
        dm = re.search(r'data-date="(\d{4}-\d{2}-\d{2})"', tag)
        lm = re.search(r'data-level="(\d)"', tag)
        if dm and lm:
            raw_days.append((dm.group(1), int(lm.group(1))))

    raw_days.sort(key=lambda x: x[0])
    if not raw_days:
        raise RuntimeError(f"Could not parse contribution days for {username}")

    first_dt = dt.date.fromisoformat(raw_days[0][0])
    # GitHub contribution weeks begin on Sunday (Sunday=0 .. Saturday=6)
    first_sunday_offset = (first_dt.weekday() + 1) % 7
    grid_start = first_dt - dt.timedelta(days=first_sunday_offset)

    weeks_map: dict[int, list[dict]] = {}
    for date_str, level in raw_days:
        cur = dt.date.fromisoformat(date_str)
        delta = (cur - grid_start).days
        w_idx = delta // 7
        weekday = delta % 7
        weeks_map.setdefault(w_idx, []).append({
            "date": date_str,
            "level": level,
            "count": level,
            "week": w_idx,
            "weekday": weekday,
        })

    weeks = [sorted(weeks_map[k], key=lambda x: x["weekday"]) for k in sorted(weeks_map)]
    return total, weeks


def load_contributions(username: str):
    if GITHUB_TOKEN:
        try:
            return fetch_via_graphql(username, GITHUB_TOKEN)
        except Exception as exc:
            print(f"[warn] GraphQL fetch failed ({exc}), falling back to public HTML...", file=sys.stderr)
    return fetch_via_public_html(username)


def build_timeline(active_days: list[dict], cell_coords: dict[str, tuple[float, float]]):
    """
    Compute per-day arrive/leave timestamps so deeper levels dwell dramatically longer.
    Base dwell durations:
      Level 1: 0.24s (light tap)
      Level 2: 0.54s (gentle pause)
      Level 3: 1.00s (steady press)
      Level 4: 1.68s (deep lingering ink soak)
    """
    base_dwell = {1: 0.24, 2: 0.54, 3: 1.00, 4: 1.68}
    n = len(active_days)
    if n == 0:
        return [], 12.0, 9.0, 10.5

    # Compute raw timing first, then normalize only if total cycle gets overly long (>48s)
    raw_steps = []
    t = 0.85  # initial brush entry glide
    prev_pos = None
    for d in active_days:
        cx, cy = cell_coords[d["date"]]
        if prev_pos is not None:
            dist = math.hypot(cx - prev_pos[0], cy - prev_pos[1])
            travel = min(0.48, max(0.14, 0.12 + dist / 460.0))
        else:
            travel = 0.0
        t += travel
        arrive = t
        dwell = base_dwell.get(d["level"], 0.35)
        leave = arrive + dwell
        raw_steps.append({
            "day": d,
            "cx": cx,
            "cy": cy,
            "prev_pos": prev_pos,
            "travel": travel,
            "arrive": arrive,
            "leave": leave,
            "dwell": dwell,
        })
        t = leave
        prev_pos = (cx, cy)

    paint_span = t
    # Keep total animation gracefully between ~16s and ~46s while preserving exact dwell ratios
    scale = 1.0
    if paint_span > 40.0:
        scale = 40.0 / paint_span
    elif paint_span < 12.0:
        scale = 12.0 / paint_span

    steps = []
    for s in raw_steps:
        steps.append({
            **s,
            "travel": s["travel"] * scale,
            "arrive": s["arrive"] * scale,
            "leave": s["leave"] * scale,
            "dwell": s["dwell"] * scale,
        })

    finish_paint = paint_span * scale
    rest_hold = 3.8
    fade_start = finish_paint + rest_hold
    fade_end = fade_start + 1.15
    total_dur = fade_end + 0.45
    return steps, total_dur, fade_start, fade_end


def pct(t: float, total: float) -> str:
    val = max(0.0, min(100.0, (t / total) * 100.0))
    return f"{val:.3f}%"


def render_svg(theme_name: str, total_contributions: int, weeks: list[list[dict]]) -> str:
    th = THEMES[theme_name]
    width, height = 880, 214

    num_weeks = len(weeks)
    cell_size = 11.4
    pitch = 14.4
    grid_w = num_weeks * pitch - (pitch - cell_size)
    grid_x = (width - grid_w) / 2.0
    grid_y = 78.0

    # Gather all cells and centers
    all_days = []
    cell_coords: dict[str, tuple[float, float]] = {}
    for w_idx, w_days in enumerate(weeks):
        for d in w_days:
            x = grid_x + w_idx * pitch
            y = grid_y + d["weekday"] * pitch
            cx = x + cell_size / 2.0
            cy = y + cell_size / 2.0
            d_copy = {**d, "x": x, "y": y, "cx": cx, "cy": cy}
            all_days.append(d_copy)
            cell_coords[d["date"]] = (cx, cy)

    active_days = [d for d in all_days if d["level"] > 0]
    active_days.sort(key=lambda d: d["date"])

    steps, total_dur, fade_start, fade_end = build_timeline(active_days, cell_coords)

    # Month labels along bottom (avoid crowding adjacent labels)
    month_labels = []
    seen_month = None
    last_label_x = -999.0
    for w_idx, w_days in enumerate(weeks):
        if not w_days:
            continue
        cur_dt = dt.date.fromisoformat(w_days[0]["date"])
        ym = (cur_dt.year, cur_dt.month)
        x = grid_x + w_idx * pitch
        if ym != seen_month and (x - last_label_x) >= 52.0:
            seen_month = ym
            last_label_x = x
            month_labels.append((x, MONTH_ZH[cur_dt.month]))

    uid = theme_name[0]
    # Build CSS keyframes for each active cell & ink-bloom halo (theme-prefixed for zero collision)
    css_lines = []
    c0, c1, c2, c3, c4 = th["levels"]
    ramp_by_level = {
        1: [c0, c1],
        2: [c0, c1, c2],
        3: [c0, c1, c2, c3],
        4: [c0, c1, c2, c3, c4],
    }

    for idx, s in enumerate(steps):
        lv = s["day"]["level"]
        ramp = ramp_by_level[lv]
        final_c = ramp[-1]
        a_t = s["arrive"]
        l_t = s["leave"]
        dwell = max(0.01, l_t - a_t)

        # Cell ink saturation progression spanning the entire dwell window
        kf_parts = [f"0%,{pct(max(0.0, a_t - 0.02), total_dur)}{{fill:{c0}}}"]
        for r_i in range(1, len(ramp)):
            frac = r_i / (len(ramp) - 1)
            kf_parts.append(f"{pct(a_t + dwell * frac, total_dur)}{{fill:{ramp[r_i]}}}")
        kf_parts.append(f"{pct(fade_start, total_dur)}{{fill:{final_c}}}")
        kf_parts.append(f"{pct(fade_end, total_dur)},100%{{fill:{c0}}}")
        css_lines.append(f"@keyframes {uid}d{idx}{{{''.join(kf_parts)}}}")
        css_lines.append(f".{uid}d{idx}{{animation:{uid}d{idx} {total_dur:.2f}s linear infinite}}")

        # Ink seepage halo for active cells (stronger & wider on deeper days)
        halo_op = {1: 0.28, 2: 0.42, 3: 0.54, 4: 0.68}[lv]
        halo_scale = {1: 1.32, 2: 1.58, 3: 1.92, 4: 2.35}[lv]
        h_mid = a_t + dwell * 0.44
        h_end = min(fade_start - 0.05, l_t + 0.36)
        h_kf = (
            f"0%,{pct(max(0.0, a_t - 0.02), total_dur)}{{opacity:0;transform:scale(0.45)}}"
            f"{pct(h_mid, total_dur)}{{opacity:{halo_op};transform:scale({halo_scale * 0.72:.2f})}}"
            f"{pct(h_end, total_dur)},100%{{opacity:0;transform:scale({halo_scale:.2f})}}"
        )
        css_lines.append(f"@keyframes {uid}h{idx}{{{h_kf}}}")
        css_lines.append(f".{uid}h{idx}{{animation:{uid}h{idx} {total_dur:.2f}s ease-out infinite}}")

    # Build calligraphy brush trajectory keyframes (lift -> glide -> press -> linger -> lift)
    brush_kf = []
    if steps:
        first_cx, first_cy = steps[0]["cx"], steps[0]["cy"]
        entry_x = min(width - 44.0, first_cx + 34.0)
        entry_y = max(36.0, first_cy - 30.0)
        brush_kf.append(
            f"0%{{opacity:0;transform:translate({entry_x:.1f}px,{entry_y:.1f}px) rotate(10deg)}}"
        )
        brush_kf.append(
            f"{pct(0.28, total_dur)}{{opacity:1;transform:translate({entry_x:.1f}px,{entry_y:.1f}px) rotate(7deg)}}"
        )

        for idx, s in enumerate(steps):
            cx, cy = s["cx"], s["cy"]
            lv = s["day"]["level"]
            a_t, l_t, dwell = s["arrive"], s["leave"], s["dwell"]

            # Mid-air lift when gliding from previous active day
            if idx > 0 and s["prev_pos"] is not None:
                px, py = s["prev_pos"]
                mid_t = a_t - s["travel"] * 0.50
                mx = (px + cx) / 2.0
                my = (py + cy) / 2.0 - min(12.0, 5.5 + math.hypot(cx - px, cy - py) * 0.04)
                brush_kf.append(
                    f"{pct(mid_t, total_dur)}{{opacity:1;transform:translate({mx:.1f}px,{my:.1f}px) rotate(5deg) scale(1,1)}}"
                )

            # Touchdown on active cell
            press_rot = {1: -1.5, 2: -3.0, 3: -4.5, 4: -6.2}[lv]
            press_dy = {1: 0.4, 2: 0.8, 3: 1.4, 4: 2.0}[lv]
            splay_x = {1: 1.02, 2: 1.05, 3: 1.08, 4: 1.12}[lv]
            splay_y = {1: 0.99, 2: 0.97, 3: 0.95, 4: 0.92}[lv]
            brush_kf.append(
                f"{pct(a_t, total_dur)}{{opacity:1;transform:translate({cx:.1f}px,{cy:.1f}px) rotate(-1deg) scale(1,1)}}"
            )
            # Deeper days sink gently into Xuan paper with subtle bristle splay while soaking pigment
            if lv >= 2:
                brush_kf.append(
                    f"{pct(a_t + dwell * 0.35, total_dur)}{{opacity:1;transform:translate({cx:.1f}px,{cy + press_dy:.1f}px) rotate({press_rot:.1f}deg) scale({splay_x:.2f},{splay_y:.2f})}}"
                )
                brush_kf.append(
                    f"{pct(a_t + dwell * 0.82, total_dur)}{{opacity:1;transform:translate({cx:.1f}px,{cy + press_dy * 0.9:.1f}px) rotate({press_rot * 0.9:.1f}deg) scale({splay_x:.2f},{splay_y:.2f})}}"
                )
            brush_kf.append(
                f"{pct(l_t, total_dur)}{{opacity:1;transform:translate({cx:.1f}px,{cy:.1f}px) rotate(0deg) scale(1,1)}}"
            )

        # Graceful lift-off to rest in top-right margin after completing the scroll
        last_cx, last_cy = steps[-1]["cx"], steps[-1]["cy"]
        rest_x = min(width - 48.0, max(last_cx + 16.0, width - 88.0))
        rest_y = 48.0
        lift_t = steps[-1]["leave"] + 0.75
        brush_kf.append(
            f"{pct(lift_t, total_dur)}{{opacity:0.92;transform:translate({rest_x:.1f}px,{rest_y:.1f}px) rotate(11deg) scale(1,1)}}"
        )
        brush_kf.append(
            f"{pct(fade_start, total_dur)}{{opacity:0.92;transform:translate({rest_x:.1f}px,{rest_y:.1f}px) rotate(11deg) scale(1,1)}}"
        )
        brush_kf.append(
            f"{pct(fade_start + 0.65, total_dur)},100%{{opacity:0;transform:translate({rest_x + 12:.1f}px,{rest_y - 8:.1f}px) rotate(14deg) scale(1,1)}}"
        )

    css_lines.append(f"@keyframes brushMove-{uid}{{{''.join(brush_kf)}}}")
    css_lines.append(f".brush-mover-{uid}{{animation:brushMove-{uid} {total_dur:.2f}s linear infinite}}")

    # Map date -> active index for SVG class binding
    active_index_by_date = {s["day"]["date"]: idx for idx, s in enumerate(steps)}

    # Render cells & halo layer
    cell_elems = []
    halo_elems = []
    for d in all_days:
        x, y, cx, cy = d["x"], d["y"], d["cx"], d["cy"]
        if d["date"] in active_index_by_date:
            idx = active_index_by_date[d["date"]]
            cell_elems.append(
                f'<rect class="{uid}d{idx}" x="{x:.1f}" y="{y:.1f}" width="{cell_size:.1f}" height="{cell_size:.1f}" rx="2.4" fill="{c0}" stroke="{th["cell_stroke"]}" stroke-width="0.45"/>'
            )
            halo_elems.append(
                f'<g transform="translate({cx:.1f},{cy:.1f})"><circle class="{uid}h{idx}" cx="0" cy="0" r="6" fill="none" stroke="{th["halo"]}" stroke-width="1.35" opacity="0"/></g>'
            )
        else:
            cell_elems.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell_size:.1f}" height="{cell_size:.1f}" rx="2.4" fill="{c0}" stroke="{th["cell_stroke"]}" stroke-width="0.45"/>'
            )

    month_elems = [
        f'<text x="{mx:.1f}" y="{grid_y + 7 * pitch + 14:.1f}" class="serif" font-size="10.2" fill="{th["muted"]}">{mlabel}</text>'
        for mx, mlabel in month_labels
    ]

    # Legend swatches on top-right
    legend_x = 738
    legend_rects = []
    for lv_i, lv_col in enumerate(th["levels"]):
        lx = legend_x + lv_i * 15
        legend_rects.append(
            f'<rect x="{lx}" y="31" width="10.5" height="10.5" rx="2" fill="{lv_col}" stroke="{th["cell_stroke"]}" stroke-width="0.45"/>'
        )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="点染 · 墨迹历：蘸满绿墨的毛笔逐日点染近一年 {total_contributions} 次提交">
  <defs>
    <!-- Calligraphy brush bristle gradient: off-white goat hair soaked in mineral green pigment at tip -->
    <linearGradient id="bristle-{uid}" x1="0" y1="1" x2="0" y2="0">
      <stop offset="0%" stop-color="{th['hair_tip']}"/>
      <stop offset="46%" stop-color="{th['hair_mid']}"/>
      <stop offset="78%" stop-color="{th['hair_top']}"/>
      <stop offset="100%" stop-color="{th['hair_top']}"/>
    </linearGradient>
    <!-- Bamboo brush shaft gradient -->
    <linearGradient id="shaft-{uid}" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{th['shaft_b']}"/>
      <stop offset="42%" stop-color="{th['shaft_a']}"/>
      <stop offset="100%" stop-color="{th['shaft_b']}"/>
    </linearGradient>
    <!-- Ferrule gradient -->
    <linearGradient id="ferrule-{uid}" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{th['ferrule_b']}"/>
      <stop offset="48%" stop-color="{th['ferrule_a']}"/>
      <stop offset="100%" stop-color="{th['ferrule_b']}"/>
    </linearGradient>
    <style>
      .serif {{ font-family: 'Songti SC', 'Noto Serif SC', 'Source Han Serif SC', 'STSong', 'SimSun', Georgia, serif; }}
      .mono  {{ font-family: 'JetBrains Mono', 'Cascadia Code', Consolas, monospace; }}
      {''.join(css_lines)}
    </style>
  </defs>

  <!-- Card Frame (matches calling-card & manifesto width) -->
  <rect x="8" y="8" width="864" height="{height - 16}" rx="4" fill="{th['card_bg']}" stroke="{th['card_border']}" stroke-opacity="{th['card_border_op']}" stroke-width="1"/>
  <rect x="14" y="14" width="852" height="{height - 28}" rx="2" fill="none" stroke="{th['card_border']}" stroke-opacity="{th['inner_border_op']}" stroke-width="0.75"/>

  <!-- Corner brackets -->
  <g stroke="{th['corner']}" stroke-width="1.4" fill="none" stroke-linecap="square" opacity="0.72">
    <path d="M8 21 V8 H21"/>
    <path d="M859 8 H872 V21"/>
    <path d="M8 {height - 21} V{height - 8} H21"/>
    <path d="M859 {height - 8} H872 V{height - 21}"/>
  </g>

  <!-- Header row -->
  <rect x="44" y="32" width="4.5" height="4.5" rx="0.8" fill="{th['cinnabar']}"/>
  <text x="56" y="40.5" class="serif" font-size="13.5" font-weight="600" fill="{th['title']}" letter-spacing="2.5">点染 · 墨迹历</text>
  <text x="166" y="40" class="mono" font-size="11" fill="{th['muted']}">· 近一年共落墨 {total_contributions} 笔（{len(active_days)} 个活动日 · 浓墨久驻）</text>

  <!-- Mineral green pigment legend -->
  <text x="729" y="40" class="serif" font-size="10.5" fill="{th['muted']}" text-anchor="end">淡</text>
  {''.join(legend_rects)}
  <text x="820" y="40" class="serif" font-size="10.5" fill="{th['muted']}">浓</text>

  <!-- Contribution grid cells -->
  <g>
    {''.join(cell_elems)}
  </g>

  <!-- Translucent wet-ink seepage halos -->
  <g>
    {''.join(halo_elems)}
  </g>

  <!-- Month labels -->
  <g>
    {''.join(month_elems)}
  </g>

  <!-- Animated Chinese Calligraphy Brush dipped in mineral green pigment -->
  <!-- Origin (0, 0) is the exact sharp bristle tip touching the cell center -->
  <g class="brush-mover-{uid}" opacity="0">
    <!-- Soft contact shadow on Xuan paper -->
    <ellipse cx="4.5" cy="2.6" rx="7.2" ry="2.4" fill="{th['shadow']}" opacity="0.16"/>
    <!-- Brush body tilted gracefully at 34deg (handle extending upper-right) -->
    <g transform="rotate(34) scale(1.10)">
      <!-- Goat-hair bristle belly & mineral-green soaked tip -->
      <path d="M 0 0 C -2.8 -4.5, -5.2 -10.5, -4.4 -18.5 C -4.0 -21.2, -3.2 -23.0, -3.0 -24.0 L 3.0 -24.0 C 3.2 -23.0, 4.0 -21.2, 4.4 -18.5 C 5.2 -10.5, 2.8 -4.5, 0 0 Z" fill="url(#bristle-{uid})"/>
      <!-- Wet pigment gleam near tip -->
      <path d="M -0.4 -2.2 C -1.8 -5.5, -2.6 -9.8, -2.0 -14.2" fill="none" stroke="{th['hair_gloss']}" stroke-width="0.95" stroke-linecap="round" opacity="0.62"/>
      <!-- Tiny extra saturated green ink drop at very tip -->
      <path d="M 0 0 C -1.3 -2.2, -2.0 -4.8, -1.6 -7.2 C -0.6 -6.2, 0.6 -6.2, 1.6 -7.2 C 2.0 -4.8, 1.3 -2.2, 0 0 Z" fill="{th['hair_tip']}" opacity="0.88"/>
      <!-- Horn / ivory ferrule (笔斗) -->
      <rect x="-3.4" y="-31.5" width="6.8" height="8.0" rx="1.2" fill="url(#ferrule-{uid})"/>
      <line x1="-3.4" y1="-24.0" x2="3.4" y2="-24.0" stroke="{th['shaft_node']}" stroke-width="0.8" opacity="0.55"/>
      <line x1="-3.4" y1="-31.2" x2="3.4" y2="-31.2" stroke="{th['shaft_node']}" stroke-width="0.8" opacity="0.55"/>
      <!-- Slender bamboo shaft (笔管) -->
      <path d="M -3.0 -31.5 L -2.3 -82.0 C -2.2 -84.0, 2.2 -84.0, 2.3 -82.0 L 3.0 -31.5 Z" fill="url(#shaft-{uid})"/>
      <!-- Bamboo node rings -->
      <line x1="-2.8" y1="-48.0" x2="2.8" y2="-48.0" stroke="{th['shaft_node']}" stroke-width="1.0" opacity="0.65"/>
      <line x1="-2.5" y1="-67.0" x2="2.5" y2="-67.0" stroke="{th['shaft_node']}" stroke-width="1.0" opacity="0.65"/>
      <!-- Cinnabar end cap & subtle cord bead (朱砂笔顶) -->
      <rect x="-2.4" y="-85.5" width="4.8" height="4.2" rx="1.2" fill="{th['cinnabar']}"/>
      <circle cx="0" cy="-87.2" r="1.4" fill="none" stroke="{th['cinnabar']}" stroke-width="0.9" opacity="0.85"/>
    </g>
  </g>
</svg>
"""
    return svg


def main():
    out_dir = Path(__file__).resolve().parent.parent / "assets"
    out_dir.mkdir(parents=True, exist_ok=True)

    total, weeks = load_contributions(USERNAME)
    print(f"[ink-brush] Loaded {USERNAME}: {total} contributions across {len(weeks)} weeks")

    for theme_name in ("light", "dark"):
        svg_text = render_svg(theme_name, total, weeks)
        target = out_dir / f"ink-brush-{theme_name}.svg"
        target.write_text(svg_text, encoding="utf-8")
        print(f"[ink-brush] Wrote {target} ({len(svg_text.encode('utf-8'))} bytes)")


if __name__ == "__main__":
    main()
