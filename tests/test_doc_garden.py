import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_doc_garden_passes():
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "doc_garden.py")],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "consistente" in result.stdout.lower() or "OK" in result.stdout