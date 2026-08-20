"""Minimal Poisson model for the Week 4 end-to-end checkpoint."""

from getpass import getpass

import pandas as pd
import psycopg
from io import StringIO

from sklearn.compose import ColumnTransformer
from sklearn.linear_model import PoissonRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


DB_NAME = "kfz_insurance"
DB_USER = "kfz_app"
DB_HOST = "localhost"
DB_PORT = 5432
MODEL_NAME = "checkpoint_poisson_v1"


NUMERIC_FEATURES = [
    "veh_power",
    "veh_age",
    "driv_age",
    "bonus_malus",
    "log_density",
]

CATEGORICAL_FEATURES = [
    "area",
    "veh_gas",
]

def load_model_data(
    connection: psycopg.Connection,
) -> pd.DataFrame:
    """Load the required checkpoint features from PostgreSQL."""

    query = """
        SELECT
            idpol,
            claim_nb,
            exposure,
            veh_power,
            veh_age,
            driv_age,
            bonus_malus,
            log_density,
            area,
            veh_gas
        FROM vw_policy_risk_base;
    """

    with connection.cursor() as cursor:
        cursor.execute(query)

        rows = cursor.fetchall()

        description = cursor.description

        if description is None:
            raise RuntimeError(
                "No column metadata returned from PostgreSQL."
            )

        columns = [
            column.name
            for column in description
        ]

    return pd.DataFrame(
        rows,
        columns=columns,
    )

def prepare_model_data(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
    """Prepare features, annual claim frequency and exposure weights."""

    model_df = df.loc[
        df["exposure"] > 0
    ].copy()

    features = (
        NUMERIC_FEATURES
        + CATEGORICAL_FEATURES
    )

    X = model_df[features]

    y = (
        model_df["claim_nb"]
        / model_df["exposure"]
    )

    sample_weight = model_df["exposure"]

    return X, y, sample_weight

def build_checkpoint_model() -> Pipeline:
    """Build the minimal Poisson pipeline for the checkpoint."""

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "numeric",
                StandardScaler(),
                NUMERIC_FEATURES,
            ),
            (
                "categorical",
                OneHotEncoder(
                    handle_unknown="ignore",
                ),
                CATEGORICAL_FEATURES,
            ),
        ]
    )

    model = PoissonRegressor(
        alpha=0.0,
        max_iter=300,
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )

def create_predictions(
    df: pd.DataFrame,
    X: pd.DataFrame,
    model: Pipeline,
) -> pd.DataFrame:
    """Create policy-level frequency and claim-count predictions."""

    prediction_df = df.loc[
        df["exposure"] > 0,
        [
            "idpol",
            "claim_nb",
            "exposure",
        ],
    ].copy()

    predicted_frequency = pd.Series(
        model.predict(X),
        index=prediction_df.index,
        dtype="float64",
    )

    prediction_df["predicted_claim_frequency"] = (
        predicted_frequency
    )

    prediction_df["predicted_claim_count"] = (
        prediction_df["predicted_claim_frequency"]
        * prediction_df["exposure"]
    )

    return prediction_df

def save_predictions(
    connection: psycopg.Connection,
    predictions: pd.DataFrame,
    model_name: str,
) -> None:
    """Save policy-level predictions to PostgreSQL."""

    output_df = predictions.copy()
    output_df["model_name"] = model_name

    columns = [
        "idpol",
        "claim_nb",
        "exposure",
        "predicted_claim_frequency",
        "predicted_claim_count",
        "model_name",
    ]

    buffer = StringIO()

    output_df[columns].to_csv(
        buffer,
        index=False,
        header=False,
    )

    buffer.seek(0)

    with connection.cursor() as cursor:

        cursor.execute(
            """
            DELETE FROM policy_frequency_predictions
            WHERE model_name = %s;
            """,
            (model_name,),
        )

        with cursor.copy(
            """
            COPY policy_frequency_predictions (
                idpol,
                claim_nb,
                exposure,
                predicted_claim_frequency,
                predicted_claim_count,
                model_name
            )
            FROM STDIN
            WITH (FORMAT CSV);
            """
        ) as copy:

            while data := buffer.read(1024 * 1024):
                copy.write(data)    

if __name__ == "__main__":
    password = getpass("PostgreSQL password: ")

    # 1. Load model data from PostgreSQL
    with psycopg.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=password,
        host=DB_HOST,
        port=DB_PORT,
    ) as connection:
        df = load_model_data(connection)

    # 2. Prepare model data
    X, y, sample_weight = prepare_model_data(df)

    portfolio_frequency = (
        df["claim_nb"].sum()
        / df["exposure"].sum()
    )

    weighted_frequency = (
        (y * sample_weight).sum()
        / sample_weight.sum()
    )

    # 3. Train checkpoint Poisson model
    checkpoint_model = build_checkpoint_model()

    checkpoint_model.fit(
        X,
        y,
        model__sample_weight=sample_weight,
    )

    # 4. Create predictions
    predictions = create_predictions(
        df,
        X,
        checkpoint_model,
    )

    predicted_total_claims = (
        predictions["predicted_claim_count"].sum()
    )

    actual_total_claims = (
        predictions["claim_nb"].sum()
    )

    predicted_portfolio_frequency = (
        predicted_total_claims
        / predictions["exposure"].sum()
    )

    # 5. Save predictions to PostgreSQL
    with psycopg.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=password,
        host=DB_HOST,
        port=DB_PORT,
    ) as connection:
        save_predictions(
            connection,
            predictions,
            MODEL_NAME,
        )

    # 6. Console summary
    print()
    print("X shape:", X.shape)
    print("Mean annual claim frequency:", y.mean())
    print("Total exposure:", sample_weight.sum())
    print("Total claims:", actual_total_claims)
    print("Portfolio claim frequency:", portfolio_frequency)
    print("Exposure-weighted frequency:", weighted_frequency)
    print("Poisson model fitted successfully.")

    print()
    print(predictions.head())

    print()
    print("Predicted total claims:", predicted_total_claims)
    print("Actual total claims:", actual_total_claims)
    print(
        "Predicted portfolio frequency:",
        predicted_portfolio_frequency,
    )

    print()
    print(
        f"Predictions saved to PostgreSQL "
        f"for model: {MODEL_NAME}"
    )