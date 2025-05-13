# Voice to Prescription CLI Tool

This project listens to a conversation between a doctor and a patient, transcribes it using Azure Speech Services, and generates a prescription using Groq's LLM.

## Setup

1. **Clone the repository** and navigate to the `pen` directory.
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Set up environment variables:**
   Create a `.env` file in the `pen` directory with the following content:
   ```env
   GROQ_API_KEY=your_groq_api_key
   AZURE_SPEECH_KEY=your_azure_speech_key
   AZURE_SPEECH_REGION=your_azure_region
   ```

## Usage

Run the script:

```bash
python voice_to_prescription.py
```

- The script will continuously listen for speech.
- Press `Ctrl+C` to stop recording.
- The conversation will be analyzed and a prescription will be generated and printed.

## Notes

- Requires valid Azure Speech and Groq API credentials.
- No UI; all interaction is via the command line.
