import os
from pathlib import Path
from slides.video_maker import generate_video
from fastapi import HTTPException

from utils.logger_config import get_logger
from utils.helpers import  raw_script_maker, ai_script_maker
from utils.tts import text_to_speech
from utils.exceptions import LLMError, TTSError, VIDError

logger = get_logger(__name__)

async def image_saver(name, month, date, generation, event, image):
  try:
    celebrant_image = f"{generation}gen_{date}_{month}_{name}.png"
    if image:
      dir_path = Path("./data") / month
      dir_path.mkdir(parents=True, exist_ok=True)
      
      # create pics folder
      (dir_path / "pics").mkdir(parents=True, exist_ok=True)
      
      # append the celebrant to the raw script
      script_file = dir_path / "script.json"
      raw_script_maker(script_file, event, celebrant_image)

      file_path = dir_path / "pics" / celebrant_image

      with open (file_path, 'wb') as f:
        f.write(await image.read())
      return {"message": f"image saved successfully in {file_path} and script updated"}
    return {"message": "no image provided"}
  except Exception as e:
    logger.exception("Error saving image or updating script")
    raise Exception("Failed to save image or update script") from e

async def video_generator(month):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ABS_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "data", month))
    try:
        # generate the voiceover script using the NLP
        raw_voiceover_dict = ai_script_maker(month)
        voiceover_text = raw_voiceover_dict.get("ai_response", "")
        
        if not voiceover_text:
            raise LLMError("Empty response received from LLM")
            
        logger.info("LLM response received successfully")
        
    except LLMError:
        raise
    except Exception as e:
        logger.error("LLM failed to generate voiceover script: %s", str(e), exc_info=True)
        raise LLMError(f"Failed to generate voiceover script: {str(e)}") from e
    
    try:
        # generate voiceover audio using TTS
        tts_response = text_to_speech(voiceover_text, month, ABS_DIR)
        logger.info("TTS response: %s", tts_response)
        
    except Exception as e:
        logger.error("TTS failed to generate audio: %s", str(e), exc_info=True)
        raise TTSError(f"Failed to generate audio: {str(e)}") from e
    try:
        # generate the video slides and compile the final video
        # tts_response =  [{'phrase': 'of [Name 1]', 'start_time': 17.055, 'end_time': 20.004}, {'phrase': 'to [Name 2]', 'start_time': 24.311, 'end_time': 25.565}, {'phrase': 'honor [Name 3]', 'start_time': 28.433, 'end_time': 30.233}],
        vid_response = generate_video(month, tts_response , ABS_DIR)
        return vid_response
    except Exception as e:
        logger.error("Video generation failed: %s", str(e), exc_info=True)
        raise VIDError(f"Failed to generate video: {str(e)}") from e
