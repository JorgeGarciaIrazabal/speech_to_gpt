from datetime import datetime
from fastapi import FastAPI, File, UploadFile
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from speech_to_gpt.constants import photos_path
from speech_to_gpt.llms.friend import chat

app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="speech_to_gpt/static", html=True), name="static")


@app.post("/upload")
async def upload_audio(audio: UploadFile = File(...)):
    contents = await audio.read()
    with open(audio.filename, "wb") as f:
        f.write(contents)
    # return {"filename": audio.filename}

    response = await chat(Path(audio.filename))
    print(response['message']["content"])
    return {"message": response['message']["content"]}


@app.post("/upload_photo")
async def upload_photo(photo: UploadFile = File(...)):
    contents = await photo.read()
    # photo path is photo_ + timestamp
    photo_path = photos_path / f"photo_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png"

    photo_path.write_bytes(contents)

    # delele old photo. only keep the last 4 based on datetime
    photo_files = sorted(photos_path.glob("photo_*.png"), key=lambda x: x.stat().st_mtime)
    for photo_file in photo_files[:-4]:
        photo_file.unlink()

    return {"message": "File uploaded successfully"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
