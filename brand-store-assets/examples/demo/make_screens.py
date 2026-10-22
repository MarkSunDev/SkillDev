#!/usr/bin/env python3
"""Generate abstract DEMO screens for the example manifest. Not real app UI."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
FONTS = ROOT.parents[1] / "assets" / "fonts"
W, H = 1320, 2868

PALETTES = [
    ("#1E2A2A", "#F3EFE4", "#D9A441"),
    ("#F3EFE4", "#1E2A2A", "#B5653A"),
    ("#DCE7DC", "#1E2A2A", "#1F6F5C"),
    ("#F3EFE4", "#1E2A2A", "#B5653A"),
    ("#1E2A2A", "#F3EFE4", "#D9A441"),
]


def font(name: str, size: int):
    return ImageFont.truetype(str(FONTS / name), size)


def rounded(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def mark(draw, x, y, size, color):
    width = max(6, int(size * 0.07))
    draw.arc(
        (x + size * 0.05, y + size * 0.025, x + size * 0.95, y + size * 0.925),
        120, 420, fill=color, width=width,
    )
    r = size * 0.045
    cx = x + size * 0.5
    cy = y + size * 0.86
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=color)


def make_screen(index: int, bg: str, ink: str, accent: str) -> Image.Image:
    image = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(image)
    display = font("InstrumentSerif-Regular.ttf", 330)
    serif = font("InstrumentSerif-Regular.ttf", 96)
    sans = font("PublicSans.ttf", 34)
    small = font("PublicSans.ttf", 24)
    tiny = font("PublicSans.ttf", 20)

    # Status bar
    draw.text((84, 70), "9:41", font=small, fill=ink)
    for i in range(4):
        draw.rounded_rectangle((W - 260 + i * 26, 72 + (3 - i) * 7, W - 248 + i * 26, 100), radius=3, fill=ink)
    draw.rounded_rectangle((W - 130, 72, W - 84, 100), radius=8, outline=ink, width=3)
    draw.rounded_rectangle((W - 124, 78, W - 100, 94), radius=4, fill=ink)

    # Brand row
    mark(draw, 84, 160, 56, ink)
    draw.text((158, 168), "Harbor", font=serif, fill=ink)
    draw.text((160, 248), "TODAY", font=small, fill=accent)

    # Big demo index
    draw.text((78, 390), f"{index:02d}", font=display, fill=accent)
    draw.text((84, 780), "DEMO SCREEN", font=small, fill=ink)
    draw.text((84, 824), "Replace this file with a real build capture.", font=tiny, fill=ink)

    # Abstract content cards
    top = 950
    card_colors = [ink, accent]
    for row in range(3):
        y = top + row * 280
        rounded(draw, (84, y, W - 84, y + 224), 42, None, outline=ink, width=3)
        draw.ellipse((126, y + 66, 218, y + 158), fill=card_colors[row % 2])
        draw.text((262, y + 62), ["Plan the day", "Protect a block", "Close the loop"][row], font=serif, fill=ink)
        draw.text((264, y + 158), ["Three things, not thirty.", "Deep work, gently held.", "A minute of reflection."][row], font=small, fill=ink)
        rounded(draw, (W - 230, y + 78, W - 126, y + 146), 34, accent)

    # Bottom tab bar
    rounded(draw, (84, H - 260, W - 84, H - 110), 56, ink)
    labels = ["Today", "Focus", "Review", "You"]
    for i, label in enumerate(labels):
        x = 150 + i * 275
        draw.ellipse((x, H - 225, x + 30, H - 195), fill=accent if i == 0 else bg)
        draw.text((x - 10, H - 178), label, font=small, fill=bg)

    draw.text((84, H - 70), "DEMO CONTENT · NOT FOR SUBMISSION", font=tiny, fill=ink)
    return image


def main() -> int:
    screens = ROOT / "screens"
    screens.mkdir(parents=True, exist_ok=True)
    for index, (bg, ink, accent) in enumerate(PALETTES, start=1):
        image = make_screen(index, bg, ink, accent)
        path = screens / f"{index:02d}.png"
        image.save(path, "PNG", optimize=True)
        print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
