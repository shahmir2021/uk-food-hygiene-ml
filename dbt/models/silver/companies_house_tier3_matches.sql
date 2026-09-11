with accepted as (

    select
        fhrsid,
        company_number,
        best_score as companies_house_match_score,
        score_gap,
        candidate_count,
        'postcode_fuzzy_name' as companies_house_match_method

    from {{ ref('companies_house_tier3_candidates') }}

    where best_score >= 0.70
      and score_gap >= 0.10

)

select *
from accepted