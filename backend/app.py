from fastapi import FastAPI, Form, File, UploadFile
from utils.lib import imageSaver
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
  image: UploadFile = File(...)
):
  response = await imageSaver(name, month, date, generation, image)
  return {"response"}

if __name__=='__main__':
  uvicorn.run("app:app", port=8001, reload=False)