import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask_cors import CORS
from api.main import create_app

app = create_app()

CORS(app, resources={r"/api/*": {"origins": "*"}})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
