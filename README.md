# Knowledge Agent

基于 RAG、Tool Calling、Multi-step Agent、Replanning 与可观测性的企业知识库智能问答系统。

Knowledge Agent 以 FastAPI 提供服务入口，由 LLM Planner 判断用户目标、选择工具，并将工具结果作为 Observation 反馈给后续规划。系统既能回答普通问题，也能组合知识库检索与计算器完成多步骤任务，同时通过 JSONL Trace 保留完整执行链路。

## 核心价值

- 将企业知识检索、计算工具与多步骤规划统一到一个可验证的 Agent Loop 中。
- 通过 Query Rewrite、向量检索和 Relevance Check 降低无关上下文进入生成阶段的概率。
- 通过 Plan Validation、Parameter Validation、Retry 与 Error Feedback 提升工具调用的稳健性。
- 使用 Request ID、Agent Trace 和 Trace Analyzer 支持问题定位与执行质量分析。
- 将 LLM 通信封装在独立的 `LLMClient` 中，使用 HTTPX 直接调用 DeepSeek API，不依赖 OpenAI SDK。

## 系统架构

```text
Client
  |
  v
FastAPI  POST /agent/chat
  |
  v
Agent -------------------------------> TraceService -> logs/agent_trace.jsonl
  |
  v
AgentPlanner -> PlanValidator -> ParamValidator
  |                                   |
  |                                   v
  |                              ToolExecutor
  |                              /          \
  |                             v            v
  |                    KnowledgeTool    CalculatorTool
  |                         |
  |                         v
  |                    RAGService
  |                         |
  +<------ Observation -----+
  |
  v
Replanning / FinalAnswerGenerator
  |
  v
Response + request_id
```

LLM 调用链路：

```text
Agent / AgentPlanner / RAG services
  -> LLMClient
  -> HTTPX POST {DEEPSEEK_BASE_URL}/chat/completions
  -> DeepSeek OpenAI-compatible API
  -> choices[0].message.content
```

`DEEPSEEK_BASE_URL` 可以配置为 `https://api.deepseek.com`，也可以包含兼容路径 `/v1`；客户端不会额外重复拼接 `/v1`。

## Agent Loop

```text
User Query
  -> Planner 生成单步计划
  -> Plan Validation
  -> Parameter Validation
  -> Tool Execution
  -> Retry（工具失败时最多额外重试一次）
  -> Observation / Error Observation
  -> Replanning
  -> Final Answer
  -> Trace Persistence
```

当前 Agent 最多执行 2 个 Step，适用于知识查询、单独计算，以及“先查知识库、再计算”的复合问题。

## RAG 流程

```text
company_handbook.txt
  -> DocumentLoader
  -> TextSplitter
  -> EmbeddingService (BAAI/bge-small-zh-v1.5)
  -> VectorStore / VectorRetriever

User Query
  -> QueryRewriter
  -> Query Embedding
  -> Top-K Retrieval
  -> RelevanceChecker
  -> Context Assembly
  -> LLMClient
  -> Answer + Source
```

向量索引保存在 `data/vector_index.json`。该文件是由演示文档生成的缓存：如果文件不存在或文档哈希发生变化，项目会自动重新构建，因此它不进入 Git 仓库。

## 已实现能力

- FastAPI `/agent/chat` 与 `/health` 接口
- DeepSeek Chat Completions API（HTTPX 直连）
- LLM Planner、Tool Registry 与 Tool Executor
- Calculator Tool 与 Knowledge QA Tool
- Multi-step Agent Loop、Observation 与 Replanning
- Plan Validation、Parameter Validation、Retry 与 Error Feedback
- 文档加载、段落切分、Embedding、向量索引与 Top-K 检索
- Query Rewrite、Relevance Check、来源标注与最终答案生成
- Request ID、Agent Trace、JSONL Logging 与 Trace Analyzer
- Retrieval Evaluation、Generation Evaluation 与 LLM-as-Judge

## 项目结构

