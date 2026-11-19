import json


class TraceAnalyzer:

    def __init__(self):
        self.log_path = "logs/agent_trace.jsonl"

    def load_traces(self) -> list[dict]:

        traces = []

        try:
            with open(
                self.log_path,
                "r",
                encoding="utf-8"
            ) as file:

                for line in file:

                    line = line.strip()

                    if not line:
                        continue

                    try:
                        trace = json.loads(line)
                        traces.append(trace)

                    except json.JSONDecodeError:
                        print("跳过损坏的日志行:", line)

        except FileNotFoundError:
            print("未找到日志文件:", self.log_path)

        return traces

    def analyze(self):

        traces = self.load_traces()

        total_requests = len(traces)

        success_requests = 0
        failed_requests_count = 0

        total_steps = 0
        multi_step_requests = 0

        tool_calls = 0
        tool_success = 0
        tool_failure = 0

        tool_stats = {}

        failed_requests = []

        for trace in traces:

            # =========================
            # 请求级统计
            # =========================

            status = trace.get("status")

            if status == "success":
                success_requests += 1
            else:
                failed_requests_count += 1

                failed_requests.append({
                    "request_id": trace.get("request_id"),
                    "timestamp": trace.get("timestamp"),
                    "user_input": trace.get("user_input"),
                    "status": status,
                    "error": trace.get("error")
                })

            # =========================
            # Step 统计
            # =========================

            steps = trace.get("steps", [])

            step_count = len(steps)

            total_steps += step_count

            if step_count > 1:
                multi_step_requests += 1

            # =========================
            # 每一步工具统计
            # =========================

            for step in steps:

                tool_name = step.get("tool_name")

                # none 表示没有调用工具
                if (
                    tool_name is None
                    or tool_name == "none"
                ):
                    continue

                tool_calls += 1

                # 第一次遇到该工具
                if tool_name not in tool_stats:

                    tool_stats[tool_name] = {
                        "calls": 0,
                        "success": 0,
                        "failure": 0
                    }

                tool_stats[tool_name]["calls"] += 1

                tool_result = step.get("tool_result")

                if (
                    isinstance(tool_result, dict)
                    and tool_result.get("success") is True
                ):

                    tool_success += 1

                    tool_stats[
                        tool_name
                    ]["success"] += 1

                else:

                    tool_failure += 1

                    tool_stats[
                        tool_name
                    ]["failure"] += 1

        # =========================
        # 计算指标
        # =========================

        if total_requests > 0:

            request_success_rate = (
                success_requests
                / total_requests
            )

            average_steps = (
                total_steps
                / total_requests
            )

        else:

            request_success_rate = 0
            average_steps = 0

        if tool_calls > 0:

            tool_success_rate = (
                tool_success
                / tool_calls
            )

        else:

            tool_success_rate = 0

        # =========================
        # 总体统计
        # =========================

        print("\n============================")
        print("Agent Trace Analysis")
        print("============================")

        print("总请求数:", total_requests)
        print("成功请求数:", success_requests)
        print("失败请求数:", failed_requests_count)

        print(
            "请求成功率:",
            request_success_rate
        )

        print("总执行 Step 数:", total_steps)

        print(
            "平均每请求 Step 数:",
            average_steps
        )

        print(
            "多步请求数:",
            multi_step_requests
        )

        print("工具调用总次数:", tool_calls)
        print("工具成功次数:", tool_success)
        print("工具失败次数:", tool_failure)

        print(
            "工具成功率:",
            tool_success_rate
        )

        # =========================
        # 按工具统计
        # =========================

        print("\n============================")
        print("Tool Statistics")
        print("============================")

        if not tool_stats:

            print("暂无工具调用")

        else:

            for tool_name, stats in tool_stats.items():

                print("\n工具:", tool_name)

                print(
                    "调用次数:",
                    stats["calls"]
                )

                print(
                    "成功次数:",
                    stats["success"]
                )

                print(
                    "失败次数:",
                    stats["failure"]
                )

                if stats["calls"] > 0:

                    success_rate = (
                        stats["success"]
                        / stats["calls"]
                    )

                else:

                    success_rate = 0

                print(
                    "成功率:",
                    success_rate
                )

        # =========================
        # 失败请求
        # =========================

        print("\n============================")
        print("Failed Requests")
        print("============================")

        if not failed_requests:

            print("暂无失败请求")

        else:

            for request in failed_requests:

                print("\nrequest_id:")
                print(request["request_id"])

                print("用户问题:")
                print(request["user_input"])

                print("状态:")
                print(request["status"])

                print("错误:")
                print(request["error"])


if __name__ == "__main__":

    analyzer = TraceAnalyzer()

    analyzer.analyze()