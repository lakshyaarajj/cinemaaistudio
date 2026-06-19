from gtts import gTTS

def generate_voice(text, filename):
    print(f"Generating voice: {filename}...")
    try:
        tts = gTTS(text=text, lang='en')
        path = f"outputs/{filename}.mp3"
        tts.save(path)
        print(f"Saved: {path}")
        return path
    except Exception as e:
        print(f"Failed: {e}")
        return None