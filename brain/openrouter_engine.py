import os
import requests
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY or "missing_key",
    timeout=25.0,
    default_headers={
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "Infera AI"
    }
)

def fetch_live_free_models():
    """Fetch active free models directly from OpenRouter API excluding retired Meta slugs."""
    fallback = {
        "Mistral 7B Instruct (Free)": "mistralai/mistral-7b-instruct:free",
        "Qwen 2.5 Coder 32B (Free)": "qwen/qwen-2.5-coder-32b-instruct:free",
        "Gemma 2 9B (Free)": "google/gemma-2-9b-it:free"
    }
    try:
        headers = {"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}
        resp = requests.get("https://openrouter.ai/api/v1/models", headers=headers, timeout=5)
        if resp.status_code == 200:
            models_data = resp.json().get("data", [])
            live_free = {}
            for item in models_data:
                m_id = item.get("id", "")
                m_name = item.get("name", m_id)
                # Filter strictly active free models and exclude deprecated Meta free slugs
                if m_id.endswith(":free") and "meta-llama" not in m_id:
                    clean_name = f"{m_name} (Free)" if "(free)" not in m_name.lower() else m_name
                    live_free[clean_name] = m_id
            if live_free:
                return dict(list(live_free.items())[:6])  # Top active free models
    except Exception:
        pass
    return fallback

AVAILABLE_MODELS = fetch_live_free_models()

def stream_response(messages, model_name=None):
    if not API_KEY or API_KEY.strip() == "":
        yield "⚠️ Configuration Error: OPENROUTER_API_KEY missing in .env"
        return

    # Select user model or fallback to first available
    primary_id = AVAILABLE_MODELS.get(model_name)
    if not primary_id:
        primary_id = list(AVAILABLE_MODELS.values())[0]

    candidate_ids = [primary_id] + [m for m in AVAILABLE_MODELS.values() if m != primary_id]

    last_error = None
    for model_id in candidate_ids:
        try:
            response = client.chat.completions.create(
                model=model_id,
                messages=messages,
                stream=True
            )
            has_content = False
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    has_content = True
                    yield chunk.choices[0].delta.content
            if has_content:
                return
        except Exception as err:
            last_error = f"{model_id}: {str(err)}"
            continue

    yield f"Inference Failure: {last_error}"