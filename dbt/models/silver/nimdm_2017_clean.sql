{{ config(materialized='table') }}

with cleaned as (

    select

        -- Keep Bronze row ID
        bronze_id,

        -- Standardise old Northern Ireland SOA code
        nullif(
            upper(trim(soa01_code)),
            ''
        ) as soa01_code,

        -- Convert NIMDM rank from text to integer
        -- Rank 1 = most deprived
        case
            when trim(nimdm2017_rank) ~ '^[0-9]+$'
                then trim(nimdm2017_rank)::integer
        end as nimdm2017_rank,

        -- Convert the 1 to 890 ranking into 10 equal deprivation groups
        -- 1 = most deprived 10%
        -- 10 = least deprived 10%
        case
            when trim(nimdm2017_rank) ~ '^[0-9]+$'
                then ceil(
                    trim(nimdm2017_rank)::numeric / 89.0
                )::integer
        end as nimdm2017_decile,

        -- Keep ingestion timestamp
        ingested_at

    from {{ source('bronze', 'nimdm_2017_raw') }}

)

select *
from cleaned