{{ config(materialized='table') }}

with enriched as (

    select

        -- Keep everything already created for
        -- FSA + ONS + England + Wales + Northern Ireland
        f.*,

        -- Scottish 2011 Data Zone
        b.datazone_code as scotland_datazone_code,

        -- Scottish deprivation measures
        s.simd2020_rank,
        s.simd2020_decile,

        -- Whether SIMD data was successfully matched
        case
            when s.datazone_code is not null then 1
            else 0
        end as simd2020_available,

        -- Final UK-wide comparable deprivation decile
        -- 1 = most deprived 10%
        -- 10 = least deprived 10%
        coalesce(
            f.uk_deprivation_decile,
            s.simd2020_decile
        ) as deprivation_decile_uk,

        -- Final source of deprivation information
        case
            when f.uk_deprivation_source is not null
                then f.uk_deprivation_source

            when s.datazone_code is not null
                then 'SIMD2020_Scotland'

            else null
        end as deprivation_source_uk

    from {{ ref('fsa_establishments_ons_ni_enriched') }} as f

    -- Match FSA postcode to Scottish Data Zone
    left join {{ ref('onspd_scotland_bridge_clean') }} as b
        on regexp_replace(
            upper(trim(f.postcode)),
            '\s+',
            '',
            'g'
        ) = b.postcode_join_key

    -- Match Scottish Data Zone to SIMD 2020
    left join {{ ref('simd_2020_clean') }} as s
        on b.datazone_code = s.datazone_code

)

select *
from enriched