# Running the planning agent

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
docker compose run --rm assistant python agent.py YOUR_EXISTING_THREAD_ID
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
