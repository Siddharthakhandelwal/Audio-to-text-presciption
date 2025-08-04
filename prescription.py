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
You are a licensed medical doctor. Below is a transcribed or recorded conversation between you and a patient during a clinical consultation. The time of the visit is {formatted}.

Based solely on this conversation, write a medically accurate, professional prescription in the format typically used by doctors. The prescription should be detailed and clinical, and it should be written naturally as a doctor would write it directly for the patient (not referring to yourself as an AI or the conversation as a transcript).

Your prescription must include only the information mentioned or clearly implied in the conversation. Do not add any assumptions or medical recommendations not supported by the dialogue.
while listing the details , ensure to include the visit the time with name and other details of the patient.

The prescription should cover the following:

Patient's chief complaints or reported symptoms

Clinical findings or observations (if mentioned)

Diagnosis (provisional or confirmed)

Medications prescribed

Include correct medicine name (check and correct any unclear or incorrect names), potency, route (if specified), dosage, frequency, and duration

Recommended laboratory or imaging investigations (if any)

Lifestyle, dietary, or activity modifications (if advised)

Clear follow-up or referral instructions (if given)

If any medication name is not recognized clearly from the conversation, verify and correct the name, and include the appropriate strength/potency based on common clinical usage.

If the patient mentions durations such as "4 to 5 days," ensure this is not misinterpreted as "45 days." Interpret such statements carefully and accurately.

If the conversation is in any language other than English, translate the content accurately and provide the final prescription in English.

Avoid commentary, notes, or third-person narration. Write as if handing the prescription directly to the patient.
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

