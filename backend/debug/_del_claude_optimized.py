import os
from concurrent.futures import ThreadPoolExecutor
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
    return ImageOps.fit(img, (width, height), method=Image.LANCZOS, centering=(0.5, 0.5))


def extend_bottom_numpy(img_array, extend_pixels=20):
    """Extend bottom of image by repeating the last row — no OpenCV resize needed"""
    last_row = img_array[-1:, :, :]  # shape (1, w, c)
    extension = np.repeat(last_row, extend_pixels, axis=0)
    return np.concatenate([img_array, extension], axis=0)


def prepare_celebrant_frame(celeb_path, frame_width=880, frame_height=880, extend_pixels=93):
    """Crop, scale, and extend a celebrant image — returns a numpy array ready for ImageClip"""
    cropped = crop_to_rectangle(celeb_path)
    img_array = np.array(cropped)

    # Scale proportionally using OpenCV (faster than PIL for numpy pipelines)
    h, w = img_array.shape[:2]
    scale = frame_height / h
    new_w = int(w * scale)
    new_h = frame_height
    img_array = cv2.resize(img_array, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

    if new_w > frame_width:
        img_array = cv2.resize(img_array, (frame_width, new_h), interpolation=cv2.INTER_LINEAR)

    img_array = extend_bottom_numpy(img_array, extend_pixels=extend_pixels)
    return img_array  # (h+extend, w, c)


def render_text_to_image(text, font, font_size, color, canvas_size):
    """
    Pre-render a TextClip to a numpy array so it's not re-rendered per-frame during video write.
    Returns a numpy RGBA array at canvas_size (w, h).
    """
    txt_clip = TextClip(text=text, font=font, font_size=font_size, color=color)
    # Get the rendered frame as numpy array (RGB)
    frame = txt_clip.get_frame(0)
    txt_clip.close()
    return frame  # shape: (h, w, 3)


def composite_slide_frame(bg_array, photo_array, text_array,
                           photo_pos=(86, 94), text_center_y=800, canvas_w=1200):
    """
    Compose all layers into a single numpy frame (no moviepy CompositeVideoClip overhead).
    All arrays are (h, w, channels).
    """
    canvas = bg_array.copy()
    canvas_h, canvas_cw = canvas.shape[:2]

    # Paste photo
    px, py = photo_pos
    ph, pw = photo_array.shape[:2]
    # Clip to canvas bounds
    py2 = min(py + ph, canvas_h)
    px2 = min(px + pw, canvas_cw)
    src_h = py2 - py
    src_w = px2 - px

    photo_rgb = photo_array[:src_h, :src_w, :3]
    if photo_array.shape[2] == 4:
        alpha = photo_array[:src_h, :src_w, 3:4] / 255.0
        canvas[py:py2, px:px2, :3] = (
            photo_rgb * alpha + canvas[py:py2, px:px2, :3] * (1 - alpha)
        ).astype(np.uint8)
    else:
        canvas[py:py2, px:px2, :3] = photo_rgb

    # Paste text (centered horizontally)
    th, tw = text_array.shape[:2]
    tx = (canvas_cw - tw) // 2
    ty = text_center_y
    ty2 = min(ty + th, canvas_h)
    tx2 = min(tx + tw, canvas_cw)
    src_h2 = ty2 - ty
    src_w2 = tx2 - tx

    # Simple paste (text clip renders with black background — use additive blend for white text)
    text_rgb = text_array[:src_h2, :src_w2, :3]
    canvas[ty:ty2, tx:tx2, :3] = np.clip(
        canvas[ty:ty2, tx:tx2, :3].astype(np.int16) + text_rgb.astype(np.int16), 0, 255
    ).astype(np.uint8)

    return canvas


# -----------------------------
# Slide Creation (Optimized)
# -----------------------------

def create_slide(bg_array, photo_array, text_array, duration):
    """
    Build a slide as a single static ImageClip (one composite frame),
    avoiding per-frame compositing during video write.
    """
    frame = composite_slide_frame(bg_array, photo_array, text_array)
    return ImageClip(frame).with_duration(duration)


# -----------------------------
# Main Function: Process Folder
# -----------------------------

def generate_slides_from_dir(pic_dir, bg_file, audio_file, duration_list):
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

    # Pre-load background once as numpy array
    bg_pil = Image.open(bg_file).convert("RGB")
    bg_array = np.array(bg_pil)  # (H, W, 3)

    # Pre-process all celebrant images in parallel
    celeb_paths = [os.path.join(pic_dir, f) for f in celeb_files]
    names = [os.path.splitext(f)[0].replace("_", " ") for f in celeb_files]

    print(f"Pre-processing {len(celeb_paths)} celebrant images in parallel...")
    with ThreadPoolExecutor() as executor:
        photo_arrays = list(executor.map(prepare_celebrant_frame, celeb_paths))

    # Pre-render text frames (fast — reuses same font/size)
    print("Pre-rendering text frames...")
    text_arrays = [
        render_text_to_image(
            text=name,
            font="fonts/arial/arial.ttf",
            font_size=50,
            color="white",
            canvas_size=(1200, 100)
        )
        for name in names
    ]

    # Build slides (each is now just one static composite frame)
    print("Building slides...")
    clips = [
        create_slide(bg_array, photo_arrays[i], text_arrays[i], duration_list[i])
        for i in range(len(celeb_files))
    ]

    final_video = concatenate_videoclips(clips, method="compose")

    if os.path.exists(audio_file):
        audio = AudioFileClip(audio_file)
        # Trim audio to video duration if longer, or loop if shorter
        if audio.duration > final_video.duration:
            audio = audio.subclipped(0, final_video.duration)
        final_video = final_video.with_audio(audio)
        print(f"Audio attached: {audio.duration:.2f}s over {final_video.duration:.2f}s video")
    else:
        print(f"WARNING: Audio file not found at {audio_file}")

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
    PIC_DIR = os.path.abspath(os.path.join(ABS_DIR, "pics"))

    tts_response = [
        {'phrase': 'to Geofrey Cheruiyot',  'start_time': 13.653, 'end_time': 14.768},
        {'phrase': 'to Brigid Chepkemoi',   'start_time': 18.913, 'end_time': 19.981},
        {'phrase': 'on March 12th',          'start_time': 25.391, 'end_time': 26.227}
    ]

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

    out_path = os.path.join(ABS_DIR, f"{month}_celebration_video.mp4")
    final_video.write_videofile(
        out_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        threads=os.cpu_count(),   # use all CPU cores for encoding
        preset="fast",            # x264 preset: ultrafast > superfast > fast > medium
        ffmpeg_params=["-crf", "23"]  # quality (18=high, 28=low, 23=default)
    )