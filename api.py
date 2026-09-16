import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any
from brain.persona_engine import SYSTEM_PERSONAS, get_system_prompt
from brain.openrouter_engine import AVAILABLE_MODELS, stream_response

from brain.openrouter_engine import AVAILABLE_MODELS, stream_response
from brain.persona_engine import PERSONAS, get_system_prompt
from brain.memory_engine import load_user_profile, increment_interaction_count

app = FastAPI(
    title="Infera AI Inference Gateway",
    description="Decoupled backend service handling persona injection, user memory, and LLM streaming.",
    version="1.0.0"
)

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request schema using Pydantic
class ChatRequest(BaseModel):
    messages: List[Dict[str, str]]
    persona: str = "Helpful Assistant"
    model_name: str = "openrouter/free"

AVAILABLE_MODELS = {
    "Llama 3.1 8B (Free)": "meta-llama/llama-3.1-8b-instruct:free",
    "Qwen 2.5 Coder 32B (Free)": "qwen/qwen-2.5-coder-32b-instruct:free",
    "Mistral 7B (Free)": "mistralai/mistral-7b-instruct:free",
    "Auto Free Route": "openrouter/free"
}
@app.get("/profile")
def get_user_profile():
    """Retrieve persistent user cognitive profile."""
    return load_user_profile()

@app.post("/chat/stream")
def chat_stream(request: ChatRequest):
    """
    Injects system persona & memory, then streams tokens back to the client.
    """
    try:
        # Increment persistent interaction counter
        increment_interaction_count()

        # Build system context
        system_prompt = get_system_prompt(request.persona)
        augmented_messages = [{"role": "system", "content": system_prompt}] + request.messages

        # Display name ko actual OpenRouter model ID me convert karo
        actual_model_id = AVAILABLE_MODELS.get(request.model_name, request.model_name)

        # Stream generator
        def event_stream():
            for chunk in stream_response(augmented_messages, actual_model_id):
                yield chunk

        return StreamingResponse(event_stream(), media_type="text/plain")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
