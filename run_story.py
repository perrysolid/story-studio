import argparse
from pathlib import Path
import sys

# allow importing from apps/api
sys.path.append(str(Path(__file__).parent / 'apps' / 'api'))

from pipeline import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a narrated story video from a prompt")
    parser.add_argument('prompt', help='Story idea to expand into scenes')
    parser.add_argument('--voice-id', default=None, help='ElevenLabs voice id')
    parser.add_argument('--style', default='cinematic soft light', help='Image style prompt suffix')
    parser.add_argument('--out', default='output', help='Directory to store generated files')
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_pipeline(args.prompt, args.voice_id, args.style, out_dir)
    print(f"Video written to {out_dir / 'final.mp4'}")


if __name__ == '__main__':
    main()
