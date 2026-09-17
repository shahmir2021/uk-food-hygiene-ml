import os

import requests
import streamlit as st


st.set_page_config(
    page_title="Predict Risk",
    page_icon="🔎",
    layout="centered",
)


# --------------------------------------------------
# API configuration
# --------------------------------------------------

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://18.130.229.195:8000",
)

PREDICT_URL = f"{API_BASE_URL}/predict"
HEALTH_URL = f"{API_BASE_URL}/health"


# --------------------------------------------------
# Business types
# --------------------------------------------------

BUSINESS_TYPES = [

    "Restaurant/Cafe/Canteen",

    "Takeaway/sandwich shop",

    "Pub/bar/nightclub",

    "Retailers - other",

    "Retailers - supermarkets/hypermarkets",

    "School/college/university",

    "Hotel/bed & breakfast/guest house",

    "Hospitals/Childcare/Caring Premises",

    "Mobile caterer",

    "Other catering premises",

    "Manufacturers/packers",

    "Distributors/Transporters",
]


# --------------------------------------------------
# ONS codes
# --------------------------------------------------

COUNTRY_CODES = {

    "England": "E92000001",

    "Scotland": "S92000003",

    "Wales": "W92000004",

    "Northern Ireland": "N92000002",
}


REGION_CODES = {

    "North East": "E12000001",

    "North West": "E12000002",

    "Yorkshire and The Humber": "E12000003",

    "East Midlands": "E12000004",

    "West Midlands": "E12000005",

    "East of England": "E12000006",

    "London": "E12000007",

    "South East": "E12000008",

    "South West": "E12000009",
}


# --------------------------------------------------
# Helper functions
# --------------------------------------------------

def api_online():

    try:

        response = requests.get(
            HEALTH_URL,
            timeout=5,
        )

        return response.status_code == 200

    except requests.RequestException:

        return False


def lookup_postcode(postcode):

    postcode = (
        postcode
        .strip()
        .replace(" ", "")
    )

    url = (
        f"https://api.postcodes.io/postcodes/{postcode}"
    )

    response = requests.get(
        url,
        timeout=10,
    )

    if response.status_code != 200:

        raise ValueError(
            "Postcode could not be found."
        )

    return response.json()["result"]


def build_payload(
    location,
    business_type,
):

    latitude = location.get(
        "latitude"
    )

    longitude = location.get(
        "longitude"
    )

    authority = (
        location.get("admin_district")
        or "Unknown"
    )

    country = (
        location.get("country")
        or "Unknown"
    )

    region = (
        location.get("region")
        or country
    )


    country_code = COUNTRY_CODES.get(
        country,
        "UNKNOWN",
    )

    region_code = REGION_CODES.get(
        region,
        country_code,
    )


    return {

        "latitude":
            latitude,

        "longitude":
            longitude,

        "deprivation_score_uk":
            None,

        "latitude_missing":
            int(latitude is None),

        "longitude_missing":
            int(longitude is None),

        "deprivation_missing":
            1,

        "business_type":
            business_type,

        "local_authority_name":
            authority,

        "country_code":
            country_code,

        "region_code":
            region_code,
    }


# --------------------------------------------------
# Page
# --------------------------------------------------

st.title("🔎 Predict Hygiene Risk")

st.write(
    """
    Check the predicted hygiene risk for a food business.

    You only need two pieces of information.
    """
)


# --------------------------------------------------
# API status
# --------------------------------------------------

if api_online():

    st.success(
        "Prediction service online"
    )

else:

    st.error(
        "Prediction service unavailable"
    )


st.divider()


# --------------------------------------------------
# Form
# --------------------------------------------------

with st.form(
    "prediction_form"
):

    business_type = st.selectbox(

        "Business type",

        BUSINESS_TYPES,

        help=(
            "Choose the category that best describes "
            "the food business."
        ),
    )


    postcode = st.text_input(

        "Business postcode",

        placeholder="Example: B1 1BB",
    )


    submitted = st.form_submit_button(

        "Predict hygiene risk",

        type="primary",

        use_container_width=True,
    )


# --------------------------------------------------
# Prediction
# --------------------------------------------------

if submitted:

    if not postcode.strip():

        st.warning(
            "Please enter a postcode."
        )

        st.stop()


    try:

        with st.spinner(
            "Analysing business location..."
        ):

            location = lookup_postcode(
                postcode
            )

            payload = build_payload(
                location,
                business_type,
            )


            response = requests.post(

                PREDICT_URL,

                json=payload,

                timeout=30,
            )


            response.raise_for_status()

            result = response.json()


        probability = float(
            result["calibrated_probability"]
        )

        prediction = int(
            result["prediction"]
        )


        st.divider()

        st.header(
            "Prediction result"
        )


        # --------------------------------------------------
        # Location
        # --------------------------------------------------

        detected_postcode = location.get(
            "postcode",
            postcode.upper(),
        )

        authority = location.get(
            "admin_district",
            "Unknown",
        )

        region = (
            location.get("region")
            or location.get("country")
            or "UK"
        )


        st.info(
            f"📍 {detected_postcode} | "
            f"{authority}, {region}"
        )


        # --------------------------------------------------
        # Result
        # --------------------------------------------------

        if prediction == 1:

            st.error(
                "⚠️ Higher risk of a low hygiene rating"
            )

        else:

            st.success(
                "✅ Lower risk of a low hygiene rating"
            )


        st.metric(

            label="Estimated risk",

            value=f"{probability * 100:.1f}%"
        )


        st.progress(
            min(
                max(
                    probability,
                    0.0,
                ),
                1.0,
            )
        )


        if prediction == 1:

            st.write(
                """
                The model identified characteristics
                associated with a higher predicted risk
                of receiving a low hygiene rating.
                """
            )

        else:

            st.write(
                """
                The model identified this business as
                having a lower predicted risk of receiving
                a low hygiene rating.
                """
            )


        st.caption(
            "This is a machine learning estimate, "
            "not an official hygiene inspection result."
        )


        # --------------------------------------------------
        # Technical details
        # --------------------------------------------------

        with st.expander(
            "Technical prediction details"
        ):

            st.write(
                "Model classification:",
                result["risk_label"],
            )

            st.write(
                "Raw XGBoost probability:",
                result["raw_probability"],
            )

            st.write(
                "Calibrated probability:",
                result[
                    "calibrated_probability"
                ],
            )

            st.write(
                "Binary prediction:",
                prediction,
            )

            st.write(
                "Local authority:",
                authority,
            )

            st.write(
                "Latitude:",
                payload["latitude"],
            )

            st.write(
                "Longitude:",
                payload["longitude"],
            )


    except ValueError as error:

        st.error(
            str(error)
        )


    except requests.exceptions.Timeout:

        st.error(
            "The prediction service took too long to respond."
        )


    except requests.exceptions.ConnectionError:

        st.error(
            "Could not connect to the prediction service."
        )


    except requests.exceptions.HTTPError:

        st.error(
            "The prediction API returned an error."
        )


    except Exception as error:

        st.error(
            f"Unexpected error: {error}"
        )