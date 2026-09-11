-- This test fails if any business
-- in the final UK dataset has no FHRSID.

select *
from {{ ref('fsa_establishments_uk_final') }}

where fhrsid is null