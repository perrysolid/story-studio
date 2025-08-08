import os, requests
from pathlib import Path
from typing import Dict, List

ELEVEN = os.getenv("ELEVENLABS_API_KEY")
BASE = "https://api.elevenlabs.io/v1"

def synthesize_segments(plan: Dict, out_dir: Path, voice_id: str | None) -> List[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    voice = voice_id or "21m00Tcm4TlvDq8ikWAM"  # Example default voice
    paths: List[Path] = []

    if not ELEVEN:
        # Fallback: write empty silence files if no key (for quick demo without network)
        for i, scene in enumerate(plan["scenes"], 1):
            p = out_dir / f"s{i}.mp3"
            with open(p, "wb") as f:
                f.write(b"")  # placeholder
            paths.append(p)
        return paths

    for i, scene in enumerate(plan["scenes"], 1):
        text = scene["narration"]
        url = f"{BASE}/text-to-speech/{voice}"
        headers = {
            "xi-api-key": ELEVEN,
            "Accept": "audio/mpeg",
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "voice_settings": {"stability": 0.6, "similarity_boost": 0.8}
        }
        r = requests.post(url, headers=headers, json=payload, timeout=60)
        r.raise_for_status()
        p = out_dir / f"s{i}.mp3"
        with open(p, "wb") as f:
            f.write(r.content)
        paths.append(p)
    return paths
