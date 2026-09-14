from unittest.mock import AsyncMock
from types import SimpleNamespace

import pytest
from langchain.messages import AIMessage
from test_tools import make_session

from nodes import summary_workflow
from schemas import ScheduleResponse


@pytest.mark.asyncio
@pytest.mark.parametrize("empty", [False, True])
async def test_summary_uses_api_result_and_returns_message_and_schedule(empty):
    session = make_session(
        session_id=42,
        start_at="2026-09-01T09:00:00+03:00",
        end_at="2026-09-01T10:00:00+03:00",
    )
    schedule = ScheduleResponse(
        drafts=[] if empty else [{"task": session.task, "sessions": [session]}]
    )
    response = AIMessage(content="No sessions created." if empty else "Created one session.")
    model = AsyncMock()
    model.ainvoke.return_value = response

    result = await summary_workflow(
        {"schedule": schedule, "draft_schedule": "UNCONFIRMED_DRAFT"},
        SimpleNamespace(context=SimpleNamespace(timezone="Asia/Beirut")),
        model,
    )

    prompt = model.ainvoke.call_args.args[0][0].content
    assert schedule.model_dump_json(indent=2) in prompt
    assert "UNCONFIRMED_DRAFT" not in prompt
    assert "Asia/Beirut" in prompt
    assert result["messages"] == [response]
    assert result["schedule"] is schedule


@pytest.mark.asyncio
async def test_summary_requires_api_result():
    model = AsyncMock()
    with pytest.raises(ValueError, match="has not been created"):
        await summary_workflow({}, SimpleNamespace(), model)
    model.ainvoke.assert_not_awaited()
