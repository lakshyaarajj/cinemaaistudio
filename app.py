from scenes import generate_scenes
from images import generate_image
from voice import generate_voice
from video import make_movie
import os

os.makedirs("outputs", exist_ok=True)

print("=" * 50)
print("CINEAI STUDIO")
print("=" * 50)

story = input("\nEnter your story: ")
genre = input("Genre (thriller/drama/sci-fi/action/romance): ")

print("\n[1/4] Analyzing story and generating scenes...")
data = generate_scenes(story, genre)
print(f"Title: {data['title']}")
print(f"Characters: {', '.join(data['characters'])}")
print(f"Scenes: {len(data['scenes'])}")

image_paths = []
audio_paths = []

print("\n[2/4] Generating images and voiceovers for each scene...")
for scene in data['scenes']:
    print(f"\n  Scene {scene['num']}: {scene['title']}")
    
    img = generate_image(scene['image_prompt'], f"scene_{scene['num']}")
    image_paths.append(img)
    
    audio = generate_voice(scene['narration'], f"scene_{scene['num']}")
    audio_paths.append(audio)

print("\n[3/4] Assembling final movie...")
movie_path = make_movie(data['scenes'], image_paths, audio_paths, "final_movie.mp4")

print("\n[4/4] Done!")
print("=" * 50)
if movie_path:
    print(f"Your movie is ready: {movie_path}")
else:
    print("Movie assembly failed - check errors above")
print("=" * 50)