from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import shutil
import os
from pydub import AudioSegment
import speech_recognition as sr

app = FastAPI()

# Directory to save uploaded audio files
UPLOAD_DIRECTORY = "uploaded_audio"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

@app.post("/upload-audio/")
async def upload_audio(file: UploadFile = File(...)):
    # Check the file type (accept only audio files)
    if not file.content_type.startswith("audio/"):
        return JSONResponse(content={"error": "Invalid file type"}, status_code=400)
    
    # Check for allowed extensions (MP3 or WAV)
    if not (file.filename.endswith(".mp3") or file.filename.endswith(".wav")):
        return JSONResponse(content={"error": "Only MP3 and WAV files are allowed"}, status_code=400)

    # Define the path to save the file
    file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)
    
    # Save the file locally
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Convert audio to text
    text = convert_audio_to_text(file_path)
    
    return JSONResponse(content={
        "filename": file.filename,
        "status": "Uploaded successfully",
        "transcription": text
    })

def convert_audio_to_text(file_path: str) -> str:
    # Initialize recognizer
    recognizer = sr.Recognizer()
    
    # Load audio file
    try:
        # Use pydub to convert audio to WAV format for better compatibility
        audio = AudioSegment.from_file(file_path)
        wav_file_path = file_path.replace(".mp3", ".wav").replace(".wav", "_converted.wav")
        audio.export(wav_file_path, format="wav")

        # Recognize speech
        with sr.AudioFile(wav_file_path) as source:
            audio_data = recognizer.record(source)  # Read the entire audio file
            text = recognizer.recognize_google(audio_data)  # Use Google Web Speech API
            return text
    except Exception as e:
        return f"Error during transcription: {str(e)}"

