"""Builds stack.svg: the tech-stack panel for the profile README.

Each tile is either a skillicons.dev icon (fetched, ids prefixed so several can
live in one SVG) or a local/iconify glyph drawn on the same #242938 rounded tile.
Edit GROUPS and rerun:  python build_stack.py
"""
import re
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
UA = {"User-Agent": "curl/8.4.0", "Accept": "*/*"}

# (label, source). Sources: "si:<id>" skillicons, "ic:<set:name>|<color>" iconify glyph,
# "file:<path>|<viewBox>" local svg (cropped by viewBox), "text:<line1>/<line2>|<color>"
GROUPS = [
    ("FABRICATION &\nPROTOTYPING", [
        ("3D Printing", "ic:mdi:printer-3d-nozzle|#f0b46a"),
        ("Laser Cutting", "ic:fluent:laser-tool-20-filled|#ff6b6b"),
        ("Prototyping", "ic:mdi:soldering-iron|#3fb6a8"),
        ("Creality Print", "ic:simple-icons:creality|#e6edf3"),
        ("LaserCAD", "text:Laser/CAD|#ff6b6b"),
        ("Fusion 360", "ic:devicon:fusion|"),
        ("Blender", "si:blender"),
    ]),
    ("ROBOTICS &\nEMBEDDED", [
        ("ROS 2", "si:ros"),
        ("RoboDK", "file:robodk-logo.svg|0.07 0.07 1.15 1.15"),
        ("ESP32", "ic:simple-icons:espressif|#E7352C"),
        ("FreeRTOS", "text:Free/RTOS|#7DB701"),
        ("Arduino", "si:arduino"),
        ("KiCad", "ic:simple-icons:kicad|#ffffff"),
        ("Linux", "si:linux"),
    ]),
    ("LANGUAGES", [
        ("Python", "si:py"), ("C++", "si:cpp"), ("C", "si:c"), ("C#", "si:cs"),
    ]),
    ("VISION &\nAPPS", [
        ("OpenCV", "si:opencv"),
        ("MediaPipe", "ic:simple-icons:mediapipe|#00C3E3"),
        ("PyQt", "si:qt"),
    ]),
    ("TOOLS &\nDESIGN", [
        ("Git", "si:git"), ("GitHub", "si:github"), ("VS Code", "si:vscode"),
        ("Photoshop", "si:ps"), ("Illustrator", "si:ai"), ("After Effects", "si:ae"),
    ]),
]

TILE, CELL, LABEL_W, ROW_H, PAD = 60, 92, 190, 112, 28
SANS = "'Segoe UI', -apple-system, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Consolas, 'Liberation Mono', monospace"


def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA)) as r:
        return r.read().decode()


def prefix_ids(svg, p):
    svg = re.sub(r'id="([^"]+)"', lambda m: f'id="{p}{m.group(1)}"', svg)
    svg = re.sub(r'url\(#([^)]+)\)', lambda m: f'url(#{p}{m.group(1)})', svg)
    svg = re.sub(r'href="#([^"]+)"', lambda m: f'href="#{p}{m.group(1)}"', svg)
    svg = re.sub(r'\.(fil\d+)', lambda m: f'.{p}{m.group(1)}', svg)
    svg = re.sub(r'class="(fil\d+)"', lambda m: f'class="{p}{m.group(1)}"', svg)
    return svg


def inner(svg):
    """Strip xml header and the outermost <svg> wrapper, return (viewBox, body)."""
    svg = re.sub(r'<\?xml.*?\?>', '', svg, flags=re.S)
    svg = re.sub(r'<metadata.*?</metadata>', '', svg, flags=re.S)
    vb = re.search(r'viewBox="([^"]+)"', svg).group(1)
    body = re.sub(r'^\s*<svg[^>]*>', '', svg.strip(), count=1, flags=re.S)
    body = re.sub(r'</svg>\s*$', '', body)
    return vb, body


