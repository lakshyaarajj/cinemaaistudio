from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")


client = InferenceClient(
    provider="auto",
    api_key=HF_TOKEN
)

def generate_image(prompt, filename):
    print(f"Generating image: {filename}...")
    try:
        image = client.text_to_image(
            prompt,
            model="black-forest-labs/FLUX.1-schnell"
        )
        path = f"outputs/{filename}.png"
        image.save(path)
        print(f"Saved: {path}")
        return path
    except Exception as e:
        print(f"Failed: {e}")
        return None