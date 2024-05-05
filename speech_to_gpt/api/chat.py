from typing import List

from fastapi import File, UploadFile
from pydantic import BaseModel
from starlette.responses import StreamingResponse

from speech_to_gpt.app import app
from speech_to_gpt.llms.chat_types import ChatMessage
from speech_to_gpt.llms.friend import chat_audio, chat_text
from speech_to_gpt.utils.measure import async_timeit, timeit


class ChatResponse(BaseModel):
    response: str


@app.post("/chat-audio")
@async_timeit
async def chat_audio_endpoint(audio: UploadFile = File(...)) -> ChatResponse:
    response = chat_audio(await audio.read())

    return ChatResponse(response="".join([m.content for m in response]))


@app.post("/chat")
@async_timeit
async def chat_endpoint(messages: List[ChatMessage]) -> StreamingResponse:
    response = chat_text(messages)

    def model_dump_json():
        for r in response:
            yield r.model_dump_json() + "%%%%"

    return StreamingResponse(model_dump_json(), media_type="application/json")


@app.get("/audio")
@timeit
def get_audio():
    pass


@app.post("/upload_photo")
async def upload_photo(photo: UploadFile = File(...)):
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
