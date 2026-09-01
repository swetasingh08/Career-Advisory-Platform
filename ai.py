import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


if load_dotenv:
    load_dotenv()
    load_dotenv(Path(__file__).resolve().parent / ".env", override=False)


DEMO_RESPONSE = """Gemini API key not configured.
Please add GEMINI_API_KEY to your .env file.

Demo response: I can still show how the app works. For a real answer, I would analyze your request, route it to the best AI agent, and generate specific recommendations."""


def _get_setting(name, default=""):
    try:
        import streamlit as st

        value = st.secrets.get(name, "")
        if value:
            return str(value).strip()
    except Exception:
        pass
    return os.getenv(name, default).strip()


def _model_candidates():
    configured_model = _get_setting("GEMINI_MODEL")
    models = [
        configured_model,
        "gemini-3.6-flash",
        "models/gemini-3.6-flash",
        "gemini-3.6-flash-latest",
    ]
    return [model for index, model in enumerate(models) if model and model not in models[:index]]


def _clear_dead_local_proxy():
    proxy_names = ["HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"]
    for name in proxy_names:
        value = os.getenv(name, "")
        if "127.0.0.1:9" in value or "localhost:9" in value:
            os.environ.pop(name, None)


def ask_ai(prompt, system_prompt=None):
    """Ask Gemini for a response, with a safe demo fallback."""
    api_key = _get_setting("GEMINI_API_KEY")
    if not api_key:
        return DEMO_RESPONSE

    try:
        import google.generativeai as genai

        _clear_dead_local_proxy()
        genai.configure(api_key=api_key)
        errors = []
        for model_name in _model_candidates():
            try:
                model = genai.GenerativeModel(
                    model_name=model_name,
                    system_instruction=system_prompt,
                )
                response = model.generate_content(
                    prompt,
                    generation_config={"temperature": 0.4},
                )
                text = (getattr(response, "text", "") or "").strip()
                if text:
                    return text
                errors.append(f"{model_name}: empty response")
            except Exception as model_exc:
                errors.append(f"{model_name}: {model_exc}")
        raise RuntimeError("No Gemini model worked. " + " | ".join(errors))
    except Exception as exc:
        return (
            "Gemini API request failed, but the app is still running.\n\n"
            f"Error: {exc}\n\n"
            "Demo response: Review the input, identify the goal, and provide practical next steps."
        )
