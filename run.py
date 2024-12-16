#!/usr/bin/env python3
import os
from backend.app import app

if __name__ == '__main__':
    # Ensure we're in the correct directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Start the application
    from backend.config import Config
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
