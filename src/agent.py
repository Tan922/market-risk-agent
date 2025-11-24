from typing import List

from llm import call_hf_inference
import os
from models import MarketRiskSnapshot

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

def generate_insight_batch(
    snapshots: List[MarketRiskSnapshot],
    type: str = "general-summary"
):
    """
    Accept a list of MarketRiskSnapshot and return model insight.

    Steps:
    - Serialize snapshots as JSON array
    - Load template
    - Replace {{input}} with full JSON list
    - Call model
    """

    if not snapshots:
        raise ValueError("snapshots list is empty")

    # Serialize list → JSON array
    snapshots_json = "[\n" + ",\n".join(
        s.model_dump_json(indent=2) for s in snapshots
    ) + "\n]"

    # Load template
    template = load_template("insight_prompt.txt")

    # Build final prompt
    prompt = build_prompt(
        template,
        input=snapshots_json,
        type=type
    )

    # Call your model (HuggingFace server / OpenAI / LM Studio etc.)
    json = call_hf_inference(prompt)

    return json["choices"][0]["message"]