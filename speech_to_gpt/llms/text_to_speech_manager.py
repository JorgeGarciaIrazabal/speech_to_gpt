from concurrent.futures import ThreadPoolExecutor
import functools
import logging
from pathlib import Path
import pickle
import time
import uuid
from RealtimeTTS import TextToAudioStream, CoquiEngine

import queue

thread_pool_executor = ThreadPoolExecutor(max_workers=4)


@functools.lru_cache(maxsize=1)
def _init_text_to_speech_model():
    print("Initializing model xtts_v2")
    model = CoquiEngine(thread_count=30)

    print("model loaded xtts_v2")
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
            output_wavfile=str(self.audio_path)
        )
        self.synthesizing_audio = False
        print("audio file completed")
    
    def feed_to_stream(self):
        self.loading_data = True
        f = thread_pool_executor.submit(self._feed_to_stream)
    
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
            time.sleep(0.01)

        with self.audio_path.open("rb") as f:
            chunk = f.read(1024)
        total_read = len(chunk)
        yield chunk
        while self.synthesizing_audio or chunk:
            with self.audio_path.open("rb") as f:
                f.seek(total_read)
                chunk = f.read(4024)
                if not chunk:
                    time.sleep(0.001)
                    continue
                total_read += len(chunk)
                print("total_read", total_read)
                yield chunk
                