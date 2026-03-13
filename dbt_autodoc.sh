#!/usr/bin/env bash
# =============================================================================
# dbt-autodoc: Generate draft YAML descriptions (heuristic mode)
#
# Usage:
#   ./dbt_autodoc.sh stg_orders              # single model → draft file
#   ./dbt_autodoc.sh                          # all models → print to terminal
#   ./dbt_autodoc.sh --all                    # all models → draft_all_models.yml
#
# The script runs dbt run-operation, strips ANSI color codes and dbt log lines,
# and writes clean YAML to a draft file next to the model's .sql file.
# =============================================================================

set -uo pipefail

MODEL_NAME="${1:-}"

if [[ -z "$MODEL_NAME" ]]; then
    echo "Usage: ./dbt_autodoc.sh <model_name>    # writes draft_<model>.yml"
    echo "       ./dbt_autodoc.sh --all            # writes draft_all_models.yml"
    exit 0
fi

# Strip dbt log prefix and noise, keeping only YAML content
# dbt 1.11.x prefixes every line with ESC[0m + "HH:MM:SS  "
strip_dbt_noise() {
    # Remove ANSI escape + timestamp prefix, then filter dbt noise lines
    sed "s/$(printf '\033')\[[0-9;]*m//g" \
      | sed 's/^[0-9][0-9]:[0-9][0-9]:[0-9][0-9]  //' \
      | grep -v '^Running with dbt=' \
      | grep -v '^Registered adapter:' \
      | grep -v '^Found [0-9]' \
      | grep -v '^dbt-autodoc:' \
      | grep -v '^Finished running' \
      | grep -v '^Completed successfully' \
      | grep -v '^Done\.' \
      | grep -v '^Concurrency:'
}

if [[ "$MODEL_NAME" == "--all" ]]; then
    echo "Generating descriptions for all models..."
    dbt run-operation generate_descriptions 2>/dev/null | strip_dbt_noise > draft_all_models.yml
    echo "Written to: draft_all_models.yml"
else
    # Find the model's .sql file to determine the output path
    MODEL_SQL=$(find models -name "${MODEL_NAME}.sql" 2>/dev/null | head -1)

    if [[ -z "$MODEL_SQL" ]]; then
        echo "Error: Could not find models/${MODEL_NAME}.sql"
        echo "Make sure you're in your dbt project root directory."
        exit 1
    fi

    MODEL_DIR=$(dirname "$MODEL_SQL")
    OUTPUT_FILE="${MODEL_DIR}/draft_${MODEL_NAME}.yml"

    echo "Generating descriptions for ${MODEL_NAME}..."
    dbt run-operation generate_descriptions --args "{model_name: ${MODEL_NAME}}" 2>/dev/null | strip_dbt_noise > "$OUTPUT_FILE"
    echo "Written to: ${OUTPUT_FILE}"
fi
