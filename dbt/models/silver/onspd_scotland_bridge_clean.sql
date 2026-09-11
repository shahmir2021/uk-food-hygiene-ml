{{ config(materialized='table') }}

with cleaned as (

    select

        -- Keep Bronze row ID
        bronze_id,

        -- Standardise postcode for joining to FSA
        nullif(
            regexp_replace(
                upper(trim(postcode)),
                '\s+',
                '',
                'g'
            ),
            ''
        ) as postcode_join_key,

        -- Scottish 2011 Data Zone code used by SIMD 2020
        nullif(
            upper(trim(datazone_code)),
            ''
        ) as datazone_code,

        -- Keep ingestion timestamp
        ingested_at

    from {{ source('bronze', 'onspd_scotland_bridge_raw') }}

)

select *
from cleaned