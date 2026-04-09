import os
from pathlib import Path
from slides.video_maker import generate_video

from utils.logger_config import get_logger
from utils.helpers import  raw_script_maker, generate_ai_script
from utils.tts import text_to_speech
from utils.exceptions import LLMError, TTSError, VIDError

logger = get_logger(__name__)

async def image_saver(name, month, date, generation, event, image, env):
  try:
    celebrant_image = f"{generation}gen_{date}_{month}_{name}.png"
    if image:
      dir_path = Path("./data") / month
      dir_path.mkdir(parents=True, exist_ok=True)
       # create base folder
      bg_path = Path("./data/_Background")
      bg_path.mkdir(parents=True, exist_ok=True)

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

async def video_generator(month, env):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ABS_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "data", month))
    if env != "dev":
      # try:
      #     # generate the voiceover script using the NLP
      #     raw_voiceover_dict = generate_ai_script(month)
      #     if not raw_voiceover_dict["is_successful"]:
      #        raise LLMError("Please try again. Error occured while generating voiceover text.")
      #     voiceover_text = raw_voiceover_dict.get("ai_response", "")
          
      #     if not voiceover_text:
      #         raise LLMError("Empty response received from LLM")
              
      #     logger.info("LLM response received successfully")
          
      # except LLMError:
      #     raise
      # except Exception as e:
      #     logger.error("LLM failed to generate voiceover script: %s", str(e), exc_info=True)
      #     raise LLMError(f"Failed to generate voiceover script: {str(e)}") from e
      
      try:
          ai_script_path = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "January", "ai_script.txt"))
          with open(ai_script_path, 'r') as f:
             voiceover_text = f.read()
          # generate voiceover audio using TTS
          tts_response = text_to_speech(voiceover_text, month, ABS_DIR)
          logger.info("TTS response: %s", tts_response)
          
      except Exception as e:
          logger.error("TTS failed to generate audio: %s", str(e), exc_info=True)
          raise TTSError(f"Failed to generate audio: {str(e)}") from e
    else:  
      try:
          # generate the video slides and compile the final video
          tts_response =  [{'phrase': 'of [Getrude]', 'end_time': 17.48}, {'phrase': 'to [Richard]', 'end_time': 21.79}, {'phrase': 'to [X]', 'end_time': 28.225}, {'phrase': 'to [X]', 'end_time': 33.377}, {'phrase': 'to [X]', 'end_time': 39.409}, {'phrase': 'to [X]', 'end_time': 50.049}, {'phrase': 'to [X]', 'end_time': 55.569}, {'phrase': 'to [X]', 'end_time': '01.01.201'}, {'phrase': 'to [X]', 'end_time': '01.08.185'}, {'phrase': 'to [X]', 'end_time': '01.14.625'}, {'phrase': 'to [X]', 'end_time': '01.22.404'}, {'phrase': 'to [X]', 'end_time': '01.26.345'}]
          vid_response = generate_video(month, tts_response , ABS_DIR)
          return vid_response
      except Exception as e:
          logger.error("Video generation failed: %s", str(e), exc_info=True)
          raise VIDError(f"Failed to generate video: {str(e)}") from e
