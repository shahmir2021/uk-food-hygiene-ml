{{ config(materialized='table') }}

with cleaned as (

    select

        -- Original Bronze row ID
        bronze_id,

        -- Standardised full postcode
        nullif(
            upper(trim(pcds)),
            ''
        ) as postcode,

        -- Join version of postcode with spaces removed
        -- Example: "AB1 0AA" becomes "AB10AA"
        regexp_replace(
            upper(trim(pcds)),
            '\s+',
            '',
            'g'
        ) as postcode_join_key,

        -- NSPL termination month
        -- Blank means the postcode is currently active
        case
            when trim(doterm) ~ '^[0-9]{6}$'
            then to_date(trim(doterm), 'YYYYMM')
        end as termination_date,

        -- Flag whether postcode has been terminated
        case
            when nullif(trim(doterm), '') is null then 0
            else 1
        end as is_terminated,

        -- 2021 Census geography codes
        nullif(trim(oa21cd), '') as oa21_code,
        nullif(trim(lsoa21cd), '') as lsoa21_code,
        nullif(trim(msoa21cd), '') as msoa21_code,

        -- Administrative geography
        nullif(trim(lad26cd), '') as local_authority_code,
        nullif(trim(ctry26cd), '') as country_code,
        nullif(trim(rgn26cd), '') as region_code,

        -- NSPL coordinates
        case
            when trim(lat) ~ '^-?[0-9]+(\.[0-9]+)?$'
            then trim(lat)::double precision
        end as latitude,

        case
            when trim(long) ~ '^-?[0-9]+(\.[0-9]+)?$'
            then trim(long)::double precision
        end as longitude,

        ingested_at

    from {{ source('bronze', 'nspl_postcodes_raw') }}

)

select *
from cleaned