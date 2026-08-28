#!/usr/bin/env python3
"""
generate.py — Builds the SVG art for the yeu-dev profile.

    python3 scripts/generate.py            # rebuild the static art
    python3 scripts/generate.py --stats    # also hit the API and rebuild stats.svg

No third-party dependencies: standard library only. The art is drawn with
<rect> because that is what survives GitHub's SVG sanitizer.

Palette and rules taken from DESIGN.md of stackfull.space:
  70% structural wine · 20% road signage (amber = action) · 10% warm neutrals
  Depth from physical bevels, zero blur.
"""

import json
import os
import sys
import urllib.error
import urllib.request

from pixelfont import (
    bevel, checker, draw_text, draw_text_centered, draw_text_centered_shadow,
    draw_text_shadow, inset, rect, scanlines, svg, text_width,
)

# ── Palette ────────────────────────────────────────────────────────────────
WINE_100 = "#FAE0DC"
WINE_200 = "#F2BDB5"
WINE_300 = "#E69086"
WINE_400 = "#E0776A"
WINE_500 = "#C4352A"
WINE_600 = "#A81C14"
WINE_700 = "#8B0000"
WINE_800 = "#6B0A0A"
WINE_900 = "#4A0606"
WINE_950 = "#2B0303"

AMBER = "#F2A900"
AMBER_DEEP = "#C48200"
RETRO = "#F7F4EC"

BONE_100 = "#F7F3EB"
BONE_200 = "#EFE9DF"
BONE_300 = "#E4DCCF"
BONE_400 = "#CFC4B5"
BONE_500 = "#A2938A"
BONE_600 = "#665850"
BONE_700 = "#463A33"
BONE_800 = "#2A211D"
BONE_900 = "#1F1815"
BONE_950 = "#16110F"

# ── Light-mode roles ──────────────────────────────────────────────────────
# The same ones :root defines in index.css on stackfull.space. This art lives
# on GitHub's light background, so the surface leads and wine becomes
# structural ink instead of a backdrop. Amber stays action-only, and never
# runs as text on light: #F2A900 on bone gives 2.4:1.
BG   = "#FFFFFF"  # the README white: hides the seam between images
SURFACE   = BONE_100
SUNKEN = BONE_300
INK   = BONE_950
INK_2 = BONE_700
INK_3 = BONE_600
HAIR  = BONE_400
ACCENT  = WINE_700
LIGHT     = "#FFFFFF"
SHADOW  = BONE_400


W = 880
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")

USER = "yeu-dev"

# GitHub counts bytes per file, so markup and stylesheets bury the languages
# actually written by hand: one compiled page or a vendored asset is worth
# more bytes than a whole module. They are left out of the chart.
IGNORED_LANGS = {"HTML", "CSS", "SCSS", "Sass", "Less"}


def write(name, content):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
    print("  %-18s %6.1f KB" % (name, len(content) / 1024))


def caret(x, y, s, fill):
    """Pixel caret, pointing right."""
    parts = []
    for i in range(4):
        h = (4 - i) * 2
        parts.append(rect(x + i * s, y + i * s, s, h * s, fill))
    return "".join(parts)


def blink(body, dur="1.1s"):
    """SMIL blink. If the viewer ignores it, the element just stays visible."""
    return (
        '<g>%s<animate attributeName="opacity" values="1;1;0;0" '
        'dur="%s" repeatCount="indefinite"/></g>' % (body, dur)
    )


def padlock(x, y, s, body_fill, shackle_fill):
    """7x9 pixel padlock."""
    rows = [
        "0111000",
        "1000100",
        "1000100",
        "1111110",
        "1111110",
        "1101110",
        "1111110",
    ]
    parts = []
    for py, row in enumerate(rows):
        fill = shackle_fill if py < 3 else body_fill
        px = 0
        while px < len(row):
            if row[px] == "1":
                start = px
                while px < len(row) and row[px] == "1":
                    px += 1
                parts.append(rect(x + start * s, y + py * s, (px - start) * s, s, fill))
            else:
                px += 1
    return "".join(parts)


