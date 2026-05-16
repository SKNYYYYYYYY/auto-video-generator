import asyncio
from typing import AsyncGenerator
import uvicorn
import argparse
import os
import json

from fastapi import FastAPI, Form, File, UploadFile, Path, HTTPException
from fastapi.responses import StreamingResponse

from pathlib import Path as Pathparam
from datetime import datetime,timedelta
from utils.lib import image_saver, video_generator
from utils.logger_config import get_logger
from utils.exceptions import VideoGenerationError
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR, EVENT_JOB_MISSED


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



scheduler = AsyncIOScheduler()


async def scheduled_video_generation():
    current_month = datetime.now().strftime("%B")
    BASE_DIR = Pathparam(__file__).resolve().parent.parent
    PIC_DIR = BASE_DIR / "data" / f"{current_month}"

    logger.info(f"[JOB START] Month: {current_month}")
    # Check if pic folder exists
    if not os.path.exists(PIC_DIR):
        logger.warning(f"[SKIP] Missing pic folder")
        return

    # Check if pic folder is empty
    if not os.listdir(PIC_DIR):
        logger.warning(f"[SKIP] Missing pic folder")
        return
    logger.info(f"[PROCESSING] Generating video for {current_month}")

    try:
        await video_generator(current_month, env)
        logger.info(f"[SUCCESS] Video generated for {current_month}")

    except Exception as e:
        logger.error(f"[FAILED] {current_month} -> {str(e)}", exc_info=True)
def job_listener(event):
    if event.exception:
        logger.error(f"[SCHEDULER ERROR] Job {event.job_id} failed", exc_info=True)
    else:
        logger.info(f"[SCHEDULER OK] Job executed: {event.job_id}")

scheduler.add_listener(
    job_listener,
    EVENT_JOB_EXECUTED | EVENT_JOB_ERROR | EVENT_JOB_MISSED
)
@app.on_event("startup")
async def startup():

    scheduler.start()

    # Default schedule:
    # Every 1st day of month at 8:00 AM
    day=1
    hour=8
    scheduler.add_job(
        scheduled_video_generation,
        "cron",
        id="monthly-video-job",
        day=day,
        hour=hour,
        minute=0,
        replace_existing=True
    )
    period = "AM" if hour < 12 else "PM"
    logger.info(f"API started successfully. Video generation is scheduled to run monthly on date {day} at {hour}:00 {period}")

@app.post("/schedule-video")
async def schedule_video(
    day: int = Form(1),
    hour: int = Form(8),
    minute: int = Form(0)
):

    job_id = "monthly-video-job"

    scheduler.add_job(
        scheduled_video_generation,
        "cron",
        id=job_id,
        day=day,
        hour=hour,
        minute=minute,
        replace_existing=True
    )
    logger.info(f"Schedule updated → day={day}, hour={hour}, minute={minute}")

    return {
        "message": "Schedule updated successfully",
        "schedule": {
            "day": day,
            "hour": hour,
            "minute": minute
        }
    }

@app.post("/test-schedule")
async def test_schedule(minutes: int | None = None):
    delay_seconds = (minutes * 60) if minutes is not None else 3

    run_time = datetime.now() + timedelta(seconds=delay_seconds)

    scheduler.add_job(
        scheduled_video_generation,
        "date",
        run_date=run_time,
        id="test-job",
        replace_existing=True
    )

    logger.info(f"Test job scheduled in {delay_seconds/60} minutes")

    return {
        "message": "Test job scheduled",
        "run_at": str(run_time)
    }
@app.get("/")
async def index():
  return {"message": "backend is live"}

@app.post("/upload")
async def upload(
  name: str = Form(...),
  month: str = Form(...),
  date: int = Form(...),
  generation: str = Form(...),
  event: str = Form(...),
  image: UploadFile = File(...),
  relation_1: str = Form(None),
  relation_2: str = Form(None),
  relation_3: str = Form(None)
):
  relation = []
  relation.append(relation_1) if relation_1 else None
  relation.append(relation_2) if relation_2 else None
  relation.append(relation_3) if relation_3 else None
  
  response = await image_saver(name, month, date, generation, event, image, relation)

  return response


@app.get("/generate-video-stream/{month}")
async def generate_video_stream(month: str, env: str = "prod"):
    async def event_generator() -> AsyncGenerator[str, None]:
        # Queue for progress messages
        message_queue = asyncio.Queue()
        
        # Progress callback that puts messages in queue
        async def progress_callback(step: str, status: str, message: str = "", data: dict = None):
            update = {
                "type": f"step_{status}" if status in ["start", "complete"] else status,
                "step": step,
                "message": message,
                "timestamp": datetime.now().isoformat()
            }
            if data:
                update["data"] = data
            await message_queue.put(update)
        
        # Run video generation
        async def run_generation():
            try:
                result = await video_generator(month, env, progress_callback)
                await message_queue.put({
                    "type": "complete",
                    "result": {
                        "video_url": f"/videos/{month.lower()}_compilation.mp4",
                        "duration": result.get("duration", 0),
                        "images_used": result.get("images_used", 0),
                        "video_path": result.get("video_path", "")
                    }
                })
            except Exception as e:
                await message_queue.put({
                    "type": "error",
                    "error": str(e)
                })
            finally:
                await message_queue.put(None)  # Signal end
        
        # Start generation
        asyncio.create_task(run_generation())
        
        # Stream messages
        while True:
            message = await message_queue.get()
            if message is None:
                break
            yield f"data: {json.dumps(message)}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )

if __name__=='__main__':
  logger.info("Application running in %s environment", env) 
  port = int(os.environ.get("PORT", 8000))
  reload_dirs=[
    "backend/slides",
    "backend/utils",
    "backend/src",
  ]
  uvicorn.run("src.app:app", port=port, reload_dirs=reload_dirs, reload=True,)
