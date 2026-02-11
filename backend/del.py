import os
import base64
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

load_dotenv()

def text_to_speech(text, voice_id="21m00Tcm4TlvDq8ikWAM", output_file="output.mp3"):
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

    alignment = stream.alignment 
    audio_base_64 = stream.audio_base_64
    audio_bytes = base64.b64decode(audio_base_64)
        
    if audio_bytes:
        with open(output_file, "wb") as f:
            f.write(audio_bytes)
        print(f"✅ Audio saved to {output_file}")
    else:
        print("❌ No valid audio bytes to save.")

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

# Example usage
if __name__ == "__main__":
    text = "This is a test <cend> for ElevenLabs API."
    alignment = text_to_speech(text)

    if alignment:
        cend_ts = cend_timestamps(text, alignment)
        print("⏱ <cend> timestamps:", cend_ts)
