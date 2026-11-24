"""Render the video's graphics as full-frame transparent PNGs (place them as overlays in the EDL).

Usage:
  python cards.py cards.json OUTDIR

cards.json:
{
  "width": 1920, "height": 1080,
  "theme": {"accent": "#FF3D7F", "accent2": "#FFC24B", "paper": "#F6F3EE", "ink": "#141414",
            "night": "#120F1C", "font_bold": null, "font_regular": null},
  "cards": [ {"name": "dazed", "kind": "quote", ...}, ... ]
}

Kinds and their fields:
  quote      source, text, states: [[phrase,...], ...]   -> name_1.png, name_2.png ... (one per highlight state;
             without states -> name.png). Phrases must appear verbatim in text (case-insensitive).
  headline   source, title, dek (optional)
  photo      image (path, relative to cards.json), name (optional), role (optional), tilt (deg, default -4)
  label      text, position: "bottom-left" (default) | "top-left" | "bottom-right"
  stamp      text, angle (default -8), color (default accent), scale (default 1)
  chapter    nodes: [..], active: index lit up to (0-based), part: "PART 03", title: "THE TWO OF YOU",
             complete: false (true = all nodes lit and connected, no title)
  stat       before, after, label_before, label_after, caption (optional)
  checklist  items: [..], checked: number checked (default all), position: "left" | "center"
  stars      total (default 6), filled, tag (optional small text, e.g. "-1"), icons: [short words] (optional)
  meter      left, right, value 0..1, chips: [..] (optional), title (optional)
  title      text, sub (optional)          big centered text, e.g. for a cold-open title or "FIVE LEFT"

Fonts: set theme font_bold / font_regular to .ttf/.otf paths for your own look. Otherwise a bold system
font is found automatically.
"""
import argparse
import json
import math
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

BOLD_CANDIDATES = [
    "C:/Windows/Fonts/seguibl.ttf", "C:/Windows/Fonts/ariblk.ttf", "C:/Windows/Fonts/arialbd.ttf",
    "/System/Library/Fonts/Supplemental/Arial Black.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
]
REGULAR_CANDIDATES = [
    "C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf", "/Library/Fonts/Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/TTF/DejaVuSans.ttf",
]
DEFAULT_THEME = {"accent": "#FF3D7F", "accent2": "#FFC24B", "paper": "#F6F3EE", "ink": "#141414",
                 "night": "#120F1C", "font_bold": None, "font_regular": None}


def find_font(explicit, candidates):
    for c in ([explicit] if explicit else []) + candidates:
        if c and Path(c).is_file():
            return c
    return None


class Kit:
    def __init__(self, w, h, theme, base):
        self.w, self.h, self.base = w, h, base
        self.t = dict(DEFAULT_THEME, **(theme or {}))
        for k in ("font_bold", "font_regular"):
            if self.t.get(k) and not Path(self.t[k]).is_absolute():
                self.t[k] = str((base / self.t[k]).resolve())
        self.bold_path = find_font(self.t["font_bold"], BOLD_CANDIDATES)
        self.reg_path = find_font(self.t["font_regular"], REGULAR_CANDIDATES) or self.bold_path
        if not self.bold_path:
            sys.exit("No usable font found. Set theme.font_bold / font_regular to .ttf files.")
        self.s = h / 1080.0

    def font(self, size, bold=True):
        return ImageFont.truetype(self.bold_path if bold else self.reg_path, max(8, int(size * self.s)))

    def rgb(self, key_or_hex, alpha=255):
        v = self.t.get(key_or_hex, key_or_hex)
        v = v.lstrip("#")
        return tuple(int(v[i:i + 2], 16) for i in (0, 2, 4)) + (alpha,)

    def canvas(self):
        return Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))

    def px(self, v):
        return int(v * self.s)


def shadow(img, box, radius, blur=24, alpha=110, offset=10):
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(sh)
    x0, y0, x1, y1 = box
    d.rounded_rectangle((x0, y0 + offset, x1, y1 + offset), radius, fill=(0, 0, 0, alpha))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)))


