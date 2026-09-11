-- This test fails if the normalised UK deprivation score
-- falls outside the valid 0 to 1 range.

select *
from {{ ref('fsa_establishments_uk_features') }}

where deprivation_score_uk is not null
  and (
      deprivation_score_uk < 0
      or deprivation_score_uk > 1
  )