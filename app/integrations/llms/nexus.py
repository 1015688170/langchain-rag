from __future__ import annotations

from typing import Any

import requests
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatResult


class NexusChatModel(BaseChatModel):
    api_url: str
    api_key: str
    model: str = "gpt-4o"
    temperature: float = 0.2
    max_tokens: int = 1200
    timeout: int = 60

    @property
    def _llm_type(self) -> str:
        return "nexus-chat"

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: Any | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        if not self.api_url:
            raise ValueError("NEXUS_CHAT_API_URL must be set when LLM_PROVIDER=nexus.")

        payload: dict[str, Any] = {
            "messages": [self._convert_message(message) for message in messages],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        if self.model:
            payload["model"] = self.model
        if stop:
            payload["stop"] = stop

        response = requests.post(
            self.api_url,
            headers={"Content-Type": "application/json", "api-key": self.api_key},
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=content))])

    def _convert_message(self, message: BaseMessage) -> dict[str, str]:
        if isinstance(message, SystemMessage):
            role = "system"
        elif isinstance(message, AIMessage):
            role = "assistant"
        elif isinstance(message, HumanMessage):
            role = "user"
        else:
            role = "user"
        content = message.content if isinstance(message.content, str) else str(message.content)
        return {"role": role, "content": content}

