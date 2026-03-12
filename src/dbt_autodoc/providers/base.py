"""Base provider interface for LLM integrations."""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Send a prompt to the LLM and return the response text."""
        ...

    @abstractmethod
    def estimate_cost(self, input_text: str, output_estimate: int) -> dict:
        """Estimate the cost for a given input. Returns dict with token counts and cost."""
        ...
