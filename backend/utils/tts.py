import json
import os
import base64
import re
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from fastapi import HTTPException
from utils.logger_config import get_logger


load_dotenv()
logger = get_logger(__name__)

def audio_generator(text, voice_id="JBFqnCBsd6RMkjVDRZzb", output_file="voiceover.mp3"):
    """
    Converts text to speech using ElevenLabs API and returns alignment info.
    Audio is saved to the specified output_file.
    """
    client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

    stream = client.text_to_speech.convert_with_timestamps(
        voice_id=voice_id,
        output_format="mp3_44100_128",
        text=text
    )
    with open("tts_cache.json", "w", encoding="utf-8") as f:
        json.dump(stream.model_dump(), f, indent=4)
    # import json
    # from elevenlabs.types import AudioWithTimestampsResponse
    # with open("tts_cache.json", "r", encoding="utf-8") as f:
    #     data = json.load(f)
    # stream = AudioWithTimestampsResponse(**data)

    alignment = stream.alignment 
    audio_base_64 = stream.audio_base_64
    audio_bytes = base64.b64decode(audio_base_64)

    if audio_bytes:
        with open(output_file, "wb") as f:
            f.write(audio_bytes)
    else:
        logger.warning("No valid voiceover audio bytes to save.")
        return

    return alignment

def phrase_to_timestamp(phrase, alignment):
    """
    Returns start and end timestamps for a given phrase from alignment.
    """
    if not alignment:
        return None

    spoken_text = "".join(alignment.characters)
    start_idx = spoken_text.find(phrase)
    if start_idx == -1:
        return None

    end_idx = start_idx + len(phrase) - 1

    return {
        "phrase": phrase,
        "start_time": alignment.character_start_times_seconds[start_idx],
        "end_time": alignment.character_end_times_seconds[end_idx]
    }

def cend_timestamps(text, alignment, window=3):
    """
    Returns timestamps for all <cend> markers in the text.
    Includes `window` words before <cend> for context.
    """
    if not alignment:
        return []

    words = text.split()
    timestamps = []

    for i, word in enumerate(words):
        if "<cend>" in word:
            # Take previous `window` words as context
            start_word_idx = max(0, i - window)
            phrase = " ".join(words[start_word_idx:i])
            ts = phrase_to_timestamp(phrase, alignment)
            if ts:
                timestamps.append(ts)

    return timestamps

def extract_anchors_and_clean_text(text, window=3):
    anchors = []
    def replacer(match):
        before = match.group(1)
        words = before.split()
        anchor = " ".join(words[-window:])
        anchors.append(anchor)
        return before
    clean_text = re.sub(
        r"(.*?)(<cend>)",
        replacer,
        text,
        flags = re.DOTALL
    )
    return clean_text, anchors


def text_to_speech(text, month, ABS_DIR):
    try:
        AUDIO_FILE = os.path.abspath(os.path.join(ABS_DIR, "voiceover.mp3"))

        cleaned_text, anchors = extract_anchors_and_clean_text(text)

        alignment = audio_generator(text=cleaned_text, output_file=AUDIO_FILE)
        timestamps = []
        if alignment:
            for anchor in anchors:
                ts = phrase_to_timestamp(anchor, alignment)
                if ts:
                    timestamps.append(ts)
        return timestamps
    except Exception as e:
        logger.error("Error generating audio: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to generate audio: {str(e)}")