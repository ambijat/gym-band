#!/usr/bin/env python3
"""Generate videos.json for the Band Training PWA/TWA.

Default source expected by the user:
  /media/ambijat/FIGHTER/ANDROIDWORKS/gym-band

Recommended layout after generation:
  /media/ambijat/FIGHTER/ANDROIDWORKS/gym-band/
    index.html
    videos.json
    videos/<your .mp4/.webm/.mov files>

Usage:
  python3 tools/generate_video_index.py \
    --source /media/ambijat/FIGHTER/ANDROIDWORKS/gym-band/videos \
    --out videos.json

If your videos are already inside ./videos, run:
  python3 tools/generate_video_index.py --source videos --out videos.json
"""
from __future__ import annotations
import argparse, json, re
from pathlib import Path
from urllib.parse import quote

VIDEO_EXTS = {".mp4", ".webm", ".mov", ".m4v", ".avi", ".mkv"}
DEFAULT_VIDEO_BASE_URL = "https://ambijat.github.io/gym-band/videos"
GROUP_HINTS = [
    ("Adductors / Groin", ["adductor", "adductors", "groin"]),
    ("Shoulders / Posture", ["shoulder", "pull-apart", "pull apart", "posture", "face-pull", "face pull", "rotator"]),
    ("Back", ["row", "pulldown", "lat", "back"]),
    ("Chest", ["chest", "press", "fly", "push"]),
    ("Arms", ["curl", "bicep", "tricep", "extension"]),
    ("Legs", ["squat", "lunge", "leg", "glute", "hip", "hamstring", "calf", "quad", "quadriceps"]),
    ("Core / Stability", ["core", "abs", "pallof", "woodchop", "anti-rotation", "plank", "stability", "balance"]),
    ("Speed / Agility", ["speed", "agility", "quick"]),
    ("Mobility", ["mobility", "stretch", "warm", "rehab"]),
]

def title_from_path(path: Path) -> str:
    stem = re.sub(r"^\d+[_\-. ]*", "", path.stem)
    stem = re.sub(r"[_\-.]+", " ", stem).strip()
    stem = re.sub(r"(?<=[A-Za-z])(?=\d)", " ", stem)
    return re.sub(r"\s+", " ", stem).title() or path.stem

def infer_group(path: Path) -> str:
    hay = " ".join(part.lower() for part in path.parts)
    for group, hints in GROUP_HINTS:
        if any(h in hay for h in hints):
            return group
    parent = path.parent.name.strip()
    if parent and parent.lower() not in {"videos", "band-training", "band_training"}:
        return parent.replace("_", " ").replace("-", " ").title()
    return "General"

def video_url(prefix: str, rel: Path) -> str:
    rel_url = "/".join(quote(part) for part in rel.parts)
    if prefix.startswith(("http://", "https://")):
        return f"{prefix.rstrip('/')}/{rel_url}"
    return f"{prefix.rstrip('/')}/{rel_url}" if prefix else rel_url

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default="/media/ambijat/FIGHTER/ANDROIDWORKS/gym-band/videos", help="Directory containing exercise videos")
    ap.add_argument("--out", default="videos.json", help="Output JSON path, normally videos.json beside index.html")
    ap.add_argument("--prefix", default=DEFAULT_VIDEO_BASE_URL, help="URL prefix used by index.html for video files")
    args = ap.parse_args()

    source = Path(args.source).expanduser().resolve()
    if not source.exists():
        raise SystemExit(f"Source directory not found: {source}")

    rows = []
    for path in sorted(p for p in source.rglob("*") if p.is_file() and p.suffix.lower() in VIDEO_EXTS):
        rel = path.relative_to(source)
        rows.append({
            "title": title_from_path(path),
            "group": infer_group(rel),
            "file": video_url(args.prefix, rel),
        })

    out = Path(args.out)
    out.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(rows)} video entries to {out}")

if __name__ == "__main__":
    main()
