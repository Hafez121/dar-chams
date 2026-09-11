#!/usr/bin/env python3
"""
Dar Chams - stand-in artwork generator.

The build environment for this demo had no outbound access to Unsplash/Pexels
(egress policy blocked every stock-photo host), so the image slots are filled
with original procedural illustrations in the site palette instead of
placeholder greys. Every file is written at the exact dimensions the markup
declares, so swapping in real photography is a straight file replace.
See ../README.md and ../HANDOFF.md.
"""
import io, math, os, random, subprocess, sys
import cairosvg
from PIL import Image, ImageFilter, ImageChops

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "img")

# ---------------------------------------------------------------- palette
LIME_L  = "#EFE7DA"; LIME    = "#E2D7C6"; LIME_D  = "#CDBFA9"
STONE_S = "#B8A991"
TERRA   = "#B3532F"; TERRA_D = "#8E3F24"; TERRA_L = "#C86A44"
OLIVE   = "#6E7A50"; OLIVE_D = "#4C5639"; OLIVE_L = "#8A9468"
SHADE   = "#2F2A25"; SHADE_2 = "#4A423A"
SKY_A   = "#D8CFC0"; SKY_B   = "#BFC6C2"
WOOD    = "#7A5942"

def svg(w, h, body, defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}"><defs>{defs}</defs>{body}</svg>')

def lin(id_, stops, x1=0, y1=0, x2=0, y2=1):
    s = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    return f'<linearGradient id="{id_}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{s}</linearGradient>'

def ridgeline(w, y, amp, seed, steps=48):
    """Smooth-ish mountain profile as a point list."""
    r = random.Random(seed)
    ph = [r.uniform(0, math.tau) for _ in range(3)]
    pts = []
    for i in range(steps + 1):
        x = w * i / steps
        t = i / steps
        v = (math.sin(t * 3.1 + ph[0]) * 0.55 +
             math.sin(t * 6.7 + ph[1]) * 0.28 +
             math.sin(t * 11.3 + ph[2]) * 0.17)
        pts.append((x, y + v * amp))
    return pts

def hill(w, h, y, amp, seed, fill, opacity=1.0):
    pts = ridgeline(w, y, amp, seed)
    d = " ".join(f"{x:.1f},{p:.1f}" for x, p in pts)
    return f'<polygon points="0,{h} {d} {w},{h}" fill="{fill}" opacity="{opacity}"/>'

