"""Builds bf-header.svg and bf-footer.svg with subsetted Google Fonts embedded.

GitHub renders README SVGs through <img>, which can't load web fonts, so each
font is fetched as a woff2 subset (only the glyphs used) and inlined as base64.
  python build_banners.py            -> writes the two banners
  python build_banners.py --compare  -> also writes _tmp/compare-*.svg font options
"""
import base64
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
CHROME = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}

NAME = "Mohammed Salah Chogle"
ROLE = "Robotics & Automation Engineer"
META = "1tsMS / VESIT '27 / Navi Mumbai"
TAG = "firmware · control · rapid prototyping"
COORD = "19.03°N  73.02°E"
QUOTE = "Everything is permitted? I like the sound of that."
QUOTE_BY = "Edward Kenway"

# display font options for the name: (css family spec, css family name, size, letter-spacing, uppercase)
DISPLAY = {
    "anton": ("Anton", "Anton", 86, 1, True),
    "bebas": ("Bebas+Neue", "Bebas Neue", 96, 3, True),
    "unbounded": ("Unbounded:wght@800", "Unbounded", 50, 0, False),
    "archivo": ("Archivo+Black", "Archivo Black", 58, 0, False),
    "syne": ("Syne:wght@800", "Syne", 48, 0, False),
}
CHOICE = "anton"


def get(url, headers):
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers)) as r:
        return r.read()


def font_face(spec, family, text, weight="normal", style="normal"):
    css = get(f"https://fonts.googleapis.com/css2?family={spec}&text={urllib.parse.quote(text)}", CHROME).decode()
    url = re.search(r"url\((https://[^)]+)\)", css).group(1)
    b64 = base64.b64encode(get(url, CHROME)).decode()
    return (f"@font-face {{ font-family: '{family}'; font-weight: {weight}; font-style: {style}; "
            f"src: url(data:font/woff2;base64,{b64}) format('woff2'); }}")


SINE = "M0 0 Q37.5 -9 75 0 T150 0 T225 0 T300 0 T375 0 T450 0 T525 0 T600 0 T675 0 T750 0 T825 0 T900 0 T975 0 T1050 0 T1125 0 T1200 0"
SHIP = """
        <g stroke="#9fb2c6" stroke-width="5" stroke-linecap="round" fill="none">
          <line x1="70" y1="104" x2="70" y2="-2"/><line x1="140" y1="104" x2="140" y2="-62"/>
          <line x1="210" y1="104" x2="210" y2="-8"/><line x1="262" y1="104" x2="320" y2="74"/>
        </g>
        <path d="M38 44 Q70 38 102 44 L99 84 Q70 79 41 84 Z"/><path d="M45 8 Q70 3 95 8 L93 40 Q70 36 47 40 Z"/>
        <path d="M100 40 Q140 33 180 40 L176 88 Q140 82 104 88 Z"/><path d="M108 -2 Q140 -8 172 -2 L169 34 Q140 29 111 34 Z"/>
        <path d="M116 -34 Q140 -39 164 -34 L162 -8 Q140 -12 118 -8 Z"/><path d="M174 42 Q210 36 246 42 L242 86 Q210 81 178 86 Z"/>
        <path d="M181 4 Q210 -1 239 4 L236 36 Q210 32 184 36 Z"/><path d="M212 -2 L310 74 L224 72 Z"/>
        <path d="M141 -62 H174 V-44 H141 Z" fill="#e3b341"/>
        <path d="M-4 84 L56 84 L56 100 L272 100 L254 134 Q140 150 24 136 L0 104 Z"/>"""


