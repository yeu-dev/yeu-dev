"""
pixelfont.py — 5x7 bitmap font and SVG drawing helpers.

Each glyph is a list of 7 five-character strings ('1' = pixel on). Text turns
into <rect> elements with an inline fill, which is all GitHub's SVG sanitizer
keeps inside a README.

Adjacent horizontal rects are merged into one so the files do not blow up in
size.
"""

GLYPHS = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01110", "10001", "10000", "10111", "10001", "10001", "01111"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "J": ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10001", "10101", "10101", "11011", "10001"],
    "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00010", "00100", "01000", "11111"],
    "3": ["11111", "00010", "00100", "00010", "00001", "10001", "01110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    "6": ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
    " ": ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
    ".": ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
    ",": ["00000", "00000", "00000", "00000", "00110", "00110", "01100"],
    ":": ["00000", "01100", "01100", "00000", "01100", "01100", "00000"],
    ";": ["00000", "01100", "01100", "00000", "00110", "00110", "01100"],
    "-": ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
    "_": ["00000", "00000", "00000", "00000", "00000", "00000", "11111"],
    "+": ["00000", "00100", "00100", "11111", "00100", "00100", "00000"],
    "/": ["00001", "00010", "00010", "00100", "01000", "01000", "10000"],
    "\\": ["10000", "01000", "01000", "00100", "00010", "00010", "00001"],
    "'": ["00100", "00100", "00100", "00000", "00000", "00000", "00000"],
    "!": ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
    "?": ["01110", "10001", "00001", "00010", "00100", "00000", "00100"],
    "(": ["00010", "00100", "01000", "01000", "01000", "00100", "00010"],
    ")": ["01000", "00100", "00010", "00010", "00010", "00100", "01000"],
    "[": ["01110", "01000", "01000", "01000", "01000", "01000", "01110"],
    "]": ["01110", "00010", "00010", "00010", "00010", "00010", "01110"],
    "<": ["00010", "00100", "01000", "10000", "01000", "00100", "00010"],
    ">": ["01000", "00100", "00010", "00001", "00010", "00100", "01000"],
    "#": ["01010", "01010", "11111", "01010", "11111", "01010", "01010"],
    "%": ["11001", "11010", "00010", "00100", "01000", "01011", "10011"],
    "*": ["00000", "00100", "10101", "01110", "10101", "00100", "00000"],
    "=": ["00000", "00000", "11111", "00000", "11111", "00000", "00000"],
    "@": ["01110", "10001", "10111", "10101", "10111", "10000", "01110"],
    "&": ["01100", "10010", "10100", "01000", "10101", "10010", "01101"],
    "·": ["00000", "00000", "00000", "01100", "01100", "00000", "00000"],
}

# Accents and enie are flattened: classic arcade fonts had neither.
FOLD = {
    "Á": "A", "É": "E", "Í": "I", "Ó": "O", "Ú": "U",
    "À": "A", "È": "E", "Ì": "I", "Ò": "O", "Ù": "U",
    "Ä": "A", "Ë": "E", "Ï": "I", "Ö": "O", "Ü": "U",
    "Ñ": "N", "Ç": "C",
}

GW, GH = 5, 7          # ancho y alto del glifo en pixeles
TRACK = 1              # separacion entre glifos, en pixeles


def normalize(text):
    """Uppercase, unaccented, only characters the font actually has."""
    out = []
    for ch in text.upper():
        ch = FOLD.get(ch, ch)
        out.append(ch if ch in GLYPHS else " ")
    return "".join(out)


def text_width(text, scale, track=TRACK):
    """Width in px the rendered text will take."""
    n = len(normalize(text))
    if n == 0:
        return 0
    return (n * GW + (n - 1) * track) * scale


def text_height(scale):
    return GH * scale


def _runs(rows):
    """Turns the bit matrix into horizontal runs (x, y, length)."""
    for y, row in enumerate(rows):
        x = 0
        while x < len(row):
            if row[x] == "1":
                start = x
                while x < len(row) and row[x] == "1":
                    x += 1
                yield start, y, x - start
            else:
                x += 1


def box_path(x, y, w, h):
    """A rectangle as a subpath. Far more compact than a <rect>."""
    return "M%g %gh%gv%gh%gz" % (x, y, w, h, -w)


def draw_text(text, x, y, scale, fill, track=TRACK):
    """
    Draws `text` with its top-left corner at (x, y).

    Every pixel of the text goes into a single <path>, since they share a
    color. Emitting one <rect> per pixel quadrupled the file size.
    """
    d = []
    cursor = x
    for ch in normalize(text):
        for px, py, run in _runs(GLYPHS[ch]):
            d.append(box_path(cursor + px * scale, y + py * scale, run * scale, scale))
        cursor += (GW + track) * scale
    if not d:
        return ""
    return '<path fill="%s" d="%s"/>' % (fill, "".join(d))


def draw_text_shadow(text, x, y, scale, fill, shadow, offset=None, track=TRACK):
    """Text with a hard offset shadow. No blur: the system bevel is physical."""
    off = scale if offset is None else offset
    return (
        draw_text(text, x + off, y + off, scale, shadow, track)
        + draw_text(text, x, y, scale, fill, track)
    )


def draw_text_centered(text, cx, y, scale, fill, track=TRACK):
    return draw_text(text, cx - text_width(text, scale, track) / 2, y, scale, fill, track)


def draw_text_centered_shadow(text, cx, y, scale, fill, shadow, offset=None, track=TRACK):
    x = cx - text_width(text, scale, track) / 2
    return draw_text_shadow(text, x, y, scale, fill, shadow, offset, track)


def rect(x, y, w, h, fill, opacity=None):
    op = "" if opacity is None else ' opacity="%g"' % opacity
    return '<rect x="%g" y="%g" width="%g" height="%g" fill="%s"%s/>' % (x, y, w, h, fill, op)


def bevel(x, y, w, h, face, light, dark, t=3):
    """
    Box with a physical bevel: light edge top/left, dark bottom/right.
    Zero blur, exactly as the stackfull.space design system calls for.
    """
    return "".join([
        rect(x, y, w, h, face),
        rect(x, y, w, t, light),
        rect(x, y, t, h, light),
        rect(x, y + h - t, w, t, dark),
        rect(x + w - t, y, t, h, dark),
    ])


def inset(x, y, w, h, face, light, dark, t=3):
    """Inverted bevel: the box reads as sunken."""
    return bevel(x, y, w, h, face, dark, light, t)


def scanlines(w, h, color, step=4, opacity=0.05):
    """CRT-style horizontal grid, in a single path."""
    d = "".join(box_path(0, y, w, 1) for y in range(0, h, step))
    return '<path fill="%s" opacity="%g" d="%s"/>' % (color, opacity, d)


def checker(x, y, w, h, size, a, b):
    """Alternating checker strip, two paths."""
    da, db = [], []
    i = 0
    cx = x
    while cx < x + w:
        cw = min(size, x + w - cx)
        (da if i % 2 == 0 else db).append(box_path(cx, y, cw, h))
        cx += size
        i += 1
    out = ""
    if da:
        out += '<path fill="%s" d="%s"/>' % (a, "".join(da))
    if db:
        out += '<path fill="%s" d="%s"/>' % (b, "".join(db))
    return out


def svg(width, height, body, title=""):
    t = "<title>%s</title>" % title if title else ""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="%g" height="%g" '
        'viewBox="0 0 %g %g" role="img" shape-rendering="crispEdges">%s%s</svg>'
        % (width, height, width, height, t, body)
    )
