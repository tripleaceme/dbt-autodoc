"""Heuristic description generator — pattern-matches column and model names."""

from __future__ import annotations


def infer_column_description(column_name: str, data_type: str | None = None) -> str:
    """Infer a description from a column name and optional data type."""
    col = column_name.lower().strip()
    dtype = (data_type or "unknown").lower().strip()

    # --- Primary key patterns ---
    if col == "id":
        return "Unique identifier for the record"
    if col.endswith("_id"):
        entity = col[:-3].replace("_", " ")
        return f"Foreign key referencing the {entity} entity"
    if col.endswith("_pk"):
        entity = col[:-3].replace("_", " ")
        return f"Primary key for the {entity} entity"
    if col.endswith("_sk"):
        entity = col[:-3].replace("_", " ")
        return f"Surrogate key for the {entity} entity"
    if col.endswith(("_nk", "_bk")):
        entity = col[:-3].replace("_", " ")
        return f"Natural/business key for the {entity} entity"

    # --- Timestamp patterns ---
    if col in ("created_at", "creation_date", "date_created"):
        return "Timestamp when the record was created"
    if col in ("updated_at", "modified_at", "last_modified", "date_updated"):
        return "Timestamp when the record was last updated"
    if col in ("deleted_at", "date_deleted"):
        return "Timestamp when the record was soft-deleted"
    if col.endswith("_at"):
        action = col[:-3].replace("_", " ")
        return f"Timestamp when the record was {action}"
    if col.endswith("_date"):
        entity = col[:-5].replace("_", " ")
        return f"Date of the {entity}"
    if col.endswith("_datetime"):
        entity = col[:-9].replace("_", " ")
        return f"Date and time of the {entity}"
    if col.endswith("_timestamp"):
        entity = col[:-10].replace("_", " ")
        return f"Timestamp of the {entity}"

    # --- Boolean patterns ---
    if col.startswith("is_"):
        trait = col[3:].replace("_", " ")
        return f"Boolean flag indicating whether the record is {trait}"
    if col.startswith("has_"):
        trait = col[4:].replace("_", " ")
        return f"Boolean flag indicating whether the record has {trait}"
    if col.startswith("can_"):
        trait = col[4:].replace("_", " ")
        return f"Boolean flag indicating whether the record can {trait}"
    if col.startswith("should_"):
        trait = col[7:].replace("_", " ")
        return f"Boolean flag indicating whether the record should {trait}"

    # --- Count / amount patterns ---
    if col.startswith("num_"):
        entity = col[4:].replace("_", " ")
        return f"Count of {entity}"
    if col.startswith("number_of_"):
        entity = col[10:].replace("_", " ")
        return f"Count of {entity}"
    if col.endswith("_count"):
        entity = col[:-6].replace("_", " ")
        return f"Count of {entity}"
    if col.startswith("total_"):
        entity = col[6:].replace("_", " ")
        return f"Total aggregated {entity}"
    if col.startswith("sum_"):
        entity = col[4:].replace("_", " ")
        return f"Sum of {entity}"
    if col.startswith(("avg_", "average_")):
        entity = col.replace("avg_", "").replace("average_", "").replace("_", " ")
        return f"Average value of {entity}"
    if col.startswith("min_"):
        entity = col[4:].replace("_", " ")
        return f"Minimum value of {entity}"
    if col.startswith("max_"):
        entity = col[4:].replace("_", " ")
        return f"Maximum value of {entity}"

    # --- Financial / metric patterns ---
    if col.endswith(("_amount", "_amt")):
        entity = col.replace("_amount", "").replace("_amt", "").replace("_", " ")
        return f"Monetary amount for {entity}"
    if col.endswith("_price"):
        entity = col[:-6].replace("_", " ")
        return f"Price of the {entity}"
    if col.endswith("_cost"):
        entity = col[:-5].replace("_", " ")
        return f"Cost of the {entity}"
    if col.endswith("_rate"):
        entity = col[:-5].replace("_", " ")
        return f"Rate of {entity}"
    if col.endswith(("_pct", "_percent", "_percentage")):
        entity = (
            col.replace("_percentage", "")
            .replace("_percent", "")
            .replace("_pct", "")
            .replace("_", " ")
        )
        return f"Percentage value of {entity}"
    if col.endswith("_ratio"):
        entity = col[:-6].replace("_", " ")
        return f"Ratio of {entity}"
    if col == "revenue":
        return "Revenue amount"
    if col == "profit":
        return "Profit amount"

    # --- Status / type / category patterns ---
    if col.endswith("_status"):
        entity = col[:-7].replace("_", " ")
        return f"Current status of the {entity}"
    if col.endswith("_type"):
        entity = col[:-5].replace("_", " ")
        return f"Type or category of the {entity}"
    if col.endswith("_category"):
        entity = col[:-9].replace("_", " ")
        return f"Category of the {entity}"
    if col == "status":
        return "Current status of the record"
    if col == "type":
        return "Type or category of the record"

    # --- Name / label patterns ---
    if col in ("name", "full_name"):
        return "Full name"
    if col == "first_name":
        return "First name"
    if col == "last_name":
        return "Last name or surname"
    if col.endswith("_name"):
        entity = col[:-5].replace("_", " ")
        return f"Name of the {entity}"
    if col == "label" or col.endswith("_label"):
        entity = col.replace("_label", "").replace("_", " ")
        return f"Display label for {entity}"
    if col == "title":
        return "Title or heading"
    if col == "description":
        return "Free-text description"

    # --- Contact patterns ---
    if col in ("email", "email_address"):
        return "Email address"
    if col in ("phone", "phone_number"):
        return "Phone number"
    if col == "address":
        return "Street address"
    if col == "city":
        return "City name"
    if col in ("state", "state_code"):
        return "State or province"
    if col in ("country", "country_code"):
        return "Country or country code"
    if col in ("zip", "zip_code", "postal_code"):
        return "Postal or ZIP code"

    # --- URL / path patterns ---
    if col == "url":
        return "URL"
    if col.endswith("_url"):
        entity = col[:-4].replace("_", " ")
        return f"URL for {entity}"
    if col.endswith("_path"):
        entity = col[:-5].replace("_", " ")
        return f"File or resource path for {entity}"

    # --- Rank / order patterns ---
    if col.endswith("_rank"):
        entity = col[:-5].replace("_", " ")
        return f"Rank or position by {entity}"
    if col in ("row_number", "rn"):
        return "Row number used for ordering or deduplication"
    if col.endswith("_order") or col == "sort_order":
        return "Sort or display order"

    # --- Duration patterns ---
    if col.endswith("_days"):
        entity = col[:-5].replace("_", " ")
        return f"Duration in days for {entity}"
    if col.endswith("_hours"):
        entity = col[:-6].replace("_", " ")
        return f"Duration in hours for {entity}"
    if col.endswith(("_minutes", "_mins")):
        entity = col.replace("_minutes", "").replace("_mins", "").replace("_", " ")
        return f"Duration in minutes for {entity}"
    if col.endswith(("_seconds", "_secs")):
        entity = col.replace("_seconds", "").replace("_secs", "").replace("_", " ")
        return f"Duration in seconds for {entity}"

    # --- Common standalone columns ---
    if col in ("quantity", "qty"):
        return "Quantity or number of items"
    if col in ("currency", "currency_code"):
        return "Currency code (e.g. USD, EUR)"
    if col == "version":
        return "Version number of the record"
    if col in ("source", "data_source"):
        return "Origin or source system of the data"
    if col in ("notes", "comments"):
        return "Free-text notes or comments"
    if col == "metadata":
        return "Additional metadata stored as structured data"
    if col == "tags":
        return "Tags or labels associated with the record"

    # --- dbt / ETL meta columns ---
    if col == "_fivetran_synced":
        return "Timestamp when Fivetran last synced this record"
    if col == "_fivetran_deleted":
        return "Boolean flag indicating if Fivetran marked this record as deleted"
    if col == "_airbyte_extracted_at":
        return "Timestamp when Airbyte extracted this record"
    if col in ("_loaded_at", "_etl_loaded_at"):
        return "Timestamp when the record was loaded into the warehouse"
    if col == "dbt_scd_id":
        return "dbt snapshot surrogate key"
    if col == "dbt_updated_at":
        return "Timestamp used by dbt snapshot to track changes"
    if col == "dbt_valid_from":
        return "Start of validity period for this snapshot record"
    if col == "dbt_valid_to":
        return "End of validity period for this snapshot record (null if current)"

    # --- Fallback: data type hint ---
    if "bool" in dtype:
        return f"Boolean flag: {col.replace('_', ' ')}"
    if any(t in dtype for t in ("date", "time")):
        return f"Date/time value: {col.replace('_', ' ')}"
    if any(t in dtype for t in ("int", "float", "numeric", "decimal", "number")):
        return f"Numeric value: {col.replace('_', ' ')}"
    if "json" in dtype:
        return f"JSON data: {col.replace('_', ' ')}"

    return f"TODO: Add description for {col.replace('_', ' ')}"