def stone_courses(x, y, w, h, seed, fill, joint="#000000", ch=13, joint_op=0.10):
    """Limestone ashlar courses - horizontal beds, staggered vertical joints."""
    r = random.Random(seed)
    out = ([] if fill == "none" else [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"/>'])
    yy = y
    row = 0
    while yy < y + h - 1:
        hh = min(ch, y + h - yy)
        out.append(f'<rect x="{x}" y="{yy + hh - 1:.1f}" width="{w}" height="1" fill="{joint}" opacity="{joint_op}"/>')
        cx = x + (ch * 1.4 if row % 2 else ch * 2.6)
        while cx < x + w:
            out.append(f'<rect x="{cx:.1f}" y="{yy:.1f}" width="1" height="{hh:.1f}" fill="{joint}" opacity="{joint_op}"/>')
            cx += r.uniform(ch * 1.7, ch * 3.4)
        yy += ch
        row += 1
    return "".join(out)

def tiled_roof(x, y, w, h, c=TERRA, cd=TERRA_D, eave=10):
    """Red mission-tile roof: slab, eave shadow, vertical tile ribs."""
    out = [f'<polygon points="{x-eave},{y+h} {x+w+eave},{y+h} {x+w-h*0.55},{y} {x+h*0.55},{y}" fill="{c}"/>']
    n = max(4, int(w / 11))
    for i in range(n + 1):
        t = i / n
        xb = x - eave + (w + 2 * eave) * t
        xt = x + h * 0.55 + (w - h * 1.1) * t
        out.append(f'<line x1="{xb:.1f}" y1="{y+h}" x2="{xt:.1f}" y2="{y}" stroke="{cd}" stroke-width="1.1" opacity=".55"/>')
    out.append(f'<rect x="{x-eave}" y="{y+h-3}" width="{w+2*eave}" height="3.5" fill="{cd}"/>')
    return "".join(out)

def arch_path(x, y, w, h):
    """Round-headed opening: semicircular head on straight jambs."""
    r = w / 2
    return (f'M{x},{y+h} L{x},{y+r} A{r},{r} 0 0 1 {x+w},{y+r} L{x+w},{y+h} Z')

def triple_arch(x, y, w, h, glass="url(#g-view)", frame=LIME_L, col=LIME_D):
    """The Lebanese central hall window: three round-headed lights, slim columns."""
    gap = w * 0.045
    aw = (w - 2 * gap) / 3
    out = [f'<rect x="{x-8}" y="{y-8}" width="{w+16}" height="{h+8}" fill="{frame}"/>']
    for i in range(3):
        ax = x + i * (aw + gap)
        ah = h if i != 1 else h + h * 0.09
        ay = y if i != 1 else y - h * 0.09
        out.append(f'<path d="{arch_path(ax, ay, aw, ah)}" fill="{glass}"/>')
        out.append(f'<path d="{arch_path(ax, ay, aw, ah)}" fill="none" stroke="{col}" stroke-width="3"/>')
    for i in (0, 1):
        cx = x + aw + gap / 2 + i * (aw + gap)
        out.append(f'<rect x="{cx-3}" y="{y+h*0.45}" width="6" height="{h*0.55}" fill="{col}"/>')
    return "".join(out)

def shutter(x, y, w, h, c=OLIVE_D):
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{c}"/>']
    n = int(h / 7)
    for i in range(1, n):
        out.append(f'<rect x="{x}" y="{y + i*h/n:.1f}" width="{w}" height="1.4" fill="#000000" opacity="0.15"/>')
    return "".join(out)

def cypress(x, y, h, c=OLIVE_D):
    w = h * 0.24
    return (f'<path d="M{x},{y} C{x-w/2},{y-h*0.35} {x-w/2},{y-h*0.7} {x},{y-h} '
            f'C{x+w/2},{y-h*0.7} {x+w/2},{y-h*0.35} {x},{y} Z" fill="{c}"/>')

def olive_tree(x, y, r, seed, c=OLIVE, trunk=SHADE_2):
    rr = random.Random(seed)
    out = [f'<rect x="{x-r*0.07:.1f}" y="{y-r*0.85:.1f}" width="{max(2,r*0.14):.1f}" height="{r*0.9:.1f}" fill="{trunk}" opacity=".75"/>']
    for _ in range(7):
        cx = x + rr.uniform(-r * 0.75, r * 0.75)
        cy = y - r * 0.95 + rr.uniform(-r * 0.55, r * 0.3)
        rad = rr.uniform(r * 0.38, r * 0.66)
        out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{rad:.1f}" fill="{c}" opacity=".92"/>')
    return "".join(out)

def village_house(x, y, w, h, seed, roof=True, flat=False):
    out = [stone_courses(x, y, w, h, seed, LIME, ch=max(7, h / 9))]
    r = random.Random(seed + 7)
    if roof and not flat:
        out.insert(0, tiled_roof(x, y - h * 0.42, w, h * 0.42, eave=w * 0.06))
    else:
        out.insert(0, f'<rect x="{x-w*0.04}" y="{y-6}" width="{w*1.08}" height="6" fill="{LIME_D}"/>')
    nw = max(1, int(w / 34))
    for i in range(nw):
        ww = w / (nw * 2.1)
        wx = x + w * 0.12 + i * (w - w * 0.24) / max(1, nw - 0.001) if nw > 1 else x + w / 2 - ww / 2
        wx = min(wx, x + w - ww - w * 0.1)
        wy = y + h * 0.3
        wh = h * 0.34
        out.append(f'<path d="{arch_path(wx, wy, ww, wh)}" fill="{SHADE}" opacity=".72"/>')
        if r.random() > 0.45:
            out.append(shutter(wx, wy + wh * 0.35, ww, wh * 0.62, OLIVE_D))
    return "".join(out)

# ---------------------------------------------------------------- scenes
def sc_village(w, h):
    """Douma across the valley at the end of the day: haze layers, one stone cluster."""
    defs = (lin("sky", [(0, "#9FAEB2"), (0.42, "#C9C2B2"), (0.72, SKY_A), (1, "#EFE2CC")]) +
            lin("slope", [(0, "#8B9670"), (1, "#59633F")]))
    b = [f'<rect width="{w}" height="{h}" fill="url(#sky)"/>']
    b.append(f'<circle cx="{w*0.72}" cy="{h*0.215}" r="{h*0.052}" fill="#F6E8CC" opacity=".85"/>')
    for i, (y, amp, col, op) in enumerate(((0.335, 0.040, "#A8B0B0", .70),
                                           (0.410, 0.045, "#94A099", .78),
                                           (0.495, 0.042, "#7E8C7C", .85),
                                           (0.585, 0.038, "#67775F", .92))):
        b.append(hill(w, h, h * y, h * amp, 41 + i * 17, col, op))
    # valley mist
    for i, (y, hh, op) in enumerate(((0.455, 0.030, .30), (0.520, 0.026, .24), (0.575, 0.022, .18))):
        b.append(f'<rect y="{h*y:.1f}" width="{w}" height="{h*hh:.1f}" fill="#E7DFD0" opacity="{op}"/>')
    # the bank the village sits on
    b.append(f'<polygon points="0,{h} 0,{h*0.565} {w*0.52},{h*0.605} {w},{h*0.660} {w},{h}" fill="url(#slope)"/>')

    def cluster(x0, base, unit, seeds, alpha):
        g = [f'<g opacity="{alpha}">']
        x = x0
        for k, sd in enumerate(seeds):
            hw = unit * (0.78 + (sd % 6) * 0.09)
            hh = unit * (0.62 + (sd % 4) * 0.10)
            y = base - (sd % 3) * unit * 0.16
            g.append(village_house(x, y, hw, hh, sd, flat=(sd % 5 == 2)))
            x += hw * (0.80 if sd % 2 else 0.94)
        g.append("</g>")
        return "".join(g)

    # upper tier, set back and hazed; lower tier, closer and full strength
    for i in range(6):
        t = i / 5
        y0 = h * (0.615 + t * 0.30); y1 = h * (0.665 + t * 0.29)
        b.append(f'<polygon points="0,{y0:.1f} {w},{y1:.1f} {w},{y1+h*0.010:.1f} 0,{y0+h*0.010:.1f}" fill="{LIME_D}" opacity=".16"/>')
    b.append(cluster(w * 0.055, h * 0.630, w * 0.068, [17, 29, 34, 41, 56, 63, 77], .62))
    b.append(cluster(w * 0.700, h * 0.700, w * 0.046, [12, 25, 38], .42))
    b.append(cluster(w * 0.075, h * 0.760, w * 0.092, [71, 88, 93, 104, 119, 126], 1.0))
    for fx, fy, sc in ((0.035, 0.700, 0.080), (0.62, 0.775, 0.072), (0.79, 0.815, 0.088), (0.955, 0.855, 0.078)):
        b.append(cypress(w * fx, h * fy, h * sc, OLIVE_D))
    for i, (fx, fy, r) in enumerate(((0.60, 0.905, 0.055), (0.72, 0.875, 0.048), (0.83, 0.915, 0.052), (0.95, 0.885, 0.046))):
        b.append(olive_tree(w * fx, h * fy, h * r, 700 + i, OLIVE))
    # foreground ridge - the side of the valley you are standing on
    b.append(f'<polygon points="0,{h} 0,{h*0.880} {w*0.30},{h*0.925} {w*0.62},{h*0.893} {w},{h*0.942} {w},{h}" fill="#333D2B"/>')
    for i, fx in enumerate((0.08, 0.21, 0.37, 0.52, 0.68, 0.86, 0.97)):
        b.append(olive_tree(w * fx, h * (0.995 if i % 2 else 0.975), h * 0.062, 800 + i, "#2F3A28"))
    return svg(w, h, "".join(b), defs)

def sc_valley(w, h):
    """The valley below the village at dusk: layered ridges, deep to pale."""
    defs = lin("dsky", [(0, "#5E6B75"), (0.35, "#93949A"), (0.62, "#C9A98D"), (0.85, "#E3BE93"), (1, "#EFD3A8")])
    b = [f'<rect width="{w}" height="{h}" fill="url(#dsky)"/>']
    b.append(f'<circle cx="{w*0.30}" cy="{h*0.615}" r="{h*0.075}" fill="#FBE7BC" opacity=".95"/>')
    b.append(f'<circle cx="{w*0.30}" cy="{h*0.615}" r="{h*0.14}" fill="#F6DCAE" opacity=".22"/>')
    layers = ((0.605, 0.035, "#9A8C7E", .85), (0.665, 0.040, "#7B7263", .92),
              (0.735, 0.038, "#565A49", .96), (0.815, 0.034, "#3B4335", 1),
              (0.895, 0.028, "#272E23", 1))
    for i, (y, amp, col, op) in enumerate(layers):
        b.append(hill(w, h, h * y, h * amp, 41 + i * 13, col, op))
        if i == 1:
            # a neighbouring hamlet catching the last of the light
            g = ['<g opacity=".9">']
            x = w * 0.56
            for k, sd in enumerate([13, 27, 31, 44]):
                hw = w * 0.030 * (1 + (sd % 3) * 0.22)
                g.append(village_house(x, h * (0.672 + (sd % 2) * 0.006), hw, h * 0.030, sd))
                x += hw * 0.92
            g.append("</g>")
            b.append("".join(g))
    for i, (fx, fy, sc) in enumerate(((0.14, 0.86, 0.115), (0.23, 0.90, 0.095),
                                      (0.69, 0.93, 0.125), (0.80, 0.885, 0.10), (0.93, 0.955, 0.115))):
        b.append(cypress(w * fx, h * fy, h * sc, "#1F2419"))
    return svg(w, h, "".join(b), defs)

def sc_facade(w, h):
    defs = (lin("sky2", [(0, "#BFC7C4"), (1, "#E3DACA")]) +
            lin("g-view", [(0, "#3C4438"), (1, "#25291F")]))
    b = [f'<rect width="{w}" height="{h}" fill="url(#sky2)"/>',
         f'<rect y="{h*0.78}" width="{w}" height="{h*0.22}" fill="{OLIVE_D}"/>']
    bx, bw = w * 0.10, w * 0.80
    by, bh = h * 0.26, h * 0.56
    b.append(tiled_roof(bx, by - h * 0.14, bw, h * 0.14, eave=w * 0.05))
    b.append(stone_courses(bx, by, bw, bh, 3, LIME, ch=h / 26))
    b.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="url(#warm)" opacity="0"/>')
    # central triple-arch window
    aw = bw * 0.44
    b.append(triple_arch(bx + bw / 2 - aw / 2, by + bh * 0.16, aw, bh * 0.42))
    # flanking shuttered windows
    for fx in (0.10, 0.78):
        sx = bx + bw * fx
        sw, sh_ = bw * 0.12, bh * 0.26
        b.append(f'<rect x="{sx-4}" y="{by+bh*0.20-4}" width="{sw+8}" height="{sh_+8}" fill="{LIME_L}"/>')
        b.append(shutter(sx, by + bh * 0.20, sw, sh_))
    # door
    dw, dh = bw * 0.11, bh * 0.30
    dx = bx + bw / 2 - dw / 2
    b.append(f'<path d="{arch_path(dx, by+bh-dh, dw, dh)}" fill="{WOOD}"/>')
    b.append(f'<path d="{arch_path(dx, by+bh-dh, dw, dh)}" fill="none" stroke="{LIME_L}" stroke-width="5"/>')
    # steps + planters
    b.append(f'<rect x="{dx-dw*0.5}" y="{by+bh}" width="{dw*2}" height="{h*0.03}" fill="{LIME_D}"/>')
    for i, fx in enumerate((0.06, 0.9)):
        b.append(olive_tree(bx + bw * fx, h * 0.86, h * 0.10, 300 + i, OLIVE))
    b.append(cypress(w * 0.045, h * 0.84, h * 0.34, OLIVE_D))
    return svg(w, h, "".join(b), defs)

def sc_arch_window(w, h):
    defs = (lin("g-view", [(0, "#9FB0A6"), (0.45, "#7C8F74"), (1, "#55633F")]))
    b = [f'<rect width="{w}" height="{h}" fill="{LIME}"/>',
         stone_courses(0, 0, w, h, 8, LIME, ch=h / 24)]
    aw = w * 0.74
    b.append(triple_arch(w / 2 - aw / 2, h * 0.17, aw, h * 0.50))
    # sill + floor tiles
    b.append(f'<rect x="{w*0.06}" y="{h*0.68}" width="{w*0.88}" height="{h*0.035}" fill="{LIME_L}"/>')
    b.append(f'<rect y="{h*0.715}" width="{w}" height="{h*0.285}" fill="{LIME_D}"/>')
    r = random.Random(4)
    for i in range(5):
        for j in range(4):
            x = -w * 0.1 + i * w * 0.26
            y = h * 0.73 + j * h * 0.075
            b.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w*0.24:.1f}" height="{h*0.065:.1f}" fill="{LIME_L if (i+j)%2 else STONE_S}" opacity=".6"/>')
    b.append(f'<rect x="{w*0.10}" y="{h*0.60}" width="{w*0.13}" height="{h*0.09}" fill="{OLIVE}" opacity=".9"/>')
    return svg(w, h, "".join(b), defs)

def interior(w, h, seed, window="arch", bedc=LIME_L, accent=TERRA, vault=False):
    """Front-elevation room vignette: plaster wall, opening, bed, light from the window."""
    defs = (lin("g-view", [(0, "#AEBBA6"), (1, "#6E7C58")]) +
            lin("plaster", [(0, "#F3ECDF"), (1, "#E2D8C6")]) +
            lin("shaft", [(0, "#FFF4DC"), (1, "#FFF4DC")], 0, 0, 1, 1))
    floor_y = h * 0.80
    b = [f'<rect width="{w}" height="{h}" fill="url(#plaster)"/>']
    b.append(f'<g opacity=".22">{stone_courses(0, 0, w, int(floor_y), seed, "none", "#6B5A44", ch=h/14)}</g>')
    if vault:
        b.append(f'<path d="M0,{h*0.26} Q{w/2},{-h*0.10} {w},{h*0.26} L{w},0 L0,0 Z" fill="#F7F1E6"/>')
        b.append(f'<path d="M0,{h*0.26} Q{w/2},{-h*0.10} {w},{h*0.26}" fill="none" stroke="{LIME_D}" stroke-width="3"/>')
    # ---- opening
    if window == "arch":
        ax, ay, aw, ah = w * 0.575, h * 0.17, w * 0.365, h * 0.40
        b.append(triple_arch(ax, ay, aw, ah))
        lx, lw = ax, aw
    else:
        wx, wy, ww, wh = w * 0.62, h * 0.19, w * 0.27, h * 0.36
        b.append(f'<rect x="{wx-9}" y="{wy-9}" width="{ww+18}" height="{wh+18}" fill="#F7F1E6"/>')
        b.append(f'<rect x="{wx}" y="{wy}" width="{ww}" height="{wh}" fill="url(#g-view)"/>')
        b.append(f'<rect x="{wx+ww/2-2.5}" y="{wy}" width="5" height="{wh}" fill="#F7F1E6"/>')
        b.append(f'<rect x="{wx}" y="{wy+wh*0.5-2}" width="{ww}" height="4" fill="#F7F1E6"/>')
        b.append(shutter(wx - ww * 0.34, wy, ww * 0.32, wh))
        b.append(shutter(wx + ww + ww * 0.02, wy, ww * 0.32, wh))
        b.append(f'<rect x="{wx-14}" y="{wy+wh+7}" width="{ww+28}" height="9" fill="#F7F1E6"/>')
        lx, lw = wx, ww
    # ---- light falling from the opening onto floor and wall
    b.append(f'<polygon points="{lx},{h*0.56} {lx+lw},{h*0.56} {lx+lw*1.45},{h} {lx-lw*0.35},{h}" fill="#FFF3D8" opacity=".28"/>')
    # ---- floor
    b.append(f'<rect y="{floor_y}" width="{w}" height="{h-floor_y}" fill="{STONE_S}"/>')
    for i in range(17):
        for j in range(4):
            x, y = i * w / 16.4 - w * 0.01, floor_y + j * (h - floor_y) / 3.9
            b.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w/16.8:.1f}" height="{(h-floor_y)/4.1:.1f}" fill="{LIME_D if (i+j)%2 else "#F0E8D9"}" opacity=".45"/>')
    b.append(f'<rect y="{floor_y-7}" width="{w}" height="7" fill="#F7F1E6"/>')
    b.append(f'<rect y="{floor_y}" width="{w}" height="3" fill="#000000" opacity="0.13"/>')
    # ---- rug
    ry0 = floor_y + (h - floor_y) * 0.26
    b.append(f'<rect x="{w*0.035}" y="{ry0:.1f}" width="{w*0.58}" height="{(h-floor_y)*0.56:.1f}" fill="{accent}" opacity=".45"/>')
    b.append(f'<rect x="{w*0.035}" y="{ry0:.1f}" width="{w*0.58}" height="{(h-floor_y)*0.56:.1f}" fill="none" stroke="#F3EBDC" stroke-width="4" opacity=".6"/>')
    b.append(f'<rect x="{w*0.09}" y="{ry0 + (h-floor_y)*0.22:.1f}" width="{w*0.47}" height="{(h-floor_y)*0.09:.1f}" fill="#F3EBDC" opacity=".4"/>')
    # ---- bed
    bx, bw_ = w * 0.055, w * 0.455
    mat_y, mat_h = h * 0.545, h * 0.155
    hb_y, hb_h = h * 0.335, h * 0.215
    b.append(f'<rect x="{bx-w*0.012}" y="{hb_y}" width="{bw_+w*0.024}" height="{hb_h}" rx="{w*0.006}" fill="{WOOD}"/>')
    for i in range(1, 9):
        xx = bx - w * 0.012 + (bw_ + w * 0.024) * i / 9
        b.append(f'<line x1="{xx:.1f}" y1="{hb_y+6}" x2="{xx:.1f}" y2="{hb_y+hb_h-4}" stroke="#000000" stroke-opacity="0.15" stroke-width="2"/>')
    b.append(f'<rect x="{bx}" y="{mat_y}" width="{bw_}" height="{mat_h}" fill="{bedc}"/>')
    b.append(f'<rect x="{bx}" y="{mat_y+mat_h}" width="{bw_}" height="{h*0.055}" fill="#EDE4D4"/>')
    b.append(f'<rect x="{bx}" y="{mat_y+mat_h*0.62}" width="{bw_}" height="{mat_h*0.42}" fill="{accent}" opacity=".8"/>')
    b.append(f'<rect x="{bx}" y="{mat_y+mat_h*0.62}" width="{bw_}" height="3" fill="#000000" opacity="0.09"/>')
    pw, ph = bw_ * 0.40, h * 0.075
    for k in (0, 1):
        b.append(f'<rect x="{bx + bw_*0.055 + k*(pw + bw_*0.05):.1f}" y="{mat_y-ph*0.86:.1f}" width="{pw:.1f}" height="{ph:.1f}" rx="{ph*0.42:.1f}" fill="#FBF7EF"/>')
    for k in (0.03, 0.94):
        b.append(f'<rect x="{bx + bw_*k:.1f}" y="{mat_y+mat_h+h*0.055}" width="{bw_*0.035:.1f}" height="{floor_y - (mat_y+mat_h+h*0.055):.1f}" fill="{WOOD}"/>')
    b.append(f'<ellipse cx="{bx+bw_/2}" cy="{floor_y+4}" rx="{bw_*0.52}" ry="{h*0.011}" fill="#3A3026" opacity="0.18"/>')
    # ---- bedside table, lamp, a hanging textile
    tx = bx + bw_ + w * 0.035
    b.append(f'<rect x="{tx}" y="{h*0.615}" width="{w*0.095}" height="{h*0.016}" fill="{WOOD}"/>')
    for k in (0.01, 0.075):
        b.append(f'<rect x="{tx + w*k}" y="{h*0.631}" width="{w*0.011}" height="{floor_y-h*0.631:.1f}" fill="{WOOD}"/>')
    b.append(f'<rect x="{tx+w*0.042}" y="{h*0.565}" width="{w*0.008}" height="{h*0.05}" fill="{SHADE_2}"/>')
    b.append(f'<path d="M{tx+w*0.022},{h*0.567} L{tx+w*0.032},{h*0.522} L{tx+w*0.062},{h*0.522} L{tx+w*0.072},{h*0.567} Z" fill="#FBF3E2"/>')
    b.append(f'<circle cx="{tx+w*0.046}" cy="{h*0.545}" r="{h*0.055}" fill="#FFF0CE" opacity=".30"/>')
    return svg(w, h, "".join(b), defs)

