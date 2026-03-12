"""LLM provider implementations."""

from __future__ import annotations

from dbt_autodoc.config import AutodocConfig
from dbt_autodoc.providers.base import BaseProvider


def get_provider(config: AutodocConfig) -> BaseProvider:
    """Factory function to create the appropriate LLM provider."""
    if config.provider == "anthropic":
        from dbt_autodoc.providers.anthropic_provider import AnthropicProvider
        return AnthropicProvider(config)
    elif config.provider in ("openai", "openai_compatible"):
        from dbt_autodoc.providers.openai_provider import OpenAIProvider
        return OpenAIProvider(config)
    else:
        raise ValueError(f"Unsupported provider: {config.provider}")
