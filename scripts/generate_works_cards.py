#!/usr/bin/env python3
"""
Generate 2x3 New-Chinese clickable project plaque SVGs (博古架 · 器物签牌)
for both Light (Xuan-paper) and Dark (Inkstone) GitHub themes.
"""

from pathlib import Path

WORKS = [
    {
        "id": "tack",
        "seal": "折",
        "seal_style": "cinnabar",
        "title": "折页 FOLD",
        "repo": "says693/tack",
        "lang": "TypeScript",
        "lang_color_l": "#1E4D45",
        "lang_color_d": "#69AEA2",
        "desc": "连接自己的 AI，依可信资料生成离线本地课程",
    },
    {
        "id": "island",
        "seal": "岛",
        "seal_style": "teal",
        "title": "灵动岛",
        "repo": "says693/dsh-composer-dynamic-island",
        "lang": "JavaScript",
        "lang_color_l": "#B08223",
        "lang_color_d": "#DFB553",
        "desc": "为 DSH 网页端裁一方克制紧凑的交互灵动岛",
    },
    {
        "id": "scatter",
        "seal": "散",
        "seal_style": "teal",
        "title": "散句",
        "repo": "says693/dsh-scatter",
        "lang": "JavaScript",
        "lang_color_l": "#B08223",
        "lang_color_d": "#DFB553",
        "desc": "DSH 输入区 Prompt 改写与多候选流式推演",
    },
    {
        "id": "tern",
        "seal": "译",
        "seal_style": "teal",
        "title": "译事",
        "repo": "says693/tern-omp-zh",
        "lang": "JavaScript",
        "lang_color_l": "#B08223",
        "lang_color_d": "#DFB553",
        "desc": "Tern / omp 简体中文汉化包与自动维护 CLI",
    },
    {
        "id": "tui",
        "seal": "协",
        "seal_style": "outline",
        "title": "dsh-TUI",
        "repo": "ccch1mneyyy/dsh-TUI",
        "lang": "TypeScript",
        "lang_color_l": "#1E4D45",
        "lang_color_d": "#69AEA2",
        "desc": "DSH 官方首推的高性能终端 TUI 交互插件",
    },
    {
        "id": "go",
        "seal": "协",
        "seal_style": "outline",
        "title": "dsh-Go",
        "repo": "ccch1mneyyy/dsh-Go",
        "lang": "Dart",
        "lang_color_l": "#23748C",
        "lang_color_d": "#5BC0DE",
        "desc": "把 DeepSeek Harness 装进口袋的移动端工具",
    },
]

THEMES = {
    "light": {
        "bg": "#FAF8F4",
        "border": "#1E4D45",
        "border_op": "0.18",
        "inner_op": "0.07",
        "corner": "#1E4D45",
        "title": "#1C2321",
        "repo": "#5D736E",
        "desc": "#364642",
        "divider": "#1E4D45",
        "cinnabar": "#B83B32",
        "teal": "#1E4D45",
        "seal_fg": "#FAF8F4",
        "arrow": "#B83B32",
        "tag_bg": "#F1EFE9",
    },
    "dark": {
        "bg": "#121820",
        "border": "#69AEA2",
        "border_op": "0.22",
        "inner_op": "0.09",
        "corner": "#69AEA2",
        "title": "#E6EEEC",
        "repo": "#7E9A94",
        "desc": "#B7C6C2",
        "divider": "#69AEA2",
        "cinnabar": "#C94A40",
        "teal": "#266358",
        "seal_fg": "#F5F2EC",
        "arrow": "#DF6A5F",
        "tag_bg": "#19222C",
    },
}


