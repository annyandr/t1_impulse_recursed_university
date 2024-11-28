from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import os
import base64

# Указываем папку с шаблонами
template_dir = os.path.abspath('templates')
app = Flask(__name__, template_folder=template_dir)
app.config['SECRET_KEY'] = 'your_secret_key'

# Инициализация SocketIO
socketio = SocketIO(app)

# Главная страница, которая будет отображать index.html
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# Страница с настройками чата
@app.route('/main', methods=['GET'])
def chatbot():
    return render_template('main.html')

# Обработчик POST-запроса для отправки параметров
@app.route('/main/settings', methods=['POST'])
def chatbotsettings():
    try:
        # Получаем данные из JSON-запроса
        data = request.get_json()

        # Проверяем, что данные получены
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Извлекаем параметры
        model = data.get('model')
        chunking = data.get('chunking')

        # Проверяем, что параметры существуют и корректны
        if not model or not chunking:
            return jsonify({"error": "Missing 'model' or 'chunking' parameter"}), 400

        # Если параметры корректны, возвращаем подтверждение
        return jsonify({"message": f"Model: {model}, Chunking: {chunking} received successfully!"})

    except Exception as e:
        # Логирование и обработка неожиданной ошибки
        app.logger.error(f"Error in /main/settings: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500

# Обработчик события подключения клиента
@socketio.on('connect')
def handle_connect():
    print('Client connected')

# Обработчик входящих сообщений
@socketio.on('message')
def handle_message(data):
    print('Received message:', data)
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
        file_content = base64.b64decode(file_data.split(',')[1])  # Декодируем base64
        f.write(file_content)

    print(f"File {file_name} saved successfully!")

    # Отправляем ответ клиенту
    socketio.emit('response', f"File {file_name} uploaded successfully.")

# Запуск приложения
if __name__ == '__main__':
    socketio.run(app, debug=True)
