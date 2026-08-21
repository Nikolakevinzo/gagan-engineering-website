import sys
from pathlib import Path

# Add backend directory to sys.path so imports resolve
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR / "backend"))

from server import app
