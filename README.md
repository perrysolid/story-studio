# One-Click Story Studio (Hackathon Starter)

End-to-end pipeline: prompt → story scenes → TTS → images → video (MP4).

## Quick Start (Local, no Docker)

### Prereqs
- Python 3.11+
- Node.js 18+ (or 20+)
- ffmpeg installed in PATH
- (Optional) AUTOMATIC1111 Stable Diffusion WebUI at http://127.0.0.1:7860

### 1) Backend
```
cd apps/api
python -m venv .venv && source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp ../../.env.example ../../.env   # or manually create .env at project root
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2) Frontend
```
cd ../../apps/web
npm install
npm run dev
```
Frontend runs at http://localhost:3000 and talks to http://localhost:8000

### 3) Environment
Create `.env` at project root with:
```
ELEVENLABS_API_KEY=YOUR_KEY
A1111_URL=http://127.0.0.1:7860
API_BASE=http://localhost:8000
FFMPEG_BIN=ffmpeg
```
Never commit real keys.

## With Docker
```
docker compose up --build
```
- Web: http://localhost:3000
- API: http://localhost:8000

## Demo Flow
1. Open frontend → enter a prompt → click Create
2. API runs pipeline (story JSON → images → TTS → compose)
3. Poll /status/{job_id} until done, then fetch /result/{job_id}
