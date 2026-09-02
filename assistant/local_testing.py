import httpx

from config import Config
from runtime_context import RequestContext

config = Config()

async def get_demo_context() -> RequestContext:
    async with httpx.AsyncClient(
        base_url=config.base_drf_api,
    ) as client:
        response = await client.post(
            "accounts/login/",
            json={
                "username": "demo_student",
                "password": "studyops123",
            },
        )
        response.raise_for_status()

        return RequestContext(
            access_token=response.cookies.get("access_token"),
            refresh_token=response.cookies.get("refresh_token"),
            timezone="Asia/Beirut",
        )