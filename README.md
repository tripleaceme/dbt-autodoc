# dbt-autodoc

Auto-generate dbt model and column descriptions using heuristics or LLMs.

Stop staring at blank `description: ""` fields. `dbt-autodoc` generates draft descriptions for your models and columns in two ways:

1. **Heuristic mode** — a dbt macro that infers descriptions from naming conventions (no API key, no Python)
2. **LLM mode** — a Python CLI that reads your model SQL and sends it to an LLM for context-aware descriptions

Both modes write `draft_<modelname>.yml` files next to your model's `.sql` file for human review.

## Installation

### Heuristic Mode (dbt Package Only)

Add to your `packages.yml`:

```yaml
packages:
  - git: "https://github.com/tripleaceme/dbt-autodoc.git"
    revision: v1.0.0
```

```bash
dbt deps
```

No Python, no API key — just dbt.

### LLM Mode (Python CLI)

```bash
# With Claude support
pip install "dbt-autodoc[anthropic] @ git+https://github.com/tripleaceme/dbt-autodoc.git"

# With OpenAI / OpenAI-compatible support
pip install "dbt-autodoc[openai] @ git+https://github.com/tripleaceme/dbt-autodoc.git"

# Both LLM providers
pip install "dbt-autodoc[all] @ git+https://github.com/tripleaceme/dbt-autodoc.git"
```

## Quick Start

### Heuristic Mode (No API Key Needed)

**Prerequisite:** Models must be materialized in the database (run `dbt run` first).

Copy `dbt_autodoc.sh` from the package into your dbt project root, then:

```bash
# Write a draft file for a single model (writes draft_stg_orders.yml next to stg_orders.sql)
./dbt_autodoc.sh stg_orders

# Write drafts for all models to a single file
./dbt_autodoc.sh --all

# Or just print to terminal to review first
dbt run-operation generate_descriptions --args '{model_name: stg_orders}'
```

The shell script runs `dbt run-operation` under the hood and strips dbt's log noise, writing clean YAML to a `draft_<model>.yml` file next to the model's `.sql` file.

### LLM Mode

**Prerequisite:** Run `dbt compile` or `dbt run` first (to generate `manifest.json`).

**1. Configure your provider** — create a `.env` file in your **dbt project root directory** (where your `dbt_project.yml` lives, **not** inside `dbt_packages/`):

```env
DBT_AUTODOC_PROVIDER=anthropic
DBT_AUTODOC_API_KEY=sk-ant-...
DBT_AUTODOC_MODEL=claude-sonnet-4-6
```

**2. Generate descriptions**

```bash
# Estimate cost first (no API calls)
dbt-autodoc generate --dry-run

# Generate for all models
dbt-autodoc generate

# Generate for a single model
dbt-autodoc generate -m stg_orders

# Specify a different project directory
dbt-autodoc generate -p /path/to/dbt/project
```

### Output

Both modes create `draft_<modelname>.yml` files next to each model's `.sql` file:

```
models/
├── staging/
│   ├── stg_orders.sql
│   ├── stg_orders.yml          ← your existing schema
│   └── draft_stg_orders.yml    ← generated draft (review & merge)
```

**Review, merge, delete:**

1. Review the draft descriptions
2. Copy approved descriptions into your schema `.yml` files
3. Delete the `draft_*.yml` files

## Supported LLM Providers

| Provider | `DBT_AUTODOC_PROVIDER` | SDK | Docs |
|---|---|---|---|
| Anthropic (Claude) | `anthropic` | `anthropic` | [Models](https://docs.anthropic.com/en/docs/about-claude/models) |
| OpenAI | `openai` | `openai` | [Models](https://platform.openai.com/docs/models) |
| DeepSeek | `openai_compatible` | `openai` | [API Docs](https://platform.deepseek.com/api-docs) |
| Perplexity | `openai_compatible` | `openai` | [Model Cards](https://docs.perplexity.ai/guides/model-cards) |
| Google Gemini | `openai_compatible` | `openai` | [Models](https://ai.google.dev/gemini-api/docs/models) |
| Groq | `openai_compatible` | `openai` | [Models](https://console.groq.com/docs/models) |
| Ollama (local) | `openai_compatible` | `openai` | [Library](https://ollama.com/library) |

For `openai_compatible` providers, also set `DBT_AUTODOC_BASE_URL`. See [.env.example](.env.example) for full configuration examples.

```bash
# List all providers from the CLI
dbt-autodoc providers
```

## How It Works

### Heuristic Mode

A pure dbt macro that queries `information_schema` for column names and data types, then pattern-matches against 50+ naming conventions:

| Pattern | Example | Generated Description |
|---|---|---|
| `*_id` | `user_id` | Foreign key referencing the user entity |
| `is_*` | `is_active` | Boolean flag indicating whether the record is active |
| `*_at` | `created_at` | Timestamp when the record was created |
| `total_*` | `total_revenue` | Total aggregated revenue |
| `*_status` | `order_status` | Current status of the order |
| `stg_*` | `stg_orders` | Staging model that cleans and standardizes raw Orders data |
| `fct_*` | `fct_sales` | Fact table recording Sales events or transactions |
| `dim_*` | `dim_customers` | Dimension table containing Customers attributes and descriptors |

Columns that don't match any pattern get a `TODO:` prefix so you can find and fill them in.

### LLM Mode

Sends rich context to your LLM for each model:

1. **Model SQL** — the actual transformation logic (compiled if available)
2. **Column names and data types** — from `manifest.json`
3. **Upstream model descriptions** — for domain context
4. **Model layer** — inferred from naming convention (staging, intermediate, mart, etc.)
5. **Existing descriptions** — so the LLM preserves what you've already written

The LLM returns structured YAML which is written as a draft file.

## Accuracy Expectations

| Mode | Accuracy | Best For |
|---|---|---|
| Heuristic | ~40-60% | Convention-heavy projects, quick drafts, no API key needed |
| LLM | ~80-90% | Complex models, domain-specific columns, production-quality drafts |

**Neither mode should be trusted blindly.** Both generate drafts for human review. The value is eliminating the blank-page problem — going from 0% documented to ~70% documented in minutes.

## CLI Reference

```
Usage: dbt-autodoc [OPTIONS] COMMAND [ARGS]...

Commands:
  generate   Generate model and column descriptions using an LLM
  providers  List supported LLM providers and their documentation links

Generate Options:
  -m, --model TEXT         Generate for a specific model (by name)
  -p, --project-dir PATH  Path to dbt project directory (default: .)
  --dry-run                Estimate cost without calling the LLM
  --version                Show version
  --help                   Show help
```

## Requirements

- **Heuristic mode**: dbt >= 1.6.0, < 2.0.0 (no Python needed)
- **LLM mode**: Python >= 3.9 + `manifest.json` (run `dbt compile` first)

## License

MIT
