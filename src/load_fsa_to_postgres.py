import json
import psycopg2
from psycopg2.extras import execute_values, Json


# -----------------------------------
# 1. Load the raw FSA JSON file
# -----------------------------------

with open("data/raw/fsa_westminster_sample.json", "r") as file:
    raw_data = json.load(file)

establishments = raw_data["establishments"]

print(f"Records found: {len(establishments)}")


# -----------------------------------
# 2. Connect to PostgreSQL
# -----------------------------------

connection = psycopg2.connect(
    host="host.docker.internal",
    port=5433,
    database="food_hygiene",
    user="postgres",
    password="postgres"
)

cursor = connection.cursor()


# -----------------------------------
# 3. Prepare the rows
# -----------------------------------

rows = []

for business in establishments:

    rows.append(
        (
            business.get("AddressLine1"),
            business.get("AddressLine2"),
            business.get("AddressLine3"),
            business.get("AddressLine4"),
            business.get("BusinessName"),
            business.get("BusinessType"),
            business.get("BusinessTypeID"),
            business.get("ChangesByServerID"),
            business.get("Distance"),
            business.get("FHRSID"),
            business.get("LocalAuthorityBusinessID"),
            business.get("LocalAuthorityCode"),
            business.get("LocalAuthorityEmailAddress"),
            business.get("LocalAuthorityName"),
            business.get("LocalAuthorityWebSite"),
            business.get("NewRatingPending"),
            business.get("Phone"),
            business.get("PostCode"),
            business.get("RatingDate"),
            business.get("RatingKey"),
            business.get("RatingValue"),
            business.get("RightToReply"),
            business.get("SchemeType"),

            # Convert Python dictionaries into PostgreSQL JSONB
            Json(business.get("geocode")),
            Json(business.get("scores"))
        )
    )


# -----------------------------------
# 4. Insert the records into Bronze
# -----------------------------------

insert_query = """
INSERT INTO bronze.fsa_establishments_raw (
    address_line1,
    address_line2,
    address_line3,
    address_line4,
    business_name,
    business_type,
    business_type_id,
    changes_by_server_id,
    distance,
    fhrsid,
    local_authority_business_id,
    local_authority_code,
    local_authority_email_address,
    local_authority_name,
    local_authority_website,
    new_rating_pending,
    phone,
    postcode,
    rating_date,
    rating_key,
    rating_value,
    right_to_reply,
    scheme_type,
    geocode,
    scores
)
VALUES %s
"""

execute_values(
    cursor,
    insert_query,
    rows
)


# -----------------------------------
# 5. Save the changes
# -----------------------------------

connection.commit()

print(f"Successfully inserted {len(rows)} records into Bronze.")


# -----------------------------------
# 6. Close the database connection
# -----------------------------------

cursor.close()
connection.close()