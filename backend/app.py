from flask import Flask, request, jsonify, make_response, render_template
from flask_socketio import SocketIO
import os
import base64

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

@socketio.on('file')
def handle_file(data):
    # Получаем имя и данные файла
    file_name = data['name']
    file_data = data['data']

    # Сохраняем файл
    file_path = os.path.join('uploads', file_name)
    with open(file_path, 'wb') as f:
        file_content = base64.b64decode(file_data.split(',')[1])  # Декодируем base64
        f.write(file_content)

    print(f"File {file_name} saved successfully!")
    socketio.emit('response', f"File {file_name} uploaded successfully.")

if __name__ == '__main__':
    socketio.run(app, debug=True)

