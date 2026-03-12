"""Orchestration logic: reads manifest, calls LLM or heuristics, writes drafts."""

from __future__ import annotations

from dbt_autodoc.config import AutodocConfig
from dbt_autodoc.heuristic import generate_heuristic_yaml
from dbt_autodoc.manifest import ManifestData, ModelInfo
from dbt_autodoc.prompt import SYSTEM_PROMPT, build_user_prompt
from dbt_autodoc.writer import extract_yaml_from_response, write_draft_file


def generate_for_model(
    model: ModelInfo,
    manifest: ManifestData,
    config: AutodocConfig | None = None,
    mode: str = "llm",
    dry_run: bool = False,
    project_dir=None,
) -> dict:
    """Generate descriptions for a single model. Returns result dict."""
    if mode == "heuristic":
        columns = [{"name": c.name, "data_type": c.data_type} for c in model.columns]
        yaml_content = generate_heuristic_yaml(model.name, columns)
        draft_path = write_draft_file(model, yaml_content, project_dir)
        return {
            "model": model.name,
            "status": "success",
            "draft_path": str(draft_path),
        }

    # LLM mode — requires config
    from dbt_autodoc.providers import get_provider

    provider = get_provider(config)

    upstream_context = manifest.get_upstream_context(model)
    user_prompt = build_user_prompt(model, upstream_context)

    if dry_run:
        cost = provider.estimate_cost(SYSTEM_PROMPT + user_prompt)
        return {
            "model": model.name,
            "status": "dry_run",
            "cost_estimate": cost,
        }

    response = provider.generate(SYSTEM_PROMPT, user_prompt)
    yaml_content = extract_yaml_from_response(response)
    draft_path = write_draft_file(model, yaml_content, config.dbt_project_dir)

    return {
        "model": model.name,
        "status": "success",
        "draft_path": str(draft_path),
    }


def generate_all(
    manifest_path,
    project_dir,
    config: AutodocConfig | None = None,
    model_name: str | None = None,
    mode: str = "llm",
    dry_run: bool = False,
) -> list[dict]:
    """Generate descriptions for one or all models."""
    manifest = ManifestData.from_file(manifest_path)

    if not manifest.models:
        return [{"status": "error", "message": "No models found in manifest.json"}]

    if model_name:
        model = manifest.get_model_by_name(model_name)
        if not model:
            available = [m.name for m in manifest.models.values()]
            return [
                {
                    "status": "error",
                    "message": f"Model '{model_name}' not found. Available: {', '.join(sorted(available))}",
                }
            ]
        models = [model]
    else:
        models = list(manifest.models.values())

    results = []
    total = len(models)

    for i, model in enumerate(sorted(models, key=lambda m: m.name), 1):
        print(f"[{i}/{total}] Processing {model.name}...")

        try:
            result = generate_for_model(
                model,
                manifest,
                config=config,
                mode=mode,
                dry_run=dry_run,
                project_dir=project_dir,
            )
            results.append(result)

            if result.get("draft_path"):
                print(f"  -> {result['draft_path']}")
            elif result.get("cost_estimate"):
                cost = result["cost_estimate"]
                print(
                    f"  -> ~{cost['input_tokens']} input tokens, "
                    f"~{cost['output_tokens']} output tokens, "
                    f"~${cost['estimated_cost_usd']}"
                )
        except Exception as e:
            results.append({"model": model.name, "status": "error", "message": str(e)})
            print(f"  -> ERROR: {e}")

    return results
