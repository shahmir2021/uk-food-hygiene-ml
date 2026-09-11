with unique_company_names as (

    select
        company_name_join_key,
        min(company_number) as company_number

    from {{ ref('companies_house_match_ready') }}

    where company_name_join_key is not null
      and company_name_join_key <> ''

    group by company_name_join_key

    having count(*) = 1

),

tier2_matches as (

    select

        f.fhrsid,

        u.company_number,

        'unique_exact_name' as companies_house_match_method,

        1.0::numeric as companies_house_match_score

    from {{ ref('fsa_establishments_companies_house_exact') }} as f

    inner join unique_company_names as u
        on f.business_name_join_key =
           u.company_name_join_key

    where f.companies_house_exact_match = 0

)

select *
from tier2_matches