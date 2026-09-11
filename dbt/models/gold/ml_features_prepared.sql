with base as (

    select *
    from {{ ref('ml_feature_base') }}

),

prepared as (

    select

        fhrsid,
        rating_date,
        target_low_hygiene,

        business_type,
        local_authority_name,

        latitude,
        longitude,

        case
            when latitude is null then 1
            else 0
        end as latitude_missing,

        case
            when longitude is null then 1
            else 0
        end as longitude_missing,

        coalesce(
            nullif(trim(country_code), ''),
            'UNKNOWN'
        ) as country_code,

        coalesce(
            nullif(trim(region_code), ''),
            nullif(trim(country_code), ''),
            'UNKNOWN'
        ) as region_code,

        deprivation_score_uk,

        case
            when deprivation_score_uk is null then 1
            else 0
        end as deprivation_missing,

        companies_house_available,

        case
            when companies_house_available = 0
                then 'NOT_MATCHED'

            when company_category is null
              or trim(company_category) = ''
                then 'MISSING'

            else company_category
        end as company_category,

        case
            when companies_house_available = 0
                then 'NOT_MATCHED'

            when country_of_origin is null
              or trim(country_of_origin) = ''
                then 'MISSING'

            else country_of_origin
        end as country_of_origin,

        company_age_years,

        case
            when company_age_years is null then 1
            else 0
        end as company_age_missing,

        case
            when companies_house_available = 0
                then 'NOT_MATCHED'

            when sic_code_1 is null
              or trim(sic_code_1) = ''
                then 'MISSING'

            when trim(sic_code_1) ~ '^[0-9]{5}$'
                then left(trim(sic_code_1), 2)

            else 'OTHER'
        end as sic_division

    from base

)

select *
from prepared