# ── 1. Marquee ─────────────────────────────────────────────────────────
def marquee():
    H = 250
    b = []
    b.append(rect(0, 0, W, H, BG))
    b.append(scanlines(W, H, INK, step=4, opacity=0.05))

    # Cabinet frame
    b.append(rect(0, 0, W, 10, ACCENT))
    b.append(rect(0, H - 10, W, 10, ACCENT))
    b.append(rect(0, 0, 10, H, ACCENT))
    b.append(rect(W - 10, 0, 10, H, ACCENT))
    b.append(rect(0, 10, W, 3, WINE_500))
    b.append(rect(0, H - 13, W, 3, WINE_900))
    b.append(rect(10, 0, 3, H, WINE_500))
    b.append(rect(W - 13, 0, 3, H, WINE_900))

    # Corner screws
    for cx, cy in ((26, 26), (W - 38, 26), (26, H - 38), (W - 38, H - 38)):
        b.append(bevel(cx, cy, 12, 12, WINE_800, WINE_600, WINE_950, 2))

    # Title
    b.append(draw_text_centered_shadow("YEUDIEL GONZALEZ", W / 2, 50, 7, ACCENT, HAIR, 5))

    # Signage rule
    b.append(rect(150, 118, W - 300, 4, AMBER))

    # Subtitle
    b.append(draw_text_centered("SOFTWARE ENGINEER", W / 2, 136, 3, INK_2))

    # Control panel
    b.append(inset(40, 176, W - 80, 50, SUNKEN, LIGHT, SHADOW, 3))
    b.append(blink(caret(62, 192, 2, ACCENT) + draw_text("INSERT COIN", 86, 194, 2, ACCENT)))
    b.append(draw_text("STACKFULL.SPACE", W - 62 - text_width("STACKFULL.SPACE", 2), 194, 2, INK_3))

    return svg(W, H, "".join(b), "Yeudiel Gonzalez - Software Engineer")


# ── 2. Inventory (stack) ─────────────────────────────────────────────────
STACK = [
    ("C#", "LANG"), ("TYPESCRIPT", "LANG"), ("JAVASCRIPT", "LANG"), ("PYTHON", "LANG"),
    ("PHP", "LANG"), ("SQL", "LANG"), (".NET", "DESKTOP"), ("WPF", "DESKTOP"),
    ("XAML", "DESKTOP"), ("REACT", "FRONT"), ("REACT NATIVE", "FRONT"), ("EXPO", "FRONT"),
    ("VITE", "FRONT"), ("TAILWIND", "FRONT"), ("DJANGO", "BACK"), ("DJANGO REST", "BACK"),
    ("POSTGRESQL", "DATA"), ("MYSQL", "DATA"), ("AZURE", "CLOUD"), ("VERCEL", "CLOUD"),
    ("RENDER", "CLOUD"), ("GIT", "TOOLS"), ("VISUAL STUDIO", "TOOLS"), ("VS CODE", "TOOLS"),
]

COLS, CELL_W, CELL_H, GAP = 4, 205, 50, 20


def inventory():
    rows = (len(STACK) + COLS - 1) // COLS
    top = 62
    H = top + rows * CELL_H + (rows - 1) * 12 + 22

    b = [rect(0, 0, W, H, BG), scanlines(W, H, INK, 4, 0.04)]
    b.append(draw_text("INVENTORY", 4, 12, 4, ACCENT))
    b.append(draw_text("EQUIPPED / " + str(len(STACK)) + " ITEMS",
                       W - 4 - text_width("EQUIPPED / " + str(len(STACK)) + " ITEMS", 2), 26, 2, INK_3))
    b.append(rect(0, 48, W, 3, ACCENT))

    for i, (name, tag) in enumerate(STACK):
        col, row = i % COLS, i // COLS
        x = col * (CELL_W + GAP)
        y = top + row * (CELL_H + 12)
        b.append(bevel(x, y, CELL_W, CELL_H, SURFACE, LIGHT, SHADOW, 3))
        # Amber is reserved for actions, so the specialty is marked with a
        # lighter wine rather than with signage.
        b.append(rect(x + 3, y + 3, 6, CELL_H - 6, WINE_500 if tag == "DESKTOP" else ACCENT))
        b.append(draw_text(name, x + 20, y + 13, 2, INK))
        b.append(draw_text(tag, x + 20, y + 31, 1, INK_3))

    return svg(W, H, "".join(b), "Yeudiel Gonzalez's stack")


