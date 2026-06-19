from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, TextClip, CompositeVideoClip

def make_movie(scenes_data, image_paths, audio_paths, output_name="movie.mp4"):
    clips = []

    for i, scene in enumerate(scenes_data):
        img_path = image_paths[i]
        audio_path = audio_paths[i]

        if not img_path or not audio_path:
            print(f"Skipping scene {i+1} - missing image or audio")
            continue

        audio = AudioFileClip(audio_path)
        image = ImageClip(img_path, duration=audio.duration)
        image = image.resized((1280, 720))
        image = image.with_audio(audio)

        clips.append(image)

    if not clips:
        print("No clips to assemble!")
        return None

    final = concatenate_videoclips(clips, method="compose")
    output_path = f"outputs/{output_name}"
    final.write_videofile(output_path, fps=24)
    print(f"Movie saved: {output_path}")
    return output_path