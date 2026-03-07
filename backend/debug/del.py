import os
import cv2
import numpy as np
from PIL import Image, ImageOps
from moviepy import ImageClip, TextClip, CompositeVideoClip, concatenate_videoclips, AudioFileClip

# -----------------------------
# Image Processing Functions
# -----------------------------

def crop_to_rectangle(image_path, width=1200, height=1168):
    """Crop and resize an image to a fixed rectangle (centered)"""
    img = Image.open(image_path).convert("RGBA")
    result = ImageOps.fit(
        img,
        (width, height),
        method=Image.LANCZOS,
        centering=(0.5, 0.5)
    )
    return result

def extend_bottom_clip(img_clip, extend_pixels=20):
    """Extend bottom of an ImageClip using OpenCV resizing"""
    img = img_clip.img  # shape: (h, w, 3)
    h, w = img.shape[:2]
    new_h = h + extend_pixels

    extended_img = cv2.resize(img, (w, new_h), interpolation=cv2.INTER_LINEAR)
    return ImageClip(extended_img).with_duration(img_clip.duration)

# -----------------------------
# Slide Creation
# -----------------------------

def create_slide(image_path, CELEBRANT_PIC_FILE, details, audio_path, duration=10):
    # 1️⃣ Background
    background = ImageClip(image_path).with_duration(duration)

    # 2️⃣ Celebrant photo
    FRAME_WIDTH, FRAME_HEIGHT = 880, 880

    photo = ImageClip(CELEBRANT_PIC_FILE)
    # Scale photo proportionally
    photo = photo.resized(height=FRAME_HEIGHT)
    if photo.w > FRAME_WIDTH:
        photo = photo.resized(width=FRAME_WIDTH)
    photo = extend_bottom_clip(photo, extend_pixels=93)
    photo = photo.with_position((86, 94)).with_duration(duration)


    # 4️⃣ Name text
    name_text = TextClip(
        text=details["name"],
        font="fonts/arial/arial.ttf",
        font_size=50,
        color="white"
    ).with_position(("center", 800)).with_duration(duration)

    # 5️⃣ Composite everything
    clips = [background, photo, name_text]

    final = CompositeVideoClip(clips)



    return final

# -----------------------------
# Main Function: Process Folder
# -----------------------------

def generate_slides_from_dir(base_dir, bg_file, audio_file, duration_per_slide=10):
    # Gather all celebrant images (exclude background)
    celeb_files = [
        f for f in os.listdir(base_dir)
        if f.lower().endswith((".jpg", ".png")) and f not in os.path.basename(bg_file)
    ]

    clips = []
    for celeb_file in celeb_files:
        celeb_path = os.path.join(base_dir, celeb_file)

        # Crop to rectangle and save as temporary file
        cropped_img = crop_to_rectangle(celeb_path)
        tmp_path = os.path.join(base_dir, f"tmp_{celeb_file}")
        cropped_img.save(tmp_path, format="PNG", optimize=True)

        # Name for slide taken from file name
        name = os.path.splitext(celeb_file)[0].replace("_", " ")

        slide = create_slide(
            image_path=bg_file,
            CELEBRANT_PIC_FILE=tmp_path,
            details={"name": name},
            audio_path=audio_file,
            duration=duration_per_slide
        )
        clips.append(slide)

    # Concatenate all slides
    final_video = concatenate_videoclips(clips, method="compose")
        # 6️⃣ Add audio (optional)
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
    AUDIO_FILE = os.path.join(ABS_DIR, "voiceover.mp3")  # optional
    PIC_DIR=os.path.join(ABS_DIR, "pics"),
    print(ABS_DIR)

    final_video = generate_slides_from_dir(
        pic_dir=PIC_DIR
        bg_file=BG_PIC_FILE,
        audio_file=AUDIO_FILE,
        duration_per_slide=10
    )
    final_video.write_videofile("multi_slides_video.mp4", fps=24)

    # Optional: clean up temporary cropped images
    for f in os.listdir(ABS_DIR):
        if f.startswith("tmp_") and f.lower().endswith((".png", ".jpg")):
            os.remove(os.path.join(ABS_DIR, f))