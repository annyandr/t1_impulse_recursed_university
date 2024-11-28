from flask import Flask, request, jsonify, make_response, render_template
from flask_socketio import SocketIO
from files_module.files_worker import save_to_txt
import os
import base64

template_dir = os.path.abspath('../frontend')
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

model_tasks = []


@app.route('/', methods=['GET'])
def chat():
    return render_template('main.html')


@app.route('/model_task', methods=['GET'])
def get_task():
    if model_tasks:
        return jsonify(model_tasks.pop()), 200

    return jsonify({'error': 'No tasks available'}), 404


@app.route('/task_completed/{task_id}', methods=['GET'])
def delete_task(task_id):
    try:
        model_tasks.remove(task_id)
        return jsonify({'message': 'Task deleted'}), 200
    except ValueError:
        return jsonify({'error': 'Task not found'}), 404


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
    save_to_txt(file_name, file_data)
    socketio.emit('response', f"File {file_name} uploaded successfully.")


if __name__ == '__main__':
    socketio.run(app, debug=True)
