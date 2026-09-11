with remaining_food_businesses as (

    select
        f.fhrsid,
        f.business_name,
        f.postcode,
        f.business_name_join_key,
        f.business_postcode_join_key

    from {{ ref('fsa_establishments_companies_house_exact') }} as f

    left join {{ ref('companies_house_tier2_matches') }} as t2
        on f.fhrsid = t2.fhrsid

    where f.companies_house_exact_match = 0
      and t2.fhrsid is null
      and f.business_name_join_key is not null
      and f.business_name_join_key <> ''
      and f.business_postcode_join_key is not null
      and f.business_postcode_join_key <> ''

),

postcode_candidates as (

    select

        f.fhrsid,
        f.business_name,
        f.postcode,
        f.business_name_join_key,

        c.company_number,
        c.company_name,
        c.company_name_join_key,

        count(*) over (
            partition by f.fhrsid
        ) as candidate_count

    from remaining_food_businesses as f

    inner join {{ ref('companies_house_match_ready') }} as c
        on f.business_postcode_join_key =
           c.company_postcode_join_key

    where c.company_name_join_key is not null
      and c.company_name_join_key <> ''

),

scored as (

    select

        *,

        similarity(
            business_name_join_key,
            company_name_join_key
        ) as similarity_score

    from postcode_candidates

    where candidate_count <= 100

),

ranked as (

    select

        *,

        row_number() over (
            partition by fhrsid
            order by
                similarity_score desc,
                company_number
        ) as match_rank,

        lead(similarity_score) over (
            partition by fhrsid
            order by
                similarity_score desc,
                company_number
        ) as second_best_score

    from scored

),

best_match as (

    select

        fhrsid,

        business_name,

        postcode,

        company_number,

        company_name as matched_company_name,

        candidate_count,

        similarity_score as best_score,

        second_best_score,

        similarity_score
            - coalesce(second_best_score, 0)
            as score_gap,

        'postcode_fuzzy_name' as companies_house_match_method

    from ranked

    where match_rank = 1

)

select *
from best_match