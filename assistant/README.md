# Running the planning agent

## Chat endpoint

Start the assistant HTTP server with `docker compose up --build assistant`.
The endpoint is `POST http://localhost:8001/chat`; interactive request docs
are available at `http://localhost:8001/docs`.

Send JSON using an existing thread ID created by the frontend/API:

```json
{
  "thread_id": "existing-thread-id",
  "user_token": "access-token",
  "refresh_token": "refresh-token",
  "time_zone": "Asia/Beirut",
  "user_input": "Plan my study sessions for tomorrow"
}
```

For a review response, replace `user_input` with `command`, for example
`"command": {"action": "approve"}`. Supported actions are `approve`, `cancel`,
and `edit` (which also requires nonblank `feedback`). Supply exactly one of
`user_input` or `command`. Invalid bodies return 422; a command without a pending
review returns 409. Credentials are passed into runtime context, not graph state.
Checkpoint tables must already be initialized, as described below.

Responses contain only frontend output: `{"status": "interrupted", "interrupts": [...]}`
for review (including after edits), `{"status": "completed", "summary": "..."}`
after approval, or `{"status": "cancelled"}` after cancellation. The graph's
messages, tool results, and planning state remain in its checkpoint.

For local development, run `python -m uvicorn main:app --port 8001 --reload`
from the `assistant` directory after installing its requirements.

The request body follows the [FastAPI request model pattern](https://fastapi.tiangolo.com/tutorial/body/).

The agent uses `ChatOpenAI` with `gpt-5.6-terra` and low reasoning effort.
Tool retrieval overrides reasoning effort to `none`, as required for Terra
function tools on the Chat Completions endpoint.
OpenAI API usage is billed to the account associated with your API key.

Add these variables to the repository-root `.env` file locally:

```dotenv
OPENAI_API_KEY=your-api-key
OPENAI_MODEL=gpt-5.6-terra
```

Keep your real key out of source control and chat messages. Docker Compose
passes these variables into the assistant container. `OPENAI_MODEL` defaults
to `gpt-5.6-terra` when omitted.

Rebuild after changing dependencies, then run the agent with the API and
database services available:

```powershell
docker compose build assistant
docker compose up assistant
```

`Config` builds the checkpoint URL from the existing `POSTGRES_USER`,
`POSTGRES_PASSWORD`, and `POSTGRES_DB` variables. Local Python defaults to
`localhost` and `DB_HOST_PORT` (5432 if unset). Compose supplies
`POSTGRES_HOST=db` and `POSTGRES_PORT=5432` for the assistant container.
Checkpoint tables must
already be initialized with `await checkpointer.setup()` once before use.

Both date resolution and draft generation use strict JSON-schema structured
output. Draft generation retains its initial attempt plus two parsing repair
attempts. Pydantic validation and the later scheduling checks are still needed
for rules that JSON Schema cannot enforce.
