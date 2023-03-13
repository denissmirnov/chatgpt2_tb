from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class GptRequest(BaseModel):
    query: str
    conversation_id: Optional[UUID]
    parent_id: Optional[UUID]
    account_id: Optional[int]

    def to_dict(self):
        data = self.dict()
        if self.conversation_id:
            data["conversation_id"] = self.conversation_id.hex
        if self.parent_id:
            data["parent_id"] = self.parent_id.hex
        return data


class AskResponse(BaseModel):
    conversation_id: Optional[UUID]
    parent_id: Optional[UUID]
    account_id: Optional[int]
    message: Optional[str]
