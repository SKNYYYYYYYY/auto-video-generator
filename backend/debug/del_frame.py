from PIL import Image, ImageDraw, ImageOps


def crop_to_circle(image_path, output_path, diameter=512):
    img = Image.open(image_path).convert("RGBA")

    # Only resize if necessary (avoid unnecessary quality loss)
    if min(img.size) != diameter:
        img = ImageOps.fit(
            img,
            (diameter, diameter),
            method=Image.LANCZOS,  # highest quality downscaling
            centering=(0.5, 0.5)
        )

    # Create anti-aliased mask
    mask = Image.new("L", (diameter, diameter), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, diameter, diameter), fill=255)

    img.putalpha(mask)

    img.save(output_path, format="PNG", optimize=True)

def crop_to_rectangle(image_path, output_path, width=1200, height= 1168):
    img = Image.open(image_path).convert("RGBA")

    result = ImageOps.fit(
        img,
        (width, height),
        method=Image.LANCZOS,  # high quality scaling
        centering=(0.5, 0.5)
    )
    result.save(output_path, format="PNG", optimize=True)
crop_to_rectangle("2.png", "output1_rectangle.png")