import os
import numpy as np

from scipy import sparse
import joblib
import pandas as pd
import psycopg2

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# Database connection settings
DB_HOST = os.environ["RDS_HOST"]
DB_NAME = os.environ["RDS_DB"]
DB_USER = os.environ["RDS_USER"]
DB_PASSWORD = os.environ["RDS_PASSWORD"]
DB_PORT = 5432


# Only load columns that we actually need for ML
QUERY = """
SELECT
    fhrsid,
    rating_date,
    target_low_hygiene,
    dataset_split,

    business_type,
    local_authority_name,

    latitude,
    longitude,
    latitude_missing,
    longitude_missing,

    country_code,
    region_code,

    deprivation_score_uk,
    deprivation_missing,

    companies_house_available,
    company_category,
    country_of_origin,
    company_age_years,
    company_age_missing,
    sic_division

FROM gold.ml_dataset_split

ORDER BY rating_date, fhrsid;
"""


print("Connecting to PostgreSQL...")

connection = psycopg2.connect(
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    port=DB_PORT
)

print("Connected.")

print("Loading ML dataset...")

df = pd.read_sql_query(
    QUERY,
    connection
)

connection.close()

print("Dataset loaded.")
print()
print(f"Total rows: {len(df):,}")
print(f"Total columns: {len(df.columns)}")

print()
print("Dataset split counts:")
print(df["dataset_split"].value_counts())

print()
print("Target distribution:")
print(df["target_low_hygiene"].value_counts())

train_df = df[df["dataset_split"] == "train"].copy()
validation_df = df[df["dataset_split"] == "validation"].copy()
test_df = df[df["dataset_split"] == "test"].copy()

print()
print("Split datasets created:")
print(f"Train:      {len(train_df):,}")
print(f"Validation: {len(validation_df):,}")
print(f"Test:       {len(test_df):,}")


TARGET_COLUMN = "target_low_hygiene"

y_train = train_df[TARGET_COLUMN].copy()
y_validation = validation_df[TARGET_COLUMN].copy()
y_test = test_df[TARGET_COLUMN].copy()

CORE_NUMERIC_FEATURES = [
    "latitude",
    "longitude",
    "deprivation_score_uk",
    "latitude_missing",
    "longitude_missing",
    "deprivation_missing",
]

CORE_CATEGORICAL_FEATURES = [
    "business_type",
    "local_authority_name",
    "country_code",
    "region_code",
]

CORE_FEATURES = (
    CORE_NUMERIC_FEATURES
    + CORE_CATEGORICAL_FEATURES
)

COMPANIES_HOUSE_NUMERIC_FEATURES = [
    "companies_house_available",
    "company_age_years",
    "company_age_missing",
]

COMPANIES_HOUSE_CATEGORICAL_FEATURES = [
    "company_category",
    "country_of_origin",
    "sic_division",
]

EXTENDED_NUMERIC_FEATURES = (
    CORE_NUMERIC_FEATURES
    + COMPANIES_HOUSE_NUMERIC_FEATURES
)

EXTENDED_CATEGORICAL_FEATURES = (
    CORE_CATEGORICAL_FEATURES
    + COMPANIES_HOUSE_CATEGORICAL_FEATURES
)

EXTENDED_FEATURES = (
    EXTENDED_NUMERIC_FEATURES
    + EXTENDED_CATEGORICAL_FEATURES
)

X_train_core = train_df[CORE_FEATURES].copy()
X_validation_core = validation_df[CORE_FEATURES].copy()
X_test_core = test_df[CORE_FEATURES].copy()

X_train_extended = train_df[EXTENDED_FEATURES].copy()
X_validation_extended = validation_df[EXTENDED_FEATURES].copy()
X_test_extended = test_df[EXTENDED_FEATURES].copy()

print()
print("CORE feature count:", len(CORE_FEATURES))
print("EXTENDED feature count:", len(EXTENDED_FEATURES))

print()
print("CORE train shape:")
print(X_train_core.shape)

print()
print("EXTENDED train shape:")
print(X_train_extended.shape)


core_numeric_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="median")
        ),
        (
            "scaler",
            StandardScaler()
        ),
    ]
)

core_categorical_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(
                strategy="most_frequent"
            )
        ),
        (
            "encoder",
            OneHotEncoder(
                handle_unknown="ignore"
            )
        ),
    ]
)


core_preprocessor = ColumnTransformer(
    transformers=[
        (
            "numeric",
            core_numeric_pipeline,
            CORE_NUMERIC_FEATURES
        ),
        (
            "categorical",
            core_categorical_pipeline,
            CORE_CATEGORICAL_FEATURES
        ),
    ]
)

