{{ config(materialized='table') }}

with fsa as (

    select *
    from {{ ref('fsa_establishments_full_clean') }}

    -- Keep the same population used for ML
    where rating_value between 0 and 5

),

enriched as (

    select

        -- FSA establishment fields
        f.fhrsid,
        f.business_name,
        f.business_type,
        f.postcode,
        f.local_authority_name,
        f.latitude,
        f.longitude,
        f.rating_date,
        f.rating_value,
        f.hygiene,
        f.structural,
        f.confidence_in_management,

        -- ONS postcode geography
        n.oa21_code,
        n.lsoa21_code,
        n.msoa21_code,
        n.local_authority_code as ons_local_authority_code,
        n.country_code,
        n.region_code,

        -- Whether the FSA postcode matched NSPL
        case
            when n.postcode_join_key is not null then 1
            else 0
        end as ons_postcode_match,

        -- Whether usable LSOA geography exists
        case
            when n.lsoa21_code is not null then 1
            else 0
        end as ons_lsoa_available,

        -- Whether NSPL says this postcode is terminated
        n.is_terminated as ons_postcode_terminated

    from fsa as f

    left join {{ ref('nspl_postcodes_clean') }} as n

        on regexp_replace(
            upper(trim(f.postcode)),
            '\s+',
            '',
            'g'
        ) = n.postcode_join_key

)

select *
from enriched