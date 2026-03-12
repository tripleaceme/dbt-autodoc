"""Anthropic (Claude) provider implementation."""

from __future__ import annotations

from dbt_autodoc.config import AutodocConfig
from dbt_autodoc.providers.base import BaseProvider


class AnthropicProvider(BaseProvider):
    def __init__(self, config: AutodocConfig):
        try:
            import anthropic
        except ImportError:
            raise ImportError(
                "The 'anthropic' package is required for the Anthropic provider.\n"
                "Install it with: pip install dbt-autodoc[anthropic]"
            )

        self.client = anthropic.Anthropic(api_key=config.api_key)
        self.model = config.model

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return response.content[0].text

    def estimate_cost(self, input_text: str, output_estimate: int = 1000) -> dict:
        # Rough estimate: ~4 chars per token
        input_tokens = len(input_text) // 4
        output_tokens = output_estimate

        # Claude Sonnet 4.6 pricing (approximate)
        cost_per_1k_input = 0.003
        cost_per_1k_output = 0.015

        estimated_cost = (
            (input_tokens / 1000) * cost_per_1k_input
            + (output_tokens / 1000) * cost_per_1k_output
        )

        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "estimated_cost_usd": round(estimated_cost, 4),
        }
