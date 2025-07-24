import os
from dotenv import load_dotenv
from datetime import datetime
import speech_recognition as sr
from google import generativeai as genai
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import requests

load_dotenv()
now=datetime.now()
formatted = now.strftime("%Y-%m-%d %H:%M:%S")

base_url = "https://api.assemblyai.com"
headers = {
    "authorization": "eb4d1dd9aa884e91b70bc8bf9f583f1c"  # Replace with your actual API key
}

def transcribe_audio(filename):
    with open(filename, "rb") as f:
        upload_response = requests.post(
            base_url + "/v2/upload",
            headers=headers,
            data=f
        )

    audio_url = upload_response.json()["upload_url"]
    print(f"Uploaded audio URL: {audio_url}")

    # 2. Submit transcription request with language auto-detection
    data = {
        "audio_url": audio_url,
        "language_detection": True  # This enables language detection
        # "speech_model": "universal"  # Optional, helps with multilingual transcription
    }

    transcript_response = requests.post(base_url + "/v2/transcript", json=data, headers=headers)
    transcript_id = transcript_response.json()["id"]
    polling_endpoint = f"{base_url}/v2/transcript/{transcript_id}"

    # 3. Poll until transcription is complete
    while True:
        result = requests.get(polling_endpoint, headers=headers).json()

        if result['status'] == 'completed':
            print("\nTranscription completed:")
            print(result['text'])
            os.remove("user_input.wav")
            return result['text']

        elif result['status'] == 'error':
            raise RuntimeError(f"Transcription failed: {result['error']}")

        else:
            print("Transcription in progress... Waiting 3 seconds.")

def manual_record_audio(filename='user_input.wav', fs=22050):
    print("Press Enter to start recording...")
    input()
    print("Recording... Press Enter to stop.")

    recording = []

    def callback(indata, frames, time, status):
        if status:
            print(status)
        recording.append(indata.copy())

    # Start the stream and record until Enter is pressed again
    with sd.InputStream(samplerate=fs, channels=1, callback=callback):
        input()  # Wait for Enter to stop
        # After Enter is pressed, the stream context will exit

    audio = np.concatenate(recording, axis=0)
    audio_int16 = np.int16(audio * 32767)
    write(filename, fs, audio_int16)
    print("Recording saved.")
    return filename

def prescription():
    text = transcribe_audio("user_input.wav")
    print("Transcribed:", text)

    # Error handling
    if "Google API error" in text or "Could not understand audio." in text or "Sorry, could not understand the audio." in text:
        return "Sorry Doc, I can't help you today."

    # Configure Gemini
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")

    prompt = f'''
    You are a doctor. The following is a recorded conversation between you and a patient during a medical consultation.and the visit time is {formatted}.
    Based on this conversation, write a clear, detailed, and medically accurate prescription for the patient — exactly as you would normally write it for them.

    Ensure the prescription includes:
    - Patient complaints/symptoms
    - Clinical observations (if mentioned)
    - Diagnosis (if implied or stated)
    - Medications (with dosage and duration)
    - Any tests or investigations advised
    - Lifestyle or dietary recommendations (if any)
    - Follow-up instructions

    The tone should be professional and direct — as if the doctor is writing it, not an AI.Don't make or add any recommendations on your own, stick to the conversations only. Do not refer to the conversation or yourself in the third person. Just write the prescription naturally, as a doctor would hand it to the patient.Conversation can be in any language , translate it to english and write the prescriptio as i described you.
    Conversation:
    {text}
    '''

    response = model.generate_content(prompt)
    print("\nPrescription:\n", response.text)
    
    return response.text

def main():
    load_dotenv()
    if not os.path.exists("user_input.wav"):
        manual_record_audio()
    prescription()

if __name__ == "__main__":
    main()

