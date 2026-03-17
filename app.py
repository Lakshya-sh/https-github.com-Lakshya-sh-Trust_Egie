from flask import Flask, render_template_string, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import secrets
import time
from models import SessionManager

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

sessions = SessionManager()  # In-memory only — destroyed on shutdown

@app.route('/')
def index():
    return render_template_string(open('../frontend/index.html').read())

# ==================== ANONYMOUS SESSION ====================
@socketio.on('connect')
def handle_connect():
    temp_id = secrets.token_hex(16)
    sessions.create_session(temp_id, request.sid)
    emit('your_id', {'id': temp_id})

@socketio.on('disconnect')
def handle_disconnect():
    sessions.destroy_session(request.sid)  # ID auto-destroyed

# ==================== SIGNALING (WebRTC + Messages) ====================
@socketio.on('offer')
def handle_offer(data):
    emit('offer', data, to=data['target'], include_self=False)

@socketio.on('answer')
def handle_answer(data):
    emit('answer', data, to=data['target'], include_self=False)

@socketio.on('ice-candidate')
def handle_ice(data):
    emit('ice-candidate', data, to=data['target'], include_self=False)

@socketio.on('message')
def handle_message(data):
    # Server ONLY relays ciphertext — never sees plaintext
    emit('message', data, to=data['target'], include_self=False)

@socketio.on('typing')
def handle_typing(data):
    emit('typing', {'from': data['from']}, to=data['target'], include_self=False)

socketio.run(app, host='0.0.0.0', port=5000, debug=False)