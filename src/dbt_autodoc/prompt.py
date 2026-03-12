"""LLM prompt templates for generating dbt model descriptions."""

from __future__ import annotations

from dbt_autodoc.manifest import ModelInfo

SYSTEM_PROMPT = """\
You are an expert analytics engineer who writes clear, concise dbt model and column \
descriptions. Your descriptions are:

- Written for a data consumer (analyst, stakeholder) who needs to understand what the \
data represents
- Specific and factual — based only on what you can see in the SQL logic and context
- Concise — one to two sentences max per description
- Written in plain English, avoiding jargon unless it's domain-appropriate
- Never speculative — if you cannot determine the purpose, say \
"TODO: Verify purpose of this column/model"

Important rules:
- Do NOT wrap descriptions in quotes
- Do NOT include the column name in the description (e.g., for column "user_id", \
don't start with "User ID is...")
- For boolean columns, describe what true/false means
- For foreign keys, mention what entity they reference
- For timestamps, specify the event they capture
- For aggregated columns, mention the aggregation logic if visible in the SQL
"""


def build_user_prompt(model: ModelInfo, upstream_context: list[dict]) -> str:
    """Build the user prompt with model context for the LLM."""
    sections = []

    # Model identity
    sections.append(f"## Model: `{model.name}`")
    sections.append(f"**Layer:** {model.layer}")
    sections.append(f"**Schema:** {model.schema}")

    if model.description:
        sections.append(f"**Existing description:** {model.description}")

    # SQL code
    code = model.compiled_code or model.raw_code
    if code:
        sections.append(f"\n## SQL Code\n```sql\n{code.strip()}\n```")

    # Column information
    if model.columns:
        sections.append("\n## Known Columns")
        for col in model.columns:
            line = f"- `{col.name}`"
            if col.data_type:
                line += f" ({col.data_type})"
            if col.description:
                line += f" — existing description: \"{col.description}\""
            sections.append(line)

    # Upstream context
    if upstream_context:
        sections.append("\n## Upstream Models (for context)")
        for up in upstream_context:
            sections.append(f"\n### `{up['name']}`")
            if up.get("description"):
                sections.append(f"Description: {up['description']}")
            if up.get("columns"):
                for c in up["columns"][:10]:  # Limit to avoid token bloat
                    sections.append(f"- `{c['name']}`: {c['description']}")

    # Instructions
    sections.append("\n## Task")
    sections.append(
        "Generate a YAML block with a model description and descriptions for every "
        "column. If a column already has a description, keep it unless it's clearly "
        "wrong or incomplete.\n"
        "\nRespond with ONLY the YAML block in this exact format, no extra text:\n"
        "```yaml\n"
        f"  - name: {model.name}\n"
        '    description: "Your model description here"\n'
        "    columns:\n"
        '      - name: column_name\n'
        '        description: "Your column description here"\n'
        "```"
    )

    return "\n".join(sections)
