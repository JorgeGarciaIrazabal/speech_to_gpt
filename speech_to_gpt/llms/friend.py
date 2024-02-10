import asyncio
import functools
from pathlib import Path
from faster_whisper import WhisperModel
from ollama import AsyncClient
from TTS.api import TTS

MODEL = "qwen:7b"
_messages = []


async def chat(audio_file: Path):
    new_user_message = audio_to_text(audio_file)
    message = {'role': 'user', 'content': new_user_message}
    response = await AsyncClient().chat(model=MODEL, messages=[message])
    return response


@functools.lru_cache(maxsize=1)
def _init_audio_to_text_model():
    print("Initializing model distil-medium.en")
    model_size = "medium.en"
    # model_size = "distil-medium.en"
    model = WhisperModel(model_size, device="cuda", compute_type="int8_float32")
    print("model loaded distil-medium.en")
    return model

@functools.lru_cache(maxsize=1)
def _init_text_to_speech_model():
    print("Initializing model xtts_v2")
    model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to("cuda")

    print("model loaded distil-medium.en")
    return model

def audio_to_text(audio_file: Path):
    model = _init_audio_to_text_model()
    with audio_file.open("rb") as f:
        segments, info = model.transcribe(f, beam_size=5, language="en")
    return " ".join([s.text for s in segments])

def text_to_speech(text: str, audio_file: Path):
    print("starting text to speech")
    model = _init_text_to_speech_model()
    model.tts_to_file(text=text, speaker_wav="speakers/jorge.wav", language="en", file_path=str(audio_file.absolute()))
    print("text to speech done")
