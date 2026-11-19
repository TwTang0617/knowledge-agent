from uuid import uuid4

from core.llm_client import LLMClient

from services.agent_planner import AgentPlanner
from services.plan_validator import PlanValidator
from services.param_validator import ParamValidator
from services.tool_executor import ToolExecutor
from services.final_answer_generator import FinalAnswerGenerator
from services.trace_service import TraceService


class Agent:

    def __init__(self):

        # 大模型客户端
        self.llm_client = LLMClient()

        # Agent Planner
        self.planner = AgentPlanner()

        # Plan 校验器
        self.plan_validator = PlanValidator()

        # 参数校验器
        self.param_validator = ParamValidator()

        # 工具执行器
        self.tool_executor = ToolExecutor()

        # 最终答案生成器
        self.final_answer_generator = FinalAnswerGenerator()

        # Trace 服务
        self.trace_service = TraceService()

    def run(self, message: str, request_id: str | None = None) -> str:

        # =========================================
        # 0. Request ID
        # =========================================

        # 如果 FastAPI 已经传入 request_id，
        # 就直接使用。
        #
        # 如果是本地：
        # python -m agent.agent
        # 没有传 request_id，
        # Agent 自己生成一个。
        if request_id is None:
            request_id = str(uuid4())

        # 上一步工具执行结果
        observation = None

        # 保存整个 Agent Loop 的所有步骤
        steps = []

        # 当前最多执行 2 个 Step
        max_steps = 2

        for step in range(max_steps):

            print(f"\n===== Agent Step {step + 1} =====")

            # =====================================
            # 1. Planner
            # =====================================

            plan = self.planner.plan(message, observation)

            print("Agent原始规划:", plan)

            # =====================================
            # 2. PlanValidator
            # =====================================

            plan_validation_result = self.plan_validator.validate(plan)

            print("Plan校验结果:", plan_validation_result)

            # 当前 Step 的 Trace
            step_trace = {
                "step": step + 1,
                "plan": plan,
                "plan_validation": plan_validation_result,
            }

            # =====================================
            # Plan 校验失败
            # =====================================

            if not plan_validation_result["success"]:

                step_trace["status"] = "plan_validation_failed"

                steps.append(step_trace)

                error_message = plan_validation_result.get("message", "未知错误")

                final_answer = "Agent规划失败：" + str(error_message)

                trace = self.trace_service.create_trace(
                    user_input=message,
                    steps=steps,
                    final_answer=final_answer,
                    status="failed",
                    error=str(error_message),
                    request_id=request_id,
                )

                self.trace_service.save_trace(trace)

                return final_answer

            # =====================================
            # Planner 校验成功
            # =====================================

            tool_name = plan_validation_result["tool_name"]

            args = plan_validation_result["args"]

            step_trace["tool_name"] = tool_name

            step_trace["args"] = args

            # =====================================
            # 3. Planner 判断任务结束
            # =====================================

            if tool_name == "none":

                step_trace["status"] = "finished"

                steps.append(step_trace)

                # -----------------------------
                # 之前已经执行过工具
                # -----------------------------

                if len(steps) > 1:

                    final_answer = self.final_answer_generator.generate(
                        user_input=message, steps=steps
                    )

                # -----------------------------
                # 没有执行过任何工具
                # 普通聊天
                # -----------------------------

                else:

                    final_answer = self.llm_client.chat(message)

                trace = self.trace_service.create_trace(
                    user_input=message,
                    steps=steps,
                    final_answer=final_answer,
                    status="success",
                    request_id=request_id,
                )

                self.trace_service.save_trace(trace)

                self._print_trace_summary(trace)

                return final_answer

            # =====================================
            # 4. ParamValidator
            # =====================================

            param_validation_result = self.param_validator.validate(tool_name, args)

            print("参数校验结果:", param_validation_result)

            step_trace["param_validation"] = param_validation_result

            # =====================================
            # 参数校验失败
            # =====================================

            if not param_validation_result["success"]:

                step_trace["status"] = "param_validation_failed"

                steps.append(step_trace)

                error_message = param_validation_result.get("message", "未知错误")

                final_answer = "工具参数校验失败：" + str(error_message)

                trace = self.trace_service.create_trace(
                    user_input=message,
                    steps=steps,
                    final_answer=final_answer,
                    status="failed",
                    error=str(error_message),
                    request_id=request_id,
                )

                self.trace_service.save_trace(trace)

                return final_answer

            # =====================================
            # 5. ToolExecutor + Retry
            # =====================================

            # 最大重试次数
            #
            # max_retries = 1 表示：
            #
            # 第一次调用
            # +
            # 最多额外重试 1 次
            max_retries = 1

            tool_result = None

            retry_count = 0

            for retry_count in range(max_retries + 1):

                tool_result = self.tool_executor.execute(tool_name, args)

                print(f"工具执行结果" f"（第 {retry_count + 1} 次尝试）:", tool_result)

                # 成功就停止 Retry
                if tool_result["success"]:

                    break

                # 还有重试机会
                if retry_count < max_retries:

                    print("工具执行失败，准备重试...")

            # 保存工具结果
            step_trace["tool_result"] = tool_result

            # retry_count = 0
            # 第一次执行成功
            #
            # retry_count = 1
            # 真正发生过一次 Retry
            step_trace["retry_count"] = retry_count

            # =====================================
            # 6. 工具最终仍失败
            # Error Feedback Replanning
            # =====================================

            if not tool_result["success"]:

                error_message = tool_result.get("error", "未知错误")

                step_trace["status"] = "tool_failed"

                step_trace["error"] = str(error_message)

                steps.append(step_trace)

                # ---------------------------------
                # 不直接 return
                #
                # 把错误作为 Observation
                # 反馈给 Planner
                # ---------------------------------

                observation = f"工具 {tool_name} 执行失败：" f"{error_message}"

                print("Error Observation:", observation)

                # 回到 Agent Loop 顶部
                # 进入下一次重新规划
                continue

            # =====================================
            # 7. Observation
            # =====================================

            observation = tool_result["result"]

            step_trace["observation"] = observation

            step_trace["status"] = "success"

            steps.append(step_trace)

            print("Observation:", observation)

        # =========================================
        # 8. 达到最大 Step 数
        # =========================================

        final_answer = self.final_answer_generator.generate(
            user_input=message, steps=steps
        )

        # 判断最终请求状态
        #
        # 这里只表示：
        # Agent 整体流程正常完成并生成了最终答案。
        #
        # 某个 Step 是否失败，
        # 可以继续从 steps 中查看。
        trace = self.trace_service.create_trace(
            user_input=message,
            steps=steps,
            final_answer=final_answer,
            status="success",
            request_id=request_id,
        )

        self.trace_service.save_trace(trace)

        self._print_trace_summary(trace)

        return final_answer

    def _print_trace_summary(self, trace: dict) -> None:

        print(
            "AGENT_TRACE:",
            {
                "request_id": trace["request_id"],
                "step_count": trace["step_count"],
                "status": trace["status"],
                "final_answer_preview": trace["final_answer_preview"],
            },
        )


# =============================================
# 本地测试
# =============================================

if __name__ == "__main__":

    agent = Agent()

    message = "12 * 12 等于多少？"

    print("用户:", message)

    answer = agent.run(message)

    print("\nAgent回答:")

    print(answer)
