select *
from {{ ref('fsa_establishments_uk_companies_house_enriched') }}

where

    (
        companies_house_available = 1
        and companies_house_company_number is null
    )

    or

    (
        companies_house_available = 0
        and companies_house_company_number is not null
    )

    or

    companies_house_available not in (0, 1)

    or

    (
        companies_house_match_method is not null
        and companies_house_match_method not in (
            'exact_name_postcode',
            'unique_exact_name',
            'postcode_fuzzy_name'
        )
    )

    or

    (
        companies_house_match_score is not null
        and (
            companies_house_match_score < 0
            or companies_house_match_score > 1
        )
    )