def infer_model_description(model_name: str) -> str:
    """Infer a model description from the model name using dbt naming conventions."""
    name = model_name.lower().strip()

    # --- Prefix-based patterns ---
    prefix_patterns = [
        ("stg_", 4, "Staging model that cleans and standardizes raw {entity} data"),
        ("int_", 4, "Intermediate model that transforms and joins {entity} data"),
        ("fct_", 4, "Fact table recording {entity} events or transactions"),
        ("fact_", 5, "Fact table recording {entity} events or transactions"),
        ("dim_", 4, "Dimension table containing {entity} attributes and descriptors"),
        ("rpt_", 4, "Report model providing aggregated view of {entity}"),
        ("report_", 7, "Report model providing aggregated view of {entity}"),
        ("agg_", 4, "Aggregated model summarizing {entity} metrics"),
        ("mart_", 5, "Data mart providing business-ready {entity} data"),
        ("mrt_", 4, "Data mart providing business-ready {entity} data"),
        ("base_", 5, "Base model providing foundational {entity} data"),
        ("snapshot_", 9, "Snapshot model tracking historical changes to {entity}"),
        ("snp_", 4, "Snapshot model tracking historical changes to {entity}"),
        ("seed_", 5, "Seed data containing reference {entity} values"),
        ("src_", 4, "Source model representing raw {entity} data from upstream systems"),
        ("bridge_", 7, "Bridge table resolving many-to-many relationships for {entity}"),
        ("brg_", 4, "Bridge table resolving many-to-many relationships for {entity}"),
        ("map_", 4, "Mapping table linking {entity} across different systems or domains"),
        ("mapping_", 8, "Mapping table linking {entity} across different systems or domains"),
        ("xref_", 5, "Mapping table linking {entity} across different systems or domains"),
        ("tmp_", 4, "Temporary model used for intermediate processing of {entity}"),
        ("temp_", 5, "Temporary model used for intermediate processing of {entity}"),
    ]

    for prefix, length, template in prefix_patterns:
        if name.startswith(prefix):
            entity = name[length:].replace("_", " ").title()
            return template.format(entity=entity)

    # --- Suffix-based patterns ---
    if name.endswith("_summary"):
        entity = name[:-8].replace("_", " ").title()
        return f"Summary model aggregating key metrics for {entity}"

    for suffix in ("_daily", "_monthly", "_weekly", "_yearly"):
        if name.endswith(suffix):
            entity = name[: -len(suffix)].replace("_", " ").title()
            grain = suffix[1:]  # remove leading underscore
            return f"{entity} data aggregated at the {grain} grain"

    if name.endswith("_snapshot"):
        entity = name[:-9].replace("_", " ").title()
        return f"Point-in-time snapshot of {entity} data"

    if name.endswith(("_pivot", "_pivoted")):
        entity = name.replace("_pivoted", "").replace("_pivot", "").replace("_", " ").title()
        return f"Pivoted view of {entity} data"

    if name.endswith(("_unioned", "_combined")):
        entity = (
            name.replace("_unioned", "").replace("_combined", "").replace("_", " ").title()
        )
        return f"Combined model unioning multiple {entity} sources"

    # --- Fallback ---
    entity = name.replace("_", " ").title()
    return f"TODO: Add description for {entity} model"


def generate_heuristic_yaml(model_name: str, columns: list[dict]) -> str:
    """Generate a complete YAML block using heuristic inference.

    Args:
        model_name: The dbt model name.
        columns: List of dicts with 'name' and optional 'data_type' keys.

    Returns:
        YAML string ready to write to a draft file.
    """
    model_desc = infer_model_description(model_name)

    lines = [
        f"  - name: {model_name}",
        f'    description: "{model_desc}"',
    ]

    if columns:
        lines.append("    columns:")
        for col in columns:
            col_desc = infer_column_description(col["name"], col.get("data_type"))
            lines.append(f"      - name: {col['name']}")
            lines.append(f'        description: "{col_desc}"')

    return "\n".join(lines)
