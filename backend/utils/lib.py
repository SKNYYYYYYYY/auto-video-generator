import os
from pathlib import Path
from slides.video_maker import generate_video

from utils.logger_config import get_logger
from utils.helpers import  raw_script_maker, generate_ai_script
from utils.tts import text_to_speech
from utils.exceptions import LLMError, TTSError, VIDError

logger = get_logger(__name__)

async def image_saver(name, month, date, generation, event, image, relation):
  try:
    logger.debug("Relation %s", relation)
    safe_relation = "_".join(relation) if relation else ""
    celebrant_image = f"{generation}gen_{date}_{month}_{name}_{safe_relation}.png" if safe_relation else f"{generation}gen_{date}_{month}_{name}.png"
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
      return {"message": f"image saved successfully"}
    return {"message": "no image provided"}
  except Exception as e:
    logger.exception("Error saving image or updating script")
    raise Exception("Failed to save image or update script") from e

async def video_generator(month, env, progress_callback=None):
    """
    Generate video with progress updates
    
    Args:
        month: The month to generate video for
        env: Environment (dev/prod)
        progress_callback: Optional async function(step, status, message, data)
    """
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ABS_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "data", month))
    
    async def send_update(step, status, message="", data=None):
        if progress_callback:
            await progress_callback(step, status, message, data)
    
    if env != "dev":
        try:
            # Step 1: LLM Start
            await send_update("llm", "start", "Generating script with AI...")
            
            # generate the voiceover script using the NLP
            raw_voiceover_dict = generate_ai_script(month)
            if not raw_voiceover_dict["is_successful"]:
                raise LLMError("Please try again. Error occured while generating voiceover text.")
            voiceover_text = raw_voiceover_dict.get("ai_response", "")
            
            if not voiceover_text:
                raise LLMError("Empty response received from LLM")
                
            logger.info("LLM response received successfully")
            
            # Step 1: LLM Complete with response
            await send_update("llm", "complete", "Script generated successfully", {
                "script": voiceover_text[:500] + "..." if len(voiceover_text) > 500 else voiceover_text
            })
            
        except LLMError:
            await send_update("llm", "error", str(e) if 'e' in locals() else "LLM error")
            raise
        except Exception as e:
            logger.error("LLM failed to generate voiceover script: %s", str(e), exc_info=True)
            await send_update("llm", "error", f"Failed to generate script: {str(e)}")
            raise LLMError(f"Failed to generate voiceover script: {str(e)}") from e
        
        try:
            # Step 2: TTS Start
            await send_update("tts", "start", "Creating voiceover audio...")
            
            ai_script_path = os.path.abspath(os.path.join(BASE_DIR, "..", "data", f"{month}", "ai_script.txt"))
            with open(ai_script_path, 'r') as f:
                voiceover_text = f.read()
            # generate voiceover audio using TTS
            tts_response = text_to_speech(voiceover_text, month, ABS_DIR)
            logger.info("TTS response received and audio saved sucessfully")
            
            # Step 2: TTS Complete
            await send_update("tts", "complete", "Voiceover created successfully", {
                "audio_duration": len(tts_response) if isinstance(tts_response, list) else None
            })
            
        except Exception as e:
            logger.error("TTS failed to generate audio: %s", str(e), exc_info=True)
            await send_update("tts", "error", f"Failed to create voiceover: {str(e)}")
            raise TTSError(f"Failed to generate audio: {str(e)}") from e
        
        try:
            # Step 3: Slideshow Start
            await send_update("slideshow", "start", "Building slideshow video...")
            
            vid_response = generate_video(month, tts_response, ABS_DIR, env)
            
            # Step 3: Slideshow Complete
            await send_update("slideshow", "complete", "Video ready", {
                "duration": vid_response.get("duration", 0),
                "images_used": vid_response.get("images_used", 0),
                "video_path": vid_response.get("video_path", "")
            })
            
            return vid_response
            
        except Exception as e:
            logger.error("Video generation failed: %s", str(e), exc_info=True)
            await send_update("slideshow", "error", f"Failed to create video: {str(e)}")
            raise VIDError(f"Failed to generate audio: {str(e)}") from e
            
    else:  # env == "dev"
        try:
            # Step 1: LLM Start (dev mode - skip actual LLM)
            await send_update("llm", "start", "Loading script (dev mode)...")
            await send_update("llm", "complete", "Script loaded", {"script": "Dev mode script"})
            
            # Step 2: TTS Start (dev mode - use existing TTS response)
            await send_update("tts", "start", "Using existing voiceover (dev mode)...")
            
            # generate the video slides and compile the final video
            tts_response = [{'phrase': 'we celebrate fg', 'start_time': 14.86, 'end_time': 15.859}, {'phrase': 'cheer for sa', 'start_time': 18.471, 'end_time': 19.272}, {'phrase': 'go to d', 'start_time': 22.825, 'end_time': 23.336}, {'phrase': 'go to e333322223', 'start_time': 25.797, 'end_time': 29.245}, {'phrase': 'on the 9th', 'start_time': 31.091, 'end_time': 31.625}, {'phrase': 'we celebrate jk', 'start_time': 33.947, 'end_time': 34.818}, {'phrase': 'and also f', 'start_time': 34.969, 'end_time': 35.7}, {'phrase': 'wishes to ds', 'start_time': 38.44, 'end_time': 39.16}, {'phrase': 'on the 18th', 'start_time': 41.807, 'end_time': 42.527}, {'phrase': 'on the 23rd', 'start_time': 45.871, 'end_time': 46.707}, {'phrase': 'yt d-o trtr', 'start_time': 53.731, 'end_time': 55.194}, {'phrase': 'dds s-o r', 'start_time': 57.945, 'end_time': 59.304}, {'phrase': 'on the 9th', 'start_time': 31.091, 'end_time': 31.625}, {'phrase': 'tr d-o trtr', 'start_time': 65.956, 'end_time': 67.733}, {'phrase': 'anniversary of g', 'start_time': 74.223, 'end_time': 75.279}, {'phrase': 'congratulations to j', 'start_time': 79.238, 'end_time': 80.503}, {'phrase': 'milestone for Newton', 'start_time': 84.88, 'end_time': 85.995}]
            
            await send_update("tts", "complete", "Voiceover loaded (dev mode)")
            
            # Step 3: Slideshow Start
            await send_update("slideshow", "start", "Building slideshow video...")
            
            vid_response = generate_video(month, tts_response, ABS_DIR, env)
            
            # Step 3: Slideshow Complete
            await send_update("slideshow", "complete", "Video ready (dev mode)", {
                "duration": vid_response.get("duration", 0),
                "images_used": vid_response.get("images_used", 0)
            })
            
            return vid_response
            
        except Exception as e:
            logger.error("Video generation failed: %s", str(e), exc_info=True)
            await send_update("slideshow", "error", f"Failed to create video: {str(e)}")
            raise VIDError(f"Failed to generate video: {str(e)}") from e