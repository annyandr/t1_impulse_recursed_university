from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import base64
from backend.parsers import db_parser, site_parser, table_parser

template_dir = os.path.abspath('templates')
upload_dir = os.path.abspath('uploads')

app = Flask(__name__, template_folder=template_dir)
app.config['SECRET_KEY'] = '3hgv3y345y44428454098nbvc513vvnbv3fg7fdakaa'

socketio = SocketIO(app)

if not os.path.exists(upload_dir):
    os.makedirs(upload_dir)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/main', methods=['GET'])
def chatbot():
    return render_template('main.html')

@app.route('/main/settings', methods=['POST'])
def chatbotsettings():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        model = data.get('model')
        chunking = data.get('chunking')

        if not model or not chunking:
            return jsonify({"error": "Missing 'model' or 'chunking' parameter"}), 400

        return jsonify({"message": f"Model: {model}, Chunking: {chunking} received successfully!"})

    except Exception as e:
        app.logger.error(f"Error in /main/settings: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('message')
def handle_message(data):
    print('Received message:', data)
    socketio.emit('response', 'Server received your message: ' + data)

@socketio.on('file')
def handle_file(data):
    file_name = data['name']
    file_data = data['data']

    file_path = os.path.join(upload_dir, file_name)
    with open(file_path, 'wb') as f:
        file_content = base64.b64decode(file_data.split(',')[1])
        f.write(file_content)

    print(f"File {file_name} saved successfully!")
    socketio.emit('response', f"File {file_name} uploaded successfully.")

class FileCreatedHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            file_path = event.src_path
            print(f"New file detected: {file_path}")
            try:
                process_files(upload_dir)
                print(f"File {file_path} processed successfully.")
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")

def process_files(input_dir):
    for file_name in os.listdir(input_dir):
        file_path = os.path.join(input_dir, file_name)
        if not os.path.isfile(file_path):
            continue

        _, ext = os.path.splitext(file_name)
        ext = ext.lower()

        try:
            if ext in {'.csv', '.xls', '.xlsx'}:
                print(f"Processing table file: {file_name}")
                table_parser.table_file_to_json(file_path, output_filepath=os.path.join(input_dir, f"{file_name}.json"))

            elif ext in {'.html', '.htm'}:
                print(f"Processing site file: {file_name}")
                site_parser.site_parser(file_path, out_file=os.path.join(input_dir, f"{file_name}.txt"))

            elif ext in {'.db', '.sqlite'}:
                print(f"Processing database file: {file_name}")
                db_parser.db_parser_function(file_path, output_filepath=os.path.join(input_dir, f"{file_name}.json"))

            else:
                print(f"Skipping unsupported file type: {file_name}")

        except Exception as e:
            print(f"Error processing file {file_name}: {e}")

def start_file_watcher():
    event_handler = FileCreatedHandler()
    observer = Observer()
    observer.schedule(event_handler, path=upload_dir, recursive=False)
    observer.start()
    print("Started watching for new files in 'uploads' folder.")
    return observer

if __name__ == '__main__':
    observer = start_file_watcher()

    try:
        socketio.run(app, debug=True)
    except KeyboardInterrupt:
        print("Shutting down file watcher...")
        observer.stop()
    observer.join()
