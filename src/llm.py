import os
from models import MarketRiskSnapshot
import requests

HF_URL = os.environ.get("HF_URL", "https://router.huggingface.co/v1/chat/completions")
HF_TOKEN = os.environ.get("HF_TOKEN", "")
HF_MODEL = os.environ.get("HF_MODEL", "meta-llama/Llama-3.2-3B-Instruct:novita")

def call_hf_inference(prompt: str, max_new_tokens: int = 256) -> str:
    if not HF_TOKEN:
        raise RuntimeError("HF_API_TOKEN not set. Set it to call Hugging Face Inference API.")

    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "model": HF_MODEL
    }

    response = requests.post(HF_URL, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    return response.json()

def load_template(name: str) -> str:
    """
    Load a prompt template from /templates folder.
    """
    base_dir = os.path.dirname(__file__)
    template_path = os.path.join(base_dir, "templates", name)

    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()

def build_prompt(template: str, **kwargs) -> str:
    """
    Replace {{placeholders}} in the template with provided values.
    """
    prompt = template
    for key, value in kwargs.items():
        placeholder = f"{{{{{key}}}}}"
        prompt = prompt.replace(placeholder, value)
    return prompt

def generate_insight(riskSnapshot: MarketRiskSnapshot, type: str = "general-summary"):
    """
    High-level function: load template → build prompt → call model.
    """
    template = load_template("insight_prompt.txt")

    prompt = build_prompt(
        template,
        input=riskSnapshot.model_dump_json(indent=2),
        type=type
    )

    json = call_hf_inference(prompt)
    return json["choices"][0]["message"]