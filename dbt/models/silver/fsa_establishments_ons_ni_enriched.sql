{{ config(materialized='table') }}

with enriched as (

    select

        -- Keep everything already created for FSA + ONS + England + Wales
        f.*,

        -- Northern Ireland old SOA geography
        b.lsoa01_code as ni_soa01_code,

        -- Northern Ireland deprivation measures
        n.nimdm2017_rank,
        n.nimdm2017_decile,

        -- Whether Northern Ireland deprivation data was available
        case
            when n.soa01_code is not null then 1
            else 0
        end as nimdm2017_available,

        -- UK comparable deprivation decile so far
        -- 1 = most deprived 10%
        -- 10 = least deprived 10%
        coalesce(
            f.deprivation_decile,
            n.nimdm2017_decile
        ) as uk_deprivation_decile,

        -- Record where the deprivation value came from
        case
            when f.deprivation_source is not null
                then f.deprivation_source
            when n.soa01_code is not null
                then 'NIMDM2017_Northern_Ireland'
            else null
        end as uk_deprivation_source

    from {{ ref('fsa_establishments_ons_deprivation_enriched') }} as f

    -- Match the FSA postcode to the old Northern Ireland geography
    left join {{ ref('onspd_ni_bridge_clean') }} as b
        on regexp_replace(
            upper(trim(f.postcode)),
            '\s+',
            '',
            'g'
        ) = b.postcode_join_key

    -- Match old SOA geography to NIMDM 2017
    left join {{ ref('nimdm_2017_clean') }} as n
        on b.lsoa01_code = n.soa01_code

)

select *
from enriched