import json

from django import template
from typing import Any

register = template.Library()


@register.filter(name="to_json")
def to_json(value: Any, indent: Any = None):
    """
    Converts a JSON-serializable value (e.g., dict, list) to a JSON string.

    Args:
        value: The object to serialize (must be JSON-serializable).
        indent (str or int, optional): Indentation level for pretty-printing.
            - If None (default), compact JSON.
            - If int (e.g., 4), uses that many spaces.
            - If 'tab', uses tabs.

    Returns:
        str: The JSON string.

    Raises:
        TypeError: If value is not JSON-serializable (e.g., Django model instance).
    """
    try:
        # Convert indent to int if it's a string like '4' or 'tab'
        if isinstance(indent, str):
            if indent == "tab":
                indent = "\t"
            else:
                indent = int(indent)

        return json.dumps(value, indent=indent, ensure_ascii=False)
    except (TypeError, ValueError) as e:
        # Handle non-serializable objects gracefully (e.g., return empty JSON)
        # You could log the error or raise it in debug mode
        if hasattr(value, "__dict__"):  # Fallback for simple objects
            return json.dumps(vars(value), indent=indent, ensure_ascii=False)
        return "{}"  # Or raise template.TemplateSyntaxError(str(e))
