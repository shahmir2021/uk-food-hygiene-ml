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

        -- Old Northern Ireland SOA code used by NIMDM 2017
        nullif(
            upper(trim(lsoa01_code)),
            ''
        ) as lsoa01_code,

        -- Current 2021 Northern Ireland LSOA code
        nullif(
            upper(trim(lsoa21_code)),
            ''
        ) as lsoa21_code,

        -- Keep ingestion timestamp
        ingested_at

    from {{ source('bronze', 'onspd_ni_bridge_raw') }}

)

select *
from cleaned