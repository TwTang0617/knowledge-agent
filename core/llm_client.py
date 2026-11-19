import os
from typing import Any
from urllib.parse import urlparse

import httpx
from dotenv import load_dotenv

load_dotenv()


class LLMClient:

    def __init__(self):

        api_key = os.getenv("DEEPSEEK_API_KEY")
        base_url = os.getenv("DEEPSEEK_BASE_URL")
        model = os.getenv("DEEPSEEK_MODEL")

        if not api_key:
            raise ValueError("未找到 DEEPSEEK_API_KEY，请检查 .env 文件")
        if not base_url:
            raise ValueError("未找到 DEEPSEEK_BASE_URL，请检查 .env 文件")
        if not model:
            raise ValueError("未找到 DEEPSEEK_MODEL，请检查 .env 文件")

        normalized_base_url = base_url.strip().rstrip("/")
        parsed_base_url = urlparse(normalized_base_url)

        if parsed_base_url.scheme not in {"http", "https"} or not parsed_base_url.netloc:
            raise ValueError("DEEPSEEK_BASE_URL 必须是有效的 HTTP(S) URL")

        self._api_key = api_key
        self.model = model
        self.chat_completions_url = f"{normalized_base_url}/chat/completions"
        self.client = httpx.Client(
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=httpx.Timeout(60.0, connect=10.0),
        )

    def chat(self, message: str, temperature: float = 1.0) -> str:

        payload = {
            "model": self.model,
            "temperature": temperature,
            "messages": [
                {"role": "system", "content": "你是一个有帮助的AI助手"},
                {"role": "user", "content": message},
            ],
        }

        try:
            response = self.client.post(self.chat_completions_url, json=payload)
            response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise RuntimeError("DeepSeek API 请求超时") from exc
        except httpx.HTTPStatusError as exc:
            detail = self._get_error_detail(exc.response)
            raise RuntimeError(
                f"DeepSeek API 请求失败，HTTP {exc.response.status_code}: {detail}"
            ) from exc
        except httpx.RequestError as exc:
            raise RuntimeError(
                f"DeepSeek API 网络请求失败: {type(exc).__name__}"
            ) from exc

        try:
            data = response.json()
        except ValueError as exc:
            raise RuntimeError("DeepSeek API 返回的响应不是有效 JSON") from exc

        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError("DeepSeek API 返回结构异常，缺少 choices[0].message.content") from exc

        if not isinstance(content, str):
            raise RuntimeError("DeepSeek API 返回结构异常，message.content 不是字符串")

        return content

    def _get_error_detail(self, response: httpx.Response) -> str:
        detail: Any = None

        try:
            error_data = response.json()
            if isinstance(error_data, dict):
                error = error_data.get("error")
                if isinstance(error, dict):
                    detail = error.get("message")
                elif isinstance(error, str):
                    detail = error
        except ValueError:
            pass

        if not isinstance(detail, str) or not detail.strip():
            detail = response.text or response.reason_phrase or "未知错误"

        sanitized_detail = detail.replace(self._api_key, "[REDACTED]")
        return sanitized_detail.strip()[:500]
