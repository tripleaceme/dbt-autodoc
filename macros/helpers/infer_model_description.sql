{% macro infer_model_description(model_name) %}
    {#
        Infers a model description from the model name using dbt naming conventions.
        Parses prefixes like stg_, int_, fct_, dim_, rpt_, etc.

        Returns a string description.
    #}

    {% set name = model_name | lower | trim %}
    {% set description = '' %}

    {# --- Parse common dbt prefixes --- #}
    {% if name.startswith('stg_') %}
        {% set entity = name[4:] | replace('_', ' ') | title %}
        {% set description = 'Staging model that cleans and standardizes raw ' ~ entity ~ ' data' %}

    {% elif name.startswith('int_') %}
        {% set entity = name[4:] | replace('_', ' ') | title %}
        {% set description = 'Intermediate model that transforms and joins ' ~ entity ~ ' data' %}

    {% elif name.startswith('fct_') or name.startswith('fact_') %}
        {% set entity = name | replace('fct_', '') | replace('fact_', '') | replace('_', ' ') | title %}
        {% set description = 'Fact table recording ' ~ entity ~ ' events or transactions' %}

    {% elif name.startswith('dim_') %}
        {% set entity = name[4:] | replace('_', ' ') | title %}
        {% set description = 'Dimension table containing ' ~ entity ~ ' attributes and descriptors' %}

    {% elif name.startswith('rpt_') or name.startswith('report_') %}
        {% set entity = name | replace('rpt_', '') | replace('report_', '') | replace('_', ' ') | title %}
        {% set description = 'Report model providing aggregated view of ' ~ entity %}

    {% elif name.startswith('agg_') %}
        {% set entity = name[4:] | replace('_', ' ') | title %}
        {% set description = 'Aggregated model summarizing ' ~ entity ~ ' metrics' %}

    {% elif name.startswith('mart_') or name.startswith('mrt_') %}
        {% set entity = name | replace('mart_', '') | replace('mrt_', '') | replace('_', ' ') | title %}
        {% set description = 'Data mart providing business-ready ' ~ entity ~ ' data' %}

    {% elif name.startswith('base_') %}
        {% set entity = name[5:] | replace('_', ' ') | title %}
        {% set description = 'Base model providing foundational ' ~ entity ~ ' data' %}

    {% elif name.startswith('snapshot_') or name.startswith('snp_') %}
        {% set entity = name | replace('snapshot_', '') | replace('snp_', '') | replace('_', ' ') | title %}
        {% set description = 'Snapshot model tracking historical changes to ' ~ entity %}

    {% elif name.startswith('seed_') %}
        {% set entity = name[5:] | replace('_', ' ') | title %}
        {% set description = 'Seed data containing reference ' ~ entity ~ ' values' %}

    {% elif name.startswith('src_') %}
        {% set entity = name[4:] | replace('_', ' ') | title %}
        {% set description = 'Source model representing raw ' ~ entity ~ ' data from upstream systems' %}

    {% elif name.startswith('bridge_') or name.startswith('brg_') %}
        {% set entity = name | replace('bridge_', '') | replace('brg_', '') | replace('_', ' ') | title %}
        {% set description = 'Bridge table resolving many-to-many relationships for ' ~ entity %}

    {% elif name.startswith('map_') or name.startswith('mapping_') or name.startswith('xref_') %}
        {% set entity = name | replace('map_', '') | replace('mapping_', '') | replace('xref_', '') | replace('_', ' ') | title %}
        {% set description = 'Mapping table linking ' ~ entity ~ ' across different systems or domains' %}

    {% elif name.startswith('tmp_') or name.startswith('temp_') %}
        {% set entity = name | replace('tmp_', '') | replace('temp_', '') | replace('_', ' ') | title %}
        {% set description = 'Temporary model used for intermediate processing of ' ~ entity %}

    {# --- Suffix-based patterns --- #}
    {% elif name.endswith('_summary') %}
        {% set entity = name[:-8] | replace('_', ' ') | title %}
        {% set description = 'Summary model aggregating key metrics for ' ~ entity %}

    {% elif name.endswith('_daily') or name.endswith('_monthly') or name.endswith('_weekly') or name.endswith('_yearly') %}
        {% set parts = name.rsplit('_', 1) %}
        {% set entity = parts[0] | replace('_', ' ') | title %}
        {% set grain = parts[1] %}
        {% set description = entity ~ ' data aggregated at the ' ~ grain ~ ' grain' %}

    {% elif name.endswith('_snapshot') %}
        {% set entity = name[:-9] | replace('_', ' ') | title %}
        {% set description = 'Point-in-time snapshot of ' ~ entity ~ ' data' %}

    {% elif name.endswith('_pivot') or name.endswith('_pivoted') %}
        {% set entity = name | replace('_pivoted', '') | replace('_pivot', '') | replace('_', ' ') | title %}
        {% set description = 'Pivoted view of ' ~ entity ~ ' data' %}

    {% elif name.endswith('_unioned') or name.endswith('_combined') %}
        {% set entity = name | replace('_unioned', '') | replace('_combined', '') | replace('_', ' ') | title %}
        {% set description = 'Combined model unioning multiple ' ~ entity ~ ' sources' %}

    {% else %}
        {% set entity = name | replace('_', ' ') | title %}
        {% set description = 'TODO: Add description for ' ~ entity ~ ' model' %}
    {% endif %}

    {{ return(description) }}
{% endmacro %}
