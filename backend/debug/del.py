from PIL import Image, ImageDraw, ImageFont

def debug_text(font_path, details):
    # Create blank canvas (like your video frame)
    img = Image.new("RGB", (1920, 1080), "black")
    draw = ImageDraw.Draw(img)

    # Fonts
    name_font = ImageFont.truetype(font_path, 85)
    rel_font = ImageFont.truetype(font_path, 40)

    # Name
    name = details["celebrant"][1]
    name_pos = (1100, 380)

    draw.text(name_pos, name, font=name_font, fill="#9b8a7c")

    # Get name height (like name_text.h)
    name_bbox = name_font.getbbox(name)
    name_height = name_bbox[3] - name_bbox[1]

    # Relation
    relation = details["celebrant"][2] if len(details["celebrant"]) > 2 else None

    if relation:
        rel_pos = (1100, 380 + name_height + 20)  # spacing instead of 100 guess
        draw.text(rel_pos, relation, font=rel_font, fill="#9b8a7c")

    img.show()  # instant preview

debug_text(font_path="DejaVuSerif.ttf", details= {'celebrant': ['2', 'Newton Kiprono', 's/o Paul']})