extended_numeric_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="median")
        ),
        (
            "scaler",
            StandardScaler()
        ),
    ]
)

extended_categorical_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(
                strategy="most_frequent"
            )
        ),
        (
            "encoder",
            OneHotEncoder(
                handle_unknown="ignore"
            )
        ),
    ]
)


extended_preprocessor = ColumnTransformer(
    transformers=[
        (
            "numeric",
            extended_numeric_pipeline,
            EXTENDED_NUMERIC_FEATURES
        ),
        (
            "categorical",
            extended_categorical_pipeline,
            EXTENDED_CATEGORICAL_FEATURES
        ),
    ]
)


print()
print("Fitting CORE preprocessor on training data...")

X_train_core_processed = (
    core_preprocessor.fit_transform(
        X_train_core
    )
)

print("CORE preprocessor fitted.")


print()
print("Transforming CORE validation and test data...")

X_validation_core_processed = (
    core_preprocessor.transform(
        X_validation_core
    )
)

X_test_core_processed = (
    core_preprocessor.transform(
        X_test_core
    )
)

print()
print("Fitting EXTENDED preprocessor on training data...")

X_train_extended_processed = (
    extended_preprocessor.fit_transform(
        X_train_extended
    )
)

print("EXTENDED preprocessor fitted.")


print()
print("Transforming EXTENDED validation and test data...")

X_validation_extended_processed = (
    extended_preprocessor.transform(
        X_validation_extended
    )
)

X_test_extended_processed = (
    extended_preprocessor.transform(
        X_test_extended
    )
)

print()
print("Processed dataset shapes:")

print(
    "CORE train:",
    X_train_core_processed.shape
)

print(
    "CORE validation:",
    X_validation_core_processed.shape
)

print(
    "CORE test:",
    X_test_core_processed.shape
)

print(
    "EXTENDED train:",
    X_train_extended_processed.shape
)

print(
    "EXTENDED validation:",
    X_validation_extended_processed.shape
)

print(
    "EXTENDED test:",
    X_test_extended_processed.shape
)

OUTPUT_DIR = "data/processed/ml_ready"
PREPROCESSOR_DIR = "models/preprocessors"

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

os.makedirs(
    PREPROCESSOR_DIR,
    exist_ok=True
)


print()
print("Checking processed matrices for missing values...")


def sparse_has_nan(matrix):

    if sparse.issparse(matrix):
        return np.isnan(matrix.data).any()

    return np.isnan(matrix).any()


datasets_to_check = {
    "X_train_core": X_train_core_processed,
    "X_validation_core": X_validation_core_processed,
    "X_test_core": X_test_core_processed,
    "X_train_extended": X_train_extended_processed,
    "X_validation_extended": X_validation_extended_processed,
    "X_test_extended": X_test_extended_processed,
}


for dataset_name, matrix in datasets_to_check.items():

    contains_nan = sparse_has_nan(matrix)

    print(
        dataset_name,
        "contains NaN:",
        contains_nan
    )


    print()
print("Saving fitted preprocessors...")

joblib.dump(
    core_preprocessor,
    os.path.join(
        PREPROCESSOR_DIR,
        "core_preprocessor.joblib"
    )
)

joblib.dump(
    extended_preprocessor,
    os.path.join(
        PREPROCESSOR_DIR,
        "extended_preprocessor.joblib"
    )
)

print("Preprocessors saved.")


print()
print("Saving processed feature matrices...")

sparse.save_npz(
    os.path.join(
        OUTPUT_DIR,
        "X_train_core.npz"
    ),
    X_train_core_processed
)

sparse.save_npz(
    os.path.join(
        OUTPUT_DIR,
        "X_validation_core.npz"
    ),
    X_validation_core_processed
)

sparse.save_npz(
    os.path.join(
        OUTPUT_DIR,
        "X_test_core.npz"
    ),
    X_test_core_processed
)

sparse.save_npz(
    os.path.join(
        OUTPUT_DIR,
        "X_train_extended.npz"
    ),
    X_train_extended_processed
)

sparse.save_npz(
    os.path.join(
        OUTPUT_DIR,
        "X_validation_extended.npz"
    ),
    X_validation_extended_processed
)

sparse.save_npz(
    os.path.join(
        OUTPUT_DIR,
        "X_test_extended.npz"
    ),
    X_test_extended_processed
)

print("Feature matrices saved.")

print()
print("Saving target arrays...")

np.save(
    os.path.join(
        OUTPUT_DIR,
        "y_train.npy"
    ),
    y_train.to_numpy()
)

