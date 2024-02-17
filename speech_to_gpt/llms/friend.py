from io import BytesIO
import functools
from pathlib import Path

from speech_to_gpt.llms.text_to_speech_manager import TTS_Manager
from speech_to_gpt.utils.measure import async_timeit, timeit
from faster_whisper import WhisperModel
from ollama import Client
import functools


from speech_to_gpt.utils.measure import timeit

MODEL = "qwen:7b"
_messages = []


@timeit
def chat(audio: bytes):
    new_user_message = speech_to_text(audio)
    message = {'role': 'user', 'content': new_user_message}
    print("new_user_message", new_user_message)
    yield new_user_message
    for m in Client().chat(model=MODEL, messages=[message], stream=True):
        yield m["message"]["content"]


@functools.lru_cache(maxsize=1)
def _init_speech_to_text_model():
    print("Initializing model distil-medium.en")
    model_size = "small.en"
    # model_size = "distil-medium.en"
    model = WhisperModel(model_size, device="cuda", compute_type="int8_float32")
    print("model loaded distil-medium.en")
    return model

@timeit
def speech_to_text(audio: bytes):
    model = _init_speech_to_text_model()
    segments, info = model.transcribe(BytesIO(audio), beam_size=5, language="en")
    return " ".join([s.text for s in segments])


@timeit
def init_text_to_speech(audio_file: Path) -> TTS_Manager:
    return TTS_Manager()
    