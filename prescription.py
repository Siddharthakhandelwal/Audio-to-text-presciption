import os
from dotenv import load_dotenv
from datetime import datetime
import speech_recognition as sr
from google import generativeai as genai
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write

load_dotenv()
now=datetime.now()
formatted = now.strftime("%Y-%m-%d %H:%M:%S")

def transcribe_audio(filename):
    recognizer = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("Sorry, could not understand the audio.")
        return "Sorry, could not understand the audio."
    except sr.RequestError:
        print("Could not request results from Google Speech Recognition service.")
        return "Sorry, could not understand the audio."



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

    The tone should be professional and direct — as if the doctor is writing it, not an AI.Don't make or add any recommendations on your own, stick to the conversations only. Do not refer to the conversation or yourself in the third person. Just write the prescription naturally, as a doctor would hand it to the patient.
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

