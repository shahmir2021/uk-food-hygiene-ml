with food_businesses as (

    select *
    from {{ ref('fsa_establishments_uk_features') }}

),

matches as (

    select *
    from {{ ref('companies_house_all_matches') }}

),

companies as (

    select *
    from {{ ref('companies_house_clean') }}

),

enriched as (

    select

        f.*,

        case
            when m.company_number is not null then 1
            else 0
        end as companies_house_available,

        m.company_number as companies_house_company_number,

        m.companies_house_match_method,

        m.companies_house_match_score,

        c.company_name as companies_house_company_name,

        c.registered_postcode as companies_house_registered_postcode,

        c.company_status,

        c.company_category,

        c.country_of_origin,

        c.incorporation_date,

        c.dissolution_date,

        c.company_active,

        c.sic_code_1,

        c.sic_code_2,

        c.sic_code_3,

        c.sic_code_4

    from food_businesses as f

    left join matches as m
        on f.fhrsid = m.fhrsid

    left join companies as c
        on m.company_number = c.company_number

)

select *
from enriched