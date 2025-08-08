from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from pathlib import Path
import uuid
from pipeline import run_pipeline

app = FastAPI()

class GenerateRequest(BaseModel):
    prompt: str
    voice_id: str | None = None
    style: str | None = "cinematic soft light"

class GenerateResponse(BaseModel):
    job_id: str

JOBS_DIR = Path("/outputs").absolute()
JOBS_DIR.mkdir(parents=True, exist_ok=True)

@app.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest, bg: BackgroundTasks):
    job_id = str(uuid.uuid4())
    job_path = JOBS_DIR / job_id
    job_path.mkdir(parents=True, exist_ok=True)
    bg.add_task(run_pipeline, req.prompt, req.voice_id, req.style, job_path)
    return GenerateResponse(job_id=job_id)

@app.get("/status/{job_id}")
def status(job_id: str):
    path = JOBS_DIR / job_id
    if not path.exists():
        return {"status": "not_found"}
    done = (path / "final.mp4").exists()
    return {"status": "done" if done else "running"}

@app.get("/result/{job_id}")
def result(job_id: str):
    path = JOBS_DIR / job_id / "final.mp4"
    if not path.exists():
        return {"error": "not_ready"}
    return {"video_path": f"/outputs/{job_id}/final.mp4"}
