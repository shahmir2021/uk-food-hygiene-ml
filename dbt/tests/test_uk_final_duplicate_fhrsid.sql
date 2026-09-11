-- This test fails if the final UK table
-- contains the same FHRSID more than once.

select
    fhrsid,
    count(*) as row_count

from {{ ref('fsa_establishments_uk_final') }}

group by fhrsid

having count(*) > 1