import os, requests, base64
from pathlib import Path
from typing import Dict, List

A1111 = os.getenv("A1111_URL", "http://127.0.0.1:7860")
PROMPT_SUFFIX = ", high detail, cinematic composition, soft rim light, 35mm, shallow depth of field"

def generate_images(plan: Dict, out_dir: Path, style: str) -> List[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: List[Path] = []
    for i, scene in enumerate(plan["scenes"], 1):
        positive = f"{scene['prompt']}, {style}{PROMPT_SUFFIX}"
        payload = {
            "prompt": positive,
            "steps": 24,
            "width": 768,
            "height": 512,
            "sampler_name": "DPM++ 2M Karras"
        }
        try:
            r = requests.post(f"{A1111}/sdapi/v1/txt2img", json=payload, timeout=120)
            r.raise_for_status()
            img_b64 = r.json()["images"][0]
            img_bytes = base64.b64decode(img_b64)
        except Exception:
            # fallback to placeholder gray image if SD not available
            from PIL import Image
            import io
            img = Image.new("RGB", (768, 512), (180, 180, 180))
            bio = io.BytesIO()
            img.save(bio, format="PNG")
            img_bytes = bio.getvalue()

        p = out_dir / f"scene_{i}.png"
        with open(p, "wb") as f:
            f.write(img_bytes)
        paths.append(p)
    return paths
