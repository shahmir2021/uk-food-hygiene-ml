{{ config(materialized='table') }}

with enriched as (

    select

        -- Keep everything already created from FSA + ONS + England IMD
        f.*,

        -- Wales-specific deprivation measures
        w.wimd2025_rank,
        w.wimd2025_decile,

        -- Whether Welsh deprivation data was available
        case
            when w.lsoa21_code is not null then 1
            else 0
        end as wimd2025_available,

        -- Comparable deprivation decile across England and Wales
        -- 1 = most deprived 10%
        -- 10 = least deprived 10%
        coalesce(
            f.imd2025_decile,
            w.wimd2025_decile
        ) as deprivation_decile,

        -- Record which national deprivation index supplied the value
        case
            when f.imd2025_available = 1 then 'IMD2025_England'
            when w.lsoa21_code is not null then 'WIMD2025_Wales'
            else null
        end as deprivation_source

    from {{ ref('fsa_establishments_ons_imd_enriched') }} as f

    left join {{ ref('wimd_2025_clean') }} as w
        on f.lsoa21_code = w.lsoa21_code

)

select *
from enriched