from fastapi import FastAPI, HTTPException
from agent import NoPendingInterruptError, main
from schemas.chat_request import ChatRequest

app = FastAPI()


@app.post("/chat")
async def chat(chat_request: ChatRequest):
    try:
        return await main(
            thread_id=chat_request.thread_id,
            user_request=chat_request.user_input,
            command=chat_request.command,
            user_token=chat_request.user_token,
            refresh_token=chat_request.refresh_token,
            time_zone=chat_request.time_zone,
        )
    except NoPendingInterruptError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
