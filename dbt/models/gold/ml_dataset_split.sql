with base as (

    select *
    from {{ ref('ml_features_prepared') }}

),

split_data as (

    select

        *,

        case

            when rating_date < date '2026-01-01'
                then 'train'

            when rating_date < date '2026-05-01'
                then 'validation'

            else 'test'

        end as dataset_split

    from base

)

select *
from split_data