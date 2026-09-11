with tier1 as (

    select
        fhrsid,
        company_number,
        'exact_name_postcode' as companies_house_match_method,
        1.0::numeric as companies_house_match_score

    from {{ ref('fsa_establishments_companies_house_exact') }}

    where companies_house_exact_match = 1

),

tier2 as (

    select
        fhrsid,
        company_number,
        companies_house_match_method,
        companies_house_match_score

    from {{ ref('companies_house_tier2_matches') }}

),

tier3 as (

    select
        fhrsid,
        company_number,
        companies_house_match_method,
        companies_house_match_score

    from {{ ref('companies_house_tier3_matches') }}

),

combined as (

    select *
    from tier1

    union all

    select *
    from tier2

    union all

    select *
    from tier3

)

select *
from combined