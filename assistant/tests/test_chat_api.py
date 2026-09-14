from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def endpoint(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    import main

    runner = AsyncMock(return_value={"messages": []})
    monkeypatch.setattr(main, "main", runner)
    return TestClient(main.app), runner


def payload(**message):
    return dict(
        thread_id="existing-thread",
        user_token="access",
        refresh_token="refresh",
        **message
    )


@pytest.mark.parametrize(
    "message",
    [
        {"user_input": "Plan tomorrow"},
        {"command": {"action": "approve"}},
        {"command": {"action": "edit", "feedback": "Start later"}},
    ],
)
def test_message_forwarding(endpoint, message):
    client, runner = endpoint
    response = client.post("/chat", json=payload(**message))
    assert response.status_code == 200
    runner.assert_awaited_once_with(
        thread_id="existing-thread",
        user_token="access",
        refresh_token="refresh",
        time_zone="Asia/Beirut",
        user_request=message.get("user_input"),
        command=message.get("command"),
    )


@pytest.mark.parametrize(
    "message",
    [
        {},
        {"user_input": " "},
        {"user_input": "Hi", "command": {"action": "approve"}},
        {"command": "approve"},
        {"command": {"action": "edit"}},
        {"command": {"action": "unknown"}},
        {"user_input": "Hi", "time_zone": "invalid/timezone"},
    ],
)
def test_invalid_message_rejected(endpoint, message):
    client, runner = endpoint
    assert client.post("/chat", json=payload(**message)).status_code == 422
    runner.assert_not_awaited()


def test_resume_without_interrupt_returns_conflict(endpoint):
    from agent import NoPendingInterruptError

    client, runner = endpoint
    runner.side_effect = NoPendingInterruptError("No pending review")
    response = client.post("/chat", json=payload(command={"action": "approve"}))
    assert response.status_code == 409


@pytest.mark.asyncio
@pytest.mark.parametrize("cancel", [False, True])
async def test_agent_uses_caller_context(monkeypatch, cancel):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    import agent

    saver = AsyncMock()
    monkeypatch.setattr(
        agent.AsyncPostgresSaver, "from_conn_string", MagicMock(return_value=saver)
    )
    monkeypatch.setattr(
        agent, "config", SimpleNamespace(checkpoint_database_url="unused")
    )
    graph_app = SimpleNamespace(
        aget_state=AsyncMock(return_value=SimpleNamespace(tasks=[SimpleNamespace(interrupts=[SimpleNamespace(value={"type": "schedule_review"})])] if cancel else [])),
        ainvoke=AsyncMock(return_value={"messages": []}),
    )
    monkeypatch.setattr(agent.graph, "compile", MagicMock(return_value=graph_app))

    result = await agent.main(
        "existing-thread",
        "caller-access",
        "caller-refresh",
        user_request=None if cancel else "Plan tomorrow",
        command={"action": "cancel"} if cancel else None,
        time_zone="UTC",
    )

    kwargs = graph_app.ainvoke.await_args.kwargs
    graph_app.ainvoke.assert_awaited_once()
    if cancel:
        assert result == {"status": "cancelled"}
        assert graph_app.ainvoke.await_args.args[0].resume == {"action": "cancel"}
    assert kwargs["context"].access_token == "caller-access"
    assert kwargs["context"].refresh_token == "caller-refresh"
    assert kwargs["context"].timezone == "UTC"
    assert kwargs["config"]["configurable"]["thread_id"] == "existing-thread"
