{{ config(materialized='view') }}

select
    address_line1,
    address_line2,
    address_line3,
    address_line4,

    business_type_id,
    fhrsid,
    business_name,
    business_type,

    confidence_in_management,
    hygiene,
    structural,

    latitude,
    longitude,

    local_authority_business_id,
    local_authority_code,
    local_authority_name,

    new_rating_pending,
    postcode,

    rating_date,
    rating_key,
    rating_value,

    right_to_reply,
    scheme_type

from {{ source('bronze', 'fsa_establishments_full_raw') }}