# ── 3. Select your project ────────────────────────────────────────────────
PROJECTS = [
    {
        "name": "STACKFULL",
        "file": "cartridge-01.svg",
        "url": "https://github.com/yeu-dev/portafolio-stackfull",
        "stack": "REACT 19 · TYPESCRIPT · VITE",
        "note": "PORTFOLIO AND ITS OWN DESIGN SYSTEM",
        "state": "PLAY",
        "locked": False,
    },
    {
        "name": "TALENTHUB MEXICO",
        "file": "cartridge-02.svg",
        "url": "https://github.com/yeu-dev/talenthub-mexico",
        "stack": "DJANGO · REACT · POSTGRESQL",
        "note": "IT JOB BOARD WITH THREE ROLES",
        "state": "PLAY",
        "locked": False,
    },
    {
        "name": "CONSULTAS MEDICAS",
        "file": "cartridge-03.svg",
        "url": "https://github.com/yeu-dev/Consultas-Medicas",
        "stack": "PHP · MYSQL · JAVASCRIPT",
        "note": "PATIENT AND DOCTOR APPOINTMENTS",
        "state": "PLAY",
        "locked": False,
    },
    {
        "name": "TALENTHUB MOBILE",
        "file": "cartridge-04.svg",
        "url": "",
        "stack": "REACT NATIVE · EXPO",
        "note": "MOBILE APP ON THE SAME API",
        "state": "IN PROGRESS",
        "locked": True,
    },
]

CARD_W, CARD_H = 425, 168


HEADER_H = 52


def select_header():
    """Title band. It sits apart from the cartridges because each cartridge is
    its own link, and a single image cannot point at four repos."""
    b = [rect(0, 0, W, HEADER_H, BG), scanlines(W, HEADER_H, INK, 4, 0.04)]
    b.append(draw_text("SELECT YOUR PROJECT", 4, 10, 4, ACCENT))
    b.append(blink(draw_text("PRESS START", W - 4 - text_width("PRESS START", 2), 24, 2, ACCENT), "1.6s"))
    b.append(rect(0, HEADER_H - 3, W, 3, ACCENT))
    return svg(W, HEADER_H, "".join(b), "Projects")


def cartridge(i, p):
    """A standalone cartridge, the same size it had inside the grid. Each one is
    drawn separately so it can sit in its own <a>; the 2x2 comes from two per
    row in the README."""
    w, h = CARD_W, CARD_H
    face = SUNKEN if p["locked"] else SURFACE
    edge = SHADOW if p["locked"] else LIGHT
    ink = INK_3 if p["locked"] else INK

    b = [rect(0, 0, w, h, BG)]
    b.append(bevel(0, 0, w, h, face, edge, SHADOW, 4))

    # Cartridge top label
    b.append(rect(4, 4, w - 8, 14, INK_3 if p["locked"] else ACCENT))
    b.append(draw_text("CARTRIDGE %02d" % (i + 1), 14, 8, 1, SURFACE))

    b.append(draw_text(p["name"], 22, 36, 3, ink))
    b.append(rect(22, 68, w - 44, 2, HAIR if p["locked"] else ACCENT))
    b.append(draw_text(p["stack"], 22, 82, 2, INK_3 if p["locked"] else ACCENT))
    b.append(draw_text(p["note"], 22, 104, 1, INK_3))

    # Status footer. On light, amber cannot be text —#F2A900 on bone gives
    # 2.4:1— so it goes as a block with dark ink on top, which is what the
    # design system calls for.
    sy = h - 40
    if p["locked"]:
        b.append(padlock(22, sy + 6, 3, INK_3, HAIR))
        b.append(draw_text(p["state"], 52, sy + 11, 2, INK_3))
    else:
        width = text_width(p["state"], 2) + 52
        b.append(bevel(22, sy, width, 30, AMBER, "#F8C64D", AMBER_DEEP, 2))
        b.append(caret(38, sy + 8, 2, BONE_950))
        b.append(draw_text(p["state"], 62, sy + 10, 2, BONE_950))

    return svg(w, h, "".join(b), p["name"])


# ── 4. Contact buttons ────────────────────────────────────────────────
BUTTONS = [
    ("btn-portfolio.svg", "PORTFOLIO", "STACKFULL.SPACE"),
    ("btn-linkedin.svg", "LINKEDIN", "YEUDIEL GONZALEZ"),
    ("btn-email.svg", "EMAIL", "DRIVSMX@GMAIL.COM"),
]


def button(label, sub):
    """Clickable arcade button. The <a> lives in the markdown, not in the SVG."""
    bw, bh = 286, 62
    b = [rect(0, 0, bw, bh, BG)]
    b.append(bevel(0, 0, bw, bh, ACCENT, WINE_600, WINE_950, 3))
    b.append(rect(bw - 9, 3, 6, bh - 6, AMBER))
    b.append(caret(16, 18, 2, AMBER))
    b.append(draw_text(label, 40, 18, 3, RETRO))
    b.append(draw_text(sub, 40, 42, 1, WINE_200))
    return svg(bw, bh, "".join(b), label)


