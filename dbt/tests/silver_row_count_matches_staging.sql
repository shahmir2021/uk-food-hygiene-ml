WITH staging_count AS (
    SELECT COUNT(*) AS row_count
    FROM {{ ref('stg_fsa_establishments') }}
),

silver_count AS (
    SELECT COUNT(*) AS row_count
    FROM {{ ref('fsa_establishments_clean') }}
)

SELECT
    staging_count.row_count AS staging_rows,
    silver_count.row_count AS silver_rows

FROM staging_count
CROSS JOIN silver_count

WHERE staging_count.row_count <> silver_count.row_count