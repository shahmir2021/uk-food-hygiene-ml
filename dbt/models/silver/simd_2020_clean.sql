{{ config(materialized='table') }}

with cleaned as (

    select

        -- Keep Bronze row ID
        bronze_id,

        -- Standardise Scottish Data Zone code
        nullif(
            upper(trim(datazone_code)),
            ''
        ) as datazone_code,

        -- Convert SIMD rank from text to integer
        -- Rank 1 = most deprived
        case
            when trim(simd2020_rank) ~ '^[0-9]+$'
                then trim(simd2020_rank)::integer
        end as simd2020_rank,

        -- Convert SIMD decile from text to integer
        -- Decile 1 = most deprived 10%
        -- Decile 10 = least deprived 10%
        case
            when trim(simd2020_decile) ~ '^[0-9]+$'
                then trim(simd2020_decile)::integer
        end as simd2020_decile,

        -- Keep ingestion timestamp
        ingested_at

    from {{ source('bronze', 'simd_2020_raw') }}

)

select *
from cleaned