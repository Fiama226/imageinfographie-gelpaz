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
def make_adresse():
    print("→ 04 Image Adresse / Hero")
    img = Image.open("Adresse.jpg.jpeg").convert("RGB")
    img = enhance_image(img)
    w, h = img.size
    # Ratio 4:5
    target_h = int(w * 5 / 4)
    if target_h < h:
        top = (h - target_h) // 2
        img = img.crop((0, top, w, top + target_h))
        h = target_h

    # Dégradé bleu fort à gauche (couvre totalement l'ancien texte)
    # On utilise un dégradé exponentiel plus doux vers la droite pour un effet "plaque" naturel
    img = add_gradient_left(img, width_ratio=0.68, color=GELPAZ_BLUE, max_alpha=252, exp=0.75)
    # Plaque rectangulaire plus basse pour effacer tout reste de l'ancien titre, avec bord droit dégradé
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    plaque_w = int(w * 0.58)
    plaque_top = int(h * 0.28)
    plaque_bot = int(h * 0.72)
    d.rectangle([0, plaque_top, plaque_w - 120, plaque_bot], fill=(*GELPAZ_BLUE, 255))
    # Bord droit de la plaque en dégradé pour transition douce
    for x in range(120):
        alpha = int(255 * (1 - x / 120) ** 0.7)
        d.line([(plaque_w - 120 + x, plaque_top),
                (plaque_w - 120 + x, plaque_bot)],
               fill=(*GELPAZ_BLUE, alpha))
    img = Image.alpha_composite(img.convert("RGBA"), overlay)
    # Léger re-dégradé pour homogénéiser
    img = add_gradient_left(img, width_ratio=0.70, color=GELPAZ_BLUE, max_alpha=120, exp=1.2)
    # Dégradé bas pour l'info contact
    grad = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dg = ImageDraw.Draw(grad)
    gh = int(h * 0.18)
    for y in range(gh):
        t = y / gh
        alpha = int(230 * t ** 1.2)
        dg.line([(0, h - gh + y), (w, h - gh + y)], fill=(*GELPAZ_DARK, alpha))
    img = Image.alpha_composite(img.convert("RGBA"), grad)
    # Barres
    add_horizontal_bars(img, GELPAZ_BLUE, GELPAZ_DARK, 16, 18)
    # Logo haut gauche — en BLANC (inversé) sur fond bleu, technique infographique standard
    img = add_logo(img, load_logo(invert_white=True), "top-left", 0.15, 55, shadow=True)
    # Badge haut droite
    img = add_badge(img, "L'ADRESSE DE VOS PROJETS", GOLD, "top-right", 70, font_ratio=0.011)
    # Bloc texte
    draw = ImageDraw.Draw(img)
    margin = 70
    text_x = margin
    text_y = int(h * 0.38)
    tag_font = ImageFont.truetype(FONT_BOLD, int(w * 0.014))
    title_font = ImageFont.truetype(FONT_BOLD, int(w * 0.062))
    sub_font = ImageFont.truetype(FONT_BOLD, int(w * 0.037))
    info_font = ImageFont.truetype(FONT_BOLD, int(w * 0.020))
    # Tag
    tag = "✦  IMMOBILIER · CONSTRUCTION · ACCOMPAGNEMENT"
    draw.text((text_x, text_y - int(w * 0.04)), tag, font=tag_font, fill=GELPAZ_LIGHT)
    # Titre
    draw.text((text_x + 3, text_y + 3), "GELPAZ IMMO SA,", font=title_font, fill=(0, 20, 60, 200))
    draw.text((text_x, text_y), "GELPAZ IMMO SA,", font=title_font, fill=WHITE)
    # Sous-titre
    sy = text_y + int(w * 0.072)
    draw.text((text_x + 3, sy + 3), "L'adresse pour votre projet de vie.", font=sub_font, fill=(0, 20, 60, 200))
    draw.text((text_x, sy), "L'adresse pour votre projet de vie.", font=sub_font, fill=WHITE)
    # Séparateur doré
    sep_y = sy + int(w * 0.048)
    draw.rectangle([text_x, sep_y, text_x + int(w * 0.09), sep_y + 8], fill=GOLD)
    draw.rectangle([text_x + int(w * 0.09), sep_y + 2, text_x + int(w * 0.18), sep_y + 6], fill=GELPAZ_LIGHT)
    # Contact en bas à gauche
    info_y = h - int(w * 0.055)
    draw.text((text_x + 2, info_y + 2),
              "📞  +225 00 00 00 00 00    ·    ✉  contact@gelpazimmo.ci",
              font=info_font, fill=(0, 0, 0, 150))
    draw.text((text_x, info_y),
              "📞  +225 00 00 00 00 00    ·    ✉  contact@gelpazimmo.ci",
              font=info_font, fill=WHITE)
    out = os.path.join(OUT_DIR, "04_Adresse_Hero_Gelpaz.jpg")
    img.convert("RGB").save(out, "JPEG", quality=93, optimize=True)
    print(f"  ✓ {out}")


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    make_reception()
    make_whatsapp()
    make_site()
    make_adresse()
    print("\n✅ Toutes les infographies finales sont dans", OUT_DIR)
