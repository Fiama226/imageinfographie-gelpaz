#!/usr/bin/env python3
"""
Infographe professionnel pour GELPAZ IMMO-SA  — Version finale corrigée
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import os

GELPAZ_BLUE = (30, 136, 229)
GELPAZ_DARK = (13, 71, 161)
GELPAZ_LIGHT = (100, 181, 246)
WHITE = (255, 255, 255)
GOLD = (255, 193, 7)
WHATSAPP_GREEN = (37, 211, 102)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
LOGO_PATH = "logo gelpazjpg.jpg"
OUT_DIR = "Infographies"
os.makedirs(OUT_DIR, exist_ok=True)


def load_logo(invert_white=False):
    """
    Charge le logo.
    - Par défaut : logo bleu sur fond transparent
    - invert_white=True : logo BLANC sur fond transparent (pour fonds sombres/colorés)
    """
    import numpy as np
    logo = Image.open(LOGO_PATH).convert("RGBA")
    arr = np.array(logo).astype(np.int16)
    # Masque : pixels non-blancs = éléments du logo
    non_white = ~((arr[..., 0] > 235) & (arr[..., 1] > 235) & (arr[..., 2] > 235))
    out = arr.copy()
    if invert_white:
        # Remplacer tous les pixels du logo par du blanc pur, alpha 255
        out[non_white] = [255, 255, 255, 255]
    # Rendre le fond transparent
    out[~non_white, 3] = 0
    return Image.fromarray(out.astype(np.uint8), "RGBA")


def enhance_image(img):
    img = ImageEnhance.Color(img).enhance(1.18)
    img = ImageEnhance.Contrast(img).enhance(1.10)
    img = ImageEnhance.Brightness(img).enhance(1.03)
    img = ImageEnhance.Sharpness(img).enhance(1.25)
    return img


def add_gradient_bottom(img, height_ratio=0.40, color=(0, 0, 0)):
    w, h = img.size
    grad_h = int(h * height_ratio)
    gradient = Image.new("RGBA", (w, grad_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(gradient)
    for y in range(grad_h):
        t = y / grad_h
        alpha = int(240 * t ** 1.5)
        draw.line([(0, y), (w, y)], fill=(*color, alpha))
    base = img.convert("RGBA")
    base.paste(gradient, (0, h - grad_h), gradient)
    return base


def add_gradient_left(img, width_ratio=0.55, color=GELPAZ_BLUE, max_alpha=235, exp=1.2):
    w, h = img.size
    grad_w = int(w * width_ratio)
    gradient = Image.new("RGBA", (grad_w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(gradient)
    for x in range(grad_w):
        t = 1 - x / grad_w
        alpha = int(max_alpha * t ** exp)
        draw.line([(x, 0), (x, h)], fill=(*color, alpha))
    base = img.convert("RGBA")
    base.paste(gradient, (0, 0), gradient)
    return base


def add_horizontal_bars(img, top_color, bottom_color, top_h=14, bottom_h=14):
    w, h = img.size
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, w, top_h], fill=top_color)
    draw.rectangle([0, h - bottom_h, w, h], fill=bottom_color)
    return img


def add_logo(img, logo, position="top-right", size_ratio=0.10, margin=40, shadow=False):
    w, h = img.size
    logo_w = int(w * size_ratio)
    logo_h = int(logo_w * logo.size[1] / logo.size[0])
    logo_r = logo.resize((logo_w, logo_h), Image.LANCZOS)
    if shadow:
        # Ombre douce sous le logo pour le détacher du fond
        sh = Image.new("RGBA", (logo_w + 20, logo_h + 20), (0, 0, 0, 0))
        ds = ImageDraw.Draw(sh)
        ds.bitmap((10, 10), logo_r.getchannel("A"), fill=(0, 0, 0, 160))
        sh = sh.filter(ImageFilter.GaussianBlur(radius=8))
        layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        px, py = {
            "top-right": (w - logo_w - margin, margin),
            "top-left": (margin, margin),
            "bottom-right": (w - logo_w - margin, h - logo_h - margin),
            "bottom-left": (margin, h - logo_h - margin),
        }[position]
        layer.paste(sh, (px - 10, py - 10), sh)
        img = Image.alpha_composite(img, layer)
    positions = {
        "top-right": (w - logo_w - margin, margin),
        "top-left": (margin, margin),
        "bottom-right": (w - logo_w - margin, h - logo_h - margin),
        "bottom-left": (margin, h - logo_h - margin),
    }
    img.paste(logo_r, positions[position], logo_r)
    return img


def add_badge(img, text, bg_color, position="top-left", margin=40, font_ratio=0.014):
    w, h = img.size
    fs = max(20, int(w * font_ratio))
    font = ImageFont.truetype(FONT_BOLD, fs)
    draw = ImageDraw.Draw(img)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad_x, pad_y = int(fs * 0.9), int(fs * 0.55)
    bw, bh = tw + pad_x * 2, th + pad_y * 2 + 8
    if position == "top-left":
        x, y = margin, margin
    else:
        x, y = w - bw - margin, margin
    draw.rounded_rectangle([x, y, x + bw, y + bh], radius=14, fill=bg_color)
    draw.text((x + pad_x, y + pad_y - 2), text, font=font, fill=WHITE)
    return img


def draw_text_block(img, title, subtitle, x, y, title_size,
                    title_color=WHITE, accent1=GELPAZ_BLUE, accent2=GELPAZ_LIGHT,
                    margin_bottom=40):
    """Dessine un bloc titre + sous-titre avec ombre et barre d'accent."""
    draw = ImageDraw.Draw(img)
    tf = ImageFont.truetype(FONT_BOLD, title_size)
    sf = ImageFont.truetype(FONT_REG, int(title_size * 0.40))
    # barre d'accent bicolore
    bar_w = int(title_size * 4.5)
    bar_h = max(8, title_size // 14)
    bar_y = y - bar_h - int(title_size * 0.25)
    draw.rectangle([x, bar_y, x + int(bar_w * 0.65), bar_y + bar_h], fill=accent1)
    draw.rectangle([x + int(bar_w * 0.65), bar_y, x + bar_w, bar_y + bar_h], fill=accent2)
    # ombre
    draw.text((x + 4, y + 4), title, font=tf, fill=(0, 0, 0, 200))
    draw.text((x, y), title, font=tf, fill=title_color)
    # sous-titre
    sy = y + title_size + int(title_size * 0.18)
    draw.text((x + 2, sy + 2), subtitle, font=sf, fill=(0, 0, 0, 180))
    draw.text((x, sy), subtitle, font=sf, fill=title_color)
    return sy + int(title_size * 0.5)


# ============================================================
# 1) RÉCEPTION EN AGENCE
# ============================================================
def make_reception():
    print("→ 01 Réception en Agence")
    img = Image.open("Service de Reception en Agence.jpg.jpeg").convert("RGB")
    img = enhance_image(img)
    w, h = img.size
    img = add_gradient_bottom(img, height_ratio=0.36, color=(0, 0, 0))
    img = add_horizontal_bars(img, GELPAZ_BLUE, GELPAZ_BLUE, 12, 12)
    img = add_logo(img, load_logo(), "top-right", 0.13, 30, shadow=True)
    img = add_badge(img, "SERVICE CLIENTÈLE", GELPAZ_BLUE, "top-left", 30)
    title_size = int(w * 0.058)
    margin = 60
    draw_text_block(img,
                    "Réception en Agence",
                    "Accueil personnalisé · Conseils experts · Projets immobiliers",
                    margin, h - int(h * 0.20), title_size,
                    accent1=GELPAZ_BLUE, accent2=GELPAZ_LIGHT)
    out = os.path.join(OUT_DIR, "01_Service_Reception_Agence_Gelpaz.jpg")
    img.convert("RGB").save(out, "JPEG", quality=95, optimize=True)
    print(f"  ✓ {out}")


# ============================================================
# 2) SERVICE WHATSAPP
# ============================================================
def make_whatsapp():
    print("→ 02 Service WhatsApp")
    img = Image.open("Service par Whatsapp.jpg.jpeg").convert("RGB")
    img = enhance_image(img)
    w, h = img.size
    # Dégradé vert à gauche
    img = add_gradient_bottom(img, height_ratio=0.28, color=(0, 50, 20))
    img = add_gradient_left(img, width_ratio=0.50, color=(7, 94, 55), max_alpha=210, exp=0.9)
    img = add_horizontal_bars(img, WHATSAPP_GREEN, WHATSAPP_GREEN, 12, 12)
    img = add_logo(img, load_logo(), "top-right", 0.13, 30, shadow=True)
    img = add_badge(img, "DISPONIBLE 7J/7", WHATSAPP_GREEN, "top-left", 30)
    title_size = int(w * 0.060)
    margin = 60
    draw_text_block(img,
                    "Service WhatsApp",
                    "Échanges rapides · Réponses instantanées · Devis en ligne",
                    margin, h - int(h * 0.20), title_size,
                    accent1=WHATSAPP_GREEN, accent2=WHITE)
    out = os.path.join(OUT_DIR, "02_Service_WhatsApp_Gelpaz.jpg")
    img.convert("RGB").save(out, "JPEG", quality=95, optimize=True)
    print(f"  ✓ {out}")


# ============================================================
# 3) SERVICE SUR SITE — corrigé : titre plus haut, sous-titre visible
# ============================================================
def make_site():
    print("→ 03 Service sur Site")
    img = Image.open("Service sur Site.png").convert("RGB")
    img = enhance_image(img)
    w, h = img.size
    # Dégradé bas plus haut pour laisser place au texte + bande bleu gauche
    img = add_gradient_bottom(img, height_ratio=0.42, color=(0, 0, 0))
    img = add_gradient_left(img, width_ratio=0.40, color=GELPAZ_DARK, max_alpha=150, exp=1.0)
    img = add_horizontal_bars(img, GELPAZ_BLUE, GELPAZ_DARK, 14, 14)
    img = add_logo(img, load_logo(), "top-right", 0.10, 40, shadow=True)
    img = add_badge(img, "SUR SITE · CHANTIER", GELPAZ_DARK, "top-left", 40)
    # Titre plus petit et plus haut pour que le sous-titre ne soit pas coupé
    title_size = int(w * 0.042)
    margin = 70
    draw = ImageDraw.Draw(img)
    tf = ImageFont.truetype(FONT_BOLD, title_size)
    sf = ImageFont.truetype(FONT_REG, int(title_size * 0.44))
    # double barre d'accent
    bx, by = margin, h - int(h * 0.32)
    bar_w = int(title_size * 5)
    draw.rectangle([bx, by - 30, bx + int(bar_w * 0.65), by - 20], fill=GELPAZ_LIGHT)
    draw.rectangle([bx + int(bar_w * 0.65), by - 30, bx + bar_w, by - 20], fill=GOLD)
    # Titre
    draw.text((bx + 4, by + 4), "Service sur Site", font=tf, fill=(0, 0, 0, 200))
    draw.text((bx, by), "Service sur Site", font=tf, fill=WHITE)
    # Sous-titre
    sy = by + title_size + int(title_size * 0.22)
    draw.text((bx + 2, sy + 2),
              "Visites de chantier · Suivi de travaux · Accompagnement terrain",
              font=sf, fill=(0, 0, 0, 180))
    draw.text((bx, sy),
              "Visites de chantier · Suivi de travaux · Accompagnement terrain",
              font=sf, fill=WHITE)
    out = os.path.join(OUT_DIR, "03_Service_Sur_Site_Gelpaz.jpg")
    img.convert("RGB").save(out, "JPEG", quality=95, optimize=True)
    print(f"  ✓ {out}")


# ============================================================
# 4) ADRESSE / HERO — recouvre l'ancien texte avec une plaque solide
# ============================================================
def patch_region_wall(img, x0, x1, y0, y1, feather_v=36, feather_h=30, band=26):
    """Efface un texte incrusté sur un mur uniforme : chaque colonne de la zone
    est reconstruite par interpolation verticale entre la bande de pixels juste
    au-dessus et celle juste en dessous (le mur est régulier verticalement, donc
    le résultat est indissociable du fond)."""
    import numpy as np
    a = np.array(img).astype(np.float32)
    H_img, W_img, _ = a.shape
    x0, x1 = max(0, x0), min(W_img, x1)
    y0, y1 = max(band * 3, y0), min(H_img - band * 3, y1)
    top = a[y0 - 2 * band:y0 - band, x0:x1].mean(axis=0)      # (W, 3)
    bot = a[y1 + band:y1 + 2 * band, x0:x1].mean(axis=0)      # (W, 3)
    H, W = y1 - y0, x1 - x0
    t = np.linspace(0.0, 1.0, H)[:, None, None]
    fill = top[None, :, :] * (1 - t) + bot[None, :, :] * t
    patch = Image.fromarray(fill.astype(np.uint8), "RGB").convert("RGBA")
    # Masque : 1 au centre, fondu sur les bords (le fondu reste hors du texte)
    g = np.ones((H, W), np.float32)
    for i in range(feather_v):
        f = i / feather_v
        g[i, :] *= f
        g[H - 1 - i, :] *= f
    for j in range(feather_h):
        f = j / feather_h
        g[:, j] *= f
        g[:, W - 1 - j] *= f
    patch.putalpha(Image.fromarray((g * 255).astype(np.uint8), "L"))
    base = img.convert("RGBA")
    base.alpha_composite(patch, (x0, y0))
    return base.convert("RGB")


def fit_font(text, target_w, font_path=FONT_BOLD):
    """Renvoie une police réglée pour que le texte occupe ~target_w de large."""
    probe = ImageFont.truetype(font_path, 100)
    bb = probe.getbbox(text)
    w100 = max(1, bb[2] - bb[0])
    return ImageFont.truetype(font_path, max(12, int(100 * target_w / w100)))


def text_soft_shadow(base, xy, text, font, fill=WHITE,
                     shadow=(5, 28, 75, 215), offset=None, blur=None, stroke=None):
    """Texte net + ombre diffuse (lisibilité sur fond clair)."""
    x, y = xy
    offset = offset or max(2, int(font.size * 0.022))
    blur = blur or max(6, int(font.size * 0.085))
    stroke = stroke if stroke is not None else max(1, int(font.size * 0.014))
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).text((x + offset, y + offset), text, font=font,
                               fill=shadow, stroke_width=stroke, stroke_fill=shadow)
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    base.alpha_composite(layer)
    ImageDraw.Draw(base).text((x, y), text, font=font, fill=fill)
    return base


