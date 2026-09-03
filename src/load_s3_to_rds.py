import os
import subprocess

import psycopg2


# AWS S3 location
S3_BUCKET = os.environ["S3_BUCKET"]
S3_KEY = "raw/fsa_establishments_full.csv"

# Temporary local copy downloaded from S3
LOCAL_FILE = "/tmp/fsa_establishments_full.csv"

# CSV columns, kept in the same order as the FSA file
COLUMNS = [
    "address_line1",
    "address_line2",
    "address_line3",
    "address_line4",
    "business_type_id",
    "fhrsid",
    "business_name",
    "business_type",
    "confidence_in_management",
    "hygiene",
    "latitude",
    "local_authority_business_id",
    "local_authority_code",
    "local_authority_name",
    "longitude",
    "new_rating_pending",
    "postcode",
    "rating_date",
    "rating_key",
    "rating_value",
    "right_to_reply",
    "scheme_type",
    "structural",
]


print("Downloading FSA dataset from S3...")

subprocess.run(
    [
        "aws",
        "s3",
        "cp",
        f"s3://{S3_BUCKET}/{S3_KEY}",
        LOCAL_FILE,
    ],
    check=True,
)


print("Connecting to AWS RDS...")

conn = psycopg2.connect(
    host=os.environ["RDS_HOST"],
    port=5432,
    dbname=os.environ["RDS_DB"],
    user=os.environ["RDS_USER"],
    password=os.environ["RDS_PASSWORD"],
)

cur = conn.cursor()


print("Creating Bronze table...")

cur.execute(
    """
    CREATE SCHEMA IF NOT EXISTS bronze;

    DROP TABLE IF EXISTS bronze.fsa_establishments_raw;

    CREATE TABLE bronze.fsa_establishments_raw (
        bronze_id BIGSERIAL PRIMARY KEY,
        address_line1 TEXT,
        address_line2 TEXT,
        address_line3 TEXT,
        address_line4 TEXT,
        business_type_id TEXT,
        fhrsid TEXT,
        business_name TEXT,
        business_type TEXT,
        confidence_in_management TEXT,
        hygiene TEXT,
        latitude TEXT,
        local_authority_business_id TEXT,
        local_authority_code TEXT,
        local_authority_name TEXT,
        longitude TEXT,
        new_rating_pending TEXT,
        postcode TEXT,
        rating_date TEXT,
        rating_key TEXT,
        rating_value TEXT,
        right_to_reply TEXT,
        scheme_type TEXT,
        structural TEXT,
        ingested_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
    );
    """
)


print("Loading data into Bronze...")

copy_sql = f"""
COPY bronze.fsa_establishments_raw ({", ".join(COLUMNS)})
FROM STDIN
WITH (
    FORMAT CSV,
    HEADER TRUE
)
"""

with open(LOCAL_FILE, "r", encoding="utf-8") as file:
    cur.copy_expert(copy_sql, file)

conn.commit()


cur.execute(
    "SELECT COUNT(*) FROM bronze.fsa_establishments_raw;"
)

row_count = cur.fetchone()[0]

print(f"Loaded {row_count:,} rows into AWS RDS Bronze.")

cur.close()
conn.close()

print("S3 to RDS load completed successfully.")
