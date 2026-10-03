from typing import Annotated

from fastapi import Cookie, FastAPI, HTTPException
from agent import NoPendingInterruptError, main
from schemas.chat_request import ChatRequest

app = FastAPI()


@app.post("/chat")
async def chat(
    chat_request: ChatRequest,
    access_token: Annotated[str | None, Cookie()] = None,
    refresh_token: Annotated[str | None, Cookie()] = None,
):
    if (
        not access_token
        or not access_token.strip()
        or not refresh_token
        or not refresh_token.strip()
    ):
        raise HTTPException(status_code=401, detail="Authentication cookies are required")

    try:
        return await main(
            thread_id=chat_request.thread_id,
            user_request=chat_request.user_input,
            command=chat_request.command,
            user_token=access_token,
            refresh_token=refresh_token,
            time_zone=chat_request.time_zone,
        )
    except NoPendingInterruptError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
