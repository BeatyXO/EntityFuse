from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
FINAL = "--final" in sys.argv
errors = []

required = [
    "README.md", "SUBMISSION.md", "DEPLOYMENT.md",
    "contracts/entity_fuse.py", "contracts/entity_gate.py",
    "docs/ARCHITECTURE.md", "docs/INVARIANTS.md", "docs/THREAT_MODEL.md",
    "tests/test_protocol_model.py", "fixtures/source_manifest.json",
]
for rel in required:
    if not (ROOT / rel).exists():
        errors.append(f"missing required file: {rel}")

for banned in ["node_modules", ".next", "dist", "build", "venv", ".venv"]:
    if (ROOT / banned).exists():
        errors.append(f"banned generated/frontend directory present: {banned}")

for ext in ("*.tsx", "*.jsx", "*.vue", "*.svelte"):
    if list(ROOT.rglob(ext)):
        errors.append(f"frontend artifact present: {ext}")

for contract in [ROOT/"contracts/entity_fuse.py", ROOT/"contracts/entity_gate.py"]:
    if contract.exists():
        first = contract.read_text(encoding="utf-8").splitlines()[0]
        if "py-genlayer:" not in first:
            errors.append(f"missing pinned py-genlayer header: {contract.name}")

readme = (ROOT/"README.md").read_text(encoding="utf-8") if (ROOT/"README.md").exists() else ""
if "61999" not in readme or "https://studio.genlayer.com/api" not in readme:
    errors.append("stable Studionet chain/RPC missing from README")

manifest = (ROOT/"fixtures/source_manifest.json").read_text(encoding="utf-8") if (ROOT/"fixtures/source_manifest.json").exists() else ""
if FINAL and "FIXTURE_COMMIT_PLACEHOLDER" in manifest:
    errors.append("fixture commit is not pinned")

if FINAL:
    deployment = (ROOT/"DEPLOYMENT.md").read_text(encoding="utf-8")
    if "No deployment is claimed in this handoff." in deployment:
        errors.append("DEPLOYMENT.md still contains handoff text instead of real final evidence")

try:
    subprocess.run([sys.executable, "-m", "compileall", "-q", str(ROOT/"scripts"), str(ROOT/"tests")], check=True)
except subprocess.CalledProcessError:
    errors.append("Python compilation failed")

if errors:
    print("PREFLIGHT FAILED")
    for e in errors:
        print(f"- {e}")
    raise SystemExit(1)

print("PREFLIGHT PASSED" + (" (final)" if FINAL else ""))
