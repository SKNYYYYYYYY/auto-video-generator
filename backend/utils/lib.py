from pathlib import Path

async def imageSaver(name, month, date, generation, image):
  filename = f"{generation}gen_{date}_{month}_{name}.png"
  if image:
    dir_path = Path("./data") / month
    dir_path.mkdir(parents=True, exist_ok=True)

    file_path = dir_path / filename

    with open (file_path, 'wb') as f:
      f.write(await image.read())
    return {"message": f"image saved successfully in {file_path} as {filename}"}
  return {"message": "no image provided"}