-- This test fails if a row comes from
-- an unexpected source system.

select *
from {{ ref('fsa_establishments_uk_final') }}

where source_system not in (
    'FSA_FHRS',
    'FSS_FHIS'
)
   or source_system is null