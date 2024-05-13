import json
import subprocess
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Annotated
from typing import List

from fastapi import Depends, Form
from fastapi import File, UploadFile
from pydantic import BaseModel, parse_obj_as
from starlette.responses import StreamingResponse

from speech_to_gpt.api import app
from speech_to_gpt.api.authenticator import User, get_current_user
from speech_to_gpt.llms.chat_types import ChatMessage
from speech_to_gpt.llms.friend import chat_audio, chat_text
from speech_to_gpt.utils.measure import async_timeit, timeit


class ChatResponse(BaseModel):
    response: str


@app.post("/chat-audio")
async def chat_audio_endpoint(
    audio: UploadFile = File(...),
    messages: str = Form(...),
) -> StreamingResponse:
    messages = parse_obj_as(List[ChatMessage], json.loads(messages))
    with TemporaryDirectory() as temp_dir:
        audio_path = Path(temp_dir) / "audio.wav"
        mp3_path = Path(temp_dir) / "audio.mp3"
        audio_path.write_bytes(await audio.read())
        subprocess.run(f"ffmpeg -i {audio_path} {mp3_path}", shell=True)
        response = chat_audio(mp3_path.read_bytes(), messages)

    def model_dump_json():
        for r in response:
            yield r.model_dump_json() + "%%%%"

    return StreamingResponse(model_dump_json(), media_type="application/json")


@app.post("/chat")
@async_timeit
async def chat_endpoint(
    messages: List[ChatMessage],
    current_user: Annotated[User, Depends(get_current_user)],
) -> StreamingResponse:
    response = chat_text(messages)

    def model_dump_json():
        for r in response:
            yield r.model_dump_json() + "%%%%"

    return StreamingResponse(model_dump_json(), media_type="application/json")


@app.get("/audio")
@timeit
def get_audio():
    raise NotImplementedError("not implemented")
    pass


@app.post("/upload_photo")
async def upload_photo(photo: UploadFile = File(...)):
    raise NotImplementedError("not implemented")
    contents = await photo.read()
    # photo path is photo_ + timestamp
    photo_path = (
        photos_path / f"photo_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png"
    )

    photo_path.write_bytes(contents)

    # delele old photo. only keep the last 4 based on datetime
    photo_files = sorted(
        photos_path.glob("photo_*.png"), key=lambda x: x.stat().st_mtime
    )
    for photo_file in photo_files[:-4]:
        photo_file.unlink()

    result = await describe_context()

    return {"message": result}