def wrap_words(draw, words, font, max_w):
    """Greedy layout. Returns list of lines; each line is list of (word_index, x, width)."""
    space = draw.textlength(" ", font=font)
    lines, cur, x = [], [], 0.0
    for i, w in enumerate(words):
        wl = draw.textlength(w, font=font)
        if cur and x + wl > max_w:
            lines.append(cur)
            cur, x = [], 0.0
        cur.append((i, x, wl))
        x += wl + space
    if cur:
        lines.append(cur)
    return lines


def norm(w):
    return re.sub(r"[^\w']", "", w.lower())


def phrase_ranges(words, phrases):
    nw = [norm(w) for w in words]
    hit = set()
    for ph in phrases:
        target = [norm(x) for x in ph.split() if norm(x)]
        found = False
        for i in range(len(nw) - len(target) + 1):
            if nw[i:i + len(target)] == target:
                hit.update(range(i, i + len(target)))
                found = True
        if not found:
            sys.exit(f"Highlight phrase not found in quote text: {ph!r}")
    return hit


def card_quote(k, c, highlights):
    img = k.canvas()
    d = ImageDraw.Draw(img)
    cw = k.px(1180)
    pad = k.px(56)
    f = k.font(c.get("size", 38), bold=False)
    words = c["text"].split()
    lines = wrap_words(d, words, f, cw - 2 * pad)
    lh = int(f.size * 1.45)
    ch = pad * 2 + lh * len(lines)
    x0, y0 = (k.w - cw) // 2, (k.h - ch) // 2 + k.px(20)
    src = k.font(22)
    d.text((x0 + k.px(4), y0 - k.px(44)), c.get("source", "").upper(), font=src, fill=k.rgb("paper", 230))
    shadow(img, (x0, y0, x0 + cw, y0 + ch), k.px(18))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((x0, y0, x0 + cw, y0 + ch), k.px(18), fill=k.rgb("paper"))
    d.rectangle((x0, y0 + k.px(18), x0 + k.px(8), y0 + ch - k.px(18)), fill=k.rgb("accent"))
    hl = phrase_ranges(words, highlights)
    space = d.textlength(" ", font=f)
    for li, line in enumerate(lines):
        y = y0 + pad + li * lh
        for i, x, wl in line:
            if i in hl:
                ext = space if (i + 1) in hl and any(j == i + 1 for j, _, _ in line) else 0
                d.rectangle((x0 + pad + x - 3, y - 2, x0 + pad + x + wl + ext + 3, y + lh - k.px(10)),
                            fill=k.rgb("accent2", 235))
        for i, x, wl in line:
            d.text((x0 + pad + x, y), words[i], font=f, fill=k.rgb("ink"))
    return img


def card_headline(k, c):
    img = k.canvas()
    d = ImageDraw.Draw(img)
    cw, pad = k.px(1100), k.px(54)
    tf, df = k.font(60), k.font(30, bold=False)
    tl = wrap_words(d, c["title"].split(), tf, cw - 2 * pad)
    dl = wrap_words(d, c.get("dek", "").split(), df, cw - 2 * pad) if c.get("dek") else []
    th, dh = int(tf.size * 1.18), int(df.size * 1.4)
    ch = pad * 2 + th * len(tl) + (k.px(24) + dh * len(dl) if dl else 0)
    x0, y0 = (k.w - cw) // 2, (k.h - ch) // 2 + k.px(20)
    d.text((x0 + k.px(4), y0 - k.px(44)), c.get("source", "").upper(), font=k.font(22), fill=k.rgb("paper", 230))
    shadow(img, (x0, y0, x0 + cw, y0 + ch), k.px(16))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((x0, y0, x0 + cw, y0 + ch), k.px(16), fill=k.rgb("night", 245),
                        outline=k.rgb("paper", 255), width=k.px(4))
    words = c["title"].split()
    for li, line in enumerate(tl):
        for i, x, _ in line:
            d.text((x0 + pad + x, y0 + pad + li * th), words[i], font=tf, fill=k.rgb("paper"))
    y = y0 + pad + th * len(tl) + k.px(24)
    dw = c.get("dek", "").split()
    for li, line in enumerate(dl):
        for i, x, _ in line:
            d.text((x0 + pad + x, y + li * dh), dw[i], font=df, fill=k.rgb("paper", 200))
    return img