def render_card(item: dict, theme_name: str) -> str:
    th = THEMES[theme_name]
    lang_col = item["lang_color_l"] if theme_name == "light" else item["lang_color_d"]

    if item["seal_style"] == "cinnabar":
        seal_svg = f"""
  <g transform="translate(20, 21)">
    <rect x="0" y="0" width="32" height="32" rx="3" fill="{th['cinnabar']}"/>
    <rect x="2.6" y="2.6" width="26.8" height="26.8" rx="1.4" fill="none" stroke="{th['seal_fg']}" stroke-width="0.8" opacity="0.86"/>
    <text x="16" y="21.5" class="serif" font-size="15.5" font-weight="700" fill="{th['seal_fg']}" text-anchor="middle">{item['seal']}</text>
  </g>"""
    elif item["seal_style"] == "teal":
        seal_svg = f"""
  <g transform="translate(20, 21)">
    <rect x="0" y="0" width="32" height="32" rx="3" fill="{th['teal']}"/>
    <rect x="2.6" y="2.6" width="26.8" height="26.8" rx="1.4" fill="none" stroke="{th['seal_fg']}" stroke-width="0.8" opacity="0.72"/>
    <text x="16" y="21.5" class="serif" font-size="15.5" font-weight="700" fill="{th['seal_fg']}" text-anchor="middle">{item['seal']}</text>
  </g>"""
    else:
        # Hollow cinnabar seal for community collaborations (镂空朱砂线印)
        seal_svg = f"""
  <g transform="translate(20, 21)">
    <rect x="0.6" y="0.6" width="30.8" height="30.8" rx="3" fill="none" stroke="{th['cinnabar']}" stroke-width="1.3"/>
    <rect x="3.2" y="3.2" width="25.6" height="25.6" rx="1.4" fill="none" stroke="{th['cinnabar']}" stroke-width="0.65" opacity="0.55"/>
    <text x="16" y="21.5" class="serif" font-size="15.5" font-weight="700" fill="{th['cinnabar']}" text-anchor="middle">{item['seal']}</text>
  </g>"""

    # Compute crisp right-aligned language badge width
    lang_text = item["lang"]
    pill_w = max(56, len(lang_text) * 7.1 + 24)
    pill_x = 412 - pill_w
    dot_x = pill_x + 11
    text_x = pill_x + 20

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="432" height="108" viewBox="0 0 432 108" role="img" aria-label="{item['title']} ({item['repo']}) - {item['desc']}">
  <style>
    .serif {{ font-family: 'Songti SC', 'Noto Serif SC', 'Source Han Serif SC', 'STSong', 'SimSun', Georgia, serif; }}
    .mono  {{ font-family: 'JetBrains Mono', 'Cascadia Code', Consolas, monospace; }}
    .sans  {{ font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif; }}
  </style>

  <!-- Xuan-paper / Inkstone Plaque -->
  <rect x="4" y="4" width="424" height="100" rx="4" fill="{th['bg']}" stroke="{th['border']}" stroke-opacity="{th['border_op']}" stroke-width="1"/>
  <rect x="8.5" y="8.5" width="415" height="91" rx="2" fill="none" stroke="{th['border']}" stroke-opacity="{th['inner_op']}" stroke-width="0.7"/>

  <!-- Diagonal minimalist Chinese corner brackets -->
  <g stroke="{th['corner']}" stroke-width="1.4" fill="none" stroke-linecap="square" opacity="0.78">
    <path d="M4 16 V4 H16"/>
    <path d="M416 104 H428 V92"/>
  </g>
{seal_svg}
  <!-- Title & repo slug -->
  <text x="64" y="35.5" class="serif" font-size="16" font-weight="600" fill="{th['title']}" letter-spacing="0.8">{item['title']}</text>
  <text x="64" y="52.5" class="mono" font-size="10.6" fill="{th['repo']}">{item['repo']}</text>

  <!-- Subtle traditional-color language tag -->
  <rect x="{pill_x:.1f}" y="21.5" width="{pill_w:.1f}" height="20" rx="10" fill="{th['tag_bg']}" stroke="{th['border']}" stroke-opacity="0.14" stroke-width="0.75"/>
  <circle cx="{dot_x:.1f}" cy="31.5" r="3.2" fill="{lang_col}"/>
  <text x="{text_x:.1f}" y="35" class="mono" font-size="10.2" fill="{th['repo']}">{lang_text}</text>

  <!-- Hairline divider -->
  <line x1="20" y1="65" x2="412" y2="65" stroke="{th['divider']}" stroke-opacity="0.12" stroke-width="0.85"/>

  <!-- One-line poetic/clear annotation + subtle external cue -->
  <text x="20" y="87" class="sans" font-size="12.2" fill="{th['desc']}">{item['desc']}</text>
  <text x="411" y="87.5" class="mono" font-size="12.5" fill="{th['arrow']}" text-anchor="end" opacity="0.78">↗</text>
</svg>
"""


def main():
    out_dir = Path(__file__).resolve().parent.parent / "assets"
    out_dir.mkdir(parents=True, exist_ok=True)
    for item in WORKS:
        for theme in ("light", "dark"):
            p = out_dir / f"work-{item['id']}-{theme}.svg"
            p.write_text(render_card(item, theme), encoding="utf-8")
    print(f"Generated {len(WORKS) * 2} work plaque SVGs in {out_dir}")


if __name__ == "__main__":
    main()
