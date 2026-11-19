from pydantic import BaseModel


class AgentChatRequest(BaseModel):
    message: str


class AgentChatResponse(BaseModel):
    request_id: str
    status: str
    answer: str