def sc_breakfast(w, h):
    """Mezze breakfast laid on a stone table, seen from above."""
    defs = ""
    b = [f'<rect width="{w}" height="{h}" fill="{WOOD}"/>']
    r = random.Random(17)
    for i in range(14):
        y = i * h / 13
        b.append(f'<rect y="{y:.1f}" width="{w}" height="{h/13*0.5:.1f}" fill="#000000" opacity="0.06"/>')
    b.append(f'<rect x="{w*0.05}" y="{h*0.06}" width="{w*0.90}" height="{h*0.88}" fill="{LIME}" rx="6"/>')
    plates = [(0.22, 0.32, 0.105), (0.44, 0.24, 0.075), (0.63, 0.33, 0.09),
              (0.80, 0.25, 0.06), (0.30, 0.66, 0.085), (0.50, 0.60, 0.115),
              (0.72, 0.68, 0.08), (0.86, 0.55, 0.055), (0.14, 0.52, 0.06)]
    fills = [LIME_L, "#F3EDE1", LIME_L, "#F3EDE1", LIME_L, "#F6F1E7", LIME_L, "#F3EDE1", LIME_L]
    foods = [OLIVE, TERRA_L, "#D9C36B", OLIVE_L, TERRA, "#EFE3C8", OLIVE_D, TERRA_L, OLIVE]
    for i, (fx, fy, fr) in enumerate(plates):
        cx, cy, rad = w * fx, h * fy, h * fr
        b.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{rad:.1f}" fill="#000000" opacity="0.07"/>')
        b.append(f'<circle cx="{cx:.1f}" cy="{cy-2:.1f}" r="{rad:.1f}" fill="{fills[i]}"/>')
        b.append(f'<circle cx="{cx:.1f}" cy="{cy-2:.1f}" r="{rad*0.78:.1f}" fill="{foods[i]}" opacity=".9"/>')
        for _ in range(6):
            a = r.uniform(0, math.tau); d = r.uniform(0, rad * 0.55)
            b.append(f'<circle cx="{cx+math.cos(a)*d:.1f}" cy="{cy-2+math.sin(a)*d:.1f}" r="{rad*0.08:.1f}" fill="#FFFFFF" opacity=".35"/>')
    # bread board, folded napkin, jar of jam, and the rakwe
    b.append(f'<rect x="{w*0.585}" y="{h*0.74}" width="{w*0.20}" height="{h*0.145}" rx="6" fill="{WOOD}" opacity=".9"/>')
    for k in range(3):
        b.append(f'<ellipse cx="{w*(0.615+k*0.055)}" cy="{h*0.812}" rx="{w*0.022}" ry="{h*0.045}" fill="#E9D7B4"/>')
        b.append(f'<ellipse cx="{w*(0.615+k*0.055)}" cy="{h*0.812}" rx="{w*0.012}" ry="{h*0.026}" fill="#D8C094" opacity=".8"/>')
    b.append(f'<rect x="{w*0.175}" y="{h*0.80}" width="{w*0.115}" height="{h*0.10}" fill="#EFE7D6"/>')
    b.append(f'<rect x="{w*0.175}" y="{h*0.845}" width="{w*0.115}" height="{h*0.008}" fill="{TERRA}" opacity=".7"/>')
    b.append(f'<rect x="{w*0.415}" y="{h*0.80}" width="{w*0.055}" height="{h*0.085}" rx="4" fill="{TERRA_D}" opacity=".85"/>')
    b.append(f'<rect x="{w*0.410}" y="{h*0.788}" width="{w*0.065}" height="{h*0.016}" rx="3" fill="{LIME_L}"/>')
    b.append(f'<path d="M{w*0.085},{h*0.13} L{w*0.145},{h*0.13} L{w*0.128},{h*0.30} L{w*0.102},{h*0.30} Z" fill="{SHADE_2}"/>')
    b.append(f'<path d="M{w*0.145},{h*0.165} q{w*0.035},{h*0.045} -{w*0.008},{h*0.085}" fill="none" stroke="{SHADE_2}" stroke-width="5"/>')
    b.append(f'<rect x="{w*0.105}" y="{h*0.115}" width="{w*0.02}" height="{h*0.02}" fill="{SHADE_2}"/>')
    for fx, fy in ((0.90, 0.83), (0.10, 0.80)):
        b.append(f'<circle cx="{w*fx}" cy="{h*fy}" r="{h*0.042}" fill="#F6F1E7"/>')
        b.append(f'<circle cx="{w*fx}" cy="{h*fy}" r="{h*0.028}" fill="{SHADE}" opacity=".8"/>')
    return svg(w, h, "".join(b), defs)

