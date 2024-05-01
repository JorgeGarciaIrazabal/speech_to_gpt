import functools
from io import BytesIO
from typing import Iterable, List

from faster_whisper import WhisperModel
from ollama import Client

from speech_to_gpt.llms.chat_types import ChatMessage
from speech_to_gpt.llms.open_ai_client import client, GENERIC_MODEL
from speech_to_gpt.utils.measure import timeit


_messages = []


@timeit
def chat_audio(audio: bytes) -> Iterable[ChatMessage]:
    new_user_message = speech_to_text(audio)
    yield from chat_text(new_user_message)


def chat_text(messages: List[ChatMessage]) -> Iterable[ChatMessage]:
    print("new_user_message", messages[-1].content)
    # additional_questions = get_questions_to_expand_context(new_user_message)
    additional_questions = []
    for question in additional_questions:
        print(question.model_dump())
        yield question
    if not additional_questions:
        response = client.chat.completions.create(
            model=GENERIC_MODEL,
            messages=[message.model_dump() for message in messages],
            stream=True,
        )
        for m in response:
            message = ChatMessage(role="assistant", content=m.choices[0].delta.content)
            yield message


def detailed_answer(message: str):
    message = ChatMessage(role="user", content=message)

    for m in Client().chat(
        model=GENERIC_MODEL, messages=[message.model_dump()], stream=True
    ):
        message = ChatMessage(role="agent", content=m["message"]["content"])
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
