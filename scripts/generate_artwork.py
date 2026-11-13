"""Regenerate bundled original artwork. Pillow is needed only for this optional step."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

IMAGES = Path(__file__).resolve().parent.parent / "images"


def rounded(name, size, color, radius):
    factor = 3
    image = Image.new("RGBA", (size[0] * factor, size[1] * factor))
    ImageDraw.Draw(image).rounded_rectangle((0, 0, image.width - 1, image.height - 1), radius=radius * factor, fill=color)
    image.resize(size, Image.Resampling.LANCZOS).save(IMAGES / name, optimize=True)


def title_art(name, size):
    image = Image.new("RGB", size, "#101724")
    draw = ImageDraw.Draw(image)
    font_path = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
    font = ImageFont.truetype(str(font_path), max(14, size[0] // 15)) if font_path.exists() else ImageFont.load_default()
    margin = size[0] // 12
    draw.rounded_rectangle((margin, margin, size[0] - margin, size[1] - margin), radius=max(12, margin // 3), fill="#20334e")
    draw.multiline_text((size[0] // 2, size[1] // 2), "CLEAN\nYOUR ROKU", font=font, fill="#e8f0ff", anchor="mm", align="center", spacing=max(5, size[0] // 60))
    image.save(IMAGES / name, optimize=True)


def main():
    IMAGES.mkdir(exist_ok=True)
    background = Image.new("RGB", (1920, 1080))
    draw = ImageDraw.Draw(background)
    for y in range(1080):
        amount = y / 1079
        color = tuple(round(a * (1 - amount) + b * amount) for a, b in zip((21, 32, 50), (9, 15, 25)))
        draw.line((0, y, 1920, y), fill=color)
    light = Image.new("RGBA", background.size)
    ImageDraw.Draw(light).ellipse((-300, -450, 1000, 450), fill=(72, 113, 177, 35))
    background = Image.alpha_composite(background.convert("RGBA"), light.filter(ImageFilter.GaussianBlur(100)))
    background.convert("RGB").save(IMAGES / "clean_background.png", optimize=True)
    rounded("clean_surface.png", (390, 290), "#1e2b40", 22)
    rounded("clean_focus.png", (400, 300), "white", 25)
    placeholder = Image.new("RGBA", (340, 220))
    ImageDraw.Draw(placeholder).polygon(((145, 65), (145, 155), (215, 110)), fill="#8fa8cc")
    placeholder.save(IMAGES / "clean_placeholder.png", optimize=True)
    for name, size in {"clean_icon_fhd.png": (540, 405), "clean_icon_hd.png": (290, 218),
                       "clean_splash_fhd.png": (1920, 1080), "clean_splash_hd.png": (1280, 720),
                       "clean_splash_sd.png": (720, 480)}.items():
        title_art(name, size)
    print("Generated nine local artwork assets.")


if __name__ == "__main__":
    main()
