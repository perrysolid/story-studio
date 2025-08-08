import json

SYSTEM = """You are a narrative designer. Produce a 5-scene, emotionally resonant story for a 60–90s video.
Use vivid imagery. Keep each scene narration 1–2 sentences.
Return strict JSON with keys: title, summary, scenes[]. scenes[] has id, prompt (for image gen), narration, duration_sec.
"""

TEMPLATE = """User prompt: {prompt}
Constraints: gentle pacing, wholesome tone, cinematic visuals, golden-hour light.
Output JSON only.
"""

def call_llm(system: str, user: str) -> str:
    # Stub deterministic sample for first run
    return json.dumps({
        "title": "Sunset Promise",
        "summary": "A tender vignette about forgiveness at dusk.",
        "music": {"track": "gentle_piano_1.mp3", "volume": -12},
        "scenes": [
            {"id": 1, "prompt": "warm sunset kitchen, soft rim light, handwritten letter on table",
             "narration": "Maya found the letter tucked beneath the sugar jar, her hands trembling at the edges of truth.",
             "duration_sec": 7},
            {"id": 2, "prompt": "close-up of letter, golden sunlight, dust motes",
             "narration": "The words were clumsy but honest, an apology written in the plain ink of ordinary love.",
             "duration_sec": 7},
            {"id": 3, "prompt": "quiet street, long shadows, slow walk",
             "narration": "She stepped outside, the street a hush of amber, and let the evening hold her together.",
             "duration_sec": 7},
            {"id": 4, "prompt": "park bench under trees, gentle breeze, distant laughter",
             "narration": "By the old bench, she rehearsed forgiveness like a song she once knew by heart.",
             "duration_sec": 7},
            {"id": 5, "prompt": "soft embrace at sunset, silhouettes, hopeful horizon",
             "narration": "When they finally met, the sky kept their secret, and the day exhaled into tomorrow.",
             "duration_sec": 8}
        ]
    })

def build_scene_plan(prompt: str):
    raw = call_llm(SYSTEM, TEMPLATE.format(prompt=prompt))
    return json.loads(raw)
