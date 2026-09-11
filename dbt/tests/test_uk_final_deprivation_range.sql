-- This test fails if a deprivation decile
-- exists outside the valid 1 to 10 range.

select *
from {{ ref('fsa_establishments_uk_final') }}

where deprivation_decile_uk is not null
  and deprivation_decile_uk not between 1 and 10