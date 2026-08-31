import pandas as pd
import psycopg2
from pathlib import Path


# --------------------------------
# 1. Full FSA bulk CSV
# --------------------------------

CSV_FILE = Path(
    "data/raw/fsa_establishments_full.csv"
)

print("Bulk FSA loader ready")
print("File exists:", CSV_FILE.exists())

# --------------------------------
# 2. Connect to PostgreSQL
# --------------------------------

connection = psycopg2.connect(
    host="host.docker.internal",
    port=5433,
    database="food_hygiene",
    user="postgres",
    password="postgres"
)

cursor = connection.cursor()

print("Connected to PostgreSQL successfully")


# --------------------------------
# 3. Create full-scale Bronze table
# --------------------------------

cursor.execute("""
CREATE SCHEMA IF NOT EXISTS bronze;

CREATE TABLE IF NOT EXISTS bronze.fsa_establishments_full_raw (
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
    structural TEXT
);
""")

connection.commit()

print("Full-scale Bronze table ready")


# --------------------------------
# 4. Load full CSV into Bronze
# --------------------------------

# Clear the table first so rerunning the script
# does not create duplicate rows
cursor.execute("""
TRUNCATE TABLE bronze.fsa_establishments_full_raw;
""")

connection.commit()

print("Bronze table cleared")


copy_sql = """
COPY bronze.fsa_establishments_full_raw (
    address_line1,
    address_line2,
    address_line3,
    address_line4,
    business_type_id,
    fhrsid,
    business_name,
    business_type,
    confidence_in_management,
    hygiene,
    latitude,
    local_authority_business_id,
    local_authority_code,
    local_authority_name,
    longitude,
    new_rating_pending,
    postcode,
    rating_date,
    rating_key,
    rating_value,
    right_to_reply,
    scheme_type,
    structural
)
FROM STDIN
WITH (
    FORMAT CSV,
    HEADER TRUE
);
"""


# Stream the CSV directly into PostgreSQL
with open(
    CSV_FILE,
    "r",
    encoding="utf-8-sig",
    newline=""
) as file:

    cursor.copy_expert(
        copy_sql,
        file
    )


connection.commit()

print("Full FSA CSV loaded into Bronze")

# --------------------------------
# 5. Verify Bronze row count
# --------------------------------

cursor.execute("""
SELECT COUNT(*)
FROM bronze.fsa_establishments_full_raw;
""")

bronze_rows = cursor.fetchone()[0]

print("Bronze rows:", bronze_rows)


cursor.close()
connection.close()