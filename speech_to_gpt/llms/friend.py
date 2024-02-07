import asyncio
import functools
from pathlib import Path
from faster_whisper import WhisperModel
from ollama import AsyncClient

MODEL = "starling-lm"
_messages = []


async def chat(audio_file: Path):
    new_user_message = audio_to_text(audio_file)
    message = {'role': 'user', 'content': new_user_message}
    _messages.append(message)
    response = await AsyncClient().chat(model=MODEL, messages=_messages)
    _messages.append({'role': 'assistant', 'content': response['message']["content"]})
    return response


@functools.lru_cache(maxsize=1)
def _init_model():
    print("Initializing model distil-medium.en")
    model_size = "medium.en"
    # model_size = "distil-medium.en"
    model = WhisperModel(model_size, device="cuda", compute_type="int8_float32")
    print("model loaded distil-medium.en")
    return model


def audio_to_text(audio_file: Path):
    model = _init_model()
    with audio_file.open("rb") as f:
        segments, info = model.transcribe(f, beam_size=5, language="en")
    return " ".join([s.text for s in segments])
