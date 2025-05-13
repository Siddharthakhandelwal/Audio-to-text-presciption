import os
import time
import json
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk
import groq

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
SERVICE_REGION = os.getenv("AZURE_SPEECH_REGION")

# Initialize speech services
def initialize_speech_services():
    try:
        speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SERVICE_REGION)
        speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)
        return speech_config, speech_synthesizer, speech_recognizer
    except Exception as e:
        print(f"Error initializing speech services: {e}")
        return None, None, None

def listen_continuous(speech_recognizer):
    print("Listening for conversation. Press Ctrl+C to stop and analyze.")
    transcript = []
    try:
        while True:
            print("Speak now...")
            result = speech_recognizer.recognize_once()
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                text = result.text.strip()
                if text:
                    print(f"Recognized: {text}")
                    transcript.append(text)
            else:
                print("No speech recognized or recognition ended.")
    except KeyboardInterrupt:
        print("\nConversation ended by user.")
    return "\n".join(transcript)

def analyze_conversation_with_groq(conversation_text):
    client = groq.Client(api_key=GROQ_API_KEY)
    prompt = (
        "You are a medical conversation analyzer. The following is a conversation between a patient and a doctor. "
        "Analyze the conversation and create a prescription based on what the doctor said. "
        "Output only the prescription in a clear, structured format.\n\n"
        f"Conversation:\n{conversation_text}"
    )
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=512,
        temperature=0.2
    )
    return response.choices[0].message.content.strip()

def main():
    _, _, speech_recognizer = initialize_speech_services()
    if not speech_recognizer:
        print("Failed to initialize speech recognizer. Exiting.")
        return
    conversation_text = listen_continuous(speech_recognizer)
    print("\nAnalyzing conversation with Groq...")
    prescription = analyze_conversation_with_groq(conversation_text)
    print("\n--- Prescription ---\n")
    print(prescription)

if __name__ == "__main__":
    main() 