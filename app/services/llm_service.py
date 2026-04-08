"""
Unified LLM Service
Supports: Azure OpenAI, Google Gemini
Routing is based on the active AIModel's `provider` field.
"""
import httpx
from sqlalchemy.orm import Session
from app.models.domain import AIModel, LLMProvider
from app.models.stats import UsageLog
from app.core.config import settings
# google.genai is imported lazily inside _call_gemini_async to avoid
# crashing the module on environments that don't have the package installed.


# ---------------------------------------------------------------------------
# Helper: Build provider-specific payloads
# ---------------------------------------------------------------------------

def _build_azure_payload(
    ai_model: AIModel,
    input_text: str | None,
    messages: list[dict] | None,
    system_prompt: str,
    temperature: float,
    max_tokens: int,
) -> tuple[str, dict, dict]:
    """Returns (url, headers, payload) for Azure OpenAI.

    Key parameter distinction:
    - Standard models (GPT-4, GPT-4o, GPT-4.5, etc.) → `max_tokens`
    - Reasoning models (o1, o3, o4-mini, etc.)         → `max_completion_tokens`
      Using `max_tokens` on a reasoning model returns HTTP 400.
    """
    api_key = settings.AZURE_OPENAI_API_KEY or settings.AZURE_OPENAI_KEY
    endpoint = settings.AZURE_OPENAI_ENDPOINT

    if not api_key or not endpoint:
        raise ValueError("Missing Azure OpenAI Credentials (AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT).")
    if not ai_model.deployment_name:
        raise ValueError(f"AIModel '{ai_model.name}' is missing deployment_name (required for Azure).")

    url = (
        f"{endpoint.rstrip('/')}/openai/deployments/{ai_model.deployment_name}"
        f"/chat/completions?api-version={ai_model.api_version}"
    )
    headers = {"Content-Type": "application/json", "api-key": api_key}

    # Choose the correct token-limit parameter name
    token_param = "max_completion_tokens" if ai_model.is_reasoning_model else "max_tokens"

    if messages:
        payload: dict = {
            "messages": messages,
            "temperature": temperature,
            token_param: max_tokens,
        }
    else:
        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": input_text},
            ],
            "temperature": temperature,
            token_param: max_tokens,
        }

    return url, headers, payload


def _call_gemini_async(
    ai_model: AIModel,
    input_text: str | None,
    messages: list[dict] | None,
    system_prompt: str,
    temperature: float,
    max_tokens: int,
):
    """Builds the Gemini client + request objects. Imports google.genai lazily."""
    try:
        from google import genai  # noqa: PLC0415
        from google.genai import types  # noqa: PLC0415
    except ImportError as exc:
        raise ImportError(
            "google-genai package is not installed. Run: pip install google-genai"
        ) from exc

    api_key = settings.GEMINI_API_KEY
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY in settings.")
    client = genai.Client(api_key=api_key)
    model_name = ai_model.model_name or settings.GEMINI_MODEL_NAME

    contents = []
    if messages:
        for msg in messages:
            if msg["role"] == "system":
                # If there are system messages in the array, override the system_prompt!
                system_prompt = msg["content"]
                continue
            role = "user" if msg["role"] == "user" else "model"
            contents.append(types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])]))
    else:
        contents.append(types.Content(role="user", parts=[types.Part.from_text(text=input_text or "")]))

    thinking_config = None
    if ai_model.is_reasoning_model and ("thinking" in model_name.lower() or "gemini-2.0-flash-thinking" in model_name.lower()):
        thinking_config = types.ThinkingConfig(thinking_level="HIGH")

    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=temperature,
        max_output_tokens=max_tokens,
        thinking_config=thinking_config,
    )

    return client, model_name, contents, config

