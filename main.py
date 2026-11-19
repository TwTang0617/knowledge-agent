from uuid import uuid4

from fastapi import FastAPI, HTTPException

from agent.agent import Agent
from schemas import AgentChatRequest, AgentChatResponse

app = FastAPI(
    title="Knowledge Agent API",
    description="基于 RAG、Tool Calling 和 Agent Loop 的企业知识助手",
    version="1.0.0",
)


agent = Agent()


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/agent/chat", response_model=AgentChatResponse)
def agent_chat(request: AgentChatRequest):

    request_id = str(uuid4())

    try:

        message = request.message.strip()

        if not message:

            raise HTTPException(status_code=400, detail="message 不能为空")

        answer = agent.run(message, request_id=request_id)

        return AgentChatResponse(request_id=request_id, status="success", answer=answer)

    except HTTPException:
        raise

    except Exception as e:

        print(f"Agent API 执行异常 " f"[request_id={request_id}]:", str(e))

        raise HTTPException(
            status_code=500,
            detail={"message": "Agent 服务执行失败", "request_id": request_id},
        )
