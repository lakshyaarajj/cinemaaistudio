import edge_tts
import asyncio

def generate_voice(text, filename):
    print(f"Generating voice: {filename}...")
    try:
        path = f"outputs/{filename}.mp3"
        asyncio.run(_generate(text, path))
        print(f"Saved: {path}")
        return path
    except Exception as e:
        print(f"Failed: {e}")
        return None

async def _generate(text, path):
    voice = "en-US-AriaNeural"  # natural-sounding free voice
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(path)
