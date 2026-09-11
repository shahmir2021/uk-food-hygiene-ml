{{ config(materialized='table') }}

with cleaned as (

    select

        -- Keep Bronze row ID
        bronze_id,

        -- Standardise Welsh LSOA join key
        nullif(
            upper(trim(lsoa21_code)),
            ''
        ) as lsoa21_code,

        -- Convert WIMD rank from text to integer
        -- Remove thousands separators such as "1,301"
        case
            when replace(trim(wimd2025_rank), ',', '') ~ '^[0-9]+$'
            then replace(trim(wimd2025_rank), ',', '')::integer
        end as wimd2025_rank,

        -- Convert WIMD decile from text to integer
        case
            when trim(wimd2025_decile) ~ '^[0-9]+$'
            then trim(wimd2025_decile)::integer
        end as wimd2025_decile,

        -- Keep ingestion timestamp for lineage
        ingested_at

    from {{ source('bronze', 'wimd_2025_raw') }}

)

select *
from cleaned