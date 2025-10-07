from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
import requests
import openai
from openai import OpenAI

#Load .env (LOCAL ONLY) -> .env should contain OPENAI_API_KEY=sk-...
load_dotenv()
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_KEY:
    raise RuntimeError("Missing OPENROUTER_API_KEY")


#OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
#if not OPENAI_API_KEY:
#    raise RuntimeError("Set OPENAI_API_KEY in your environment or .env")

#openai.api_key = OPENAI_API_KEY

app = FastAPI(title="AI Summarizer API")
#client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Allow the React dev server origin during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # change for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionGeneratorRequest(BaseModel):
    text: str
    question_count: int = 5 #default number of questions
    difficulty: str # can be easy, hard ..
    max_tokens: int = 100000


@app.post("/generate")
def generate(req: QuestionGeneratorRequest):
    if not req.text or len(req.text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Please provide more text.")

    system_msg = "You are a professional quiz creator that generates thoughtful questions."
    user_msg = f"Generate {req.question_count} {req.difficulty} questions based on the text:\n{req.text}"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5173",  # required by OpenRouter
        "X-Title": "AI Question Generator",
    }

    payload = {
        "model": "z-ai/glm-4.5-air:free",  # ✅ valid OpenRouter model
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
        "max_tokens": req.max_tokens,
        "temperature": 0.7,
    }

    resp = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
    print("STATUS:", resp.status_code)
    print("TEXT:", resp.text[:500])

    if resp.status_code != 200:
        raise HTTPException(status_code=500, detail=f"OpenRouter error: {resp.text}")

    try:
        result = resp.json()
        questions = result["choices"][0]["message"]["content"]
        return {"questions": questions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Invalid response: {e}")
