from types import SimpleNamespace

from langchain.messages import AIMessage, HumanMessage

from chat_output import format_chat_output


def test_interrupt_exposes_only_review_payload():
    review = {"type": "schedule_review", "draft": {"drafts": []}, "options": []}
    result = format_chat_output({
        "messages": [HumanMessage(content="Plan my exam")],
        "planning_constraints": {"internal": True},
        "__interrupt__": [SimpleNamespace(value=review)],
    })
    assert result == {"status": "interrupted", "interrupts": [review]}


def test_completion_exposes_only_final_summary():
    result = format_chat_output({
        "messages": [HumanMessage(content="Plan my exam"), AIMessage(content="Saved your sessions.", response_metadata={"internal": True})],
        "schedule": {"internal": True},
        "draft_schedule": {"internal": True},
    })
    assert result == {"status": "completed", "summary": "Saved your sessions."}


def test_summary_extracts_text_blocks_only():
    result = format_chat_output({"messages": [AIMessage(content=[{"type": "text", "text": "Saved."}, {"type": "reasoning", "reasoning": "Internal"}])]})
    assert result == {"status": "completed", "summary": "Saved."}
