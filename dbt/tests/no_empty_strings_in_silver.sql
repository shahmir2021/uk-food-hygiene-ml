SELECT
    bronze_id,
    business_name,
    business_type,
    postcode,
    rating_value

FROM {{ ref('fsa_establishments_clean') }}

WHERE business_name = ''
   OR business_type = ''
   OR postcode = ''
   OR rating_value = ''