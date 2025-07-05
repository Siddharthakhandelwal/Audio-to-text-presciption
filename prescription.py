import speech_recognition as sr
from google import generativeai as genai
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()
now=datetime.now()
formatted = now.strftime("%Y-%m-%d %H:%M:%S")
def audio_text():
    r = sr.Recognizer()
    with sr.Microphone(sample_rate=44100, chunk_size=2048) as source:
        print("Say something...")
        r.adjust_for_ambient_noise(source, duration=0.5)
        audio = r.listen(source, timeout=10, phrase_time_limit=180)

    try:
        text = r.recognize_google(audio, language='en-IN')
        print("You said:", text)
        return text
    except sr.UnknownValueError:
        return "Could not understand audio."
    except sr.RequestError as e:
        return f"Google API error: {e}"

def prescription():
    text = audio_text()
    print("Transcribed:", text)

    # Error handling
    if "Google API error" in text or "Could not understand audio." in text:
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

# Run it
prescription()
