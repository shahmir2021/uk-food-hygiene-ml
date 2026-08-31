{{ config(materialized='table') }}

with valid_ratings as (

    select
        fhrsid,
        business_type,
        postcode,
        local_authority_name,
        latitude,
        longitude,
        rating_date,
        rating_value

    from {{ ref('fsa_establishments_full_clean') }}

    -- Only businesses with usable 0 to 5 ratings
    where rating_value between 0 and 5

),

features as (

    select
        fhrsid,

        business_type,

        -- First part of postcode, for example SW, B, NG
        upper(
            substring(postcode from '^[A-Z]+')
        ) as postcode_area,

        -- Time features
        extract(year from rating_date)::integer as rating_year,
        extract(month from rating_date)::integer as rating_month,

        latitude,
        longitude,

        -- Flag missing coordinates
        case
            when latitude is null
              or longitude is null
            then 1
            else 0
        end as coordinates_missing,

        rating_value,

        -- ML target
        case
            when rating_value in (0, 1, 2) then 1
            when rating_value in (3, 4, 5) then 0
        end as low_hygiene

    from valid_ratings

)

select *
from features