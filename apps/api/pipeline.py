import os
from pathlib import Path
from typing import List, Dict
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, CompositeAudioClip
from story import build_scene_plan
from tts import synthesize_segments
from images import generate_images

def run_pipeline(prompt: str, voice_id: str | None, style: str, job_dir: Path):
    plan = build_scene_plan(prompt)

    images = generate_images(plan, job_dir / "images", style)
    audio_segments = synthesize_segments(plan, job_dir / "audio", voice_id)
    make_video(plan, images, audio_segments, job_dir)

def make_video(plan: Dict, images: List[Path], audio_paths: List[Path], job_dir: Path):
    clips = []
    for scene, img, audio in zip(plan["scenes"], images, audio_paths):
        dur = float(scene.get("duration_sec", 6))
        ic = ImageClip(str(img)).set_duration(dur)
        ac = AudioFileClip(str(audio))
        # Optionally align durations: ic = ic.set_duration(ac.duration)
        ic = ic.set_audio(ac)
        clips.append(ic)

    video = concatenate_videoclips(clips, method="compose")

    if plan.get("music"):
        music_path = Path("assets/music") / plan["music"]["track"]
        if music_path.exists():
            music = AudioFileClip(str(music_path)).volumex(0.3)
            video_audio = CompositeAudioClip([video.audio, music])
            video = video.set_audio(video_audio)

    out = job_dir / "final.mp4"
    video.write_videofile(str(out), fps=24, codec="libx264", audio_codec="aac")
