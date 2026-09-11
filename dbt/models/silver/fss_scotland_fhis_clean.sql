{{ config(materialized='table') }}

with cleaned as (

    select

        -- Keep Bronze lineage ID
        bronze_id,

        -- Business identifier
        nullif(
            trim(fhrsid),
            ''
        ) as fhrsid,

        -- Business information
        nullif(
            trim(business_name),
            ''
        ) as business_name,

        nullif(
            trim(business_type),
            ''
        ) as business_type,

        nullif(
            trim(business_type_id),
            ''
        ) as business_type_id,

        -- Address
        nullif(trim(address_line1), '') as address_line1,
        nullif(trim(address_line2), '') as address_line2,
        nullif(trim(address_line3), '') as address_line3,
        nullif(trim(address_line4), '') as address_line4,

        -- Keep readable postcode
        nullif(
            upper(trim(postcode)),
            ''
        ) as postcode,

        -- Remove spaces for postcode joins
        nullif(
            regexp_replace(
                upper(trim(postcode)),
                '\s+',
                '',
                'g'
            ),
            ''
        ) as postcode_join_key,

        -- Scottish FHIS rating
        nullif(
            trim(rating_value),
            ''
        ) as rating_value,

        -- Convert rating date where possible
        case
            when substring(trim(rating_date), 1, 10)
                 ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'
            then substring(trim(rating_date), 1, 10)::date
            else null
        end as rating_date,

        -- Local authority information
        nullif(
            trim(local_authority_code),
            ''
        ) as local_authority_code,

        nullif(
            trim(local_authority_name),
            ''
        ) as local_authority_name,

        -- Inspection scores
        case
            when trim(hygiene_score) ~ '^-?[0-9]+$'
            then trim(hygiene_score)::integer
            else null
        end as hygiene,

        case
            when trim(structural_score) ~ '^-?[0-9]+$'
            then trim(structural_score)::integer
            else null
        end as structural,

        case
            when trim(confidence_in_management_score) ~ '^-?[0-9]+$'
            then trim(confidence_in_management_score)::integer
            else null
        end as confidence_in_management,

        -- Coordinates
        case
            when trim(longitude) ~ '^-?[0-9]+(\.[0-9]+)?$'
            then trim(longitude)::double precision
            else null
        end as longitude,

        case
            when trim(latitude) ~ '^-?[0-9]+(\.[0-9]+)?$'
            then trim(latitude)::double precision
            else null
        end as latitude,

        -- Scotland country code
        'S92000003' as country_code,

        -- Identify the data source
        'FSS_FHIS' as source_system,

        -- Original XML council file
        source_xml,

        -- Lineage timestamp
        ingested_at

    from {{ source('bronze', 'fss_scotland_fhis_raw') }}

)

select *
from cleaned