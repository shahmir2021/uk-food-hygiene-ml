{{ config(materialized='table') }}

with cleaned as (

    select

        -- IDs
        case
            when trim(fhrsid) ~ '^[0-9]+$'
            then trim(fhrsid)::bigint
        end as fhrsid,

        case
            when trim(business_type_id) ~ '^[0-9]+$'
            then trim(business_type_id)::integer
        end as business_type_id,

        -- Business information
        nullif(trim(business_name), '') as business_name,
        nullif(trim(business_type), '') as business_type,

        -- Location
        nullif(trim(address_line1), '') as address_line1,
        nullif(trim(address_line2), '') as address_line2,
        nullif(trim(address_line3), '') as address_line3,
        nullif(trim(address_line4), '') as address_line4,

        nullif(upper(trim(postcode)), '') as postcode,
        nullif(trim(local_authority_name), '') as local_authority_name,

        -- Coordinates
        case
            when trim(latitude) ~ '^-?[0-9]+(\.[0-9]+)?$'
            then trim(latitude)::double precision
        end as latitude,

        case
            when trim(longitude) ~ '^-?[0-9]+(\.[0-9]+)?$'
            then trim(longitude)::double precision
        end as longitude,

        -- Rating
        trim(rating_value) as rating_value_raw,

        case
            when trim(rating_value) in ('0', '1', '2', '3', '4', '5')
            then trim(rating_value)::integer
        end as rating_value,

        case
            when trim(rating_date) ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}'
            then left(trim(rating_date), 10)::date
        end as rating_date,

        -- Inspection scores
        case
            when trim(hygiene) ~ '^-?[0-9]+(\.[0-9]+)?$'
            then trim(hygiene)::double precision
        end as hygiene,

        case
            when trim(structural) ~ '^-?[0-9]+(\.[0-9]+)?$'
            then trim(structural)::double precision
        end as structural,

        case
            when trim(confidence_in_management) ~ '^-?[0-9]+(\.[0-9]+)?$'
            then trim(confidence_in_management)::double precision
        end as confidence_in_management,

        nullif(trim(new_rating_pending), '') as new_rating_pending,
        nullif(trim(scheme_type), '') as scheme_type

    from {{ ref('stg_fsa_establishments_full') }}

)

select *
from cleaned
where scheme_type = 'FHRS'