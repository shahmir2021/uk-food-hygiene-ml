{{ config(materialized='table') }}

with base as (

    select *
    from {{ ref('fsa_establishments_uk_final') }}

)

select

    *,

    -- ============================================================
    -- NORMALISED UK DEPRIVATION SCORE
    --
    -- 1.0 = most deprived
    -- 0.0 = least deprived
    --
    -- Each country has a different number of deprivation areas,
    -- so raw ranks cannot be compared directly.
    -- ============================================================

    case

        -- England, IMD 2025
        when country_code = 'E92000001'
             and imd2025_rank is not null
        then
            1.0 -
            (
                (imd2025_rank - 1)::numeric
                /
                (33755 - 1)::numeric
            )


        -- Wales, WIMD 2025
        when country_code = 'W92000004'
             and wimd2025_rank is not null
        then
            1.0 -
            (
                (wimd2025_rank - 1)::numeric
                /
                (1917 - 1)::numeric
            )


        -- Northern Ireland, NIMDM 2017
        when country_code = 'N92000002'
             and nimdm2017_rank is not null
        then
            1.0 -
            (
                (nimdm2017_rank - 1)::numeric
                /
                (890 - 1)::numeric
            )


        -- Scotland, SIMD 2020
        when country_code = 'S92000003'
             and simd2020_rank is not null
        then
            1.0 -
            (
                (simd2020_rank - 1)::numeric
                /
                (6976 - 1)::numeric
            )

        else null

    end as deprivation_score_uk

from base