from fastapi import FastAPI, Form, File, UploadFile, Path
from utils.lib import image_saver, video_generator
import uvicorn

app = FastAPI()

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
async def generate_video(month= Path(...)):
  response = await video_generator(month)
  return response

if __name__=='__main__':
  uvicorn.run("app:app", port=8000, reload=True)