def sc_terraces(w, h):
    """Olive terraces: dry-stone retaining walls stepping down the hillside."""
    defs = lin("tsky", [(0, "#BAC4C4"), (1, "#E4DCCC")])
    b = [f'<rect width="{w}" height="{h}" fill="url(#tsky)"/>']
    b.append(hill(w, h, h * 0.16, h * 0.04, 61, "#A9B2AC", .75))
    b.append(f'<polygon points="0,{h} 0,{h*0.26} {w},{h*0.20} {w},{h}" fill="{OLIVE_L}"/>')
    rows = 5
    for i in range(rows):
        t = i / (rows - 1)
        y0 = h * (0.26 + t * 0.60); y1 = h * (0.20 + t * 0.66)
        wall_h = h * (0.045 + t * 0.028)
        b.append(f'<polygon points="0,{y0:.1f} {w},{y1:.1f} {w},{y1+wall_h:.1f} 0,{y0+wall_h:.1f}" fill="{LIME}"/>')
        b.append(f'<g opacity=".75">{stone_courses(0, min(y0, y1), w, wall_h + abs(y1-y0) + 2, 70+i*11, "none", "#6B5A44", ch=max(6, wall_h/2.2))}</g>')
        b.append(f'<polygon points="0,{y0+wall_h:.1f} {w},{y1+wall_h:.1f} {w},{y1+wall_h+h*0.012:.1f} 0,{y0+wall_h+h*0.012:.1f}" fill="#000000" opacity=".10"/>')
        band = h * (0.09 + t * 0.035)
        b.append(f'<polygon points="0,{y0+wall_h:.1f} {w},{y1+wall_h:.1f} {w},{y1+wall_h+band:.1f} 0,{y0+wall_h+band:.1f}" fill="{OLIVE if i%2 else OLIVE_L}" opacity=".9"/>')
        n = 4 if i > 1 else 5
        for j in range(n):
            fx = (j + 0.35 + (i % 2) * 0.3) / n
            yy = (y0 + (y1 - y0) * fx) + wall_h + band * 0.82
            b.append(olive_tree(w * fx, yy, h * (0.055 + t * 0.045), 400 + i * 10 + j, OLIVE_D if i % 2 else OLIVE))
    # a stone field hut on the third terrace
    hy = h * 0.545
    b.append(village_house(w * 0.70, hy, w * 0.10, h * 0.085, 91))
    b.append(cypress(w * 0.60, hy + h * 0.085, h * 0.15, OLIVE_D))
    return svg(w, h, "".join(b), defs)