def tile(src, x, y, k):
    p = f"t{k}_"
    bg = f'<rect x="{x}" y="{y}" width="{TILE}" height="{TILE}" rx="14" fill="#242938"/>'
    kind, _, rest = src.partition(":")
    if kind == "si":
        vb, body = inner(fetch(f"https://skillicons.dev/icons?i={rest}"))
        # skillicons wraps the real icon in <g transform><svg ...>; keep it whole
        return f'<svg x="{x}" y="{y}" width="{TILE}" height="{TILE}" viewBox="{vb}">{prefix_ids(body, p)}</svg>'
    ref, _, color = rest.partition("|")
    g = TILE * 0.62
    gx, gy = x + (TILE - g) / 2, y + (TILE - g) / 2
    if kind == "ic":
        vb, body = inner(fetch(f"https://api.iconify.design/{ref.replace(':', '/', 1)}.svg"))
        body = prefix_ids(body, p)
        if color:
            body = body.replace('currentColor', color)
            body = f'<g fill="{color}">{body}</g>'
        scale = {"fusion": 0.72, "creality": 0.88}  # app logo / wide wordmark: fill more of the tile
        hit = next((v for key, v in scale.items() if key in ref), None)
        if hit:
            g = TILE * hit
            gx, gy = x + (TILE - g) / 2, y + (TILE - g) / 2
        return bg + f'<svg x="{gx:.1f}" y="{gy:.1f}" width="{g:.1f}" height="{g:.1f}" viewBox="{vb}">{body}</svg>'
    if kind == "file":
        _, body = inner((HERE / ref).read_text(encoding="utf-8"))
        return bg + f'<svg x="{gx:.1f}" y="{gy:.1f}" width="{g:.1f}" height="{g:.1f}" viewBox="{color}">{prefix_ids(body, p)}</svg>'
    if kind == "text":
        a, b = ref.split("/")
        cx = x + TILE / 2
        return bg + (f'<text x="{cx}" y="{y + 27}" text-anchor="middle" font-family="{SANS}" font-weight="600" font-size="13" fill="#c9d1d9">{a}</text>'
                     f'<text x="{cx}" y="{y + 45}" text-anchor="middle" font-family="{SANS}" font-weight="800" font-size="17" fill="{color}">{b}</text>')
    raise ValueError(src)


def build():
    widest = max(len(items) for _, items in GROUPS)
    W = PAD + LABEL_W + widest * CELL + PAD - (CELL - TILE) // 2
    H = PAD + len(GROUPS) * ROW_H + PAD // 2
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Tech stack">',
           f'<rect width="{W}" height="{H}" rx="18" fill="#0e1a26"/>']
    k = 0
    for r, (title, items) in enumerate(GROUPS):
        y0 = PAD + r * ROW_H
        if r:
            out.append(f'<line x1="{PAD}" y1="{y0 - 14}" x2="{W - PAD}" y2="{y0 - 14}" stroke="#ffffff" stroke-opacity="0.06"/>')
        lines = title.split("\n")
        ty = y0 + TILE / 2 - (len(lines) - 1) * 9 + 5
        out.append(f'<rect x="{PAD}" y="{y0 + 8}" width="3" height="{TILE - 16}" rx="1.5" fill="#3fb6a8"/>')
        for i, ln in enumerate(lines):
            out.append(f'<text x="{PAD + 16}" y="{ty + i * 18}" font-family="{MONO}" font-size="13" letter-spacing="1.5" fill="#9ba7b4">{ln.replace("&", "&amp;")}</text>')
        for c, (label, src) in enumerate(items):
            x = PAD + LABEL_W + c * CELL
            out.append(tile(src, x, y0, k))
            out.append(f'<text x="{x + TILE / 2}" y="{y0 + TILE + 20}" text-anchor="middle" font-family="{SANS}" font-size="12" fill="#8b98a5">{label}</text>')
            k += 1
    out.append("</svg>")
    (HERE / "stack.svg").write_text("\n".join(out), encoding="utf-8")
    print("stack.svg", W, "x", H)


if __name__ == "__main__":
    build()
