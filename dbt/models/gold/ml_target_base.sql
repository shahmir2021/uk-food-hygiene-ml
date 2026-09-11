with base as (

    select *
    from {{ ref('fsa_establishments_uk_companies_house_enriched') }}

),

targeted as (

    select

        *,

        case

            when source_system = 'FSA_FHRS'
                 and rating_value in ('0', '1', '2')
                then 1

            when source_system = 'FSA_FHRS'
                 and rating_value in ('3', '4', '5')
                then 0

            when source_system = 'FSS_FHIS'
                 and rating_value = 'Improvement Required'
                then 1

            when source_system = 'FSS_FHIS'
                 and rating_value in (
                     'Pass',
                     'Pass and Eat Safe'
                 )
                then 0

            else null

        end as target_low_hygiene

    from base

)

select *
from targeted

where target_low_hygiene is not null