np.save(
    os.path.join(
        OUTPUT_DIR,
        "y_validation.npy"
    ),
    y_validation.to_numpy()
)

np.save(
    os.path.join(
        OUTPUT_DIR,
        "y_test.npy"
    ),
    y_test.to_numpy()
)

print("Target arrays saved.")


core_feature_names = (
    core_preprocessor
    .get_feature_names_out()
)

extended_feature_names = (
    extended_preprocessor
    .get_feature_names_out()
)


pd.DataFrame(
    {
        "feature_name": core_feature_names
    }
).to_csv(
    os.path.join(
        OUTPUT_DIR,
        "core_feature_names.csv"
    ),
    index=False
)


pd.DataFrame(
    {
        "feature_name": extended_feature_names
    }
).to_csv(
    os.path.join(
        OUTPUT_DIR,
        "extended_feature_names.csv"
    ),
    index=False
)

train_metadata = train_df[
    [
        "fhrsid",
        "rating_date"
    ]
].copy()

validation_metadata = validation_df[
    [
        "fhrsid",
        "rating_date"
    ]
].copy()

test_metadata = test_df[
    [
        "fhrsid",
        "rating_date"
    ]
].copy()


train_metadata.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "train_metadata.csv"
    ),
    index=False
)

validation_metadata.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "validation_metadata.csv"
    ),
    index=False
)

test_metadata.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "test_metadata.csv"
    ),
    index=False
)


print()
print("=" * 60)
print("ML DATASET BUILD COMPLETE")
print("=" * 60)

print()
print(
    f"CORE features: {len(core_feature_names):,}"
)

print(
    f"EXTENDED features: {len(extended_feature_names):,}"
)

print()
print(
    f"Train rows: {len(y_train):,}"
)

print(
    f"Validation rows: {len(y_validation):,}"
)

print(
    f"Test rows: {len(y_test):,}"
)

print()
print(
    f"Output directory: {OUTPUT_DIR}"
)

print()
print("Running final saved-artifact validation...")


loaded_X_train_core = sparse.load_npz(
    os.path.join(
        OUTPUT_DIR,
        "X_train_core.npz"
    )
)

loaded_X_validation_core = sparse.load_npz(
    os.path.join(
        OUTPUT_DIR,
        "X_validation_core.npz"
    )
)

loaded_X_test_core = sparse.load_npz(
    os.path.join(
        OUTPUT_DIR,
        "X_test_core.npz"
    )
)


loaded_X_train_extended = sparse.load_npz(
    os.path.join(
        OUTPUT_DIR,
        "X_train_extended.npz"
    )
)

loaded_X_validation_extended = sparse.load_npz(
    os.path.join(
        OUTPUT_DIR,
        "X_validation_extended.npz"
    )
)

loaded_X_test_extended = sparse.load_npz(
    os.path.join(
        OUTPUT_DIR,
        "X_test_extended.npz"
    )
)


loaded_y_train = np.load(
    os.path.join(
        OUTPUT_DIR,
        "y_train.npy"
    )
)

loaded_y_validation = np.load(
    os.path.join(
        OUTPUT_DIR,
        "y_validation.npy"
    )
)

loaded_y_test = np.load(
    os.path.join(
        OUTPUT_DIR,
        "y_test.npy"
    )
)


assert loaded_X_train_core.shape == (199339, 401)
assert loaded_X_validation_core.shape == (84455, 401)
assert loaded_X_test_core.shape == (64472, 401)

assert loaded_X_train_extended.shape == (199339, 495)
assert loaded_X_validation_extended.shape == (84455, 495)
assert loaded_X_test_extended.shape == (64472, 495)

assert len(loaded_y_train) == 199339
assert len(loaded_y_validation) == 84455
assert len(loaded_y_test) == 64472

assert len(core_feature_names) == 401
assert len(extended_feature_names) == 495

assert not sparse_has_nan(
    loaded_X_train_core
)

assert not sparse_has_nan(
    loaded_X_validation_core
)

assert not sparse_has_nan(
    loaded_X_test_core
)

assert not sparse_has_nan(
    loaded_X_train_extended
)

assert not sparse_has_nan(
    loaded_X_validation_extended
)

assert not sparse_has_nan(
    loaded_X_test_extended
)

assert set(np.unique(loaded_y_train)).issubset({0, 1})
assert set(np.unique(loaded_y_validation)).issubset({0, 1})
assert set(np.unique(loaded_y_test)).issubset({0, 1})


print()
print("All saved-artifact validation checks passed.")

print()
print("=" * 60)
print("STAGE 14 ML DATA PREPARATION COMPLETE")
print("=" * 60)