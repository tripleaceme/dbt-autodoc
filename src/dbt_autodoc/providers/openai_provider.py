"""OpenAI and OpenAI-compatible provider implementation."""

from __future__ import annotations

from dbt_autodoc.config import AutodocConfig
from dbt_autodoc.providers.base import BaseProvider


class OpenAIProvider(BaseProvider):
    def __init__(self, config: AutodocConfig):
        try:
            import openai
        except ImportError:
            raise ImportError(
                "The 'openai' package is required for the OpenAI provider.\n"
                "Install it with: pip install dbt-autodoc[openai]"
            )

        kwargs = {"api_key": config.api_key}
        if config.base_url:
            kwargs["base_url"] = config.base_url

        self.client = openai.OpenAI(**kwargs)
        self.model = config.model

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=4096,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content

    def estimate_cost(self, input_text: str, output_estimate: int = 1000) -> dict:
        input_tokens = len(input_text) // 4
        output_tokens = output_estimate

        # GPT-4o pricing (approximate)
        cost_per_1k_input = 0.0025
        cost_per_1k_output = 0.01

        estimated_cost = (
            (input_tokens / 1000) * cost_per_1k_input
            + (output_tokens / 1000) * cost_per_1k_output
        )

        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "estimated_cost_usd": round(estimated_cost, 4),
        }
