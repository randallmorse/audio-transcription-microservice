
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import signal
import speech_recognition as sr
from pydub import AudioSegment
from pymongo import MongoClient
import gridfs
from bson import ObjectId
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = int(eval(os.getenv('MAX_CONTENT_LENGTH', '16 * 1024 * 1024')))  # Default to 16 MB
PROCESSING_TIMEOUT = int(os.getenv('PROCESSING_TIMEOUT', '30'))  # Default to 30 seconds

# MongoDB setup
mongo_host = os.getenv('MONGO_HOST')
mongo_user = os.getenv('MONGO_USER')
mongo_pass = os.getenv('MONGO_PASS')
client = MongoClient(mongo_host, username=mongo_user, password=mongo_pass)
db = client.transcriptions_db
fs = gridfs.GridFS(db)
transcriptions_collection = db.transcriptions

def transcribe_audio(file_path):
    recognizer = sr.Recognizer()
    audio_file = sr.AudioFile(file_path)
    with audio_file as source:
        audio_data = recognizer.record(source)
    return recognizer.recognize_google(audio_data)

def timeout_handler(signum, frame):
    raise TimeoutError("Processing time exceeded the limit")

@app.route('/upload', methods=['POST'])
def upload_file():
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(PROCESSING_TIMEOUT)
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        # Optional name field from the form
        name = request.form.get('name', 'Unknown')

        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Convert to WAV if necessary
            if not filename.lower().endswith('.wav'):
                audio = AudioSegment.from_file(file_path)
                wav_path = os.path.splitext(file_path)[0] + '.wav'
                audio.export(wav_path, format='wav')
                file_path = wav_path

            # Store the file in GridFS
            with open(file_path, 'rb') as f:
                grid_fs_file_id = fs.put(f, filename=filename)

            try:
                text = transcribe_audio(file_path)
                transcription = {
                    'name': name,
                    'filename': filename,
                    'grid_fs_file_id': str(grid_fs_file_id),
                    'text': text
                }
                result = transcriptions_collection.insert_one(transcription)
                return jsonify({'filename': filename, 'transcription': text, 'id': str(result.inserted_id)}), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        signal.alarm(0)  # Disable the alarm
    except TimeoutError:
        return jsonify({'error': 'Processing time exceeded the limit'}), 500

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
