"""Parse dbt manifest.json to extract model metadata."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ColumnInfo:
    name: str
    data_type: str | None = None
    description: str = ""


@dataclass
class ModelInfo:
    unique_id: str
    name: str
    description: str = ""
    schema: str = ""
    database: str = ""
    resource_type: str = "model"
    original_file_path: str = ""
    raw_code: str = ""
    compiled_code: str = ""
    columns: list[ColumnInfo] = field(default_factory=list)
    depends_on_nodes: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    @property
    def layer(self) -> str:
        """Infer the model layer from naming convention."""
        prefix_map = {
            "stg_": "staging",
            "int_": "intermediate",
            "fct_": "fact",
            "fact_": "fact",
            "dim_": "dimension",
            "rpt_": "report",
            "agg_": "aggregate",
            "mart_": "mart",
            "mrt_": "mart",
            "base_": "base",
            "src_": "source",
        }
        for prefix, layer in prefix_map.items():
            if self.name.startswith(prefix):
                return layer
        return "unknown"


@dataclass
class ManifestData:
    models: dict[str, ModelInfo] = field(default_factory=dict)
    project_name: str = ""

    @classmethod
    def from_file(cls, manifest_path: Path) -> ManifestData:
        """Parse a manifest.json file and extract model information."""
        if not manifest_path.exists():
            raise FileNotFoundError(
                f"manifest.json not found at {manifest_path}\n"
                "Run 'dbt compile' or 'dbt run' first to generate it."
            )

        with open(manifest_path) as f:
            raw = json.load(f)

        data = cls()

        # Extract project name from metadata
        metadata = raw.get("metadata", {})
        data.project_name = metadata.get("project_name", "")

        # Parse nodes
        for node_id, node in raw.get("nodes", {}).items():
            if node.get("resource_type") != "model":
                continue

            # Only include models from the user's project, not packages
            if node.get("package_name") != data.project_name:
                continue

            columns = []
            for col_name, col_data in node.get("columns", {}).items():
                columns.append(
                    ColumnInfo(
                        name=col_name,
                        data_type=col_data.get("data_type"),
                        description=col_data.get("description", ""),
                    )
                )

            model = ModelInfo(
                unique_id=node_id,
                name=node.get("name", ""),
                description=node.get("description", ""),
                schema=node.get("schema", ""),
                database=node.get("database", ""),
                resource_type=node.get("resource_type", "model"),
                original_file_path=node.get("original_file_path", ""),
                raw_code=node.get("raw_code", ""),
                compiled_code=node.get("compiled_code", ""),
                columns=columns,
                depends_on_nodes=node.get("depends_on", {}).get("nodes", []),
                tags=node.get("tags", []),
            )

            data.models[node_id] = model

        return data

    def get_model_by_name(self, name: str) -> ModelInfo | None:
        """Find a model by its short name."""
        for model in self.models.values():
            if model.name == name:
                return model
        return None

    def get_upstream_context(self, model: ModelInfo) -> list[dict]:
        """Get descriptions of upstream models for richer context."""
        upstream = []
        for dep_id in model.depends_on_nodes:
            if dep_id in self.models:
                dep = self.models[dep_id]
                upstream.append(
                    {
                        "name": dep.name,
                        "description": dep.description,
                        "columns": [
                            {"name": c.name, "description": c.description}
                            for c in dep.columns
                            if c.description
                        ],
                    }
                )
        return upstream
