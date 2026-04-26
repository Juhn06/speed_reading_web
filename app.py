from pathlib import Path
import os
import sys

PROJECT_ROOT = Path(__file__).resolve().parent
BACKEND_DIR = PROJECT_ROOT / 'backend'

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from server import create_app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
