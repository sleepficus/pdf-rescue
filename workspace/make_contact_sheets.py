#!/usr/bin/env python3
"""Create labeled source/candidate contact sheets for human render review."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageOps


def make_sheet(source_paths: list[Path], candidate_paths: list[Path], output: Path) -> None:
    pairs = list(zip(source_paths, candidate_paths))
    thumb_size = (510, 660)
    label_height = 36
    gap = 18
    sheet = Image.new("RGB", (thumb_size[0] * 2 + gap * 3,
                              len(pairs) * (thumb_size[1] + label_height + gap) + gap), "white")
    draw = ImageDraw.Draw(sheet)
    for row, (source, candidate) in enumerate(pairs):
        top = gap + row * (thumb_size[1] + label_height + gap)
        for col, (path, role) in enumerate(((source, "SOURCE"), (candidate, "CANDIDATE"))):
            with Image.open(path) as image:
                rendered = ImageOps.contain(image.convert("RGB"), thumb_size)
            left = gap + col * (thumb_size[0] + gap)
            draw.rectangle((left, top, left + thumb_size[0], top + thumb_size[1]), outline="#777777", width=2)
            sheet.paste(rendered, (left + (thumb_size[0] - rendered.width) // 2, top))
            draw.text((left, top + thumb_size[1] + 8), f"{role} — {path.name}", fill="black")
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, optimize=True)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    source_root = root / "outputs/renders/source"
    candidate_root = root / "outputs/renders/candidate"
    contact_root = root / "outputs/renders/contact-sheets"
    for doc_id in [f"F{i:02d}" for i in range(1, 9)]:
        sources = sorted(source_root.glob(f"{doc_id}-*-*.png"))
        candidates = sorted(candidate_root.glob(f"{doc_id}-*-candidate-*.png"))
        if not sources or len(sources) != len(candidates):
            raise RuntimeError(f"render pairing failed for {doc_id}: {len(sources)} vs {len(candidates)}")
        make_sheet(sources, candidates, contact_root / f"{doc_id}-source-vs-candidate.png")


if __name__ == "__main__":
    main()