def sc_souk(w, h):
    defs = lin("g-view", [(0, "#CFC4B2"), (1, "#A79880")])
    b = [f'<rect width="{w}" height="{h}" fill="#BEB09A"/>']
    b.append(f'<rect width="{w}" height="{h*0.70}" fill="url(#g-view)"/>')
    # arcade on both sides
    b.append(stone_courses(0, 0, w * 0.34, h, 12, LIME, ch=h / 30))
    b.append(stone_courses(w * 0.66, 0, w * 0.34, h, 19, LIME_D, ch=h / 30))
    for i in range(3):
        y = h * (0.30 + i * 0.005)
        b.append(f'<path d="{arch_path(w*0.045, h*0.34+i*h*0.19, w*0.19, h*0.17)}" fill="{SHADE}" opacity=".55"/>')
        b.append(f'<path d="{arch_path(w*0.75, h*0.30+i*h*0.19, w*0.18, h*0.16)}" fill="{SHADE}" opacity=".62"/>')
    # awnings
    for i, (fx, fy, c) in enumerate(((0.05, 0.28, TERRA), (0.70, 0.24, OLIVE), (0.06, 0.60, OLIVE_D))):
        b.append(f'<polygon points="{w*fx},{h*fy} {w*(fx+0.22)},{h*(fy-0.02)} {w*(fx+0.22)},{h*(fy+0.05)} {w*fx},{h*(fy+0.07)}" fill="{c}" opacity=".9"/>')
    # cobbled street receding
    b.append(f'<polygon points="{w*0.34},0 {w*0.66},0 {w*0.78},{h} {w*0.22},{h}" fill="{STONE_S}"/>')
    r = random.Random(21)
    for i in range(22):
        t = i / 21
        y = h * t
        half = (0.16 + 0.12 * t) * w
        b.append(f'<rect x="{w*0.5-half:.1f}" y="{y:.1f}" width="{half*2:.1f}" height="{h*0.012:.1f}" fill="#000000" opacity="0.075"/>')
    b.append(f'<rect x="{w*0.40}" y="0" width="{w*0.20}" height="{h*0.22}" fill="#000000" opacity="0.09"/>')
    return svg(w, h, "".join(b), defs)