```text
knowledge-agent/
├── agent/
│   └── agent.py                  # Agent Loop 与多步骤执行
├── core/
│   └── llm_client.py             # HTTPX -> DeepSeek API
├── data/
│   ├── company_handbook.txt      # 可公开的演示知识库
│   └── vector_index.json         # 自动生成，不提交
├── services/
│   ├── agent_planner.py
│   ├── document_loader.py
│   ├── embedding_service.py
│   ├── final_answer_generator.py
│   ├── generation_evaluator.py
│   ├── param_validator.py
│   ├── plan_validator.py
│   ├── query_rewriter.py
│   ├── rag_evaluator.py
│   ├── rag_service.py
│   ├── relevance_checker.py
│   ├── retriever.py
│   ├── text_splitter.py
│   ├── tool_executor.py
│   ├── trace_analyzer.py
│   ├── trace_service.py
│   ├── vector_retriever.py
│   └── vector_store.py
├── tools/
│   ├── calculator_tool.py
│   ├── knowledge_tool.py
│   └── tool_registry.py
├── main.py                       # FastAPI 应用
├── schemas.py                    # Pydantic 请求与响应模型
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## 技术栈

| 技术 | 用途 |
|---|---|
| Python 3.10.4 | 运行环境 |
| FastAPI / Uvicorn | HTTP API 服务 |
| DeepSeek API | Planner、判断与答案生成 |
| HTTPX | DeepSeek HTTP 通信 |
| Sentence Transformers | 文本向量化 |
| BAAI/bge-small-zh-v1.5 | 中文 Embedding 模型 |
| Pydantic | API 数据模型 |
| JSONL | Agent Trace 持久化 |
| Git | 版本管理 |

## Windows 安装

以下命令均在 PowerShell 中、项目根目录执行。

1. 确认 Python：

```powershell
python --version
```

项目当前验证环境为 Python 3.10.4。

2. 创建并激活虚拟环境：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

如果 PowerShell 阻止激活脚本，也可以不激活，直接使用 `.\.venv\Scripts\python.exe` 执行后续命令。

3. 安装依赖：

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
```

首次加载 Embedding 模型可能需要下载模型文件，请确保网络可以访问模型源。

## 环境变量

复制示例文件：

```powershell
Copy-Item .env.example .env
```

编辑 `.env`：

```dotenv
DEEPSEEK_API_KEY=your_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=your_model
```

> **安全要求：`.env` 包含真实 API Key，绝对不要提交或上传到公开仓库。** 项目只提交不含密钥的 `.env.example`。

## 启动 FastAPI

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

健康检查：

```text
GET http://127.0.0.1:8000/health
```

Swagger UI：

```text
http://127.0.0.1:8000/docs
```

在 Swagger 中展开 `POST /agent/chat`，点击 **Try it out**，填入请求体后执行。

## API 示例

请求：

```http
POST /agent/chat
Content-Type: application/json

{
  "message": "公司年假有多少天，如果我已经休了5天，还剩多少天？"
}
```

PowerShell 示例：

```powershell
$body = @{ message = "12 * 37 等于多少？" } | ConvertTo-Json
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/agent/chat" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

响应结构：

```json
{
  "request_id": "generated-request-id",
  "status": "success",
  "answer": "..."
}
```

## 核心测试案例

| 场景 | 输入 | 预期行为 |
|---|---|---|
| 普通问答 | `什么是 AI Agent？` | Planner 返回 `none`，由 LLM 直接回答 |
| Calculator | `12 * 37 等于多少？` | 调用 `calculator`，得到 `444` |
| RAG + Multi-step | `公司年假有多少天，如果我已经休了5天，还剩多少天？` | 先查询 12 天年假，再计算剩余 7 天 |
| 错误反馈 | `10 / 0 等于多少？` | 工具失败、重试，并将错误作为 Observation 反馈给 Planner |

基础验证命令：

```powershell
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -c "import fastapi, httpx, pydantic, sentence_transformers; print('dependencies ok')"
.\.venv\Scripts\python.exe -c "from core.llm_client import LLMClient; print('LLMClient import ok')"
.\.venv\Scripts\python.exe -c "from services.embedding_service import EmbeddingService; print(len(EmbeddingService().embed('测试文本')))"
```

真实 Agent 场景会调用 DeepSeek API 并消耗少量额度，请按需执行。

## Evaluation

- `services/rag_evaluator.py`：评估 Top-1 Accuracy、Top-2 Recall、Answerability、False Positive 与 False Negative。
- `services/generation_evaluator.py`：使用 LLM-as-Judge 评估 Answer Relevance、Faithfulness 与 Refusal Correctness。

评估脚本会发起多次模型调用，运行前应确认 API 额度，并以实际输出为准，不预设或伪造指标。

## Observability

每次 Agent 请求会生成或接收一个 `request_id`，Trace 包含：

- 用户输入与时间戳
- Planner 计划与校验结果
- 工具名称、参数、重试次数和执行结果
- Observation、最终答案与请求状态

Trace 默认写入 `logs/agent_trace.jsonl`。日志可能包含用户问题和模型输出，已通过 `.gitignore` 排除，不应上传到公开仓库。

分析已有 Trace：

```powershell
.\.venv\Scripts\python.exe -m services.trace_analyzer
```

## 未来优化方向

- 将同步 LLM 调用与 FastAPI 路由逐步改为异步链路。
- 增加自动化单元测试、集成测试和 CI。
- 为 Agent Loop 增加更通用的最大步数配置与防循环策略。
- 为向量索引增加原子写入、损坏恢复和模型版本元数据。
- 引入持久化向量数据库和多知识库管理。
- 增加鉴权、限流、审计脱敏与多租户隔离。
- 增加 Docker 部署与生产环境结构化日志。

## 免责声明

`data/company_handbook.txt` 是用于演示的虚构制度数据。将项目用于真实企业场景前，应替换为已获授权的知识库，并评估访问控制、数据保密、日志留存和模型服务合规要求。
