from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os, uuid

from scenes import generate_scenes
from images import generate_image
from voice import generate_voice
from video import make_movie

app = FastAPI()

# Allow your frontend (on Vercel) to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # we'll restrict this later to your actual frontend URL
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("outputs", exist_ok=True)
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

# in-memory job tracker (simple, fine for a portfolio demo)
jobs = {}

class StoryRequest(BaseModel):
    story: str
    genre: str = "thriller"

def run_pipeline(job_id: str, story: str, genre: str):
    try:
        jobs[job_id]["status"] = "analyzing"
        data = generate_scenes(story, genre)
        jobs[job_id]["title"] = data["title"]
        jobs[job_id]["scenes"] = data["scenes"]

        image_paths = []
        audio_paths = []

        jobs[job_id]["status"] = "generating_assets"
        for i, scene in enumerate(data["scenes"]):
            jobs[job_id]["progress"] = f"Scene {i+1}/{len(data['scenes'])}: image"
            img = generate_image(scene["image_prompt"], f"{job_id}_scene_{scene['num']}")
            image_paths.append(img)

            jobs[job_id]["progress"] = f"Scene {i+1}/{len(data['scenes'])}: voice"
            audio = generate_voice(scene["narration"], f"{job_id}_scene_{scene['num']}")
            audio_paths.append(audio)

        jobs[job_id]["status"] = "assembling"
        movie_path = make_movie(data["scenes"], image_paths, audio_paths, f"{job_id}_movie.mp4")

        jobs[job_id]["status"] = "done"
        jobs[job_id]["movie_url"] = f"/outputs/{job_id}_movie.mp4"

    except Exception as e:
        jobs[job_id]["status"] = "error"
        jobs[job_id]["error"] = str(e)

@app.post("/generate")
def generate(req: StoryRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())[:8]
    jobs[job_id] = {"status": "queued"}
    background_tasks.add_task(run_pipeline, job_id, req.story, req.genre)
    return {"job_id": job_id}

@app.get("/status/{job_id}")
def status(job_id: str):
    return jobs.get(job_id, {"status": "not_found"})

@app.get("/")
def root():
    return {"message": "CineAI Studio API is running"}