def sc_stair(w, h):
    b = [f'<rect width="{w}" height="{h}" fill="{LIME}"/>',
         stone_courses(0, 0, w, h, 27, LIME, ch=h / 30)]
    steps = 9
    for i in range(steps):
        t = i / steps
        y = h * (0.30 + t * 0.68)
        wd = w * (0.42 + t * 0.5)
        x = w * 0.20 - w * 0.12 * t
        b.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{wd:.1f}" height="{h*0.045:.1f}" fill="{LIME_L}"/>')
        b.append(f'<rect x="{x:.1f}" y="{y+h*0.045:.1f}" width="{wd:.1f}" height="{h*0.028:.1f}" fill="{STONE_S}"/>')
    b.append(f'<path d="{arch_path(w*0.30, h*0.08, w*0.34, h*0.26)}" fill="{SHADE}" opacity=".6"/>')
    for i, (fx, fy, rad) in enumerate(((0.88, 0.55, 0.06), (0.08, 0.72, 0.05), (0.93, 0.85, 0.07), (0.05, 0.40, 0.045))):
        b.append(f'<circle cx="{w*fx}" cy="{h*fy}" r="{h*rad}" fill="{OLIVE}" opacity=".9"/>')
        b.append(f'<rect x="{w*fx-w*0.035}" y="{h*fy+h*rad*0.6}" width="{w*0.07}" height="{h*0.05}" fill="{TERRA}"/>')
    return svg(w, h, "".join(b), defs="")

