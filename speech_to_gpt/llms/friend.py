from enum import Enum
from io import BytesIO
import functools
import json
from pathlib import Path

from pydantic import BaseModel
from speech_to_gpt.llms.chat_types import ChatMessage, QuestionMessage
from speech_to_gpt.llms.context_creator import get_questions_to_expand_context

from speech_to_gpt.llms.text_to_speech_manager import TTS_Manager
from speech_to_gpt.utils.measure import async_timeit, timeit
from faster_whisper import WhisperModel
from ollama import Client
import functools


from speech_to_gpt.utils.measure import timeit

MODEL = "mistral:latest"
_messages = []


@timeit
def chat(audio: bytes):
    new_user_message = speech_to_text(audio)
    print("new_user_message", new_user_message)
    message = ChatMessage(role="user", content=new_user_message)
    yield message

    aditional_questions = get_questions_to_expand_context(new_user_message)
    for question in aditional_questions:
        print(question.model_dump())
        yield question

    if not aditional_questions:
        for m in Client().chat(model=MODEL, messages=[message.model_dump()], stream=True):
            message = ChatMessage(role="agent", content= m["message"]["content"])
            yield message

def detailed_answer(message: str):
    message = ChatMessage(role="user", content=message)

    for m in Client().chat(model=MODEL, messages=[message.model_dump()], stream=True):
        message = ChatMessage(role="agent", content= m["message"]["content"])
        yield message


@functools.lru_cache(maxsize=1)
def _init_speech_to_text_model():
    print("Initializing model distil-medium.en")
    # model_size = "small.en"
    model_size = "medium.en"
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
    