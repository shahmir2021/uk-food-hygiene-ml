import json

import joblib
import mlflow
import mlflow.pyfunc
import numpy as np
import pandas as pd
import sklearn
import xgboost


# --------------------------------------------------
# 1. MLflow configuration
# --------------------------------------------------

MLFLOW_TRACKING_URI = "http://127.0.0.1:5000"

EXPERIMENT_NAME = "uk-food-hygiene-stage16"

REGISTERED_MODEL_NAME = "uk-food-hygiene-risk-model"


mlflow.set_tracking_uri(
    MLFLOW_TRACKING_URI
)

mlflow.set_experiment(
    EXPERIMENT_NAME
)


# --------------------------------------------------
# 2. Define complete production prediction model
# --------------------------------------------------

class FoodHygieneRiskModel(
    mlflow.pyfunc.PythonModel
):

    def load_context(
        self,
        context
    ):

        # Load the fitted preprocessing object
        self.preprocessor = joblib.load(
            context.artifacts["preprocessor"]
        )

        # Load the fitted XGBoost model
        self.model = joblib.load(
            context.artifacts["xgboost_model"]
        )

        # Load the fitted Platt calibrator
        self.calibrator = joblib.load(
            context.artifacts["calibrator"]
        )

        # Load the locked Stage 15 configuration
        with open(
            context.artifacts["config"],
            "r"
        ) as file:

            self.config = json.load(file)

        # Locked decision threshold chosen in Stage 15
        self.threshold = float(
            self.config["Decision_Threshold"]
        )

        # Raw columns expected by the preprocessor
        self.required_columns = [
            "latitude",
            "longitude",
            "deprivation_score_uk",
            "latitude_missing",
            "longitude_missing",
            "deprivation_missing",
            "business_type",
            "local_authority_name",
            "country_code",
            "region_code",
        ]


    def predict(
        self,
        context,
        model_input,
        params=None
    ):

        # MLflow normally supplies a DataFrame,
        # but this makes the wrapper more defensive.
        if not isinstance(
            model_input,
            pd.DataFrame
        ):
            model_input = pd.DataFrame(
                model_input
            )

        # --------------------------------------------------
        # Validate required input columns
        # --------------------------------------------------

        missing_columns = [
            column
            for column in self.required_columns
            if column not in model_input.columns
        ]

        if missing_columns:

            raise ValueError(
                "Missing required input columns: "
                + ", ".join(missing_columns)
            )


        # Keep the exact feature order used during training
        raw_features = model_input[
            self.required_columns
        ].copy()


        # --------------------------------------------------
        # Step 1: preprocessing
        # --------------------------------------------------

        transformed_features = (
            self.preprocessor.transform(
                raw_features
            )
        )


        # --------------------------------------------------
        # Step 2: XGBoost raw probability
        # --------------------------------------------------

        raw_probability = (
            self.model.predict_proba(
                transformed_features
            )[:, 1]
        )


        # --------------------------------------------------
        # Step 3: Platt probability calibration
        #
        # The calibrator was trained using one feature,
        # the raw XGBoost probability.
        # --------------------------------------------------

        calibrator_input = np.asarray(
            raw_probability
        ).reshape(-1, 1)

        calibrated_probability = (
            self.calibrator.predict_proba(
                calibrator_input
            )[:, 1]
        )


        # --------------------------------------------------
        # Step 4: apply locked Stage 15 threshold
        # --------------------------------------------------

        prediction = (
            calibrated_probability
            >= self.threshold
        ).astype(int)


        # --------------------------------------------------
        # Return prediction output
        # --------------------------------------------------

        result = pd.DataFrame(
            {
                "raw_probability":
                    raw_probability,

                "calibrated_probability":
                    calibrated_probability,

                "prediction":
                    prediction,

                "risk_label":
                    np.where(
                        prediction == 1,
                        "Low hygiene risk detected",
                        "No low hygiene risk detected"
                    ),
            },
            index=model_input.index
        )

        return result


# --------------------------------------------------
# 3. Model artifacts
# --------------------------------------------------

artifacts = {

    "preprocessor":
        "models/preprocessors/core_preprocessor.joblib",

    "xgboost_model":
        "models/stage15_final_xgboost_core.joblib",

    "calibrator":
        "models/stage15_platt_calibrator.joblib",

    "config":
        "results/stage15_final_model_config.json",
}


# --------------------------------------------------
# 4. Reproducible Python dependencies
# --------------------------------------------------

pip_requirements = [
    f"mlflow=={mlflow.__version__}",
    f"pandas=={pd.__version__}",
    f"numpy=={np.__version__}",
    f"scikit-learn=={sklearn.__version__}",
    f"xgboost=={xgboost.__version__}",
    f"joblib=={joblib.__version__}",
]


# --------------------------------------------------
# 5. Start MLflow run
# --------------------------------------------------

with mlflow.start_run(
    run_name="stage16-deployable-model-v1"
) as run:

    # Log important deployment information
    mlflow.log_param(
        "model_type",
        "XGBoost"
    )

    mlflow.log_param(
        "calibration",
        "Platt"
    )

    mlflow.log_param(
        "decision_threshold",
        0.07
    )

    mlflow.log_param(
        "raw_feature_count",
        10
    )

    mlflow.log_param(
        "transformed_feature_count",
        401
    )


    # --------------------------------------------------
    # 6. Package complete model as MLflow PyFunc
    # --------------------------------------------------

    model_info = mlflow.pyfunc.log_model(

        artifact_path=(
            "food_hygiene_risk_model"
        ),

        python_model=(
            FoodHygieneRiskModel()
        ),

        artifacts=artifacts,

        pip_requirements=(
            pip_requirements
        ),
    )


    print(
        "\nMLflow model packaged successfully."
    )

    print(
        "Model URI:",
        model_info.model_uri
    )


    # --------------------------------------------------
    # 7. Reload model to prove package is valid
    # --------------------------------------------------

    loaded_model = (
        mlflow.pyfunc.load_model(
            model_info.model_uri
        )
    )

    print(
        "Model reload test: SUCCESS"
    )


    # --------------------------------------------------
    # 8. Register model in MLflow Model Registry
    # --------------------------------------------------

    registered_model = (
        mlflow.register_model(
            model_uri=model_info.model_uri,
            name=REGISTERED_MODEL_NAME
        )
    )


    print(
        "\nModel registered successfully."
    )

    print(
        "Registered model:",
        REGISTERED_MODEL_NAME
    )

    print(
        "Model version:",
        registered_model.version
    )

    print(
        "Run ID:",
        run.info.run_id
    )