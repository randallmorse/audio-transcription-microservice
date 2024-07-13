
# Audio Transcription Microservice

This project is a Flask-based microservice for transcribing audio files. It allows users to upload audio files, transcribe them to text, and store the results in a MongoDB database using GridFS for storing the audio files. The transcription results and metadata are then saved in the database.

## Features

- Upload audio files for transcription
- Transcribe audio to text using Google Web Speech API
- Store audio files in MongoDB GridFS
- Store transcription results and metadata in MongoDB
- Configurable processing timeout

## Requirements

- Python 3.9+
- MongoDB
- ffmpeg (for audio processing with `pydub`)

## Installation

1. Clone the repository:

   \`\`\`bash
   git clone https://github.com/randallmorse/audio-transcription-microservice.git
   cd audio-transcription-microservice
   \`\`\`

2. Create and activate a virtual environment:

   \`\`\`bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use \`venv\Scripts\activate\`
   \`\`\`

3. Install the required Python packages:

   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

4. Create a .env file in the project root directory and add the following environment variables:

   \`\`\`plaintext
   MONGO_HOST=mongodb://admin:secret@localhost:27017/
   MONGO_USER=admin
   MONGO_PASS=secret
   MAX_CONTENT_LENGTH=16 * 1024 * 1024  # 16 MB
   PROCESSING_TIMEOUT=30  # Timeout in seconds
   \`\`\`

## Running MongoDB with Docker

To run MongoDB in a Docker container with a persistent volume:

1. **Create a Docker volume**:

   \`\`\`bash
   docker volume create mongodb_data
   \`\`\`

2. **Run MongoDB container with authentication**:

   \`\`\`bash
   docker run -d -p 27017:27017 --name mongodb \
     -e MONGO_INITDB_ROOT_USERNAME=admin \
     -e MONGO_INITDB_ROOT_PASSWORD=secret \
     -v mongodb_data:/data/db \
     mongo
   \`\`\`

3. **Verify MongoDB is running**:

   \`\`\`bash
   mongo -u admin -p secret --authenticationDatabase admin
   \`\`\`

## Usage

1. Start the Flask application:

   \`\`\`bash
   python app.py
   \`\`\`

2. Use \`curl\` or a tool like Postman to upload an audio file for transcription.

### Example \`curl\` Command

   \`\`\`bash
   curl -X POST http://localhost:5000/upload \
     -F "file=@/path/to/your/audiofile.wav" \
     -F "name=OptionalName"
   \`\`\`

### Expected Response

\`\`\`json
{
  "filename": "audiofile.wav",
  "transcription": "Transcribed text of the audio file.",
  "id": "60d5f3b3e1b5f5b8c5d1f5e3"
}
\`\`\`

## Dockerize the Flask Application

To build and run the Flask application using Docker:

1. **Build the Docker image**:

   \`\`\`bash
   docker build -t audio-transcriber .
   \`\`\`

2. **Run the Docker container**:

   \`\`\`bash
   docker run -p 5000:5000 --env-file .env audio-transcriber
   \`\`\`

## Notes

- Ensure your .env file is not exposed in version control by adding it to your .gitignore file.
- Adjust the MAX_CONTENT_LENGTH and PROCESSING_TIMEOUT settings in the .env file according to your requirements.
- For a production environment, consider additional security measures, such as authentication for MongoDB and securing the Flask API.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
