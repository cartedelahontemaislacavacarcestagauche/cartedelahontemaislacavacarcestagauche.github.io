"""Image d'aperçu (Telegram, WhatsApp, X…) dans le style de celle de cartedelahonte.github.io."""
import math

from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
S = 2  # rendu en 2x puis réduit, pour lisser les contours

SEA = (214, 226, 234)
LAND = (247, 246, 242)
LINE = (58, 58, 58)
INK = (17, 17, 17)
RED = (232, 69, 60)

AVENIR = "/System/Library/Fonts/Avenir Next.ttc"
HEAVY, BOLD, MEDIUM, DEMI_ITALIC = 8, 0, 5, 3


def font(face, size):
    return ImageFont.truetype(AVENIR, size * S, index=face)


def rgb(css):
    r, g, b = css[css.index("(") + 1:].split(",")[:3]
    return int(r), int(g), int(b)


def rings(geom):
    polys = [geom["coordinates"]] if geom["type"] == "Polygon" else geom["coordinates"]
    for poly in polys:
        yield poly[0]


def make(entries, circos, depts, colors, mix, out_path, title_lines, cats_text, stat_text, tagline=""):
    img = Image.new("RGB", (W * S, H * S), SEA)
    d = ImageDraw.Draw(img)

    # Projection de Mercator, France métropolitaine (Corse comprise) dans la moitié gauche.
    lon0, lon1, lat0, lat1 = -5.3, 9.7, 41.25, 51.2
    my = lambda lat: math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))
    box = (20, 18, 700, 612)
    sx = (box[2] - box[0]) / math.radians(lon1 - lon0)
    sy = (box[3] - box[1]) / (my(lat1) - my(lat0))
    k = min(sx, sy)
    ox = box[0] + ((box[2] - box[0]) - k * math.radians(lon1 - lon0)) / 2
    oy = box[1] + ((box[3] - box[1]) - k * (my(lat1) - my(lat0))) / 2

    def pt(lon, lat):
        return ((ox + k * math.radians(lon - lon0)) * S, (oy + k * (my(lat1) - my(lat))) * S)

    metro = [dp for dp in depts if len(dp["code"]) == 2]
    for dp in metro:
        for ring in rings(dp["g"]):
            d.polygon([pt(*c) for c in ring], fill=LAND)

    # Une couleur par circonscription : la catégorie, ou « un peu de tout » si plusieurs.
    groups = {}
    for e in entries:
        key = f"{e['dep']}-{e['circo']}" if e.get("dep") and e.get("circo") else None
        if key and key in circos and len(e["dep"]) == 2:
            groups.setdefault(key, set()).update(e["cats"])
    fills = {key: rgb(colors[mix] if len(cats) > 1 else colors[next(iter(cats))]) for key, cats in groups.items()}

    for key, fill in fills.items():
        for ring in rings(circos[key]):
            d.polygon([pt(*c) for c in ring], fill=fill, outline=(35, 35, 35))
    for dp in metro:
        for ring in rings(dp["g"]):
            d.line([pt(*c) for c in ring] + [pt(*ring[0])], fill=LINE, width=int(1.1 * S), joint="curve")

    # Points pour les petites circonscriptions urbaines, comme sur la carte en vue large.
    r = 7.5 * S
    for key, fill in fills.items():
        xs, ys = zip(*[pt(*c) for ring in rings(circos[key]) for c in ring])
        cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=fill, outline=(255, 255, 255), width=int(1.6 * S))

    # Titre à droite.
    x = 735 * S
    right = (W - 28) * S
    d.text((x, 22 * S), "Carte", font=font(HEAVY, 92), fill=INK)
    d.text((x + 4 * S, 136 * S), "de la", font=font(HEAVY, 58), fill=INK)
    honte = font(HEAVY, 96)
    tb = d.textbbox((0, 0), "honte", font=honte)
    bw, bh = tb[2] - tb[0] + 52 * S, tb[3] - tb[1] + 34 * S
    by = 216 * S
    d.rounded_rectangle((x - 6 * S, by, x - 6 * S + bw, by + bh), radius=20 * S, fill=RED)
    d.text((x - 6 * S + 26 * S - tb[0], by + 17 * S - tb[1]), "honte", font=honte, fill=INK)

    y = by + bh + 18 * S
    if tagline:
        # Petite mention sous « honte », façon astérisque de bas de page.
        d.text((x + 2 * S, by + bh + 8 * S), tagline, font=font(DEMI_ITALIC, 21), fill=(60, 60, 60))
        y += 30 * S
    for line in title_lines:
        d.text((x, y), line, font=font(BOLD, 29), fill=INK)
        y += 37 * S
    y += 6 * S
    small = font(MEDIUM, 16)
    for line in wrap(d, cats_text, small, right - x):
        d.text((x, y), line, font=small, fill=(40, 40, 40))
        y += 21 * S
    y += 12 * S
    stat = font(BOLD, 18)
    for line in wrap(d, stat_text, stat, right - x):
        d.text((x, y), line, font=stat, fill=INK)
        y += 24 * S
    assert y <= (H - 8) * S, f"texte trop long pour l'image ({y / S:.0f} px)"

    img.resize((W, H), Image.LANCZOS).save(out_path, optimize=True)


def wrap(d, text, fnt, width):
    lines, cur = [], ""
    for word in text.split(" "):
        test = f"{cur} {word}".strip()
        if d.textlength(test, font=fnt) <= width:
            cur = test
        else:
            lines.append(cur)
            cur = word
    return lines + [cur]
