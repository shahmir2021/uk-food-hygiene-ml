{{ config(materialized='table') }}

with enriched as (

    select

        -- Keep all existing FSA + ONS fields
        f.*,

        -- English deprivation features
        i.imd2025_rank,
        i.imd2025_decile,

        -- Shows whether an IMD record was available
        case
            when i.lsoa21_code is not null then 1
            else 0
        end as imd2025_available

    from {{ ref('fsa_establishments_ons_enriched') }} as f

    left join {{ ref('imd_2025_clean') }} as i
        on f.lsoa21_code = i.lsoa21_code

)

select *
from enriched