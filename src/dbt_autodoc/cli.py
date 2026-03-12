"""CLI entry point for dbt-autodoc."""

from __future__ import annotations

from pathlib import Path

import click

from dbt_autodoc import __version__


@click.group()
@click.version_option(version=__version__)
def cli():
    """dbt-autodoc: Auto-generate dbt model and column descriptions using LLMs."""
    pass


@cli.command()
@click.option(
    "--model", "-m",
    default=None,
    help="Generate descriptions for a specific model (by name). Omit for all models.",
)
@click.option(
    "--project-dir", "-p",
    default=".",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Path to the dbt project directory. Defaults to current directory.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Estimate token usage and cost without calling the LLM.",
)
def generate(model: str | None, project_dir: Path, dry_run: bool):
    """Generate model and column descriptions using an LLM.

    Reads your dbt manifest.json, sends model SQL and metadata to your
    configured LLM provider, and writes draft_<model>.yml files next to
    each model's .sql file.

    Prerequisites:
      1. Run 'dbt compile' or 'dbt run' first (to generate manifest.json)
      2. Configure .env with your LLM provider settings (see .env.example)
      3. Install provider SDK: pip install dbt-autodoc[anthropic] or [openai]
    """
    project_dir = project_dir.resolve()

    from dbt_autodoc.config import AutodocConfig

    config = AutodocConfig.from_env(project_dir=project_dir)

    if dry_run:
        click.echo("DRY RUN: Estimating costs without calling the LLM\n")

    click.echo(f"Provider: {config.provider}")
    click.echo(f"Model:    {config.model}")
    click.echo(f"Project:  {project_dir}")
    click.echo(f"Manifest: {config.manifest_path}\n")

    from dbt_autodoc.generator import generate_all

    results = generate_all(config, model_name=model, dry_run=dry_run)

    # Summary
    click.echo("\n" + "=" * 60)
    successes = [r for r in results if r.get("status") == "success"]
    errors = [r for r in results if r.get("status") == "error"]
    dry_runs = [r for r in results if r.get("status") == "dry_run"]

    if dry_runs:
        total_cost = sum(r["cost_estimate"]["estimated_cost_usd"] for r in dry_runs)
        click.echo(f"Estimated total cost: ${total_cost:.4f} for {len(dry_runs)} model(s)")
    elif successes:
        click.echo(f"Generated {len(successes)} draft file(s)")
        if errors:
            click.echo(f"Failed: {len(errors)} model(s)")
        click.echo("\nNext steps:")
        click.echo("  1. Review the draft_*.yml files next to your model .sql files")
        click.echo("  2. Copy approved descriptions into your schema .yml files")
        click.echo("  3. Delete the draft files")
    elif errors:
        click.echo(f"All {len(errors)} model(s) failed. Check errors above.")


@cli.command()
def providers():
    """List supported LLM providers and their documentation links."""
    from dbt_autodoc.config import SUPPORTED_PROVIDERS

    click.echo("Supported providers:\n")
    for name, info in SUPPORTED_PROVIDERS.items():
        click.echo(f"  {name}")
        click.echo(f"    SDK:           {info['sdk']}")
        click.echo(f"    Default model: {info.get('default_model', 'N/A (must specify)')}")
        click.echo(f"    Docs:          {info['docs']}")
        if info.get("requires_base_url"):
            click.echo("    Note:          Requires DBT_AUTODOC_BASE_URL")
        click.echo()


if __name__ == "__main__":
    cli()
