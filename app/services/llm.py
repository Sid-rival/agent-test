"""Pluggable LLM service.

Default provider is a deterministic extractive generator: it selects the most
relevant retrieved chunks and returns a concise, source-grounded answer. This
keeps the whole pipeline testable offline. Implement ``LLMProvider`` and set
``llm_provider`` to plug in a hosted model (OpenAI/Anthropic/etc.).
"""
import re
from abc import ABC, abstractmethod

_SENT_RE = re.compile(r"(?<=[.!?])\s+")


class LLMProvider(ABC):
    name: str = "base"

    @abstractmethod
    def generate(self, question: str, contexts: list[str]) -> str:
        ...


class LocalExtractiveProvider(LLMProvider):
    """Deterministic, offline answer generator grounded in retrieved chunks."""

    name = "local"

    def generate(self, question: str, contexts: list[str]) -> str:
        if not contexts:
            return (
                "I could not find any relevant information in the indexed "
                "documents to answer this question. Please rephrase or add "
                "documents covering this topic."
            )

        # Pick the most relevant sentence(s) across contexts.
        q_tokens = set(_tok(question))
        best: list[str] = []
        best_score = 0.0
        for ctx in contexts:
            for sent in _SENT_RE.split(ctx):
                sent = sent.strip()
                if not sent:
                    continue
                s_tokens = set(_tok(sent))
                if not s_tokens:
                    continue
                overlap = len(q_tokens & s_tokens)
                score = overlap / len(s_tokens)
                if score > best_score:
                    best_score = score
                    best = [sent]
                elif score == best_score and score > 0:
                    best.append(sent)

        if not best:
            return contexts[0][:400]

        answer = " ".join(best[:3])
        return answer.strip()


def _tok(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


class LLMService:
    def __init__(self, provider: str | None = None):
        self.provider = self._build(provider)

    def _build(self, provider: str | None) -> LLMProvider:
        p = (provider or "local").lower()
        if p == "local":
            return LocalExtractiveProvider()
        raise ValueError(f"Unknown LLM provider: {p}")

    def generate(self, question: str, contexts: list[str]) -> str:
        return self.provider.generate(question, contexts)


llm_service = LLMService()