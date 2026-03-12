# dbt-autodoc

Auto-generate dbt model and column descriptions using heuristics or LLMs.

Stop staring at blank `description: ""` fields. `dbt-autodoc` generates draft descriptions for your models and columns in two ways:

1. **Heuristic mode** — infers descriptions from naming conventions (no API key needed)
2. **LLM mode** — reads your model SQL and sends it to an LLM for context-aware descriptions

Both modes write `draft_<modelname>.yml` files next to your model's `.sql` file for human review.

## Installation

```bash
# Heuristic mode only (no API key needed)
pip install "dbt-autodoc @ git+https://github.com/tripleaceme/dbt-autodoc.git"

# With Claude support
pip install "dbt-autodoc[anthropic] @ git+https://github.com/tripleaceme/dbt-autodoc.git"

# With OpenAI / OpenAI-compatible support
pip install "dbt-autodoc[openai] @ git+https://github.com/tripleaceme/dbt-autodoc.git"

# Both LLM providers
pip install "dbt-autodoc[all] @ git+https://github.com/tripleaceme/dbt-autodoc.git"
```

You can also use it as a dbt package (macros only, prints to stdout):

```yaml
# packages.yml
packages:
  - git: "https://github.com/tripleaceme/dbt-autodoc.git"
    revision: master
```

## Quick Start

**Prerequisite:** Run `dbt compile` or `dbt run` first (to generate `manifest.json`).

### Heuristic Mode (No API Key Needed)

```bash
# Generate draft files for all models
dbt-autodoc generate --mode heuristic

# Generate for a single model
dbt-autodoc generate --mode heuristic -m stg_orders
```

### LLM Mode

**1. Configure your provider** — copy `.env.example` to `.env` in your dbt project root:

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

### dbt Macro (Alternative)

The dbt macro prints to stdout instead of writing files:

```bash
dbt run-operation generate_descriptions
dbt run-operation generate_descriptions --args '{model_name: stg_orders}'
```

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

Parses column and model names against 50+ patterns:

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
  generate   Generate model and column descriptions
  providers  List supported LLM providers and their documentation links

Generate Options:
  -m, --model TEXT         Generate for a specific model (by name)
  -p, --project-dir PATH  Path to dbt project directory (default: .)
  --mode [llm|heuristic]   Generation mode (default: llm)
  --dry-run                Estimate cost without calling the LLM (llm mode only)
  --version                Show version
  --help                   Show help
```

## Requirements

- **dbt**: >= 1.6.0, < 2.0.0
- **Python**: >= 3.9 (for LLM mode)
- **manifest.json**: Run `dbt compile` before using LLM mode

## License

MIT
