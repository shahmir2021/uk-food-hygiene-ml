import os
import boto3
import psycopg2


# ============================================================
# 1. AWS SETTINGS
# ============================================================

AWS_REGION = os.environ.get(
    "AWS_REGION",
    "eu-west-2"
)

S3_BUCKET = os.environ["S3_BUCKET"]

S3_KEY = (
    "raw/companies_house/2026-09/"
    "companies_house_selected_2026_09.csv"
)

# Temporary local copy downloaded from S3
LOCAL_FILE = "/tmp/companies_house_selected_2026_09.csv"


# ============================================================
# 2. AWS RDS SETTINGS
#
# These match the variable names already stored
# inside your .env.airflow file.
# ============================================================

RDS_HOST = os.environ["RDS_HOST"]

RDS_PORT = os.environ.get(
    "RDS_PORT",
    "5432"
)

RDS_DB = os.environ["RDS_DB"]

RDS_USER = os.environ["RDS_USER"]

RDS_PASSWORD = os.environ["RDS_PASSWORD"]


# ============================================================
# 3. START
# ============================================================

print()
print("=" * 65)
print("COMPANIES HOUSE S3 TO RDS BRONZE LOAD")
print("=" * 65)


# ============================================================
# 4. DOWNLOAD COMPANIES HOUSE CSV FROM S3
# ============================================================

print()
print("Connecting to AWS S3...")

s3 = boto3.client(
    "s3",
    region_name=AWS_REGION
)

print("Downloading Companies House dataset from S3...")
print(f"Bucket: {S3_BUCKET}")
print(f"Key: {S3_KEY}")

s3.download_file(
    S3_BUCKET,
    S3_KEY,
    LOCAL_FILE
)

print("Companies House data downloaded.")

file_size_mb = os.path.getsize(LOCAL_FILE) / (1024 * 1024)

print(
    f"Temporary file size: "
    f"{file_size_mb:,.2f} MB"
)


# ============================================================
# 5. CONNECT TO AWS RDS POSTGRESQL
# ============================================================

print()
print("Connecting to AWS RDS...")

conn = psycopg2.connect(
    host=RDS_HOST,
    port=RDS_PORT,
    dbname=RDS_DB,
    user=RDS_USER,
    password=RDS_PASSWORD,
    connect_timeout=30
)

cur = conn.cursor()

print("Connected to AWS RDS.")


# ============================================================
# 6. CREATE BRONZE SCHEMA
# ============================================================

print()
print("Preparing Bronze schema...")

cur.execute(
    """
    CREATE SCHEMA IF NOT EXISTS bronze;
    """
)

conn.commit()

print("Bronze schema ready.")


# ============================================================
# 7. DROP OLD COMPANIES HOUSE TABLE
#
# We are creating a fresh snapshot from the
# September 2026 Companies House bulk dataset.
# ============================================================

print()
print("Removing previous Companies House Bronze table if present...")

cur.execute(
    """
    DROP TABLE IF EXISTS bronze.companies_house_raw;
    """
)

conn.commit()


# ============================================================
# 8. CREATE COMPANIES HOUSE BRONZE TABLE
#
# Bronze keeps the source data close to its original form.
# Most fields are TEXT.
#
# We will clean and cast fields later using dbt Silver.
# ============================================================

print("Creating bronze.companies_house_raw...")

cur.execute(
    """
    CREATE TABLE bronze.companies_house_raw (

        company_name TEXT,

        company_number TEXT,

        registered_postcode TEXT,

        company_status TEXT,

        company_category TEXT,

        country_of_origin TEXT,

        incorporation_date TEXT,

        dissolution_date TEXT,

        accounts_category TEXT,

        accounts_last_made_up_date TEXT,

        accounts_next_due_date TEXT,

        mortgages_num_charges TEXT,

        mortgages_num_outstanding TEXT,

        mortgages_num_part_satisfied TEXT,

        mortgages_num_satisfied TEXT,

        sic_text_1 TEXT,

        sic_text_2 TEXT,

        sic_text_3 TEXT,

        sic_text_4 TEXT,

        ingested_at TIMESTAMPTZ
            DEFAULT CURRENT_TIMESTAMP
    );
    """
)

conn.commit()

print("Companies House Bronze table created.")


# ============================================================
# 9. LOAD CSV USING POSTGRESQL COPY
#
# COPY is much faster than INSERT for 5.7 million rows.
#
# The input CSV contains 19 columns.
#
# ingested_at is not included because PostgreSQL
# generates it automatically.
# ============================================================

print()
print("Loading Companies House data into RDS...")
print("Approximately 5.7 million rows will be loaded.")
print("This may take several minutes.")
print()

