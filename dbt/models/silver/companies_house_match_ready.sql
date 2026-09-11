with base as (

    select *
    from {{ ref('companies_house_clean') }}

),

match_ready as (

    select

        *,

        regexp_replace(
            upper(trim(company_name)),
            '[^A-Z0-9]',
            '',
            'g'
        ) as company_name_join_key,

        regexp_replace(
            upper(trim(registered_postcode)),
            '\s+',
            '',
            'g'
        ) as company_postcode_join_key

    from base

)

select *
from match_ready