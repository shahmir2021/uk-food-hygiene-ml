with source as (

    select *
    from {{ source('bronze', 'companies_house_raw') }}

),

cleaned as (

    select

        trim(company_name) as company_name,

        upper(trim(company_number)) as company_number,

        nullif(upper(trim(registered_postcode)), '') as registered_postcode,

        regexp_replace(
            upper(trim(registered_postcode)),
            '\s+',
            '',
            'g'
        ) as postcode_join_key,

        nullif(trim(company_status), '') as company_status,

        nullif(trim(company_category), '') as company_category,

        nullif(trim(country_of_origin), '') as country_of_origin,

        case
            when nullif(trim(incorporation_date), '') is not null
            then to_date(
                trim(incorporation_date),
                'DD/MM/YYYY'
            )
        end as incorporation_date,

        case
            when nullif(trim(dissolution_date), '') is not null
            then to_date(
                trim(dissolution_date),
                'DD/MM/YYYY'
            )
        end as dissolution_date,

        nullif(trim(accounts_category), '') as accounts_category,

        case
            when nullif(trim(accounts_last_made_up_date), '') is not null
            then to_date(
                trim(accounts_last_made_up_date),
                'DD/MM/YYYY'
            )
        end as accounts_last_made_up_date,

        case
            when nullif(trim(accounts_next_due_date), '') is not null
            then to_date(
                trim(accounts_next_due_date),
                'DD/MM/YYYY'
            )
        end as accounts_next_due_date,

        case
            when nullif(trim(mortgages_num_charges), '') is not null
            then mortgages_num_charges::integer
        end as mortgages_num_charges,

        case
            when nullif(trim(mortgages_num_outstanding), '') is not null
            then mortgages_num_outstanding::integer
        end as mortgages_num_outstanding,

        case
            when nullif(trim(mortgages_num_part_satisfied), '') is not null
            then mortgages_num_part_satisfied::integer
        end as mortgages_num_part_satisfied,

        case
            when nullif(trim(mortgages_num_satisfied), '') is not null
            then mortgages_num_satisfied::integer
        end as mortgages_num_satisfied,

        nullif(trim(sic_text_1), '') as sic_text_1,

        nullif(trim(sic_text_2), '') as sic_text_2,

        nullif(trim(sic_text_3), '') as sic_text_3,

        nullif(trim(sic_text_4), '') as sic_text_4,

        case
            when sic_text_1 ~ '^[0-9]{5}'
            then substring(sic_text_1 from '^[0-9]{5}')
        end as sic_code_1,

        case
            when sic_text_2 ~ '^[0-9]{5}'
            then substring(sic_text_2 from '^[0-9]{5}')
        end as sic_code_2,

        case
            when sic_text_3 ~ '^[0-9]{5}'
            then substring(sic_text_3 from '^[0-9]{5}')
        end as sic_code_3,

        case
            when sic_text_4 ~ '^[0-9]{5}'
            then substring(sic_text_4 from '^[0-9]{5}')
        end as sic_code_4,

        case
            when lower(trim(company_status)) = 'active'
            then 1
            else 0
        end as company_active,

        ingested_at

    from source

)

select *
from cleaned