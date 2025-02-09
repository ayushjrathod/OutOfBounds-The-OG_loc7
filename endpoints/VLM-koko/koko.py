from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from kokoro import KPipeline
import soundfile as sf
import shutil
import os

app = FastAPI()

# Enable CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Groq client
client = Groq(api_key="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")

# Global conversation history list
conversation_history = [
    {"role": "system", "content": "You are KoKo. You are an interrogator for suspicious receipts. Ask questions to know the events, details of vendors, and purpose of spending from the user, how this aligns with the company's business development, questiosn like that. This is the receipt: Employee EMP005, name : Mathew,  from department DEP005 submitted a pending travel expense of 4143.6 INR on 2024-12-10 for bus tickets purchased from Indian Railways (Bill No: PS24222516569711) with item details including Ticket Fare (4120.0 INR) and IRCTC Convenience Fee (23.6 INR), described as travel for a client meeting, flagged as an anomaly with a anamoly score of 0.8 due to exceeding the Travel Expenses category limit of 300.0 and maxPerExpenseSpend limit of 600.0, submitted on 2025-02-08, and created/updated at 2025-02-08 23:28:31., dont ask too many questions in one go ask two at once. ask a maximum of 8 questions then end the conversation with the employee saying we will get back to you via mail about the results"}
]

@app.post("/conversation")
async def handle_audio(file: UploadFile = File(...)):
    # Save the uploaded audio file
    file_path = f"uploaded_{file.filename}"
    with open(file_path, "wb") as audio_file:
        shutil.copyfileobj(file.file, audio_file)

    # Transcribe audio
    with open(file_path, "rb") as audio:
        transcription = client.audio.transcriptions.create(
            file=(file.filename, audio.read()),
            model="whisper-large-v3-turbo",
            response_format="json",
            language="en",
            temperature=0.0
        )
    os.remove(file_path)  # Clean up audio file

    transcribed_text = transcription.text

    # Append user's transcription to conversation history
    conversation_history.append({"role": "user", "content": transcribed_text})

    # Send conversation history to LLM
    chat_completion = client.chat.completions.create(
        messages=conversation_history,
        model="llama-3.1-8b-instant",
        stream=False
    )

    llm_response = chat_completion.choices[0].message.content

    # Append LLM's response to conversation history
    conversation_history.append({"role": "assistant", "content": llm_response})

    # Convert response text to audio using Kokoro
    pipeline = KPipeline(lang_code='a')
    generator = pipeline(
        llm_response, voice='af_heart', speed=1, split_pattern=r'\n+'
    )

    audio_responses = []
    for i, (gs, ps, audio) in enumerate(generator):
        audio_filename = f"response_{i}.wav"
        sf.write(audio_filename, audio, 24000)
        audio_responses.append(audio_filename)

    return {
        "transcription": transcribed_text,
        "response": llm_response,
        "audio_responses": audio_responses
    }
