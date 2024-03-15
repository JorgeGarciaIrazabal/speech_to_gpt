import functools
from speech_to_gpt.constants import photos_path
from transformers import AutoModelForCausalLM, CodeGenTokenizerFast as Tokenizer
from PIL import Image
from ollama import AsyncClient

promt = "Only if it is very clear that the main person in the image is pointing to something, describe that thing. Otherwise, describe what is the sentiment of the person"
MODEL = "llava:7b-v1.5-q3_K_S"

@functools.lru_cache(maxsize=1)
def _init_model():
    print("initializing moondream1")
    model_id = "vikhyatk/moondream1"
    model = AutoModelForCausalLM.from_pretrained(model_id, trust_remote_code=True)
    tokenizer = Tokenizer.from_pretrained(model_id)
    print("model loaded moondream1")
    return model, tokenizer


async def describe_context():
    # get latest photo from photos_path
    photo_files = sorted(photos_path.glob("photo_*.png"), key=lambda x: x.stat().st_mtime)
    photo_path = photo_files[-1]
    response = await AsyncClient().generate(model=MODEL, prompt=promt, images=[str(photo_path.absolute())])
    print(response["response"])

    return response
    

if __name__ == "__main__":
    describe_context()