def sc_courtyard(w, h):
    defs = lin("csky", [(0, "#C8CEC7"), (1, "#E9E0CE")])
    b = [f'<rect width="{w}" height="{h}" fill="url(#csky)"/>']
    b.append(stone_courses(0, 0, w, int(h * 0.62), 33, LIME, ch=h / 16))
    for i in range(4):
        x = w * (0.06 + i * 0.24)
        b.append(f'<path d="{arch_path(x, h*0.16, w*0.16, h*0.44)}" fill="{SHADE}" opacity=".55"/>')
        b.append(f'<path d="{arch_path(x, h*0.16, w*0.16, h*0.44)}" fill="none" stroke="{LIME_L}" stroke-width="6"/>')
    b.append(f'<rect y="{h*0.62}" width="{w}" height="{h*0.38}" fill="{STONE_S}"/>')
    for i in range(12):
        for j in range(3):
            b.append(f'<rect x="{i*w/11.5:.1f}" y="{h*0.63+j*h*0.13:.1f}" width="{w/12:.1f}" height="{h*0.12:.1f}" fill="{LIME_D if (i+j)%2 else LIME_L}" opacity=".5"/>')
    b.append(f'<circle cx="{w*0.5}" cy="{h*0.82}" r="{h*0.14}" fill="{LIME_L}"/>')
    b.append(f'<circle cx="{w*0.5}" cy="{h*0.82}" r="{h*0.10}" fill="#8E9C93" opacity=".8"/>')
    for i, fx in enumerate((0.17, 0.83)):
        b.append(olive_tree(w * fx, h * 0.92, h * 0.14, 500 + i, OLIVE))
    return svg(w, h, "".join(b), defs)

