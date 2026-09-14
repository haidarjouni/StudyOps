from typing import Any


def format_chat_output(state: dict[str, Any]) -> dict[str, Any]:
    """Expose only the review payload or final text, keeping graph state internal."""
    interrupts = state.get("__interrupt__", ())
    if interrupts:
        return {
            "status": "interrupted",
            "interrupts": [item.value for item in interrupts],
        }

    messages = state.get("messages", [])
    content = messages[-1].content if messages else ""
    if isinstance(content, list):
        content = "\n".join(
            block if isinstance(block, str) else block.get("text", "")
            for block in content
            if isinstance(block, str)
            or (isinstance(block, dict) and block.get("type") == "text")
        )
    return {"status": "completed", "summary": content}
