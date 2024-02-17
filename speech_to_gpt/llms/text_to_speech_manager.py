import asyncio
from concurrent.futures import Future, ThreadPoolExecutor
import functools
import logging
from pathlib import Path
import time
import uuid
import wave
from RealtimeTTS import TextToAudioStream, CoquiEngine
from speech_to_gpt.utils.audio import generate_audio

import queue

thread_pool_executor = ThreadPoolExecutor(max_workers=4)


@functools.lru_cache(maxsize=1)
def _init_text_to_speech_model():
    print("Initializing model xtts_v2")
    model = CoquiEngine(
        thread_count=60,
        model_name="tts_models/en/ljspeech/speedy-speech",
        # use_deepspeed=True,
        level=logging.ERROR
    )

    print("model loaded speedy-speech")
    return model


class TTS_Manager():
    def __init__(self) -> None:
        engine = _init_text_to_speech_model()
        self.text_queue = queue.Queue()
        self.audio_queue = queue.Queue()
        self._audio_list = []
        self.stream = TextToAudioStream(engine, level=logging.CRITICAL)
        self.stream.muted = True
        self.loading_data = False
        self.synthesizing_audio = False
        self.audio_path = Path(f"audio_path_{uuid.uuid4().hex}.wav")

    
    def play(self):
        self.synthesizing_audio = True
        self.stream.play(
            fast_sentence_fragment=True,
            muted=True,
            output_wavfile=str(self.audio_path),
            buffer_threshold_seconds=3.0,
            on_audio_chunk=self.audio_queue.put
        )
        self.synthesizing_audio = False
        print("audio file completed", len(self.audio_path.read_bytes()))
    
    def feed_to_stream(self) -> Future:
        self.loading_data = True
        return thread_pool_executor.submit(self._feed_to_stream)
    
    def _feed_to_stream(self):
        def text_generator():
            while self.loading_data or not self.text_queue.empty():
                try:
                    item = self.text_queue.get_nowait()
                    yield item
                except queue.Empty:
                    time.sleep(0.1)
                    
        self.stream.feed(text_generator())
        self.play()

    
    def audio_chunk_generator(self):
        while self.synthesizing_audio and not self.audio_path.exists():
            time.sleep(0.1)
        total_bytes = b""
        was_synthesizing = True
        bps, channels, rate = self.stream.engine.get_stream_info()
        while was_synthesizing  or not self.audio_queue.empty():
            was_synthesizing = self.synthesizing_audio
            try:
                c = b""
                while not self.audio_queue.empty():
                    c += self.audio_queue.get(block=False)
                if c:
                    yield generate_audio(channels, rate, 16, c)
                time.sleep(2.0)
            except queue.Empty:
                time.sleep(0.5)
                continue
            
        print("first chuck", self.audio_path.read_bytes()[:60])
        print("finished", len(self.audio_path.read_bytes()), len(total_bytes))