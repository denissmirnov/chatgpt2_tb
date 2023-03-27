from typing import Optional
from uuid import UUID

import httpx
from loguru import logger as LOGGER

from models.schemas import AskResponse, GptRequest


class GptApiClient:
    url: str

    def __init__(self, url: str):
        self.url = url

    async def ask(
        self, query: str, conversation_id: UUID = None, parent_id: UUID = None, account_id: int = None
    ) -> Optional[AskResponse]:
        req = GptRequest(
            query=query,
            conversation_id=conversation_id,
            parent_id=parent_id,
            account_id=account_id,
            use_free_node=False
        )
        url = self.url + "/api/v1/ask"
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=req.to_dict(), timeout=240)

        res = None
        try:
            res = AskResponse.parse_raw(resp.text)
        except Exception as e:
            LOGGER.error(f"Exception during parsing response: {e}")

        return res
