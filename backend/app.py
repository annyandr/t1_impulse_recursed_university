from flask import Flask, request, jsonify, make_response, render_template
from flask_socketio import SocketIO
import os
template_dir = os.path.abspath('../frontend')


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)


@app.route('/', methods=['GET'])
def chat():
    return render_template('main.html')


@socketio.on('connect')
def handle_connect():
    print('Client connected')


@socketio.on('message')
def handle_message(data):
    print('Received message:', data)
    socketio.emit('response', 'Server received your message: ' + data)


if __name__ == '__main__':
    socketio.run(app, debug=True)
