import os
import numpy as np
from PIL import Image, ImageOps, ImageDraw, ImageFont
from moviepy import ImageClip, CompositeVideoClip, concatenate_videoclips, AudioFileClip


# -----------------------------
# Image Processing
# -----------------------------

def crop_to_rectangle(image_path, width=1200, height=1168):
    """Crop and resize image to fixed rectangle"""
    img = Image.open(image_path).convert("RGBA")

    result = ImageOps.fit(
        img,
        (width, height),
        method=Image.LANCZOS,
        centering=(0.5, 0.5)
    )

    return result


def extend_bottom(img, extend_pixels=93):
    """Extend bottom of image"""
    w, h = img.size
    canvas = Image.new("RGBA", (w, h + extend_pixels))
    canvas.paste(img, (0, 0))
    return canvas


def render_text_image(text):
    """Create text image using PIL"""
    width = 1200
    height = 150

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    font = ImageFont.truetype("fonts/arial/arial.ttf", 50)

    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]

    draw.text(
        ((width - text_w) // 2, 10),
        text,
        font=font,
        fill="white"
    )

    return np.array(img)


# -----------------------------
# Slide Creation
# -----------------------------

def create_slide(background_clip, celebrant_img, name, duration):

    background = background_clip.with_duration(duration)

    photo_clip = ImageClip(np.array(celebrant_img))
    photo_clip = photo_clip.with_position((86, 94)).with_duration(duration)

    text_img = render_text_image(name)
    text_clip = ImageClip(text_img).with_position(("center", 800)).with_duration(duration)

    slide = CompositeVideoClip([
        background,
        photo_clip,
        text_clip
    ])

    return slide


# -----------------------------
# Slide Generator
# -----------------------------

def generate_slides_from_dir(pic_dir, bg_file, audio_file, duration_list):

    celeb_files = sorted(
        [
            f for f in os.listdir(pic_dir)
            if f.lower().endswith((".png", ".jpg")) and f != os.path.basename(bg_file)
        ],
        key=lambda x: (
            int(x.split("_")[0].replace("gen", "")),
            int(x.split("_")[1])
        )
    )

    clips = []

    # load background once
    bg_clip = ImageClip(bg_file)

    for i, celeb_file in enumerate(celeb_files):

        celeb_path = os.path.join(pic_dir, celeb_file)

        img = crop_to_rectangle(celeb_path)
        img = extend_bottom(img)

        name = os.path.splitext(celeb_file)[0].replace("_", " ")

        slide = create_slide(
            background_clip=bg_clip,
            celebrant_img=img,
            name=name,
            duration=duration_list[i]
        )

        clips.append(slide)

    final_video = concatenate_videoclips(clips, method="chain")

    if os.path.exists(audio_file):
        audio = AudioFileClip(audio_file)
        final_video = final_video.with_audio(audio)

    return final_video


# -----------------------------
# Run
# -----------------------------

if __name__ == "__main__":

    month = "March"

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ABS_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "data", month))

    BG_PIC_FILE = os.path.join(ABS_DIR, "pics", "base_celebrant.png")
    AUDIO_FILE = os.path.join(ABS_DIR, "voiceover.mp3")
    PIC_DIR = os.path.join(ABS_DIR, "pics")

    tts_response = [
        {'phrase': 'to Geofrey Cheruiyot', 'start_time': 13.653, 'end_time': 14.768},
        {'phrase': 'to Brigid Chepkemoi', 'start_time': 18.913, 'end_time': 19.981},
        {'phrase': 'on March 12th', 'start_time': 25.391, 'end_time': 26.227}
    ]

    # convert end timestamps → durations
    timestamps = []
    prev = 0

    for phrase in tts_response:
        duration = phrase["end_time"] - prev
        timestamps.append(duration)
        prev = phrase["end_time"]

    final_video = generate_slides_from_dir(
        pic_dir=PIC_DIR,
        bg_file=BG_PIC_FILE,
        audio_file=AUDIO_FILE,
        duration_list=timestamps
    )

    output_path = os.path.join(ABS_DIR, f"{month}_celebration_video.mp4")

    final_video.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        threads=4
    )