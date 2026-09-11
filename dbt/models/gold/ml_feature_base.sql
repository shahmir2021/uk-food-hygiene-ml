with base as (

    select *
    from {{ ref('ml_target_base') }}

),

recent as (

    select *
    from base

    where rating_date >= date '2025-01-01'

),

features as (

    select

        fhrsid,

        rating_date,

        target_low_hygiene,

        business_type,

        local_authority_name,

        latitude,

        longitude,

        country_code,

        region_code,

        deprivation_score_uk,

        companies_house_available,

        company_category,

        country_of_origin,

        case
            when incorporation_date is not null
             and incorporation_date <= rating_date
            then round(
                (
                    (rating_date - incorporation_date)::numeric
                    / 365.25
                ),
                2
            )
            else null
        end as company_age_years,

        sic_code_1,

        sic_code_2,

        sic_code_3,

        sic_code_4

    from recent

)

select *
from features