def _format_gemini_response(response) -> dict:
    prompt_tokens = response.usage_metadata.prompt_token_count if response.usage_metadata else 0
    completion_tokens = response.usage_metadata.candidates_token_count if response.usage_metadata else 0
    total_tokens = response.usage_metadata.total_token_count if response.usage_metadata else 0
    return {
        "choices": [
            {
                "message": {"role": "assistant", "content": response.text},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens, "total_tokens": total_tokens},
    }


# ---------------------------------------------------------------------------
# Async public API
# ---------------------------------------------------------------------------

async def call_llm(
    db: Session,
    user_id: int | None = None,  # Made optional for compatibility
    input_text: str | None = None,
    messages: list[dict] | None = None,
    system_prompt: str = "You are a helpful AI assistant.",
    model_id: str | None = None,
    app_name: str = "Assistant", # Added: Name of the application (e.g. "Chatbot", "PPT Generator")
    temperature: float = 0.7,
    max_tokens: int = 2000,
) -> dict:
    """
    Unified async entry point.
    Resolves the active model from DB, then routes to the correct provider.
    Logs usage (tokens, model, user) after successful completion.
    """
    ai_model = _resolve_model(db, model_id)

    if ai_model.provider == LLMProvider.AZURE:
        url, headers, payload = _build_azure_payload(
            ai_model, input_text, messages, system_prompt, temperature, max_tokens
        )
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            raise ValueError(f"LLM API Error [{ai_model.provider}] ({response.status_code}): {response.text}")
        res = response.json()
    elif ai_model.provider == LLMProvider.GOOGLE:
        client, model_name, contents, config = _call_gemini_async(
            ai_model, input_text, messages, system_prompt, temperature, max_tokens
        )
        response = await client.aio.models.generate_content(
            model=model_name, contents=contents, config=config
        )
        res = _format_gemini_response(response)
    else:
        raise ValueError(f"Unsupported LLM provider: {ai_model.provider}")

    # Log Usage
    _log_usage(db, user_id, ai_model.name, app_name, res)
    
    return res


# ---------------------------------------------------------------------------
# Sync public API  (for legacy synchronous skills)
# ---------------------------------------------------------------------------

def call_llm_sync(
    db: Session,
    user_id: int | None = None,  # Added: ID of the user calling the LLM
    input_text: str | None = None,
    messages: list[dict] | None = None,
    system_prompt: str = "You are a helpful AI assistant.",
    model_id: str | None = None,
    app_name: str = "Assistant", # Added
    temperature: float = 0.7,
    max_tokens: int = 2000,
) -> dict:
    """
    Synchronous version of call_llm.
    Uses the same payload builders so behaviour is identical.
    Logs usage (tokens, model, user) after successful completion.
    """
    ai_model = _resolve_model(db, model_id)

    if ai_model.provider == LLMProvider.AZURE:
        url, headers, payload = _build_azure_payload(
            ai_model, input_text, messages, system_prompt, temperature, max_tokens
        )
        with httpx.Client(timeout=60.0) as client:
            response = client.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            raise ValueError(f"LLM API Error [{ai_model.provider}] ({response.status_code}): {response.text}")
        res = response.json()
    elif ai_model.provider == LLMProvider.GOOGLE:
        client, model_name, contents, config = _call_gemini_async(
            ai_model, input_text, messages, system_prompt, temperature, max_tokens
        )
        response = client.models.generate_content(
            model=model_name, contents=contents, config=config
        )
        res = _format_gemini_response(response)
    else:
        raise ValueError(f"Unsupported LLM provider: {ai_model.provider}")

    # Log Usage
    _log_usage(db, user_id, ai_model.name, app_name, res)

    return res


# ---------------------------------------------------------------------------
# Private helper
# ---------------------------------------------------------------------------

def _resolve_model(db: Session, model_id: str | None) -> AIModel:
    """
    Looks up the requested model, falls back to the single active model.
    Raises if neither is found.
    """
    ai_model: AIModel | None = None

    if model_id:
        ai_model = db.query(AIModel).filter(AIModel.id == model_id).first()

    if not ai_model:
        ai_model = db.query(AIModel).filter(AIModel.is_active == True).first()

    if not ai_model:
        raise ValueError(
            "No active AIModel found. "
            "Please create a model and mark it as active via /api/v1/models."
        )

    return ai_model


def _log_usage(db: Session, user_id: int, model_name: str, app_name: str, response_json: dict):
    """Creates a UsageLog entry in the database based on the LLM response."""
    try:
        usage = response_json.get("usage", {})
        
        # Azure / OpenAI standard structure
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", prompt_tokens + completion_tokens)

        # Create record
        log = UsageLog(
            user_id=user_id,
            app_name=app_name,
            model_name=model_name,
            tokens_input=prompt_tokens,
            tokens_output=completion_tokens,
            total_tokens=total_tokens,
            # We can calculate estimated cost here if we have a pricing table
            estimated_cost=0.0 
        )
        db.add(log)
        db.commit()
    except Exception as e:
        # We don't want to crash the main response if logging fails
        import logging
        logging.getLogger("uvicorn").error(f"Failed to log LLM usage: {e}")
