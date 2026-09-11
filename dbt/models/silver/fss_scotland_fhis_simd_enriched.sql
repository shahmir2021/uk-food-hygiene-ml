{{ config(materialized='table') }}

with enriched as (

    select

        -- Keep all cleaned Scottish business columns
        f.*,

        -- Scottish Data Zone from ONSPD
        b.datazone_code,

        -- SIMD 2020 deprivation information
        s.simd2020_rank,
        s.simd2020_decile,

        -- Flag showing whether SIMD was successfully matched
        case
            when s.datazone_code is not null then 1
            else 0
        end as simd2020_available

    from {{ ref('fss_scotland_fhis_clean') }} as f

    -- Match business postcode to Scottish Data Zone
    left join {{ ref('onspd_scotland_bridge_clean') }} as b
        on f.postcode_join_key = b.postcode_join_key

    -- Match Data Zone to SIMD 2020
    left join {{ ref('simd_2020_clean') }} as s
        on b.datazone_code = s.datazone_code

)

select *
from enriched