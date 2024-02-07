from datetime import datetime
import functools
from pathlib import Path
from tempfile import TemporaryDirectory

from ollama import AsyncClient
from speech_to_gpt.constants import photos_path
from transformers import AutoModelForCausalLM, CodeGenTokenizerFast as Tokenizer
from PIL import Image
import ollama


def _copy_last_4_photos(temp_folder: Path):
    photo_files = sorted(photos_path.glob("photo_*.png"), key=lambda x: x.stat().st_mtime)
    for photo_file in photo_files[-2:]:
        # copy photo in temp folder
        temp_photo = temp_folder / photo_file.name
        temp_photo.write_bytes(photo_file.read_bytes())


def _concat_pictures_into_one(temp_folder):
    _copy_last_4_photos(Path(temp_folder))
    # combine photos into one
    combined_photo = Path(temp_folder) / "concat.png"
    images = [Image.open(photo) for photo in Path(temp_folder).glob("photo_*.png")]
    widths, heights = zip(*(i.size for i in images))

    total_width = sum(widths)
    max_height = max(heights)

    new_im = Image.new('RGB', (total_width, max_height))

    x_offset = 0
    for im in images:
        new_im.paste(im, (x_offset, 0))
        x_offset += im.size[0]

    new_im.save(combined_photo)
    return combined_photo


@functools.lru_cache(maxsize=1)
def _init_model():
    print("initializing moondream1")
    model_id = "vikhyatk/moondream1"
    model = AutoModelForCausalLM.from_pretrained(model_id, trust_remote_code=True)
    tokenizer = Tokenizer.from_pretrained(model_id)
    print("model loaded moondream1")
    return model, tokenizer


async def describe_context():
    with TemporaryDirectory() as temp_folder:
        combined_photo_path = _concat_pictures_into_one(temp_folder)

        # get the text
        question = """Given the information that the 2 images are taken 2 seconds apart and are of the same person,
Tell me how the person is feeling. Only tell me the emotions that are visible in the images."""
        response = await AsyncClient().generate(model="llava", prompt=question, images=[combined_photo_path])

        print(response["response"])
        return response["response"]
