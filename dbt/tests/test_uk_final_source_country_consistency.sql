-- This test fails if the data source and country
-- classification contradict each other.

select *
from {{ ref('fsa_establishments_uk_final') }}

where
    (
        source_system = 'FSS_FHIS'
        and country_code <> 'S92000003'
    )

    or

    (
        source_system = 'FSA_FHRS'
        and country_code = 'S92000003'
    )

    or

    (
        source_system = 'FSS_FHIS'
        and country_code is null
    )