"""Put the project root on sys.path so `import polarity` works when a script is
run directly as `python scripts/<name>.py` from anywhere."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
