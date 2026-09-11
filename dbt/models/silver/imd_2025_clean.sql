{{ config(materialized='table') }}

with cleaned as (

    select

        -- Keep the Bronze row ID
        bronze_id,

        -- Standardise the LSOA join key
        nullif(
            upper(trim(lsoa21_code)),
            ''
        ) as lsoa21_code,

        -- Convert IMD rank from text to integer
        case
            when trim(imd2025_rank) ~ '^[0-9]+$'
            then trim(imd2025_rank)::integer
        end as imd2025_rank,

        -- Convert IMD decile from text to integer
        case
            when trim(imd2025_decile) ~ '^[0-9]+$'
            then trim(imd2025_decile)::integer
        end as imd2025_decile,

        ingested_at

    from {{ source('bronze', 'imd_2025_raw') }}

)

select *
from cleaned