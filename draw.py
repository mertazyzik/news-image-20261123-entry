#!/usr/bin/env python3
"""Render the front page of 'The World in One Day' for 23 November 2026.

A single 1024x1024 PNG newspaper page, drawn with Pillow. Every word is
baked into this file, so the render is deterministic: the same input
always produces the same bytes. Run: python3 draw.py  (writes entry.png
next to this file).
"""

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (248, 244, 236)
INK = (22, 20, 16)
RED = (156, 26, 30)
GREY = (98, 92, 82)
FAINT = (182, 174, 158)
CREAM = (238, 231, 216)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

MARGIN = 38
CW = W - 2 * MARGIN  # 948


def fnt(path, size):
    return ImageFont.truetype(path, size)


def split_lines(d, text, font, width):
    """Greedy word wrap returning a list of lines that fit in width."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=font) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def block(d, x, y, lines, font, fill=INK, leading=0):
    """Draw lines, return the y just below the last one."""
    lh = font.size + leading
    for line in lines:
        d.text((x, y), line, font=font, fill=fill)
        y += lh
    return y


def rule(d, x, y, w, color=INK, weight=2):
    d.rectangle([x, y, x + w - 1, y + weight - 1], fill=color)
    return y + weight


def kicker_head_body(d, x, y, w, kick, head, body, head_size=20,
                     body_size=15, body_leading=5):
    """One news item: red kicker, serif headline, serif body. Returns y below."""
    y = block(d, x, y, [kick], fnt(SANS_B, 12), RED)
    y += 5
    head_lines = split_lines(d, head, fnt(SERIF_B, head_size), w)
    y = block(d, x, y, head_lines, fnt(SERIF_B, head_size), INK, 2)
    y += 4
    body_lines = split_lines(d, body, fnt(SERIF, body_size), w)
    y = block(d, x, y, body_lines, fnt(SERIF, body_size), INK, body_leading)
    return y


def draw_globe(d, cx, cy, r):
    """Simple line-art globe: circle, meridians, red sun above it."""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK, width=3)
    d.ellipse([cx - r * 0.45, cy - r, cx + r * 0.45, cy + r],
              outline=INK, width=2)
    d.line([cx - r, cy, cx + r, cy], fill=INK, width=2)
    d.arc([cx - r, cy - r * 0.55, cx + r, cy + r * 0.55],
          300, 60, fill=INK, width=2)
    d.arc([cx - r, cy - r * 0.55, cx + r, cy + r * 0.55],
          120, 240, fill=INK, width=2)
    sun_x, sun_y, sun_r = cx + r * 0.62, cy - r * 0.72, 13
    d.ellipse([sun_x - sun_r, sun_y - sun_r, sun_x + sun_r, sun_y + sun_r],
              fill=RED)
    for ang in range(0, 360, 45):
        import math
        a = math.radians(ang)
        x0 = sun_x + math.cos(a) * (sun_r + 3)
        y0 = sun_y + math.sin(a) * (sun_r + 3)
        x1 = sun_x + math.cos(a) * (sun_r + 10)
        y1 = sun_y + math.sin(a) * (sun_r + 10)
        d.line([x0, y0, x1, y1], fill=RED, width=2)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W - 1, H - 1], outline=INK, width=4)

    y = 30
    # --- masthead ---
    title = "THE WORLD IN ONE DAY"
    tf = fnt(SERIF_B, 62)
    tw = d.textlength(title, font=tf)
    d.text(((W - tw) / 2, y), title, font=tf, fill=INK)
    y += 76
    date_line = "MONDAY 23 NOVEMBER 2026  ·  THE DAY'S NEWS IN ONE PAGE"
    df = fnt(SANS_B, 17)
    dw = d.textlength(date_line, font=df)
    d.text(((W - dw) / 2, y), date_line, font=df, fill=RED)
    y += 30
    y = rule(d, MARGIN, y, CW, INK, 3)
    y = rule(d, MARGIN, y + 4, CW, INK, 1)
    y += 14

    # --- lead story: COP31, with globe art on the right ---
    lead_w = 690
    art_x0 = MARGIN + lead_w + 24
    art_w = W - MARGIN - art_x0
    ly = y
    ly = block(d, MARGIN, ly, ["CLIMATE  ·  ANTALYA, TURKEY"],
               fnt(SANS_B, 13), RED)
    ly += 6
    ly = block(d, MARGIN, ly,
               split_lines(d, "COP31 collapses as deal drops fossil fuels",
                           fnt(SERIF_B, 33), lead_w),
               fnt(SERIF_B, 33), INK, 2)
    ly += 6
    ly = block(d, MARGIN, ly,
               split_lines(d,
                           "The UN climate summit ended on Sunday with no "
                           "overarching deal — the first such failure since "
                           "Copenhagen in 2009. The EU, Britain, Panama and "
                           "Norway rejected the final “Antalya Pact” because "
                           "it never mentioned fossil fuels, only recalling "
                           "the 2023 Dubai pledge. After 44 hours of "
                           "overtime, the longest COP ever, president Murat "
                           "Kurum conceded there was no consensus.",
                           fnt(SERIF, 16), lead_w),
               fnt(SERIF, 16), INK, 5)
    # globe art, vertically centred on the lead block
    draw_globe(d, art_x0 + art_w // 2, y + 88, 62)
    cap = "No deal in Antalya"
    cf = fnt(SANS, 12)
    cw_ = d.textlength(cap, font=cf)
    d.text((art_x0 + (art_w - cw_) / 2, y + 168), cap, font=cf, fill=GREY)
    y = max(ly, y + 190) + 8
    y = rule(d, MARGIN, y, CW, INK, 2)
    y += 12

    # --- grid: five stories + a numbers box, 2 columns x 3 rows ---
    col_w = (CW - 28) // 2
    col2_x = MARGIN + col_w + 28
    row_h = 148
    grid_top = y

    items = [
        ("UNITED STATES  ·  WASHINGTON",
         "Democrats win biggest House majority since 1992",
         "Democrats clinched at least 258 seats on Sunday as Chuck "
         "Hubbard beat Republican Virginia Foxx in North Carolina — a "
         "gain of 44 seats. Four races remain uncalled; Republicans "
         "hold at least 173."),
        ("UKRAINE  ·  KYIV REGION",
         "14 missing after drone hits flats near Kyiv",
         "A Russian drone struck a five-storey block in Dymer, 45 km "
         "north of Kyiv, on Sunday morning, collapsing a stairwell. "
         "Nine residents were evacuated; rescuers search the rubble. "
         "Ukraine says 186 drones were launched overnight, 161 shot down."),
        ("INDONESIA  ·  WEST JAVA",
         "Dozens still missing after candy factory fire",
         "Rescuers resumed the search on Monday at the PT Fonusa Agung "
         "Mulia factory in Cikande, Serang, after Saturday's blaze "
         "killed at least three. Officials say 36 are unaccounted for; "
         "police recovered 24 body bags on Sunday."),
        ("SOUTH ASIA  ·  NEW DELHI",
         "Nepal's PM holds talks with Modi in Delhi",
         "Nepal's prime minister Balendra Shah, on his first bilateral "
         "trip abroad since taking office in March, holds "
         "delegation-level talks with Narendra Modi on Monday. Energy, "
         "trade and connectivity top the agenda."),
        ("SPORT  ·  WELLINGTON",
         "India pile up record 720/9 in Wellington",
         "India declared on 720 for 9 on day four of the first Test — "
         "the highest total ever in New Zealand — with centuries from "
         "KL Rahul (136) and Rishabh Pant (128). New Zealand closed on "
         "119 for 2, still 233 behind."),
    ]
    cells = [(MARGIN, grid_top), (col2_x, grid_top),
             (MARGIN, grid_top + row_h), (col2_x, grid_top + row_h),
             (MARGIN, grid_top + 2 * row_h), (col2_x, grid_top + 2 * row_h)]
    for (cx, cy), (kick, head, body) in zip(cells[:5], items):
        rule(d, cx, cy, col_w, FAINT, 1)
        kicker_head_body(d, cx, cy + 8, col_w, kick, head, body,
                         head_size=19, body_size=14, body_leading=4)

    # numbers box in the last cell
    bx, by = cells[5]
    d.rectangle([bx, by, bx + col_w - 1, by + row_h - 14], fill=INK)
    d.text((bx + 16, by + 10), "BY THE NUMBERS", font=fnt(SANS_B, 12),
           fill=(232, 196, 120))
    nums = [("258", "seats won by US Democrats"),
            ("14", "missing in Dymer, near Kyiv"),
            ("720/9", "India's record Test total"),
            ("36", "missing in the Java factory fire")]
    ny = by + 34
    for val, lab in nums:
        d.text((bx + 16, ny), val, font=fnt(SERIF_B, 17), fill=(248, 244, 236))
        d.text((bx + 92, ny + 2), lab, font=fnt(SANS, 13),
               fill=(205, 198, 184))
        ny += 26

    y = grid_top + 3 * row_h + 4
    y = rule(d, MARGIN, y, CW, INK, 2)
    y += 10

    # --- also in the news ---
    d.text((MARGIN, y), "ALSO IN THE NEWS", font=fnt(SANS_B, 13), fill=RED)
    y += 22
    also_left = [
        ("LISBON — ", "Thousands march in the rain over living costs and housing."),
        ("GENEVA — ", "UN states agree to draft rules on “killer robots” by 2028, but no binding commitment."),
        ("GULF OF FINLAND — ", "Russian cargo ship Sparta II still burning after a drone attack."),
    ]
    also_right = [
        ("SOUTH SUDAN — ", "SPLA-IO attack leaves 24 civilians dead."),
        ("FOOTBALL — ", "Liverpool thrash 10-man Manchester United."),
    ]
    ay = y
    for tag, txt in also_left:
        lines = split_lines(d, tag + txt, fnt(SANS, 13), col_w)
        ay = block(d, MARGIN, ay, lines, fnt(SANS, 13), INK, 4)
        ay += 3
    ay2 = y
    for tag, txt in also_right:
        lines = split_lines(d, tag + txt, fnt(SANS, 13), col_w)
        ay2 = block(d, col2_x, ay2, lines, fnt(SANS, 13), INK, 4)
        ay2 += 3
    y = max(ay, ay2) + 6
    y = rule(d, MARGIN, y, CW, INK, 1)
    y += 10

    # --- footer ---
    foot = ("THE WORLD IN ONE DAY  ·  MONDAY 23 NOVEMBER 2026  ·  "
            "SOURCES: REUTERS, ASSOCIATED PRESS, CNN, THE TIMES, "
            "LE MONDE, EURONEWS, ESPNCRICINFO")
    flines = split_lines(d, foot, fnt(SANS, 11), CW)
    y = block(d, MARGIN, y, flines, fnt(SANS, 11), GREY, 3)
    y += 8
    if y > H - 24:
        raise SystemExit(f"OVERFLOW: content ends at y={y}, frame is {H}")
    print(f"rendered OK, content ends at y={y}")

    img.save("entry.png", optimize=True)
    print("wrote entry.png")


if __name__ == "__main__":
    main()
