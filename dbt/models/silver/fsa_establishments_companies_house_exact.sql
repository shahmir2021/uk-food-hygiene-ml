with food_businesses as (

    select

        *,

        regexp_replace(
            upper(trim(business_name)),
            '[^A-Z0-9]',
            '',
            'g'
        ) as business_name_join_key,

        regexp_replace(
            upper(trim(postcode)),
            '\s+',
            '',
            'g'
        ) as business_postcode_join_key

    from {{ ref('fsa_establishments_uk_features') }}

),

company_candidates as (

    select

        *,

        count(*) over (
            partition by
                company_name_join_key,
                company_postcode_join_key
        ) as companies_at_name_postcode

    from {{ ref('companies_house_match_ready') }}

    where company_name_join_key is not null
      and company_name_join_key <> ''
      and company_postcode_join_key is not null
      and company_postcode_join_key <> ''

),

unique_company_matches as (

    select *
    from company_candidates

    where companies_at_name_postcode = 1

),

matched as (

    select

        f.*,

        c.company_number,
        c.company_status,
        c.company_category,
        c.country_of_origin,
        c.incorporation_date,
        c.dissolution_date,
        c.accounts_category,
        c.accounts_last_made_up_date,
        c.accounts_next_due_date,

        c.mortgages_num_charges,
        c.mortgages_num_outstanding,
        c.mortgages_num_part_satisfied,
        c.mortgages_num_satisfied,

        c.sic_code_1,
        c.sic_code_2,
        c.sic_code_3,
        c.sic_code_4,

        c.sic_text_1,
        c.sic_text_2,
        c.sic_text_3,
        c.sic_text_4,

        c.company_active,

        case
            when c.company_number is not null then 1
            else 0
        end as companies_house_exact_match

    from food_businesses as f

    left join unique_company_matches as c

        on f.business_name_join_key = c.company_name_join_key

       and f.business_postcode_join_key =
           c.company_postcode_join_key

)

select *
from matched