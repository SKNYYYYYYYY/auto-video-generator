import uvicorn
import os
from fastapi import FastAPI, Form, File, UploadFile, Path, HTTPException
from utils.lib import image_saver, video_generator
from utils.logger_config import get_logger
from utils.exceptions import VideoGenerationError

app = FastAPI()
logger = get_logger(__name__)


@app.get("/")
async def index():
  return {"message": "backend is live"}

@app.post("/upload")
async def upload(
  name: str = Form(...),
  month: str = Form(...),
  date: int = Form(...),
  generation: int = Form(...),
  type: str = Form(...),
  image: UploadFile = File(...)
):
  response = await image_saver(name, month, date, generation, type, image)
  return response

@app.get("/generate-video/{month}")
async def generate_video(month: str = Path(...)):  # Added type hint
    try:
        response = await video_generator(month)
        logger.info("Video generated successfully for month: %s", month)
        return {"message": "Video generated successfully", "response": response}
    except VideoGenerationError as e:
        logger.error("Video generation failed: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error("Unexpected error generating video: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

if __name__=='__main__':
  port = int(os.environ.get("PORT", 8000))  
  uvicorn.run("app:app", host="0.0.0.0", 
