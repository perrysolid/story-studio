import os, io, json, time, base64, tempfile
from pathlib import Path

import streamlit as st
import requests
from PIL import Image, ImageDraw
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

ELEVENLABS_API_KEY = "sk_2b7788ba2746749a23b2f455a17636a4242c2806db65a103"


# ---- Streamlit must be configured first ----
st.set_page_config(page_title="One-Click Story Studio", page_icon="🎬", layout="centered")
st.title("🎬 One-Click Story Studio")
st.caption("Prompt → Emotional Story → TTS → Images → Video (Streamlit Edition)")

# ---- Secrets/env (NO hardcoding) ----
ELEVEN = st.secrets.get("ELEVENLABS_API_KEY") or os.getenv("ELEVENLABS_API_KEY") or ""
STABILITY_KEY = st.secrets.get("STABILITY_API_KEY") or os.getenv("STABILITY_API_KEY") or ""
STABILITY_ENGINE = "stable-diffusion-xl-1024-v1-0"

def build_scene_plan(user_prompt: str):
    scenes = [
        dict(id=1, prompt=f"{user_prompt}, warm sunset kitchen, soft rim light",
             narration="She found the letter beneath the sugar jar and felt the day pause.", duration_sec=5),
        dict(id=2, prompt=f"{user_prompt}, close-up of paper, gentle dust motes in sunbeam",
             narration="The words were uneven but honest, stitched with small courage.", duration_sec=5),
        dict(id=3, prompt=f"{user_prompt}, quiet street, amber hour, long shadows",
             narration="Outside, the amber light held her together like careful hands.", duration_sec=5),
        dict(id=4, prompt=f"{user_prompt}, park bench under trees, breeze, distant laughter",
             narration="She practiced forgiveness like a melody she almost remembered.", duration_sec=5),
        dict(id=5, prompt=f"{user_prompt}, soft embrace at sunset, silhouettes, hopeful horizon",
             narration="When they finally met, the sky kept their secret and exhaled tomorrow.", duration_sec=6),
    ]
    return dict(title="Sunset Promise", summary="Tender vignette at dusk.", scenes=scenes)

def generate_image_bytes(prompt: str) -> bytes:
    if STABILITY_KEY:
        url = f"https://api.stability.ai/v1/generation/{STABILITY_ENGINE}/text-to-image"
        headers = {"Authorization": f"Bearer {STABILITY_KEY}", "Content-Type": "application/json"}
        payload = {"text_prompts": [{"text": prompt}], "width": 1024, "height": 576, "cfg_scale": 7, "samples": 1, "steps": 30}
        r = requests.post(url, headers=headers, json=payload, timeout=60); r.raise_for_status()
        return base64.b64decode(r.json()["artifacts"][0]["base64"])
    # Placeholder if no Stability key
    from PIL import Image
    img = Image.new("RGB", (1024, 576), (180, 180, 180))
    d = ImageDraw.Draw(img); d.text((20,20), "Image Placeholder", fill=(30,30,30))
    bio = io.BytesIO(); img.save(bio, format="PNG"); return bio.getvalue()

def tts_bytes(text: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM") -> bytes:
    if not ELEVEN: 
        return b""
    headers = {"xi-api-key": ELEVEN, "Accept": "audio/mpeg", "Content-Type": "application/json"}
    payload = {"text": text, "voice_settings": {"stability": 0.6, "similarity_boost": 0.8}}
    r = requests.post(f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}", headers=headers, json=payload, timeout=60)
    r.raise_for_status(); return r.content

def compose_video(scenes, image_paths, audio_paths, out_path: Path):
    clips = []
    for scene, img_p, aud_p in zip(scenes, image_paths, audio_paths):
        dur = float(scene.get("duration_sec", 5))
        ic = ImageClip(str(img_p)).set_duration(dur)
        if aud_p.exists() and aud_p.stat().st_size > 0:
            ic = ic.set_audio(AudioFileClip(str(aud_p)))
        clips.append(ic)
    video = concatenate_videoclips(clips, method="compose")
    video.write_videofile(str(out_path), fps=24, codec="libx264", audio_codec="aac", verbose=False, logger=None)

with st.form("prompt_form"):
    user_prompt = st.text_area("Your story idea", placeholder="A letter found at golden hour, forgiveness, healing", height=120)
    col1, col2 = st.columns(2)
    with col1: voice = st.text_input("ElevenLabs Voice ID", value="21m00Tcm4TlvDq8ikWAM")
    with col2: _hires = st.checkbox("High quality images (needs Stability key)", value=True)
    submitted = st.form_submit_button("Create Story Video")

progress = st.progress(0, text="Idle")
status = st.empty()

if submitted and user_prompt.strip():
    try:
        t0 = time.time()
        progress.progress(5, text="Planning story"); status.write("Building scene plan…")
        plan = build_scene_plan(user_prompt); scenes = plan["scenes"]

        tmpdir = Path(tempfile.mkdtemp(prefix="story_"))
        img_dir = tmpdir / "images"; img_dir.mkdir(parents=True, exist_ok=True)
        aud_dir = tmpdir / "audio"; aud_dir.mkdir(parents=True, exist_ok=True)
        out_mp4 = tmpdir / "final.mp4"

        status.write("Generating images…"); n = len(scenes)
        for i, sc in enumerate(scenes, 1):
            (img_dir / f"scene_{i}.png").write_bytes(generate_image_bytes(sc["prompt"]))
            progress.progress(5 + int(45 * (i / n)), text=f"Images {i}/{n}")

        status.write("Generating narration…"); audio_paths = []
        for i, sc in enumerate(scenes, 1):
            p = aud_dir / f"s{i}.mp3"; p.write_bytes(tts_bytes(sc["narration"], voice)); audio_paths.append(p)
            progress.progress(50 + int(30 * (i / n)), text=f"Narration {i}/{n}")

        status.write("Composing video…")
        image_paths = [img_dir / f"scene_{i}.png" for i in range(1, n+1)]
        compose_video(scenes, image_paths, audio_paths, out_mp4)
        progress.progress(100, text="Done")

        st.success("Video ready!")
        st.video(str(out_mp4))
        st.download_button("Download MP4", out_mp4.read_bytes(), file_name="story.mp4", mime="video/mp4")
        st.caption(f"Total time: {int(time.time()-t0)}s")
    except Exception as e:
        st.error(f"Failed: {e}")
        st.stop()