def header(display_key, faces):
    spec, fam, size, ls, upper = DISPLAY[display_key]
    name = NAME.upper() if upper else NAME
    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 1200 320" role="img" aria-label="{NAME}, {ROLE.replace('&', '&amp;')}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0a0f1a"/><stop offset="1" stop-color="#0e1a26"/></linearGradient>
    <linearGradient id="water" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0f2a3b"/><stop offset="1" stop-color="#0a1520"/></linearGradient>
    <radialGradient id="glow" cx="0.84" cy="0.8" r="0.42"><stop offset="0" stop-color="#e3b341" stop-opacity="0.14"/><stop offset="1" stop-color="#e3b341" stop-opacity="0"/></radialGradient>
    <clipPath id="frame"><rect width="1200" height="320" rx="18"/></clipPath>
    <path id="sine" d="{SINE}"/>
    <path id="sea" d="{SINE} V90 H0 Z"/>
    <style>
      {faces}
      .run {{ animation: run 12s linear infinite; }}
      .run.slow {{ animation-duration: 20s; }}
      @keyframes run {{ from {{ transform: translateX(0); }} to {{ transform: translateX(-1200px); }} }}
      .ship {{ transform-box: view-box; transform-origin: 1012px 252px; animation: bob 6s ease-in-out infinite; }}
      @keyframes bob {{ 0%, 100% {{ transform: translateY(0) rotate(-1.4deg); }} 50% {{ transform: translateY(4px) rotate(1.4deg); }} }}
      .cursor {{ animation: blink 1.1s steps(1) infinite; }}
      @keyframes blink {{ 50% {{ opacity: 0; }} }}
      @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
      .name {{ font-family: '{fam}', Impact, 'Arial Black', sans-serif; }}
      .role {{ font-family: 'Space Grotesk', 'Segoe UI', Helvetica, Arial, sans-serif; font-weight: 500; }}
      .mono {{ font-family: 'JetBrains Mono', ui-monospace, Consolas, monospace; }}
    </style>
  </defs>
  <g clip-path="url(#frame)">
    <rect width="1200" height="320" fill="url(#bg)"/>
    <rect width="1200" height="320" fill="url(#glow)"/>
    <g stroke="#ffffff" stroke-opacity="0.035"><path d="M0 64 H1200 M0 128 H1200 M0 192 H1200 M150 0 V320 M300 0 V320 M450 0 V320 M600 0 V320 M750 0 V320 M900 0 V320 M1050 0 V320"/></g>

    <g class="ship" fill="#9fb2c6"><g transform="translate(948 198) scale(0.42)">{SHIP}
    </g></g>

    <!-- water body moves with the wave and sits in front of the hull, so the ship floats in it -->
    <g transform="translate(0 252)">
      <g class="run"><use xlink:href="#sea" fill="url(#water)"/><use xlink:href="#sea" x="1200" fill="url(#water)"/>
        <use xlink:href="#sine" fill="none" stroke="#3fb6a8" stroke-width="2.2"/><use xlink:href="#sine" x="1200" fill="none" stroke="#3fb6a8" stroke-width="2.2"/></g>
    </g>
    <g transform="translate(0 270)" fill="none" stroke="#e3b341" stroke-opacity="0.25" stroke-width="1.5">
      <g class="run slow"><use xlink:href="#sine" x="-40"/><use xlink:href="#sine" x="1160"/></g>
    </g>

    <text x="72" y="62" class="mono" font-size="15" fill="#6e8296">{META.replace('/', '<tspan fill="#3fb6a8">/</tspan>')}</text>
    <text x="68" y="{92 + size * 0.74:.0f}" class="name" font-size="{size}" letter-spacing="{ls}" fill="#e6edf3">{name}</text>
    <text x="72" y="{92 + size * 0.74 + 42:.0f}" class="role" font-size="26" fill="#9ba7b4">{ROLE.replace('&', '&amp;')}</text>
    <text x="72" y="{92 + size * 0.74 + 76:.0f}" class="mono" font-size="15" fill="#e3b341">{TAG}<tspan class="cursor"> _</tspan></text>
    <text x="1128" y="52" text-anchor="end" class="mono" font-size="13" fill="#8b9bb0" letter-spacing="1">{COORD}</text>
  </g>
</svg>
"""


def footer(faces):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 1200 150" role="img" aria-label="{QUOTE} {QUOTE_BY}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0e1a26"/><stop offset="1" stop-color="#0a0f1a"/></linearGradient>
    <clipPath id="frame"><rect width="1200" height="150" rx="18"/></clipPath>
    <path id="sine" d="{SINE}"/>
    <style>
      {faces}
      .run {{ animation: run 12s linear infinite; }}
      .run.slow {{ animation-duration: 20s; }}
      @keyframes run {{ from {{ transform: translateX(0); }} to {{ transform: translateX(-1200px); }} }}
      @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
      .q {{ font-family: 'Space Grotesk', 'Segoe UI', Helvetica, Arial, sans-serif; font-weight: 500; }}
      .mono {{ font-family: 'JetBrains Mono', ui-monospace, Consolas, monospace; }}
    </style>
  </defs>
  <g clip-path="url(#frame)">
    <rect width="1200" height="150" fill="url(#bg)"/>
    <g transform="translate(0 30)" fill="none" stroke="#3fb6a8" stroke-width="2.2">
      <g class="run"><use xlink:href="#sine"/><use xlink:href="#sine" x="1200"/></g>
    </g>
    <g transform="translate(0 42)" fill="none" stroke="#e3b341" stroke-opacity="0.25" stroke-width="1.5">
      <g class="run slow"><use xlink:href="#sine" x="-40"/><use xlink:href="#sine" x="1160"/></g>
    </g>
    <text x="600" y="98" text-anchor="middle" class="q" font-size="26" fill="#e6edf3">“{QUOTE}”</text>
    <text x="600" y="128" text-anchor="middle" class="mono" font-size="14" fill="#e3b341" letter-spacing="1">— {QUOTE_BY}</text>
  </g>
</svg>
"""


def main():
    role_text = ROLE + QUOTE + "“”"
    mono_text = META + TAG + COORD + " _—" + QUOTE_BY
    base = (font_face("Space+Grotesk:wght@500", "Space Grotesk", role_text, 500)
            + "\n      " + font_face("JetBrains+Mono:wght@500", "JetBrains Mono", mono_text, 500))
    keys = DISPLAY if "--compare" in sys.argv else [CHOICE]
    for key in keys:
        spec, fam, *_ = DISPLAY[key]
        faces = base + "\n      " + font_face(spec, fam, NAME + NAME.upper())
        svg = header(key, faces)
        if key == CHOICE:
            (HERE / "bf-header.svg").write_text(svg, encoding="utf-8")
        if "--compare" in sys.argv:
            (HERE / "_tmp" / f"compare-{key}.svg").write_text(svg, encoding="utf-8")
    (HERE / "bf-footer.svg").write_text(footer(base), encoding="utf-8")
    print("banners written", "(+ compare)" if "--compare" in sys.argv else "")


if __name__ == "__main__":
    main()
