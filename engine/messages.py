"""
Turn an engine decision into the farmer-facing sentence.

    from engine.messages import render
    render(generate_daily_decision(...), "hi")
"""

from engine.data import load_json


LANGUAGES = ("en", "hi")


def _format_number(value):
    """
    40.0 -> "40", 36.4 -> "36.4": the farmer sees whole numbers
    where possible.
    """
    if isinstance(value, float):
        value = round(value, 1)
        return str(int(value)) if value.is_integer() else str(value)

    return value


def render(result, lang="hi"):
    """
    result is the dict returned by generate_daily_decision or
    generate_daily_decision_paddy.
    """
    if lang not in LANGUAGES:
        raise ValueError(f"Unknown language: {lang}")

    messages = load_json("messages.json")
    reason_code = result["reason_code"]

    if reason_code not in messages["reasons"]:
        raise ValueError(f"No message for reason code: {reason_code}")

    values = {key: _format_number(value) for key, value in result.items()}

    stage = result.get("heat_stage")
    values["heat_stage"] = messages["stages"][stage][lang] if stage else ""

    return messages["reasons"][reason_code][lang].format(**values)
