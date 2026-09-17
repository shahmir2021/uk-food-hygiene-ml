import os

import mlflow
import numpy as np
import pandas as pd

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional


# --------------------------------------------------
# 1. FastAPI application
# --------------------------------------------------

app = FastAPI(
    title="UK Food Hygiene Risk API",
    description=(
        "API for predicting whether a food business "
        "is at risk of receiving a low hygiene rating."
    ),
    version="1.0.0",
)


# --------------------------------------------------
# 2. Production model location
# --------------------------------------------------

MODEL_URI = os.getenv(
    "MODEL_URI",
    "models/deploy/production_model"
)


# --------------------------------------------------
# 3. Load production model
# --------------------------------------------------

model = mlflow.pyfunc.load_model(
    MODEL_URI
)


# --------------------------------------------------
# 4. API input schema
# --------------------------------------------------

class BusinessInput(BaseModel):

    latitude: Optional[float] = None

    longitude: Optional[float] = None

    deprivation_score_uk: Optional[float] = None

    latitude_missing: int

    longitude_missing: int

    deprivation_missing: int

    business_type: str

    local_authority_name: str

    country_code: str

    region_code: str


# --------------------------------------------------
# 5. Root endpoint
# --------------------------------------------------

@app.get("/")
def root():

    return {
        "message": "UK Food Hygiene Risk API",
        "docs": "/docs",
        "health": "/health",
        "predict": "/predict",
    }


# --------------------------------------------------
# 6. Health endpoint
# --------------------------------------------------

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "uk-food-hygiene-risk-api",
        "model": "uk-food-hygiene-risk-model",
        "model_source": MODEL_URI,
    }


# --------------------------------------------------
# 7. Prediction endpoint
# --------------------------------------------------

@app.post("/predict")
def predict(
    business: BusinessInput
):

    try:

        # --------------------------------------------------
        # Convert API input into model input
        # --------------------------------------------------

        input_data = pd.DataFrame(
            [
                {
                    "latitude": (
                        business.latitude
                        if business.latitude is not None
                        else np.nan
                    ),

                    "longitude": (
                        business.longitude
                        if business.longitude is not None
                        else np.nan
                    ),

                    "deprivation_score_uk": (
                        business.deprivation_score_uk
                        if business.deprivation_score_uk is not None
                        else np.nan
                    ),

                    "latitude_missing":
                        business.latitude_missing,

                    "longitude_missing":
                        business.longitude_missing,

                    "deprivation_missing":
                        business.deprivation_missing,

                    "business_type":
                        business.business_type,

                    "local_authority_name":
                        business.local_authority_name,

                    "country_code":
                        business.country_code,

                    "region_code":
                        business.region_code,
                }
            ]
        )


        # --------------------------------------------------
        # Run packaged production model
        # --------------------------------------------------

        prediction = model.predict(
            input_data
        )


        # Extract first prediction row
        result = prediction.iloc[0]


        # --------------------------------------------------
        # Extract prediction values
        # --------------------------------------------------

        raw_probability = float(
            result["raw_probability"]
        )

        calibrated_probability = float(
            result["calibrated_probability"]
        )

        prediction_class = int(
            result["prediction"]
        )


        # --------------------------------------------------
        # Correct human-readable risk wording
        # --------------------------------------------------

        if prediction_class == 1:

            risk_label = (
                "Risk of low hygiene rating detected"
            )

        else:

            risk_label = (
                "Lower risk of low hygiene rating"
            )


        # --------------------------------------------------
        # JSON response
        # --------------------------------------------------

        return {

            "raw_probability":
                raw_probability,

            "calibrated_probability":
                calibrated_probability,

            "prediction":
                prediction_class,

            "risk_label":
                risk_label,
        }


    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )