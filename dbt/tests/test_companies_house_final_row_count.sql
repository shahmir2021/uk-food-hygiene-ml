with counts as (

    select
        (
            select count(*)
            from {{ ref('fsa_establishments_uk_features') }}
        ) as source_rows,

        (
            select count(*)
            from {{ ref('fsa_establishments_uk_companies_house_enriched') }}
        ) as final_rows

)

select *
from counts

where source_rows <> final_rows