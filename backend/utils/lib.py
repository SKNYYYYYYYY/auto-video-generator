from pathlib import Path
from utils.helpers import extract_anchors_and_clean_text, raw_script_maker, ai_script_maker, text_to_speech

async def image_saver(name, month, date, generation, event, image):
  celebrant_image = f"{generation}gen_{date}_{month}_{name}.png"
  if image:
    dir_path = Path("./data") / month
    dir_path.mkdir(parents=True, exist_ok=True)

    # append the celebrant to the raw script
    script_file = dir_path / "script.json"
    script_response = raw_script_maker(script_file, event, celebrant_image)

    file_path = dir_path / "pics" / celebrant_image

    with open (file_path, 'wb') as f:
      f.write(await image.read())
    return {"message": f"image saved successfully in {file_path} and script updated"}
  return {"message": "no image provided"}

async def video_generator(month):
  # generate the voiceover script using the NLP
  raw_voiceover = ai_script_maker(month)
  print(raw_voiceover)
  # clean the script and extract anchors for timestamp matching
  clean_voiceover, anchors = extract_anchors_and_clean_text(raw_voiceover.get("ai_response"))

  # generate voiceover audio using TTS
  tts_response = text_to_speech(clean_voiceover)

  return tts_response