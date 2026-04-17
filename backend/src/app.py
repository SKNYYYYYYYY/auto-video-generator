import uvicorn
import argparse
import os
from fastapi import FastAPI, Form, File, UploadFile, Path, HTTPException
from utils.lib import image_saver, video_generator
from utils.logger_config import get_logger
from utils.exceptions import VideoGenerationError
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()
logger = get_logger(__name__)

parser = argparse.ArgumentParser(usage="Run environment: dev, test, prod")
parser.add_argument("--env", choices=["dev", "prod", "test"], required=True)
args = parser.parse_args()
env = args.env

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
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
  image: UploadFile = File(...),
  relation: str = Form(None)
):
  response = await image_saver(name, month, date, generation, type, image, relation)
  return response

@app.get("/generate-video/{month}")
async def generate_video(month: str = Path(...)): 
    try:
        response = await video_generator(month, env)
        logger.info("Video generated successfully for month: %s", month)
        return {"message": "Video generated successfully", "response": response}
    except VideoGenerationError as e:
        logger.error("Video generation failed: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error("Unexpected error generating video: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")

if __name__=='__main__':
  logger.info("Application running in %s environment", env) 
  port = int(os.environ.get("PORT", 8000))
  reload_dirs=[
    "backend/slides",
    "backend/utils",
    "backend/src",
  ]
  uvicorn.run("src.app:app", port=port, reload_dirs=reload_dirs, reload=True,)
