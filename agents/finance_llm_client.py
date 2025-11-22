import os
import json
from typing import Any, Dict, Optional
from openai import OpenAI

_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
DEFAULT_MODEL = "gpt-4.1-mini"

def call_llm(
    system_prompt: str,
    user_message: str,
    response_format: str = "json",
    model: Optional[str] = None,
) -> Dict[str, Any]:
    if model is None:
        model = DEFAULT_MODEL

    input_content = [{"role": "user", "content": user_message}]

    if response_format == "json":
        resp = _client.responses.create(
            model=model,
            instructions=system_prompt,
            input=input_content,
            response_format={"type": "json_object"},
        )
        raw = resp.output_text
        return json.loads(raw)
    else:
        resp = _client.responses.create(
            model=model,
            instructions=system_prompt,
            input=input_content,
        )
        return {"text": resp.output_text}
