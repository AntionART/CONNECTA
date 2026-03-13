"""
Application Entry Point
========================
Development Environment: Starts the Flask app with SocketIO support.
MVP Integration: Single command to run the entire CRM application.
Debugging: debug=True enables auto-reload and detailed error pages.
"""
from app import create_app
from app.extensions import socketio

# Professional Output: Creates the app using the factory pattern
app = create_app()

if __name__ == '__main__':
    # Dynamic Input: Host and port configurable; 0.0.0.0 allows Docker access
    # Debugging: debug=True enables Flask debugger and hot-reload
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
