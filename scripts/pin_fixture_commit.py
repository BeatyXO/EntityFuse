from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "fixtures" / "source_manifest.json"

if len(sys.argv) != 2 or not re.fullmatch(r"[0-9a-fA-F]{40}", sys.argv[1]):
    raise SystemExit("usage: python scripts/pin_fixture_commit.py <40-char-commit-sha>")

sha = sys.argv[1].lower()
text = MANIFEST.read_text(encoding="utf-8")
text = re.sub(r"[0-9a-f]{40}|FIXTURE_COMMIT_PLACEHOLDER", sha, text)
MANIFEST.write_text(text, encoding="utf-8")
print(f"pinned fixtures to {sha}")
