import os
import cv2
import numpy as np
from time import time
from PIL import Image, ImageOps
from moviepy import ImageClip, TextClip, CompositeVideoClip, concatenate_videoclips, AudioFileClip

from utils.logger_config import get_logger

logger = get_logger(__name__)


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

def create_slide(background_clip, celebrant_img, details, duration=10):
    # 1️⃣ Background
    background = background_clip.with_duration(duration)
    # 2️⃣ Celebrant photo
    FRAME_WIDTH, FRAME_HEIGHT = 880, 880

    photo = ImageClip(np.array(celebrant_img))
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

def generate_slides_from_dir(pic_dir, bg_file, audio_file, duration_list):
    
    # Gather all celebrant images (exclude background)
    celeb_files = sorted(
        [
            f for f in os.listdir(pic_dir)
            if f.lower().endswith((".jpg", ".png")) and f != os.path.basename(bg_file)
        ],
        key=lambda x: (
            int(x.split("_")[0].replace("gen", "")),
            int(x.split("_")[1])
        )
    )

    clips = []
    bg_clip = ImageClip(bg_file)
    for i, celeb_file in enumerate(celeb_files):


        celeb_path = os.path.join(pic_dir, celeb_file)
        # Crop to rectangle and save as temporary file
        cropped_img = crop_to_rectangle(celeb_path)

        # Name for slide taken from file name
        name = os.path.splitext(celeb_file)[0].replace("_", " ")
        slide = create_slide(
            background_clip=bg_clip,
            celebrant_img=cropped_img,
            details={"name": name},
            duration=duration_list[i]
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

def generate_video(month, tts_response, ABS_DIR):
    try:

        BG_PIC_FILE = os.path.join(ABS_DIR, "pics", "base_celebrant.png")
        AUDIO_FILE = os.path.join(ABS_DIR, "voiceover.mp3")  # optional
        PIC_DIR=os.path.abspath(os.path.join(ABS_DIR, "pics"))

        timestamps = []
        prev = 0
        for phrase in tts_response:
            duration = phrase["end_time"] - prev + 1  # add 1s buffer after each phrase
            timestamps.append(duration)
            prev = phrase["end_time"]
        final_video = generate_slides_from_dir(
            pic_dir=PIC_DIR,
            bg_file=BG_PIC_FILE,
            audio_file=AUDIO_FILE,
            duration_list=timestamps
        )

        t = time()
        video_path = os.path.join(ABS_DIR, f"{month}_celebration_video.mp4")
        final_video.write_videofile(video_path, fps=24)
        logger.info(f"write_videofile took {time()-t:.2f}s")

        return {'message': 'Video generated successfully', 'video_path': video_path}
    except Exception as e:
        logger.error(f"Error generating video for month {month}: {str(e)}", exc_info=True)
        raise Exception("Failed to generate video") from e