from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

import nodes
from nodes import create_schedule
from runtime_context import RequestContext


@pytest.mark.asyncio
async def test_create_schedule_persists_draft_and_returns_schedule(monkeypatch):
    draft_schedule = MagicMock()
    draft_schedule.drafts = [MagicMock()]
    persisted_schedule = MagicMock()

    client = AsyncMock()
    client.create_draft_schedule.return_value = persisted_schedule

    client_context = MagicMock()
    client_context.__aenter__ = AsyncMock(return_value=client)
    client_context.__aexit__ = AsyncMock(return_value=None)
    client_factory = MagicMock(return_value=client_context)

    monkeypatch.setattr(nodes, "StudyOpsAPIClient", client_factory)
    monkeypatch.setattr(
        nodes,
        "Config",
        lambda: SimpleNamespace(base_drf_api="http://test/api/"),
    )

    runtime = SimpleNamespace(
        context=RequestContext(
            access_token="access-token",
            refresh_token="refresh-token",
            timezone="Asia/Beirut",
        )
    )

    result = await create_schedule(
        {"draft_schedule": draft_schedule},
        runtime,
    )

    assert result == {"schedule": persisted_schedule}
    client_factory.assert_called_once_with(
        "http://test/api/",
        access_token="access-token",
        refresh_token="refresh-token",
    )
    client.create_draft_schedule.assert_awaited_once_with(draft_schedule)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "state",
    [
        {},
        {"draft_schedule": SimpleNamespace(drafts=[])},
    ],
    ids=["missing-draft", "empty-draft"],
)
async def test_create_schedule_requires_an_approved_draft(state):
    runtime = SimpleNamespace(
        context=RequestContext(
            access_token=None,
            refresh_token=None,
        )
    )

    with pytest.raises(
        ValueError,
        match="Cannot create a schedule without an approved draft",
    ):
        await create_schedule(state, runtime)
