"""Configuration loader for dbt-autodoc. Reads .env and validates settings."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

SUPPORTED_PROVIDERS = {
    "anthropic": {
        "sdk": "anthropic",
        "docs": "https://docs.anthropic.com/en/docs/about-claude/models",
        "default_model": "claude-sonnet-4-6",
    },
    "openai": {
        "sdk": "openai",
        "docs": "https://platform.openai.com/docs/models",
        "default_model": "gpt-4o",
    },
    "openai_compatible": {
        "sdk": "openai",
        "docs": "See your provider's documentation",
        "default_model": None,
        "requires_base_url": True,
    },
}


@dataclass
class AutodocConfig:
    provider: str
    api_key: str
    model: str
    base_url: str | None = None
    dbt_project_dir: Path = field(default_factory=lambda: Path.cwd())
    manifest_path: Path | None = None

    def __post_init__(self):
        if not self.manifest_path:
            self.manifest_path = self.dbt_project_dir / "target" / "manifest.json"

    @classmethod
    def from_env(cls, project_dir: Path | None = None) -> AutodocConfig:
        """Load configuration from .env file and environment variables."""
        project_dir = project_dir or Path.cwd()

        # Load .env from project directory, then from cwd
        for env_path in [project_dir / ".env", Path.cwd() / ".env"]:
            if env_path.exists():
                load_dotenv(env_path)
                break

        provider = os.getenv("DBT_AUTODOC_PROVIDER")
        api_key = os.getenv("DBT_AUTODOC_API_KEY")
        model = os.getenv("DBT_AUTODOC_MODEL")
        base_url = os.getenv("DBT_AUTODOC_BASE_URL")

        # Validate required fields
        errors = []
        if not provider:
            errors.append("DBT_AUTODOC_PROVIDER is not set")
        elif provider not in SUPPORTED_PROVIDERS:
            errors.append(
                f"DBT_AUTODOC_PROVIDER='{provider}' is not supported. "
                f"Choose from: {', '.join(SUPPORTED_PROVIDERS.keys())}"
            )

        if not api_key:
            errors.append("DBT_AUTODOC_API_KEY is not set")

        if provider and provider in SUPPORTED_PROVIDERS:
            provider_info = SUPPORTED_PROVIDERS[provider]
            if not model:
                model = provider_info.get("default_model")
                if not model:
                    errors.append(
                        f"DBT_AUTODOC_MODEL is required for provider '{provider}'"
                    )
            if provider_info.get("requires_base_url") and not base_url:
                errors.append(
                    f"DBT_AUTODOC_BASE_URL is required for provider '{provider}'"
                )

        if errors:
            print("Configuration errors:", file=sys.stderr)
            for e in errors:
                print(f"  - {e}", file=sys.stderr)
            print(
                "\nSee .env.example for setup instructions.",
                file=sys.stderr,
            )
            sys.exit(1)

        return cls(
            provider=provider,
            api_key=api_key,
            model=model,
            base_url=base_url,
            dbt_project_dir=project_dir,
        )