# ── 5. Language stats (live data) ────────────────────────────────────────
def api(path, token):
    req = urllib.request.Request(
        "https://api.github.com" + path,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "yeu-dev-readme",
            **({"Authorization": "Bearer " + token} if token else {}),
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def fetch():
    """Returns (summary, languages). Returns None if the API fails."""
    token = os.environ.get("GITHUB_TOKEN", "")
    try:
        user = api("/users/" + USER, token)
        repos, page = [], 1
        while True:
            batch = api("/users/%s/repos?per_page=100&type=owner&page=%d" % (USER, page), token)
            repos.extend(batch)
            if len(batch) < 100:
                break
            page += 1
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as err:
        print("  API unavailable: %s" % err)
        return None, None

    stars = sum(r.get("stargazers_count", 0) for r in repos)
    forks = sum(r.get("forks_count", 0) for r in repos)

    langs = {}
    for r in repos:
        if r.get("fork"):
            continue
        try:
            for name, size in api("/repos/%s/languages" % r["full_name"], token).items():
                if name in IGNORED_LANGS:
                    continue
                langs[name] = langs.get(name, 0) + size
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
            continue

    summary = [
        ("REPOS", user.get("public_repos", 0)),
        ("STARS", stars),
        ("FOLLOWERS", user.get("followers", 0)),
        ("FORKS", forks),
    ]
    return summary, langs


def stats(langs):
    top = sorted(langs.items(), key=lambda kv: kv[1], reverse=True)[:6] if langs else []
    total = sum(v for _, v in top) or 1

    head, bar_h = 62, 34
    H = head + len(top) * (bar_h + 12) + 18

    b = [rect(0, 0, W, H, BG), scanlines(W, H, INK, 4, 0.04)]
    b.append(draw_text("TOP LANGUAGES", 4, 12, 4, ACCENT))
    b.append(draw_text("UPDATED BY GITHUB ACTIONS",
                       W - 4 - text_width("UPDATED BY GITHUB ACTIONS", 2), 26, 2, INK_3))
    b.append(rect(0, 48, W, 3, ACCENT))

    if top:
        label_w = max(text_width(n, 2) for n, _ in top)
        track_x = label_w + 24
        track_w = W - track_x - 76
        for i, (name, size) in enumerate(top):
            y = head + i * (bar_h + 12)
            pct = size / total
            b.append(draw_text(name, 4, y + 10, 2, INK))
            b.append(inset(track_x, y, track_w, bar_h, SUNKEN, LIGHT, SHADOW, 3))
            seg, gap = 12, 3
            filled = int((track_w - 8) * pct)
            sx = track_x + 4
            while sx < track_x + 4 + filled - seg:
                b.append(rect(sx, y + 4, seg, bar_h - 8, AMBER if i == 0 else ACCENT))
                sx += seg + gap
            b.append(draw_text("%d%%" % round(pct * 100),
                               W - 4 - text_width("%d%%" % round(pct * 100), 2), y + 10, 2, INK_3))
    else:
        b.append(draw_text("NO API DATA ON THIS RUN", 4, head, 2, INK_3))

    return svg(W, H, "".join(b), "Yeudiel Gonzalez's most used languages")


# ── Main ──────────────────────────────────────────────────────────────────
def main():
    print("Building static art:")
    write("marquee.svg", marquee())
    write("inventory.svg", inventory())
    write("select-header.svg", select_header())
    for i, p in enumerate(PROJECTS):
        write(p["file"], cartridge(i, p))
    for filename, label, sub in BUTTONS:
        write(filename, button(label, sub))

    if "--demo" in sys.argv:
        print("Stats with sample data (design check only):")
        write("stats.svg", stats(
            {"TypeScript": 480000, "Python": 310000, "C#": 260000,
             "PHP": 150000, "JavaScript": 96000, "CSS": 54000},
        ))
        return

    if "--stats" in sys.argv:
        print("Querying the GitHub API:")
        summary, langs = fetch()
        if summary is None:
            # Without data we do not overwrite: better to keep the previous
            # SVG than to publish a profile full of zeros.
            print("  stats.svg was NOT rebuilt.")
            sys.exit(1)
        write("stats.svg", stats(langs))


if __name__ == "__main__":
    main()