copy_sql = """
COPY bronze.companies_house_raw (

    company_name,

    company_number,

    registered_postcode,

    company_status,

    company_category,

    country_of_origin,

    incorporation_date,

    dissolution_date,

    accounts_category,

    accounts_last_made_up_date,

    accounts_next_due_date,

    mortgages_num_charges,

    mortgages_num_outstanding,

    mortgages_num_part_satisfied,

    mortgages_num_satisfied,

    sic_text_1,

    sic_text_2,

    sic_text_3,

    sic_text_4

)

FROM STDIN

WITH (

    FORMAT CSV,

    HEADER TRUE,

    DELIMITER ',',

    QUOTE '"',

    ESCAPE '"'

);
"""


with open(
    LOCAL_FILE,
    "r",
    encoding="utf-8",
    newline=""
) as csv_file:

    cur.copy_expert(
        copy_sql,
        csv_file
    )


conn.commit()

print("Companies House load committed successfully.")


# ============================================================
# 10. VALIDATE TOTAL ROW COUNT
# ============================================================

print()
print("Validating Companies House Bronze table...")

cur.execute(
    """
    SELECT COUNT(*)
    FROM bronze.companies_house_raw;
    """
)

row_count = cur.fetchone()[0]


# ============================================================
# 11. VALIDATE IMPORTANT COLUMNS
# ============================================================

cur.execute(
    """
    SELECT

        COUNT(*) FILTER (
            WHERE company_number IS NOT NULL
              AND TRIM(company_number) <> ''
        ) AS company_numbers_present,

        COUNT(*) FILTER (
            WHERE company_name IS NOT NULL
              AND TRIM(company_name) <> ''
        ) AS company_names_present,

        COUNT(*) FILTER (
            WHERE registered_postcode IS NOT NULL
              AND TRIM(registered_postcode) <> ''
        ) AS postcodes_present,

        COUNT(*) FILTER (
            WHERE company_status IS NOT NULL
              AND TRIM(company_status) <> ''
        ) AS company_status_present,

        COUNT(*) FILTER (
            WHERE sic_text_1 IS NOT NULL
              AND TRIM(sic_text_1) <> ''
        ) AS sic_present

    FROM bronze.companies_house_raw;
    """
)

validation = cur.fetchone()

company_number_count = validation[0]

company_name_count = validation[1]

postcode_count = validation[2]

company_status_count = validation[3]

sic_count = validation[4]


# ============================================================
# 12. CHECK DUPLICATE COMPANY NUMBERS
#
# CompanyNumber should identify a company uniquely.
# We only print the count here.
# Later dbt tests will enforce data quality.
# ============================================================

cur.execute(
    """
    SELECT COUNT(*)
    FROM (
        SELECT company_number
        FROM bronze.companies_house_raw
        WHERE company_number IS NOT NULL
          AND TRIM(company_number) <> ''
        GROUP BY company_number
        HAVING COUNT(*) > 1
    ) AS duplicates;
    """
)

duplicate_company_numbers = cur.fetchone()[0]


# ============================================================
# 13. SAMPLE DATA
# ============================================================

cur.execute(
    """
    SELECT
        company_name,
        company_number,
        registered_postcode,
        company_status,
        incorporation_date,
        sic_text_1

    FROM bronze.companies_house_raw

    LIMIT 5;
    """
)

sample_rows = cur.fetchall()


# ============================================================
# 14. CLOSE DATABASE CONNECTION
# ============================================================

cur.close()

conn.close()

print()
print("AWS RDS connection closed.")


# ============================================================
# 15. REMOVE TEMPORARY 1.1 GB FILE
# ============================================================

if os.path.exists(LOCAL_FILE):

    os.remove(LOCAL_FILE)

    print("Temporary local Companies House file removed.")


# ============================================================
# 16. FINAL RESULTS
# ============================================================

print()
print("=" * 65)
print("COMPANIES HOUSE S3 TO RDS BRONZE COMPLETE")
print("=" * 65)

print()
print(f"Rows loaded:               {row_count:,}")

print(
    f"Company numbers present:   "
    f"{company_number_count:,}"
)

print(
    f"Company names present:     "
    f"{company_name_count:,}"
)

print(
    f"Postcodes present:         "
    f"{postcode_count:,}"
)

print(
    f"Company statuses present:  "
    f"{company_status_count:,}"
)

print(
    f"Primary SIC present:       "
    f"{sic_count:,}"
)

print(
    f"Duplicate company numbers: "
    f"{duplicate_company_numbers:,}"
)


# ============================================================
# 17. PRINT SAMPLE
# ============================================================

print()
print("Sample Companies House rows:")
print()

for row in sample_rows:

    print(row)


# ============================================================
# 18. DESTINATION
# ============================================================

print()
print("Destination table:")

print(
    "bronze.companies_house_raw"
)

print()
print("=" * 65)