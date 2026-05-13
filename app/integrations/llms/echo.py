from __future__ import annotations

from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult


class EchoChatModel(BaseChatModel):
    """Local smoke-test chat model."""

    max_preview_chars: int = 1200

    @property
    def _llm_type(self) -> str:
        return "echo"

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: Any | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        content = self._message_text(messages[-1]) if messages else ""
        preview = content[: self.max_preview_chars]
        answer = (
            "当前使用 echo 本地模型，仅用于接口烟测。\n\n"
            "已收到的最终提示词片段：\n"
            f"{preview}"
        )
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=answer))])

    def _message_text(self, message: BaseMessage) -> str:
        if isinstance(message.content, str):
            return message.content
        return str(message.content)

