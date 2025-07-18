import json
from typing import List, Dict
from openai_helper import chat_completion

# Workflow A: Code Issue
WORKFLOW_A_SYS = (
    "You are an expert software architect. Follow the user prompt to analyze a code issue. "
    "Generate exactly three candidate solutions. Score each on a 1-10 scale (higher is better) "
    "and give a concise rationale. Then pick the best candidate and explain why. "
    "Reply ONLY in JSON with this schema:\n"
    "{\n"
    "  \"candidates\": [\n"
    "    {\"title\": \"str\", \"score\": int, \"rationale\": \"str\"}\n"
    "  ],\n"
    "  \"recommendation\": \"str\",\n"
    "  \"why\": \"str\",\n"
    "  \"acceptance\": [\"str\"]\n"
    "}"
)

def run_workflow_a(
    prompt: str,
    model: str | None = None,
) -> Dict:
    """Invoke LLM for Workflow A and parse its JSON response."""
    messages = [
        {"role": "system", "content": WORKFLOW_A_SYS},
        {"role": "user", "content": prompt},
    ]
    raw = chat_completion(messages, model=model)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON from LLM: {e}\nRaw: {raw}")
    return {"task": prompt, **data}

# Workflow B: Requirements Template
WORKFLOW_B_SYS_BASE = (
    "You are a senior product consultant. The user will provide a development task prompt "
    "and three distinct critique roles. First, draft a concise user-requirements template. "
    "Then critique that template from each role. Finally, output an improved template. "
    "Respond ONLY in JSON with this schema:\n"
    "{\n"
    "  \"template_initial\": \"str\",\n"
    "  \"critique\": {critique_schema},\n"
    "  \"template_improved\": \"str\"\n"
    "}"
)

def run_workflow_b(
    prompt: str,
    roles: List[str],
    model: str | None = None,
) -> Dict:
    """Invoke LLM for Workflow B, building a dynamic critique schema."""
    # Build schema placeholder
    crit_items = ", ".join(f'\\"{r}\\": \\\"str\\\"' for r in roles)
    critique_schema = "{" + crit_items + "}"

    system_prompt = WORKFLOW_B_SYS_BASE.replace("{critique_schema}", critique_schema)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
    ]
    raw = chat_completion(messages, model=model)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON from LLM: {e}\nRaw: {raw}")
    return {"task": prompt, **data}