{{ config(materialized='table') }}

with fsa_uk as (

    select

        -- =========================================================
        -- CORE BUSINESS FIELDS
        -- =========================================================

        -- Convert ID to text so it matches the Scottish FHIS ID type
        fhrsid::text as fhrsid,

        business_name,
        business_type,
        postcode,
        local_authority_name,

        latitude::double precision as latitude,
        longitude::double precision as longitude,

        rating_date,

        -- Scotland uses text ratings, so standardise the UK field to text
        rating_value::text as rating_value,

        hygiene::double precision as hygiene,
        structural::double precision as structural,
        confidence_in_management::double precision
            as confidence_in_management,


        -- =========================================================
        -- ONS GEOGRAPHY
        -- =========================================================

        oa21_code,
        lsoa21_code,
        msoa21_code,
        ons_local_authority_code,
        country_code,
        region_code,

        ons_postcode_match,
        ons_lsoa_available,
        ons_postcode_terminated,


        -- =========================================================
        -- ENGLAND, IMD 2025
        -- =========================================================

        imd2025_rank,
        imd2025_decile,
        imd2025_available,


        -- =========================================================
        -- WALES, WIMD 2025
        -- =========================================================

        wimd2025_rank,
        wimd2025_decile,
        wimd2025_available,


        -- =========================================================
        -- EARLIER ENGLAND / WALES UNIFIED DEPRIVATION FIELDS
        -- =========================================================

        deprivation_decile,
        deprivation_source,


        -- =========================================================
        -- NORTHERN IRELAND, NIMDM 2017
        -- =========================================================

        ni_soa01_code,
        nimdm2017_rank,
        nimdm2017_decile,
        nimdm2017_available,


        -- =========================================================
        -- UK DEPRIVATION FIELDS CREATED BEFORE SCOTLAND
        -- =========================================================

        uk_deprivation_decile,
        uk_deprivation_source,


        -- =========================================================
        -- SCOTLAND FIELDS
        -- Existing FSA rows will normally be NULL here
        -- =========================================================

        scotland_datazone_code,
        simd2020_rank,
        simd2020_decile,
        simd2020_available,


        -- =========================================================
        -- FINAL UK WIDE DEPRIVATION FIELDS
        -- =========================================================

        deprivation_decile_uk,
        deprivation_source_uk,


        -- =========================================================
        -- DATA SOURCE
        -- =========================================================

        'FSA_FHRS'::text as source_system

    from {{ ref('fsa_establishments_ons_uk_deprivation_enriched') }}

),


scotland as (

    select

        -- =========================================================
        -- CORE BUSINESS FIELDS
        -- =========================================================

        fhrsid::text as fhrsid,

        business_name,
        business_type,
        postcode,
        local_authority_name,

        latitude::double precision as latitude,
        longitude::double precision as longitude,

        rating_date,

        -- Scottish FHIS ratings are categorical text
        rating_value::text as rating_value,

        hygiene::double precision as hygiene,
        structural::double precision as structural,
        confidence_in_management::double precision
            as confidence_in_management,


        -- =========================================================
        -- ONS GEOGRAPHY
        -- England / Wales / NI geography is not applicable
        -- =========================================================

        null::text as oa21_code,
        null::text as lsoa21_code,
        null::text as msoa21_code,

        null::text as ons_local_authority_code,

        country_code,

        null::text as region_code,


        -- If a Scottish Data Zone was found through the postcode
        -- bridge, the postcode successfully matched ONSPD
        case
            when datazone_code is not null then 1
            else 0
        end::integer as ons_postcode_match,

        -- LSOA is not the Scottish geography system
        null::integer as ons_lsoa_available,

        null::integer as ons_postcode_terminated,


        -- =========================================================
        -- ENGLAND, NOT APPLICABLE
        -- =========================================================

        null::integer as imd2025_rank,
        null::integer as imd2025_decile,
        null::integer as imd2025_available,


        -- =========================================================
        -- WALES, NOT APPLICABLE
        -- =========================================================

        null::integer as wimd2025_rank,
        null::integer as wimd2025_decile,
        null::integer as wimd2025_available,


        -- =========================================================
        -- UNIFIED DEPRIVATION
        -- =========================================================

        simd2020_decile::integer as deprivation_decile,

        case
            when simd2020_available = 1
                then 'SIMD2020_Scotland'
            else null
        end::text as deprivation_source,


        -- =========================================================
        -- NORTHERN IRELAND, NOT APPLICABLE
        -- =========================================================

        null::text as ni_soa01_code,
        null::integer as nimdm2017_rank,
        null::integer as nimdm2017_decile,
        null::integer as nimdm2017_available,


        -- =========================================================
        -- UK DEPRIVATION
        -- =========================================================

        simd2020_decile::integer as uk_deprivation_decile,

        case
            when simd2020_available = 1
                then 'SIMD2020_Scotland'
            else null
        end::text as uk_deprivation_source,


        -- =========================================================
        -- SCOTLAND, SIMD 2020
        -- =========================================================

        datazone_code::text as scotland_datazone_code,
        simd2020_rank::integer as simd2020_rank,
        simd2020_decile::integer as simd2020_decile,
        simd2020_available::integer as simd2020_available,


        -- =========================================================
        -- FINAL UK WIDE DEPRIVATION
        -- =========================================================

        simd2020_decile::integer as deprivation_decile_uk,

        case
            when simd2020_available = 1
                then 'SIMD2020_Scotland'
            else null
        end::text as deprivation_source_uk,


        -- =========================================================
        -- DATA SOURCE
        -- =========================================================

        source_system::text as source_system

    from {{ ref('fss_scotland_fhis_simd_enriched') }}

),


final as (

    select *
    from fsa_uk

    union all

    select *
    from scotland

)

select *
from final