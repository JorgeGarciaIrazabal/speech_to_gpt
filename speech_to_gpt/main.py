import asyncio
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from random import randint
import random
import subprocess
from typing import Annotated, Iterable
from fastapi import Body, FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from pydantic import BaseModel
from speech_to_gpt.constants import photos_path
from speech_to_gpt.llms.friend import chat, detailed_answer
from speech_to_gpt.llms.image_analyzer import describe_context
from speech_to_gpt.llms.text_to_speech_manager import TTS_Manager
from speech_to_gpt.utils.measure import async_timeit, timeit
import aiohttp

app = FastAPI()
managers: list[TTS_Manager] = []

# Serve static files
app.mount("/static", StaticFiles(directory="speech_to_gpt/static", html=True), name="static")


async def text_generator(tts_manager: TTS_Manager, response: Iterable[BaseModel]):
    for i, message in enumerate(response):
        # if i != 0:
            # tts_manager.text_queue.put(message)
        yield message.model_dump_json() + "|||"
    # tts_manager.loading_data = False
        
@app.post("/chat")
@async_timeit
async def chat_endpoint(audio: UploadFile = File(...)):
    response = chat(await audio.read())

    # tts_manager = init_text_to_speech(Path("audio_path.wav"))
    # tts_manager.feed_to_stream()
    # managers.append(tts_manager)

    return StreamingResponse(text_generator(None, response))
    # return StreamingResponse(text_generator(tts_manager, response))


class MessageInput(BaseModel):
    message: str

@app.post("/detailed_answer")
async def detailed_answer_endpoint(message_input: MessageInput):
    response = detailed_answer(message_input.message)

    return StreamingResponse(text_generator(None, response))



@app.get("/audio")
@timeit
def get_audio():
    tts_manager = managers.pop(-1)
    return StreamingResponse(tts_manager.audio_chunk_generator(), media_type="audio/wav")


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

    result = await describe_context()

    return {"message": result}


if __name__ == "__main__":
    import uvicorn
    # TTS_Manager()
    uvicorn.run(app, host="0.0.0.0", port=8181)
