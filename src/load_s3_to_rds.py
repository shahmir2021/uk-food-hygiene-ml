import os
import boto3
import psycopg2


# ============================================================
# AWS S3 SETTINGS
# ============================================================

S3_BUCKET = os.environ["S3_BUCKET"]
AWS_REGION = os.environ["AWS_REGION"]

# Location of the full FSA dataset inside S3
S3_KEY = "raw/fsa_establishments_full.csv"

# Temporary local copy inside the Airflow container
LOCAL_FILE = "/tmp/fsa_establishments_full.csv"


# ============================================================
# CSV COLUMN ORDER
# Must match the order in the FSA CSV file
# ============================================================

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


# ============================================================
# 1. DOWNLOAD DATA FROM AWS S3
# ============================================================

print("Downloading FSA dataset from S3...")

# Connect to AWS S3 using boto3
s3 = boto3.client(
    "s3",
    region_name=AWS_REGION,
)

# Download the full FSA CSV from S3
s3.download_file(
    S3_BUCKET,
    S3_KEY,
    LOCAL_FILE,
)

print("FSA dataset downloaded successfully.")


# ============================================================
# 2. CONNECT TO AWS RDS POSTGRESQL
# ============================================================

print("Connecting to AWS RDS...")

conn = psycopg2.connect(
    host=os.environ["RDS_HOST"],
    port=5432,
    dbname=os.environ["RDS_DB"],
    user=os.environ["RDS_USER"],
    password=os.environ["RDS_PASSWORD"],
)

cur = conn.cursor()

print("Connected to AWS RDS.")


# ============================================================
# 3. CREATE / RESET BRONZE TABLE
# ============================================================

print("Preparing Bronze table...")

cur.execute(
    """
    CREATE SCHEMA IF NOT EXISTS bronze;

    CREATE TABLE IF NOT EXISTS bronze.fsa_establishments_raw (
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

    TRUNCATE TABLE bronze.fsa_establishments_raw
    RESTART IDENTITY;
    """
)

print("Bronze table ready.")


# ============================================================
# 4. LOAD CSV INTO BRONZE
# ============================================================

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
    cur.copy_expert(
        copy_sql,
        file,
    )

conn.commit()

print("Data load committed.")


# ============================================================
# 5. CHECK NUMBER OF LOADED ROWS
# ============================================================

cur.execute(
    """
    SELECT COUNT(*)
    FROM bronze.fsa_establishments_raw;
    """
)

row_count = cur.fetchone()[0]

print(f"Loaded {row_count:,} rows into AWS RDS Bronze.")


# ============================================================
# 6. CLOSE DATABASE CONNECTION
# ============================================================

cur.close()
conn.close()

print("S3 to RDS load completed successfully.")