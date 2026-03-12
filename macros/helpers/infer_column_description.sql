{% macro infer_column_description(column_name, data_type) %}
    {#
        Infers a human-readable description from a column name and data type
        using common naming conventions and patterns.

        Returns a string description or 'No description available.' if no pattern matches.
    #}

    {% set col = column_name | lower | trim %}
    {% set dtype = (data_type | default('unknown') | lower | trim) %}
    {% set description = '' %}

    {# --- Primary key patterns --- #}
    {% if col == 'id' %}
        {% set description = 'Unique identifier for the record' %}
    {% elif col.endswith('_id') %}
        {% set entity = col[:-3] | replace('_', ' ') %}
        {% set description = 'Foreign key referencing the ' ~ entity ~ ' entity' %}
    {% elif col.endswith('_pk') %}
        {% set entity = col[:-3] | replace('_', ' ') %}
        {% set description = 'Primary key for the ' ~ entity ~ ' entity' %}
    {% elif col.endswith('_sk') %}
        {% set entity = col[:-3] | replace('_', ' ') %}
        {% set description = 'Surrogate key for the ' ~ entity ~ ' entity' %}
    {% elif col.endswith('_nk') or col.endswith('_bk') %}
        {% set entity = col[:-3] | replace('_', ' ') %}
        {% set description = 'Natural/business key for the ' ~ entity ~ ' entity' %}

    {# --- Timestamp patterns --- #}
    {% elif col == 'created_at' or col == 'creation_date' or col == 'date_created' %}
        {% set description = 'Timestamp when the record was created' %}
    {% elif col == 'updated_at' or col == 'modified_at' or col == 'last_modified' or col == 'date_updated' %}
        {% set description = 'Timestamp when the record was last updated' %}
    {% elif col == 'deleted_at' or col == 'date_deleted' %}
        {% set description = 'Timestamp when the record was soft-deleted' %}
    {% elif col.endswith('_at') %}
        {% set action = col[:-3] | replace('_', ' ') %}
        {% set description = 'Timestamp when the record was ' ~ action %}
    {% elif col.endswith('_date') %}
        {% set entity = col[:-5] | replace('_', ' ') %}
        {% set description = 'Date of the ' ~ entity %}
    {% elif col.endswith('_datetime') %}
        {% set entity = col[:-9] | replace('_', ' ') %}
        {% set description = 'Date and time of the ' ~ entity %}
    {% elif col.endswith('_timestamp') %}
        {% set entity = col[:-10] | replace('_', ' ') %}
        {% set description = 'Timestamp of the ' ~ entity %}

    {# --- Boolean patterns --- #}
    {% elif col.startswith('is_') %}
        {% set trait = col[3:] | replace('_', ' ') %}
        {% set description = 'Boolean flag indicating whether the record is ' ~ trait %}
    {% elif col.startswith('has_') %}
        {% set trait = col[4:] | replace('_', ' ') %}
        {% set description = 'Boolean flag indicating whether the record has ' ~ trait %}
    {% elif col.startswith('can_') %}
        {% set trait = col[4:] | replace('_', ' ') %}
        {% set description = 'Boolean flag indicating whether the record can ' ~ trait %}
    {% elif col.startswith('should_') %}
        {% set trait = col[7:] | replace('_', ' ') %}
        {% set description = 'Boolean flag indicating whether the record should ' ~ trait %}

    {# --- Count / amount patterns --- #}
    {% elif col.startswith('num_') or col.startswith('number_of_') %}
        {% set entity = col | replace('num_', '') | replace('number_of_', '') | replace('_', ' ') %}
        {% set description = 'Count of ' ~ entity %}
    {% elif col.endswith('_count') %}
        {% set entity = col[:-6] | replace('_', ' ') %}
        {% set description = 'Count of ' ~ entity %}
    {% elif col.startswith('total_') %}
        {% set entity = col[6:] | replace('_', ' ') %}
        {% set description = 'Total aggregated ' ~ entity %}
    {% elif col.startswith('sum_') %}
        {% set entity = col[4:] | replace('_', ' ') %}
        {% set description = 'Sum of ' ~ entity %}
    {% elif col.startswith('avg_') or col.startswith('average_') %}
        {% set entity = col | replace('avg_', '') | replace('average_', '') | replace('_', ' ') %}
        {% set description = 'Average value of ' ~ entity %}
    {% elif col.startswith('min_') %}
        {% set entity = col[4:] | replace('_', ' ') %}
        {% set description = 'Minimum value of ' ~ entity %}
    {% elif col.startswith('max_') %}
        {% set entity = col[4:] | replace('_', ' ') %}
        {% set description = 'Maximum value of ' ~ entity %}

    {# --- Financial / metric patterns --- #}
    {% elif col.endswith('_amount') or col.endswith('_amt') %}
        {% set entity = col | replace('_amount', '') | replace('_amt', '') | replace('_', ' ') %}
        {% set description = 'Monetary amount for ' ~ entity %}
    {% elif col.endswith('_price') %}
        {% set entity = col[:-6] | replace('_', ' ') %}
        {% set description = 'Price of the ' ~ entity %}
    {% elif col.endswith('_cost') %}
        {% set entity = col[:-5] | replace('_', ' ') %}
        {% set description = 'Cost of the ' ~ entity %}
    {% elif col.endswith('_rate') %}
        {% set entity = col[:-5] | replace('_', ' ') %}
        {% set description = 'Rate of ' ~ entity %}
    {% elif col.endswith('_pct') or col.endswith('_percent') or col.endswith('_percentage') %}
        {% set entity = col | replace('_percentage', '') | replace('_percent', '') | replace('_pct', '') | replace('_', ' ') %}
        {% set description = 'Percentage value of ' ~ entity %}
    {% elif col.endswith('_ratio') %}
        {% set entity = col[:-6] | replace('_', ' ') %}
        {% set description = 'Ratio of ' ~ entity %}
    {% elif col == 'revenue' %}
        {% set description = 'Revenue amount' %}
    {% elif col == 'profit' %}
        {% set description = 'Profit amount' %}

    {# --- Status / type / category patterns --- #}
    {% elif col.endswith('_status') %}
        {% set entity = col[:-7] | replace('_', ' ') %}
        {% set description = 'Current status of the ' ~ entity %}
    {% elif col.endswith('_type') %}
        {% set entity = col[:-5] | replace('_', ' ') %}
        {% set description = 'Type or category of the ' ~ entity %}
    {% elif col.endswith('_category') %}
        {% set entity = col[:-9] | replace('_', ' ') %}
        {% set description = 'Category of the ' ~ entity %}
    {% elif col == 'status' %}
        {% set description = 'Current status of the record' %}
    {% elif col == 'type' %}
        {% set description = 'Type or category of the record' %}

    {# --- Name / label patterns --- #}
    {% elif col == 'name' or col == 'full_name' %}
        {% set description = 'Full name' %}
    {% elif col == 'first_name' %}
        {% set description = 'First name' %}
    {% elif col == 'last_name' %}
        {% set description = 'Last name or surname' %}
    {% elif col.endswith('_name') %}
        {% set entity = col[:-5] | replace('_', ' ') %}
        {% set description = 'Name of the ' ~ entity %}
    {% elif col == 'label' or col.endswith('_label') %}
        {% set entity = col | replace('_label', '') | replace('_', ' ') %}
        {% set description = 'Display label for ' ~ entity %}
    {% elif col == 'title' %}
        {% set description = 'Title or heading' %}
    {% elif col == 'description' %}
        {% set description = 'Free-text description' %}

    {# --- Contact patterns --- #}
    {% elif col == 'email' or col == 'email_address' %}
        {% set description = 'Email address' %}
    {% elif col == 'phone' or col == 'phone_number' %}
        {% set description = 'Phone number' %}
    {% elif col == 'address' %}
        {% set description = 'Street address' %}
    {% elif col == 'city' %}
        {% set description = 'City name' %}
    {% elif col == 'state' or col == 'state_code' %}
        {% set description = 'State or province' %}
    {% elif col == 'country' or col == 'country_code' %}
        {% set description = 'Country or country code' %}
    {% elif col == 'zip' or col == 'zip_code' or col == 'postal_code' %}
        {% set description = 'Postal or ZIP code' %}

    {# --- URL / path patterns --- #}
    {% elif col.endswith('_url') or col == 'url' %}
        {% set entity = col | replace('_url', '') | replace('_', ' ') %}
        {% set description = 'URL for ' ~ entity if entity else 'URL' %}
    {% elif col.endswith('_path') %}
        {% set entity = col[:-5] | replace('_', ' ') %}
        {% set description = 'File or resource path for ' ~ entity %}

    {# --- Rank / order patterns --- #}
    {% elif col.endswith('_rank') %}
        {% set entity = col[:-5] | replace('_', ' ') %}
        {% set description = 'Rank or position by ' ~ entity %}
    {% elif col == 'row_number' or col == 'rn' %}
        {% set description = 'Row number used for ordering or deduplication' %}
    {% elif col.endswith('_order') or col == 'sort_order' %}
        {% set description = 'Sort or display order' %}

    {# --- Duration patterns --- #}
    {% elif col.endswith('_days') %}
        {% set entity = col[:-5] | replace('_', ' ') %}
        {% set description = 'Duration in days for ' ~ entity %}
    {% elif col.endswith('_hours') %}
        {% set entity = col[:-6] | replace('_', ' ') %}
        {% set description = 'Duration in hours for ' ~ entity %}
    {% elif col.endswith('_minutes') or col.endswith('_mins') %}
        {% set entity = col | replace('_minutes', '') | replace('_mins', '') | replace('_', ' ') %}
        {% set description = 'Duration in minutes for ' ~ entity %}
    {% elif col.endswith('_seconds') or col.endswith('_secs') %}
        {% set entity = col | replace('_seconds', '') | replace('_secs', '') | replace('_', ' ') %}
        {% set description = 'Duration in seconds for ' ~ entity %}

    {# --- Common standalone columns --- #}
    {% elif col == 'quantity' or col == 'qty' %}
        {% set description = 'Quantity or number of items' %}
    {% elif col == 'currency' or col == 'currency_code' %}
        {% set description = 'Currency code (e.g. USD, EUR)' %}
    {% elif col == 'version' %}
        {% set description = 'Version number of the record' %}
    {% elif col == 'source' or col == 'data_source' %}
        {% set description = 'Origin or source system of the data' %}
    {% elif col == 'notes' or col == 'comments' %}
        {% set description = 'Free-text notes or comments' %}
    {% elif col == 'metadata' %}
        {% set description = 'Additional metadata stored as structured data' %}
    {% elif col == 'tags' %}
        {% set description = 'Tags or labels associated with the record' %}

    {# --- dbt meta columns --- #}
    {% elif col == '_fivetran_synced' %}
        {% set description = 'Timestamp when Fivetran last synced this record' %}
    {% elif col == '_fivetran_deleted' %}
        {% set description = 'Boolean flag indicating if Fivetran marked this record as deleted' %}
    {% elif col == '_airbyte_extracted_at' %}
        {% set description = 'Timestamp when Airbyte extracted this record' %}
    {% elif col == '_loaded_at' or col == '_etl_loaded_at' %}
        {% set description = 'Timestamp when the record was loaded into the warehouse' %}
    {% elif col == 'dbt_scd_id' %}
        {% set description = 'dbt snapshot surrogate key' %}
    {% elif col == 'dbt_updated_at' %}
        {% set description = 'Timestamp used by dbt snapshot to track changes' %}
    {% elif col == 'dbt_valid_from' %}
        {% set description = 'Start of validity period for this snapshot record' %}
    {% elif col == 'dbt_valid_to' %}
        {% set description = 'End of validity period for this snapshot record (null if current)' %}

    {# --- Fallback: use data type hint --- #}
    {% elif 'bool' in dtype %}
        {% set description = 'Boolean flag: ' ~ col | replace('_', ' ') %}
    {% elif 'date' in dtype or 'time' in dtype %}
        {% set description = 'Date/time value: ' ~ col | replace('_', ' ') %}
    {% elif 'int' in dtype or 'float' in dtype or 'numeric' in dtype or 'decimal' in dtype or 'number' in dtype %}
        {% set description = 'Numeric value: ' ~ col | replace('_', ' ') %}
    {% elif 'json' in dtype %}
        {% set description = 'JSON data: ' ~ col | replace('_', ' ') %}
    {% else %}
        {% set description = 'TODO: Add description for ' ~ col | replace('_', ' ') %}
    {% endif %}

    {{ return(description) }}
{% endmacro %}
