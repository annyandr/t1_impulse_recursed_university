from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import os
import base64

template_dir = os.path.abspath('../frontend')
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Инициализация SocketIO
socketio = SocketIO(app)

model_tasks = []


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# Страница с настройками чата


@app.route('/main', methods=['GET'])
def chatbot():
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

# Обработчик входящих сообщений


@socketio.on('message')
def handle_message(data):
    print('Received message:', data)
    append_task(data)
    socketio.emit('response', 'Server received your message: ' + data)

# Обработчик загрузки файлов


@socketio.on('file')
def handle_file(data):
    # Получаем имя файла и его содержимое
    file_name = data['name']
    file_data = data['data']

    # Указываем путь для сохранения файла
    file_path = os.path.join('uploads', file_name)

    # Декодируем данные из base64 и сохраняем файл
    with open(file_path, 'wb') as f:
        file_content = base64.b64decode(
            file_data.split(',')[1])  # Декодируем base64
        f.write(file_content)

    print(f"File {file_name} saved successfully!")

    # Отправляем ответ клиенту
    socketio.emit('response', f"File {file_name} uploaded successfully.")


# Запуск приложения
if __name__ == '__main__':
    socketio.run(app, debug=True, host='192.168.182.31',
                 port=5000)