def text_halo(base, xy, text, font, fill, halo=(255, 255, 255, 170), r=3):
    """Texte avec halo clair (petits textes sur fond moyen)."""
    x, y = xy
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for dx in range(-r, r + 1, 2):
        for dy in range(-r, r + 1, 2):
            if dx or dy:
                d.text((x + dx, y + dy), text, font=font, fill=halo)
    layer = layer.filter(ImageFilter.GaussianBlur(max(1, r // 2)))
    base.alpha_composite(layer)
    ImageDraw.Draw(base).text((x, y), text, font=font, fill=fill)
    return base


def paste_logo_shadowed(base, logo, xy, logo_w, shadow_alpha=150):
    """Colle le logo avec une ombre portée douce et proportionnée."""
    lw = logo_w
    lh = int(logo_w * logo.size[1] / logo.size[0])
    logo_r = logo.resize((lw, lh), Image.LANCZOS)
    blur = max(8, int(lw * 0.055))
    off = max(3, int(lw * 0.020))
    pad = blur * 2
    alpha = logo_r.getchannel("A")
    sh = Image.new("RGBA", (lw + 2 * pad, lh + 2 * pad), (0, 0, 0, 0))
    sh.paste(Image.new("RGBA", (lw, lh), (2, 22, 60, 255)), (pad, pad), alpha)
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    sh.putalpha(sh.getchannel("A").point(lambda p: int(p * shadow_alpha / 255)))
    x, y = xy
    lay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    lay.alpha_composite(sh, (max(0, x - pad + off), max(0, y - pad + off)))
    base = Image.alpha_composite(base, lay)
    lay2 = Image.new("RGBA", base.size, (0, 0, 0, 0))
    lay2.paste(logo_r, (x, y), logo_r)
    return Image.alpha_composite(base, lay2)


# ============================================================
# 4) IMAGE ADRESSE / HERO
# ============================================================
def make_adresse():
    print("→ 04 Image Adresse / Hero")
    img = Image.open("Adresse.jpg.jpeg").convert("RGB")
    img = enhance_image(img)
    w, h = img.size

    # 1) Effacer le texte incrusté d'origine (posé sur le mur bleu clair uni)
    img = patch_region_wall(img, int(0.044 * w), int(0.544 * w), int(0.371 * h), int(0.481 * h))
    base = img.convert("RGBA")

    # 2) Barres d'identité GELPAZ (fines, en haut et en bas)
    add_horizontal_bars(base, GELPAZ_BLUE, GELPAZ_DARK,
                        max(8, int(w * 0.0035)), max(10, int(w * 0.0040)))

    # 3) Logo blanc (inversé) ombré en haut à gauche + badge doré en haut à droite
    base = paste_logo_shadowed(base, load_logo(invert_white=True),
                               (int(w * 0.014), int(w * 0.014)), int(w * 0.145))
    base = add_badge(base, "L'ADRESSE DE VOS PROJETS", GOLD, "top-right",
                     int(w * 0.016), font_ratio=0.011)

    # 4) Bloc texte — à l'emplacement naturel du texte d'origine (zone nettoyée)
    x_txt = int(w * 0.055)
    f_tag = ImageFont.truetype(FONT_BOLD, int(w * 0.0132))
    f_title = fit_font("GELPAZ IMMO SA,", int(w * 0.470))
    f_sub = fit_font("L'adresse pour votre projet de vie.", int(w * 0.455))
    tag = "IMMOBILIER   ·   CONSTRUCTION   ·   ACCOMPAGNEMENT"
    tag_y = int(h * 0.349)
    title = "GELPAZ IMMO SA,"
    t_y = int(h * 0.380)
    sub = "L'adresse pour votre projet de vie."
    s_y = t_y + int(w * 0.0625)

    text_halo(base, (x_txt, tag_y), tag, f_tag, GELPAZ_DARK, r=4)
    text_soft_shadow(base, (x_txt, t_y), title, f_title)
    text_soft_shadow(base, (x_txt, s_y), sub, f_sub)

    # Barre d'accent dorée + bleue sous le slogan
    d = ImageDraw.Draw(base)
    bar_y = s_y + int(w * 0.0465)
    h_bar = max(6, int(w * 0.0022))
    d.rectangle([x_txt, bar_y, x_txt + int(w * 0.065), bar_y + h_bar - 2], fill=GOLD)
    d.rectangle([x_txt + int(w * 0.065), bar_y, x_txt + int(w * 0.130), bar_y + h_bar - 4],
                fill=GELPAZ_LIGHT)

    # 5) Carte contact (bas gauche) — vraies coordonnées
    contacts = [("Tél.", "+226 25 37 10 55"),
                ("WhatsApp", "+226 67 30 81 85"),
                ("Email", "infos@gelpaz.com")]
    f_lab = ImageFont.truetype(FONT_BOLD, int(w * 0.0165))
    f_val = ImageFont.truetype(FONT_BOLD, int(w * 0.0195))
    meas = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    lab_w = max(meas.textbbox((0, 0), l, font=f_lab)[2] for l, _ in contacts)
    val_w = max(meas.textbbox((0, 0), v, font=f_val)[2] for _, v in contacts)
    bullet_w = max(6, int(w * 0.0038))
    gap = int(w * 0.0075)
    inner = int(w * 0.018)
    line_h = int(w * 0.033)
    card_w = inner * 2 + bullet_w + gap + lab_w + gap + val_w
    card_h = inner * 2 + line_h * len(contacts)
    card_x = int(w * 0.014)
    card_y = h - card_h - int(w * 0.014) - int(w * 0.0040)

    # Ombre douce de la carte
    sh = Image.new("RGBA", base.size, (0, 0, 0, 0))
    o = max(6, int(w * 0.004))
    ImageDraw.Draw(sh).rounded_rectangle(
        [card_x + o, card_y + o * 2, card_x + card_w + o, card_y + card_h + o * 2],
        radius=int(w * 0.009), fill=(0, 15, 45, 140))
    sh = sh.filter(ImageFilter.GaussianBlur(max(8, int(w * 0.005))))
    base.alpha_composite(sh)

    card = Image.new("RGBA", base.size, (0, 0, 0, 0))
    dc = ImageDraw.Draw(card)
    dc.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h],
                         radius=int(w * 0.009), fill=(*GELPAZ_DARK, 210),
                         outline=(255, 255, 255, 80), width=max(2, int(w * 0.0006)))
    base = Image.alpha_composite(base, card)

    d = ImageDraw.Draw(base)
    for i, (lab, val) in enumerate(contacts):
        cy = card_y + inner + line_h * i + line_h // 2
        bx = card_x + inner
        d.rectangle([bx, cy - int(line_h * 0.28), bx + bullet_w, cy + int(line_h * 0.28)],
                    fill=GOLD)
        tx = bx + bullet_w + gap
        d.text((tx, cy), lab, font=f_lab, fill=GELPAZ_LIGHT, anchor="lm")
        d.text((tx + lab_w + gap, cy), val, font=f_val, fill=WHITE, anchor="lm")

    # 6) Fond opaque + enregistrement
    out_img = Image.alpha_composite(Image.new("RGBA", base.size, (255, 255, 255, 255)), base)
    out = os.path.join(OUT_DIR, "04_Adresse_Hero_Gelpaz.jpg")
    out_img.convert("RGB").save(out, "JPEG", quality=93, optimize=True)
    print(f"  ✓ {out}")


# ============================================================
# 5) SUITE
# ============================================================
if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    make_reception()
    make_whatsapp()
    make_site()
    make_adresse()
    print("\n✅ Toutes les infographies finales sont dans", OUT_DIR)