def card_photo(k, c):
    img = k.canvas()
    ph = Image.open(k.base / c["image"]).convert("RGBA")
    target_h = k.px(c.get("height", 560))
    ph = ph.resize((int(ph.width * target_h / ph.height), target_h), Image.LANCZOS)
    b = k.px(16)
    framed = Image.new("RGBA", (ph.width + 2 * b, ph.height + 2 * b), k.rgb("paper"))
    framed.paste(ph, (b, b))
    framed = framed.rotate(c.get("tilt", -4), resample=Image.BICUBIC, expand=True)
    has_name = bool(c.get("name"))
    cx = k.w * (0.66 if has_name else 0.5)
    x, y = int(cx - framed.width / 2), int(k.h / 2 - framed.height / 2)
    shadow(img, (x + k.px(20), y + k.px(20), x + framed.width - k.px(20), y + framed.height - k.px(20)), 6)
    img.alpha_composite(framed, (x, y))
    if has_name:
        d = ImageDraw.Draw(img)
        parts = c["name"].split(" ", 1)
        nx, ny = k.px(150), k.h // 2 - k.px(90)
        if len(parts) == 2:
            d.text((nx, ny), parts[0].upper(), font=k.font(34), fill=k.rgb("paper"))
            ny += k.px(44)
        d.text((nx, ny), parts[-1].upper(), font=k.font(96), fill=k.rgb("paper"))
        if c.get("role"):
            rf = k.font(24)
            rw = d.textlength(c["role"].upper(), font=rf)
            ry = ny + k.px(120)
            d.rectangle((nx, ry, nx + rw + k.px(24), ry + k.px(40)), fill=k.rgb("accent2"))
            d.text((nx + k.px(12), ry + k.px(6)), c["role"].upper(), font=rf, fill=k.rgb("ink"))
    return img


