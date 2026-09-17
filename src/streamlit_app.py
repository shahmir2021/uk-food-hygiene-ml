import streamlit as st


st.set_page_config(
    page_title="UK Food Hygiene ML",
    page_icon="🍽️",
    layout="wide",
)


# --------------------------------------------------
# Header
# --------------------------------------------------

st.title("🍽️ UK Food Hygiene Risk")

st.subheader(
    "Machine learning analysis of UK food hygiene risk"
)

st.write(
    """
    This project uses public UK data and machine learning
    to estimate whether a food business may be at risk of
    receiving a low hygiene rating.
    """
)


st.divider()


# --------------------------------------------------
# Main navigation cards
# --------------------------------------------------

col1, col2, col3 = st.columns(3)


with col1:

    st.subheader("🔎 Predict Risk")

    st.write(
        """
        Enter a business type and postcode.

        The application automatically retrieves the
        location information needed by the model.
        """
    )

    st.page_link(
        "pages/1_Predict_Risk.py",
        label="Open predictor",
        icon="🔎",
    )


with col2:

    st.subheader("📊 Hygiene Analytics")

    st.write(
        """
        Explore hygiene ratings across business types
        and local authorities.
        """
    )

    st.page_link(
        "pages/2_Hygiene_Analytics.py",
        label="View analytics",
        icon="📊",
    )


with col3:

    st.subheader("🧠 Model Performance")

    st.write(
        """
        Explore the selected machine learning model,
        validation metrics, calibration and threshold.
        """
    )

    st.page_link(
        "pages/3_Model_Performance.py",
        label="View model",
        icon="🧠",
    )


st.divider()


# --------------------------------------------------
# Project overview
# --------------------------------------------------

st.header("How it works")

st.write(
    """
    **1. Public UK data**

    Food Standards Agency and geographical data are
    collected and processed.

    **2. Feature engineering**

    Business and area information is transformed into
    machine learning features.

    **3. Machine learning**

    The production XGBoost model estimates the probability
    of a low hygiene rating.

    **4. Production API**

    The trained model is served through FastAPI running
    inside Docker on AWS ECS Fargate.

    **5. User interface**

    This Streamlit application communicates with the
    production API and displays the prediction.
    """
)


st.info(
    "This system provides a machine learning risk estimate. "
    "It is not an official Food Standards Agency hygiene rating."
)