def sc_og(w, h):
    b = [sc_village(w, h)]
    return b[0]

# ---------------------------------------------------------------- pipeline
def finish(svg_text, w, h, name, jpeg_q=74, webp_q=76, grain=6):
    png = cairosvg.svg2png(bytestring=svg_text.encode(), output_width=w, output_height=h)
    im = Image.open(io.BytesIO(png)).convert("RGB")
    if grain:
        noise = Image.effect_noise((w, h), 22).convert("L").filter(ImageFilter.GaussianBlur(0.4))
        im = ImageChops.blend(im, Image.merge("RGB", (noise, noise, noise)), grain / 100)
    # gentle corner falloff so flat art does not read as a UI panel
    v = Image.new("L", (w, h), 0)
    import PIL.ImageDraw as D
    d = D.Draw(v)
    d.ellipse((-w * 0.25, -h * 0.30, w * 1.25, h * 1.30), fill=255)
    v = v.filter(ImageFilter.GaussianBlur(min(w, h) / 12))
    dark = Image.new("RGB", (w, h), (34, 30, 26))
    im = Image.composite(im, Image.blend(im, dark, 0.14), v)
    im.save(os.path.join(OUT, name + ".jpg"), "JPEG", quality=jpeg_q, optimize=True, progressive=True)
    im.save(os.path.join(OUT, name + ".webp"), "WEBP", quality=webp_q, method=6)
    j = os.path.getsize(os.path.join(OUT, name + ".jpg"))
    p = os.path.getsize(os.path.join(OUT, name + ".webp"))
    print(f"{name:22s} {w}x{h}  jpg {j//1024:>4}KB  webp {p//1024:>4}KB")
    return j, p

SCENES = [
    ("hero-village",  1600, 1000, sc_village),
    ("house-facade",  1200,  900, sc_facade),
    ("arch-window",    800, 1000, sc_arch_window),
    ("breakfast",     1200,  800, sc_breakfast),
    ("terraces",      1200,  800, sc_terraces),
    ("valley-dusk",   1600,  900, sc_valley),
    ("souk",           800, 1000, sc_souk),
    ("stone-stair",    800, 1000, sc_stair),
    ("courtyard",     1600,  700, sc_courtyard),
    ("og-cover",      1200,  630, sc_og),
]

def main():
    os.makedirs(OUT, exist_ok=True)
    total = 0
    for name, w, h, fn in SCENES:
        total += finish(fn(w, h), w, h, name)[1]
    # rooms share the interior generator with different fittings
    for name, seed, win, bedc, acc, vault in (
        ("room-garden", 71, "square", "#F2ECE0", OLIVE,  False),
        ("room-arch",   83, "arch",   "#F4EEE3", TERRA,  False),
        ("room-suite",  97, "arch",   "#F1EADC", TERRA_D, True),
    ):
        total += finish(interior(1200, 900, seed, win, bedc, acc, vault), 1200, 900, name)[1]
    print(f"total webp payload: {total//1024} KB")

if __name__ == "__main__":
    main()