def chip(k, img, text, xy, anchor="lt", fg="ink", bg="paper", size=24, dot=None):
    d = ImageDraw.Draw(img)
    f = k.font(size)
    tw = d.textlength(text, font=f)
    padx, h = k.px(16), int(f.size * 1.75)
    dw = k.px(22) if dot else 0
    w = int(tw + 2 * padx + dw)
    x, y = xy
    if anchor[0] == "r":
        x -= w
    if anchor[1] == "b":
        y -= h
    d.rounded_rectangle((x, y, x + w, y + h), h // 2, fill=k.rgb(bg, 235))
    if dot:
        r = k.px(6)
        d.ellipse((x + padx - 2, y + h // 2 - r, x + padx - 2 + 2 * r, y + h // 2 + r), fill=k.rgb(dot))
    d.text((x + padx + dw, y + (h - f.size) // 2 - k.px(2)), text, font=f, fill=k.rgb(fg))
    return img


def card_label(k, c):
    img = k.canvas()
    m = k.px(48)
    pos = c.get("position", "bottom-left")
    xy = {"bottom-left": ((m, k.h - m), "lb"), "top-left": ((m, m), "lt"),
          "bottom-right": ((k.w - m, k.h - m), "rb")}[pos]
    return chip(k, img, c["text"].upper(), xy[0], xy[1], fg="paper", bg="night", size=c.get("size", 26),
                dot="accent")


def credit_pill(k, credit):
    img = k.canvas()
    m = k.px(36)
    return chip(k, img, f"FOOTAGE · {credit.upper()}", (k.w - m, m), "rt", fg="ink", bg="paper", size=18,
                dot="accent")


def card_stamp(k, c):
    f = k.font(110 * c.get("scale", 1))
    tmp = Image.new("RGBA", (10, 10))
    tw = ImageDraw.Draw(tmp).textlength(c["text"].upper(), font=f)
    pad = k.px(34)
    w, h = int(tw + 2 * pad), int(f.size * 1.5)
    st = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(st)
    col = k.rgb(c.get("color", "accent"))
    d.rounded_rectangle((4, 4, w - 4, h - 4), k.px(14), outline=col, width=k.px(10))
    d.text((pad, (h - f.size) // 2 - k.px(10)), c["text"].upper(), font=f, fill=col)
    st = st.rotate(c.get("angle", -8), resample=Image.BICUBIC, expand=True)
    img = k.canvas()
    img.alpha_composite(st, ((k.w - st.width) // 2, (k.h - st.height) // 2))
    return img


def card_chapter(k, c):
    img = k.canvas()
    d = ImageDraw.Draw(img)
    nodes = c["nodes"]
    n = len(nodes)
    complete = c.get("complete", False)
    active = n - 1 if complete else int(c.get("active", 0))
    cx, cy = (k.w // 2, k.h // 2) if complete else (int(k.w * 0.3), k.h // 2)
    R = k.px(330 if complete else 300)
    pts = [(cx + R * math.cos(-math.pi / 2 + 2 * math.pi * i / n), cy + R * math.sin(-math.pi / 2 + 2 * math.pi * i / n))
           for i in range(n)]
    d.ellipse((cx - R, cy - R, cx + R, cy + R), outline=k.rgb("paper", 40), width=k.px(2))
    lit = k.rgb("accent")
    for i in range(active):
        d.line((pts[i], pts[i + 1]), fill=lit, width=k.px(6))
    if complete:
        for i in range(n):
            for j in range(i + 2, n):
                if not (i == 0 and j == n - 1):
                    d.line((pts[i], pts[j]), fill=k.rgb("accent", 120), width=k.px(3))
        d.line((pts[-1], pts[0]), fill=lit, width=k.px(6))
    f = k.font(22)
    for i, (x, y) in enumerate(pts):
        on = i <= active
        r = k.px(44 if i == active and not complete else 34)
        if on:
            glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
            ImageDraw.Draw(glow).ellipse((x - r * 1.7, y - r * 1.7, x + r * 1.7, y + r * 1.7), fill=k.rgb("accent", 90))
            img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(k.px(18))))
            d = ImageDraw.Draw(img)
        d.ellipse((x - r, y - r, x + r, y + r), fill=k.rgb("accent" if on else "night", 255),
                  outline=k.rgb("paper", 255 if on else 90), width=k.px(4))
        num = str(i + 1)
        nf = k.font(28 if on else 24)
        d.text((x - d.textlength(num, font=nf) / 2, y - nf.size * 0.62), num, font=nf,
               fill=k.rgb("ink" if on else "paper", 255 if on else 130))
        lab = nodes[i].upper()
        lw = d.textlength(lab, font=f)
        ly = y + r + k.px(8) if y >= cy - 1 else y - r - k.px(34)
        d.text((x - lw / 2, ly), lab, font=f, fill=k.rgb("paper", 255 if on else 110))
    if not complete:
        tx = int(k.w * 0.56)
        d.text((tx, k.h // 2 - k.px(110)), c.get("part", f"PART {active + 1:02d}").upper(), font=k.font(30),
               fill=k.rgb("accent2"))
        tf = k.font(96)
        words = c.get("title", nodes[active]).upper().split()
        lines = wrap_words(d, words, tf, k.w - tx - k.px(80))
        for li, line in enumerate(lines):
            for i, x, _ in line:
                d.text((tx + x, k.h // 2 - k.px(60) + li * int(tf.size * 1.08)), words[i], font=tf, fill=k.rgb("paper"))
        d.rectangle((tx, k.h // 2 - k.px(60) + len(lines) * int(tf.size * 1.08) + k.px(16), tx + k.px(160),
                     k.h // 2 - k.px(52) + len(lines) * int(tf.size * 1.08) + k.px(16)), fill=k.rgb("accent"))
    return img


def card_stat(k, c):
    img = k.canvas()
    d = ImageDraw.Draw(img)
    bf, af, lf = k.font(110), k.font(170), k.font(30)
    bw, aw = d.textlength(c["before"], font=bf), d.textlength(c["after"], font=af)
    gap = k.px(140)
    total = bw + gap + aw
    x = (k.w - total) / 2
    yb = k.h / 2 - k.px(40)
    d.text((x, yb - bf.size * 0.2), c["before"], font=bf, fill=k.rgb("paper", 170))
    ax0 = x + bw + k.px(30)
    d.polygon([(ax0, yb + k.px(20)), (ax0 + k.px(70), yb + k.px(55)), (ax0, yb + k.px(90))], fill=k.rgb("accent2"))
    d.text((x + bw + gap, yb - af.size * 0.45), c["after"], font=af, fill=k.rgb("accent"))
    if c.get("label_before"):
        d.text((x, yb + k.px(110)), c["label_before"].upper(), font=lf, fill=k.rgb("paper", 170))
    if c.get("label_after"):
        d.text((x + bw + gap, yb + k.px(110)), c["label_after"].upper(), font=lf, fill=k.rgb("paper"))
    if c.get("caption"):
        cf = k.font(26, bold=False)
        d.text(((k.w - d.textlength(c["caption"], font=cf)) / 2, k.h - k.px(170)), c["caption"], font=cf,
               fill=k.rgb("paper", 200))
    return img


def card_checklist(k, c):
    img = k.canvas()
    d = ImageDraw.Draw(img)
    items = c["items"]
    checked = c.get("checked", len(items))
    f = k.font(40)
    lh = k.px(76)
    x = k.px(160) if c.get("position", "left") == "left" else (k.w - k.px(420)) // 2
    y0 = (k.h - lh * len(items)) // 2
    for i, it in enumerate(items):
        y = y0 + i * lh
        box = k.px(44)
        on = i < checked
        d.rounded_rectangle((x, y, x + box, y + box), k.px(8), fill=k.rgb("accent" if on else "night", 255),
                            outline=k.rgb("paper"), width=k.px(3))
        if on:
            d.line([(x + k.px(10), y + k.px(23)), (x + k.px(19), y + k.px(33)), (x + k.px(35), y + k.px(11))],
                   fill=k.rgb("ink"), width=k.px(6))
        d.text((x + box + k.px(22), y - k.px(2)), it.upper(), font=f, fill=k.rgb("paper", 255 if on else 140))
    return img


def star(cx, cy, r):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts


def card_stars(k, c):
    img = k.canvas()
    d = ImageDraw.Draw(img)
    total, filled = c.get("total", 6), c.get("filled", 0)
    r, gap = k.px(54), k.px(122)
    x0 = k.w - k.px(140) - gap * (total - 1)
    y = k.px(170)
    for i in range(total):
        pts = star(x0 + i * gap, y, r)
        d.polygon(pts, fill=k.rgb("paper" if i < filled else "night", 255 if i < filled else 120),
                  outline=k.rgb("ink"), width=k.px(5))
    icons = c.get("icons") or []
    for i, ic in enumerate(icons):
        chip(k, img, ic.upper(), (k.w - k.px(100) - (len(icons) - 1 - i) * k.px(190), y + k.px(110)), "rt",
             fg="paper", bg="accent", size=20)
    if c.get("tag"):
        d = ImageDraw.Draw(img)
        tf = k.font(64)
        tag = c["tag"].replace("★", "").strip()
        tx, ty = x0 - k.px(40), y + k.px(200)
        d.text((tx, ty), tag, font=tf, fill=k.rgb("accent2"))
        if "★" in c["tag"]:
            sx = tx + d.textlength(tag, font=tf) + k.px(42)
            d.polygon(star(sx, ty + tf.size * 0.62, k.px(30)), fill=k.rgb("accent2"))
    return img


def card_meter(k, c):
    img = k.canvas()
    d = ImageDraw.Draw(img)
    w, h = k.px(1100), k.px(26)
    x, y = (k.w - w) // 2, k.h - k.px(230)
    if c.get("title"):
        d.text((x, y - k.px(70)), c["title"].upper(), font=k.font(28), fill=k.rgb("paper"))
    steps = 40
    for i in range(steps):
        t = i / (steps - 1)
        col = tuple(int(a + (b - a) * t) for a, b in zip(k.rgb("accent2")[:3], k.rgb("accent")[:3])) + (255,)
        d.rectangle((x + w * i / steps, y, x + w * (i + 1) / steps, y + h), fill=col)
    v = max(0.0, min(1.0, float(c.get("value", 0.5))))
    mx = x + w * v
    d.ellipse((mx - k.px(22), y + h / 2 - k.px(22), mx + k.px(22), y + h / 2 + k.px(22)), fill=k.rgb("paper"),
              outline=k.rgb("ink"), width=k.px(5))
    lf = k.font(22)
    d.text((x, y + k.px(44)), c.get("left", "").upper(), font=lf, fill=k.rgb("paper"))
    rt = c.get("right", "").upper()
    d.text((x + w - d.textlength(rt, font=lf), y + k.px(44)), rt, font=lf, fill=k.rgb("paper"))
    cx = x
    for ch in c.get("chips", []):
        chip(k, img, ch.upper(), (cx, y - k.px(140)), "lt", fg="ink", bg="paper", size=20)
        cx += ImageDraw.Draw(img).textlength(ch.upper(), font=k.font(20)) + k.px(60)
    return img


def card_title(k, c):
    img = k.canvas()
    d = ImageDraw.Draw(img)
    f = k.font(c.get("size", 130))
    words = c["text"].upper().split()
    lines = wrap_words(d, words, f, k.w - k.px(240))
    lh = int(f.size * 1.05)
    y0 = (k.h - lh * len(lines)) // 2 - (k.px(30) if c.get("sub") else 0)
    for li, line in enumerate(lines):
        lw = line[-1][1] + line[-1][2]
        for i, x, _ in line:
            d.text(((k.w - lw) / 2 + x, y0 + li * lh), words[i], font=f, fill=k.rgb("paper"),
                   stroke_width=k.px(4), stroke_fill=k.rgb("ink"))
    if c.get("sub"):
        sf = k.font(36)
        d.text(((k.w - d.textlength(c["sub"].upper(), font=sf)) / 2, y0 + lh * len(lines) + k.px(20)),
               c["sub"].upper(), font=sf, fill=k.rgb("accent2"), stroke_width=k.px(2), stroke_fill=k.rgb("ink"))
    return img


RENDER = {"headline": card_headline, "photo": card_photo, "label": card_label, "stamp": card_stamp,
          "chapter": card_chapter, "stat": card_stat, "checklist": card_checklist, "stars": card_stars,
          "meter": card_meter, "title": card_title}


def render_all(spec_path, outdir):
    spec_path = Path(spec_path)
    spec = json.loads(spec_path.read_text(encoding="utf-8-sig"))
    k = Kit(spec.get("width", 1920), spec.get("height", 1080), spec.get("theme"), spec_path.parent)
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    made = []
    for c in spec["cards"]:
        name, kind = c["name"], c["kind"]
        if not re.fullmatch(r"[A-Za-z0-9_-]+", name):
            sys.exit(f"Card name {name!r}: letters, digits, - and _ only.")
        if kind == "quote":
            states = c.get("states") or [[]]
            for si, st in enumerate(states, 1):
                p = outdir / (f"{name}_{si}.png" if c.get("states") else f"{name}.png")
                card_quote(k, c, st).save(p)
                made.append(p)
        elif kind in RENDER:
            p = outdir / f"{name}.png"
            RENDER[kind](k, c).save(p)
            made.append(p)
        else:
            sys.exit(f"Unknown card kind {kind!r} for {name}")
    return made


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("outdir")
    a = ap.parse_args()
    for p in render_all(a.spec, a.outdir):
        print(p)


if __name__ == "__main__":
    main()
