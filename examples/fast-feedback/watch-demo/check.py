"""Exit 1 if notes.txt does not hold the expected total."""
import sys
from pathlib import Path

EXPECTED = "2120"

text = Path("notes.txt").read_text().strip()
found = text.removeprefix("total:").strip()
if found != EXPECTED:
    print(f"notes.txt: found {found}, expected {EXPECTED}")
    sys.exit(1)
