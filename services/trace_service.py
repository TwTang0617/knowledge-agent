import json
import os

from datetime import datetime
from uuid import uuid4


class TraceService:

    def __init__(self):

        self.log_path = "logs/agent_trace.jsonl"

        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)

    def create_trace(
        self,
        user_input: str,
        steps: list[dict],
        final_answer: str,
        status: str = "success",
        error: str | None = None,
        request_id: str | None = None,
    ) -> dict:

        if request_id is None:
            request_id = str(uuid4())

        trace = {
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "status": status,
            "error": error,
            "step_count": len(steps),
            "steps": steps,
            "final_answer": final_answer,
            "final_answer_length": len(final_answer),
            "final_answer_preview": final_answer[:200],
        }

        return trace

    def save_trace(self, trace: dict):

        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)

        with open(self.log_path, "a", encoding="utf-8") as file:

            file.write(json.dumps(trace, ensure_ascii=False))
            file.write("\n")
