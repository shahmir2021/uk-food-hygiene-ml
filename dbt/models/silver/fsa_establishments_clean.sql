SELECT
    bronze_id,

    -- Clean text fields
    NULLIF(TRIM(address_line1), '') AS address_line1,
    NULLIF(TRIM(address_line2), '') AS address_line2,
    NULLIF(TRIM(address_line3), '') AS address_line3,

    NULLIF(TRIM(business_name), '') AS business_name,
    NULLIF(TRIM(business_type), '') AS business_type,

    business_type_id,
    changes_by_server_id,

    fhrsid,

    NULLIF(TRIM(local_authority_business_id), '') AS local_authority_business_id,
    NULLIF(TRIM(local_authority_code), '') AS local_authority_code,
    NULLIF(TRIM(local_authority_email_address), '') AS local_authority_email_address,
    NULLIF(TRIM(local_authority_name), '') AS local_authority_name,
    NULLIF(TRIM(local_authority_website), '') AS local_authority_website,

    new_rating_pending,

    -- Standardise postcode
    UPPER(NULLIF(TRIM(postcode), '')) AS postcode,

    -- Convert rating date from text
    NULLIF(rating_date, '')::TIMESTAMP AS rating_date,

    NULLIF(TRIM(rating_key), '') AS rating_key,
    NULLIF(TRIM(rating_value), '') AS rating_value,
    NULLIF(TRIM(scheme_type), '') AS scheme_type,

    -- Flatten geocode JSON
    NULLIF(geocode ->> 'latitude', '')::NUMERIC AS latitude,
    NULLIF(geocode ->> 'longitude', '')::NUMERIC AS longitude,

    -- Flatten inspection score JSON
    NULLIF(scores ->> 'Hygiene', '')::INTEGER AS hygiene,
    NULLIF(scores ->> 'Structural', '')::INTEGER AS structural,
    NULLIF(scores ->> 'ConfidenceInManagement', '')::INTEGER
        AS confidence_in_management,

    ingested_at

FROM {{ ref('stg_fsa_establishments') }}