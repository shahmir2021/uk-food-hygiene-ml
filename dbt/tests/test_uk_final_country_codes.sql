-- This test fails if a non-null country code
-- is not one of the four expected UK country codes.

select *
from {{ ref('fsa_establishments_uk_final') }}

where country_code is not null
  and country_code not in (
      'E92000001',  -- England
      'W92000004',  -- Wales
      'N92000002',  -- Northern Ireland
      'S92000003'   -- Scotland
  )