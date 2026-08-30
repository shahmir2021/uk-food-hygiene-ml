-- Gold model for machine learning
-- Creates model-ready features and the binary hygiene-risk target

select
    fhrsid,
    business_type,
    local_authority_name,

    -- Convert full postcode into broader postcode area
    coalesce(
    nullif(trim(regexp_replace(upper(postcode), '[0-9].*$', '')), ''),
    'UNKNOWN'
) as postcode_area,

    -- Create date features
    extract(year from rating_date) as rating_year,
    extract(month from rating_date) as rating_month,

    scheme_type,
    latitude,
    longitude,

    case
    when latitude is null or longitude is null then 1
    else 0
    end as coordinates_missing,

    -- Binary ML target
    case
        when rating_value in ('0', '1', '2') then 1
        when rating_value in ('3', '4', '5') then 0
        else null
    end as is_low_hygiene_rating

from {{ ref('fsa_establishments_clean') }}