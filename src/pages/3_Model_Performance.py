import altair as alt
import pandas as pd
import streamlit as st


# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Model Performance",
    page_icon="🧠",
    layout="wide",
)


# ============================================================
# 2. MODEL INFORMATION
# ============================================================

MODEL_NAME = "Tuned XGBoost"

CALIBRATION_METHOD = "Platt scaling"

DECISION_THRESHOLD = 0.07

SELECTION_STATUS = "Locked before test evaluation"


# ============================================================
# 3. VALIDATION METRICS
# ============================================================

PR_AUC = 0.185
ROC_AUC = 0.773
PRECISION = 0.146
RECALL = 0.539
F1 = 0.230
F2 = 0.351


# ============================================================
# 4. PAGE CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ======================================================
       MAIN PAGE
       ====================================================== */

    .block-container {
        max-width: 1450px;
        padding-top: 2rem;
        padding-bottom: 5rem;
    }


    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(
                circle at 90% 0%,
                rgba(14, 165, 233, 0.07),
                transparent 25%
            ),
            radial-gradient(
                circle at 10% 30%,
                rgba(239, 68, 68, 0.035),
                transparent 22%
            ),
            #0e1117;
    }


    /* ======================================================
       SIDEBAR
       ====================================================== */

    [data-testid="stSidebar"] {
        background: #151923;
        border-right: 1px solid rgba(255,255,255,0.06);
    }


    /* ======================================================
       HEADINGS
       ====================================================== */

    h1 {
        font-size: 2.8rem !important;
        font-weight: 800 !important;
        letter-spacing: -1.3px !important;
    }


    h2 {
        font-weight: 750 !important;
        margin-top: 0.4rem !important;
    }


    h3 {
        font-weight: 700 !important;
    }


    /* ======================================================
       METRIC CARDS
       ====================================================== */

    [data-testid="stMetric"] {

        background:
            linear-gradient(
                145deg,
                rgba(24, 34, 52, 0.98),
                rgba(17, 24, 39, 0.98)
            );

        border:
            1px solid rgba(255,255,255,0.08);

        border-radius: 18px;

        padding: 20px 22px;

        min-height: 120px;

        box-shadow:
            0px 8px 28px rgba(0,0,0,0.15);
    }


    [data-testid="stMetric"]:hover {

        border-color:
            rgba(56, 189, 248, 0.22);

        box-shadow:
            0px 10px 35px rgba(0,0,0,0.20);
    }


    [data-testid="stMetricLabel"] {

        color: #91a4bb !important;

        font-weight: 650 !important;

        font-size: 0.92rem !important;
    }


    [data-testid="stMetricValue"] {

        font-size: 1.8rem !important;

        font-weight: 800 !important;

        white-space: normal !important;

        overflow-wrap: anywhere !important;

        word-break: normal !important;

        line-height: 1.15 !important;
    }


    /* ======================================================
       BORDERED CONTAINERS
       ====================================================== */

    [data-testid="stVerticalBlockBorderWrapper"] {

        background:
            linear-gradient(
                145deg,
                rgba(24,34,52,0.58),
                rgba(17,24,39,0.58)
            );

        border-radius: 18px !important;

        border-color:
            rgba(255,255,255,0.08) !important;
    }


    /* ======================================================
       TABS
       ====================================================== */

    [data-testid="stTabs"] [data-baseweb="tab-list"] {

        gap: 12px;

        background:
            rgba(15, 23, 42, 0.72);

        padding: 10px;

        border-radius: 18px;

        border:
            1px solid rgba(255,255,255,0.08);

        margin-top: 8px;

        margin-bottom: 25px;
    }


    [data-testid="stTabs"]
    button[data-baseweb="tab"] {

        height: 58px;

        padding-left: 22px;

        padding-right: 22px;

        border-radius: 12px;

        background:
            rgba(30, 41, 59, 0.65);

        border:
            1px solid rgba(255,255,255,0.05);

        font-weight: 700;

        color: #aebed1;

        flex: 1;
    }


    [data-testid="stTabs"]
    button[data-baseweb="tab"]:hover {

        background:
            rgba(56, 189, 248, 0.10);

        color: white;
    }


    [data-testid="stTabs"]
    button[data-baseweb="tab"][aria-selected="true"] {

        background:
            linear-gradient(
                135deg,
                rgba(239,68,68,0.18),
                rgba(56,189,248,0.10)
            );

        border:
            1px solid rgba(239,68,68,0.45);

        color: white;
    }


    [data-testid="stTabs"]
    [data-baseweb="tab-highlight"] {

        display: none;
    }


    /* ======================================================
       DATA TABLE
       ====================================================== */

    [data-testid="stDataFrame"] {

        border-radius: 14px;

        overflow: hidden;
    }


    /* ======================================================
       DIVIDERS
       ====================================================== */

    hr {
        border-color:
            rgba(255,255,255,0.07) !important;
    }


    footer {
        visibility: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 5. CHART STYLE FUNCTION
# ============================================================

def chart_style(chart):

    return (
        chart
        .configure_view(
            strokeOpacity=0
        )
        .configure_axis(
            gridColor="#263244",
            gridOpacity=0.45,
            domain=False,
            labelColor="#a9b5c5",
            titleColor="#cbd5e1",
            tickColor="#475569",
            labelFontSize=12,
            titleFontSize=12,
        )
        .configure_legend(
            labelColor="#cbd5e1",
            titleColor="#cbd5e1",
        )
    )


# ============================================================
# 6. HERO SECTION
# ============================================================

with st.container(
    border=True
):

    st.caption(
        "UK FOOD HYGIENE ML  •  PRODUCTION MODEL"
    )

    st.title(
        "🧠 Model Performance"
    )

    st.write(
        """
        Technical evaluation of the machine learning model selected
        for production. This page shows the final model configuration,
        validation performance, classification trade-offs and the
        reasoning behind the production decision.
        """
    )

    hero1, hero2, hero3, hero4 = st.columns(
        4
    )

    hero1.caption(
        "🤖 XGBoost classifier"
    )

    hero2.caption(
        "🎯 Imbalanced classification"
    )

    hero3.caption(
        "📐 Probability calibration"
    )

    hero4.caption(
        "🚀 Production deployment"
    )


st.write("")


# ============================================================
# 7. PRODUCTION MODEL
# ============================================================

st.header(
    "Production model"
)

st.caption(
    "Configuration of the model currently used by the prediction API."
)


# First row
model_col, calibration_col = st.columns(
    2
)


with model_col:

    st.metric(
        label="Model",
        value=MODEL_NAME,
        help=(
            "The tuned XGBoost classifier selected "
            "during model comparison and tuning."
        ),
    )


with calibration_col:

    st.metric(
        label="Probability calibration",
        value=CALIBRATION_METHOD,
        help=(
            "Platt scaling transforms the raw model score "
            "into a calibrated probability."
        ),
    )


# Second row
threshold_col, status_col = st.columns(
    2
)


with threshold_col:

    st.metric(
        label="Decision threshold",
        value=f"{DECISION_THRESHOLD:.2f}",
        help=(
            "Predictions at or above this decision threshold "
            "are classified as higher risk."
        ),
    )


with status_col:

    st.metric(
        label="Model selection status",
        value=SELECTION_STATUS,
        help=(
            "Model selection and threshold decisions were "
            "locked before final test evaluation."
        ),
    )


st.write("")


# ============================================================
# 8. VALIDATION PERFORMANCE
# ============================================================

st.header(
    "Validation performance"
)

st.caption(
    "Performance measured on validation data during model development."
)


# ============================================================
# ROW 1
# ============================================================

v1, v2, v3 = st.columns(
    3
)


v1.metric(
    label="PR-AUC",
    value=f"{PR_AUC:.3f}",
    help=(
        "Precision Recall Area Under the Curve. "
        "Especially useful when the positive class is rare."
    ),
)


v2.metric(
    label="ROC-AUC",
    value=f"{ROC_AUC:.3f}",
    help=(
        "Measures how well the model separates "
        "low hygiene and non-low hygiene businesses."
    ),
)


v3.metric(
    label="Precision",
    value=f"{PRECISION:.3f}",
    help=(
        "Of businesses predicted as higher risk, "
        "the proportion that were actually low rated."
    ),
)


# ============================================================
# ROW 2
# ============================================================

v4, v5, v6 = st.columns(
    3
)


v4.metric(
    label="Recall",
    value=f"{RECALL:.3f}",
    help=(
        "Of actual low rated businesses, "
        "the proportion identified by the model."
    ),
)


v5.metric(
    label="F1",
    value=f"{F1:.3f}",
    help=(
        "Harmonic mean of precision and recall."
    ),
)


v6.metric(
    label="F2",
    value=f"{F2:.3f}",
    help=(
        "Similar to F1, but places greater emphasis on recall."
    ),
)


st.write("")


# ============================================================
# 9. NAVIGATION
# ============================================================

st.header(
    "Explore model evaluation"
)

st.caption(
    "Use the sections below to inspect model metrics, "
    "classification trade-offs and production decisions."
)


(
    metrics_tab,
    tradeoff_tab,
    model_tab,
) = st.tabs(
    [
        "📊 Performance Metrics",
        "⚖️ Precision vs Recall",
        "🚀 Production Decision",
    ]
)


# ============================================================
# TAB 1
# PERFORMANCE METRICS
# ============================================================

with metrics_tab:

    st.header(
        "Metric comparison"
    )

    st.caption(
        "The metrics measure different aspects of classification performance."
    )


    metric_df = pd.DataFrame(
        {
            "Metric": [
                "PR-AUC",
                "ROC-AUC",
                "Precision",
                "Recall",
                "F1",
                "F2",
            ],

            "Score": [
                PR_AUC,
                ROC_AUC,
                PRECISION,
                RECALL,
                F1,
                F2,
            ],
        }
    )


    # ========================================================
    # MAIN METRIC CHART
    # ========================================================

    with st.container(
        border=True
    ):

        st.subheader(
            "Validation metric comparison"
        )


        metric_chart = (
            alt.Chart(
                metric_df
            )
            .mark_bar(
                cornerRadiusTopLeft=8,
                cornerRadiusTopRight=8,
            )
            .encode(

                x=alt.X(
                    "Metric:N",
                    title=None,
                    sort=[
                        "PR-AUC",
                        "ROC-AUC",
                        "Precision",
                        "Recall",
                        "F1",
                        "F2",
                    ],
                    axis=alt.Axis(
                        labelAngle=0
                    ),
                ),

                y=alt.Y(
                    "Score:Q",
                    title="Score",
                    scale=alt.Scale(
                        domain=[
                            0,
                            1
                        ]
                    ),
                ),

                color=alt.Color(
                    "Score:Q",
                    scale=alt.Scale(
                        scheme="blues"
                    ),
                    legend=None,
                ),

                tooltip=[
                    alt.Tooltip(
                        "Metric:N",
                        title="Metric"
                    ),

                    alt.Tooltip(
                        "Score:Q",
                        title="Score",
                        format=".3f"
                    ),
                ],
            )
            .properties(
                height=430
            )
        )


        metric_labels = (
            alt.Chart(
                metric_df
            )
            .mark_text(
                dy=-12,
                fontSize=14,
                color="#d1d5db",
                fontWeight="bold",
            )
            .encode(

                x=alt.X(
                    "Metric:N",
                    sort=[
                        "PR-AUC",
                        "ROC-AUC",
                        "Precision",
                        "Recall",
                        "F1",
                        "F2",
                    ],
                ),

                y="Score:Q",

                text=alt.Text(
                    "Score:Q",
                    format=".3f"
                ),
            )
        )


        st.altair_chart(
            chart_style(
                metric_chart
                +
                metric_labels
            ),
            use_container_width=True,
        )


    st.write("")


    # ========================================================
    # METRIC TABLE
    # ========================================================

    with st.container(
        border=True
    ):

        st.subheader(
            "What each metric tells us"
        )


        metric_explanations = pd.DataFrame(
            {
                "Metric": [
                    "PR-AUC",
                    "ROC-AUC",
                    "Precision",
                    "Recall",
                    "F1",
                    "F2",
                ],

                "Score": [
                    PR_AUC,
                    ROC_AUC,
                    PRECISION,
                    RECALL,
                    F1,
                    F2,
                ],

                "Meaning": [
                    (
                        "Overall precision and recall performance "
                        "across decision thresholds."
                    ),

                    (
                        "Ability to rank low hygiene businesses "
                        "above lower risk businesses."
                    ),

                    (
                        "How often a positive prediction "
                        "is actually correct."
                    ),

                    (
                        "How many actual low hygiene businesses "
                        "the model successfully finds."
                    ),

                    (
                        "Balance between precision and recall."
                    ),

                    (
                        "Balance that gives more importance "
                        "to recall than precision."
                    ),
                ],
            }
        )


        st.dataframe(
            metric_explanations,
            use_container_width=True,
            hide_index=True,
            column_config={

                "Score":
                    st.column_config.NumberColumn(
                        format="%.3f"
                    ),
            },
        )


# ============================================================
# TAB 2
# PRECISION VS RECALL
# ============================================================

with tradeoff_tab:

    st.header(
        "Precision and recall trade-off"
    )


    st.caption(
        "The project places greater importance on detecting businesses "
        "that may receive a low hygiene rating, while accepting more "
        "false positive predictions."
    )


    # ========================================================
    # PRECISION RECALL DATA
    # ========================================================

    tradeoff_df = pd.DataFrame(
        {
            "Metric": [
                "Precision",
                "Recall",
            ],

            "Score": [
                PRECISION,
                RECALL,
            ],
        }
    )


    trade_left, trade_right = st.columns(
        [1.4, 1]
    )


    # ========================================================
    # PRECISION VS RECALL CHART
    # ========================================================

    with trade_left:

        with st.container(
            border=True
        ):

            st.subheader(
                "Precision versus recall"
            )


            tradeoff_chart = (
                alt.Chart(
                    tradeoff_df
                )
                .mark_bar(
                    cornerRadiusTopLeft=10,
                    cornerRadiusTopRight=10,
                )
                .encode(

                    x=alt.X(
                        "Metric:N",
                        title=None,
                        axis=alt.Axis(
                            labelAngle=0
                        ),
                    ),

                    y=alt.Y(
                        "Score:Q",
                        title="Score",
                        scale=alt.Scale(
                            domain=[
                                0,
                                0.65
                            ]
                        ),
                    ),

                    color=alt.Color(
                        "Metric:N",
                        scale=alt.Scale(
                            domain=[
                                "Precision",
                                "Recall",
                            ],
                            range=[
                                "#38bdf8",
                                "#f87171",
                            ],
                        ),
                        legend=None,
                    ),

                    tooltip=[
                        alt.Tooltip(
                            "Metric:N"
                        ),

                        alt.Tooltip(
                            "Score:Q",
                            format=".3f"
                        ),
                    ],
                )
                .properties(
                    height=390
                )
            )


            tradeoff_labels = (
                alt.Chart(
                    tradeoff_df
                )
                .mark_text(
                    dy=-15,
                    fontSize=15,
                    fontWeight="bold",
                    color="#d1d5db",
                )
                .encode(

                    x="Metric:N",

                    y="Score:Q",

                    text=alt.Text(
                        "Score:Q",
                        format=".3f"
                    ),
                )
            )


            st.altair_chart(
                chart_style(
                    tradeoff_chart
                    +
                    tradeoff_labels
                ),
                use_container_width=True,
            )


    # ========================================================
    # INTERPRETATION
    # ========================================================

    with trade_right:

        with st.container(
            border=True
        ):

            st.subheader(
                "How to interpret this"
            )

            st.write(
                """
                **Recall = 0.539**

                The model identifies about 53.9% of the actual
                low hygiene cases in the validation data.

                **Precision = 0.146**

                About 14.6% of businesses flagged by the model
                were actually low rated.

                **Why accept this trade-off?**

                Low hygiene ratings are uncommon in the dataset.
                A higher recall approach allows the model to identify
                more potentially risky businesses for further attention,
                rather than missing most positive cases.
                """
            )


    st.write("")


    # ========================================================
    # CLASS IMBALANCE NOTE
    # ========================================================

    with st.container(
        border=True
    ):

        st.subheader(
            "Why accuracy is not the main metric"
        )

        st.write(
            """
            The low hygiene class represents only a small proportion
            of the full dataset.

            A model could therefore obtain very high accuracy simply
            by predicting that almost every business is not low hygiene.

            For this reason, the project focuses more heavily on
            **PR-AUC, recall, precision, F1 and F2** when evaluating
            useful classification performance.
            """
        )


# ============================================================
# TAB 3
# PRODUCTION DECISION
# ============================================================

with model_tab:

    st.header(
        "Production model decision"
    )


    st.caption(
        "Summary of how the final model is used in the deployed system."
    )


    # ========================================================
    # MODEL PIPELINE
    # ========================================================

    with st.container(
        border=True
    ):

        st.subheader(
            "Production prediction pipeline"
        )

        st.write(
            """
            **1. Business information enters the API**

            Latitude, longitude, deprivation information,
            business type, local authority and geographic codes
            are passed to the deployed prediction service.

            **2. XGBoost generates the raw risk score**

            The tuned XGBoost model processes the same feature
            structure used during model training.

            **3. Platt scaling calibrates the probability**

            The raw model score is transformed into a calibrated
            probability.

            **4. Decision threshold is applied**

            A calibrated prediction is converted into the final
            classification using the production decision logic.

            **5. FastAPI returns the prediction**

            The API returns the raw probability, calibrated probability,
            binary prediction and risk label.

            **6. Streamlit displays the result**

            The front end presents the prediction in a format that
            can be understood without needing to inspect the raw model.
            """
        )


    st.write("")


    # ========================================================
    # PRODUCTION CONFIGURATION
    # ========================================================

    with st.container(
        border=True
    ):

        st.subheader(
            "Production configuration"
        )


        config_df = pd.DataFrame(
            {
                "Component": [
                    "Classifier",
                    "Calibration",
                    "Decision threshold",
                    "Serving layer",
                    "Containerisation",
                    "Cloud deployment",
                    "Model tracking",
                ],

                "Production configuration": [
                    MODEL_NAME,
                    CALIBRATION_METHOD,
                    f"{DECISION_THRESHOLD:.2f}",
                    "FastAPI",
                    "Docker",
                    "AWS ECS",
                    "MLflow",
                ],
            }
        )


        st.dataframe(
            config_df,
            use_container_width=True,
            hide_index=True,
        )


    st.write("")


    # ========================================================
    # MODEL GOVERNANCE
    # ========================================================

    with st.container(
        border=True
    ):

        st.subheader(
            "Model selection discipline"
        )

        st.success(
            "Model and threshold decisions were locked before "
            "final test evaluation."
        )

        st.write(
            """
            Keeping model selection separate from final test evaluation
            helps reduce the risk of repeatedly changing the model after
            seeing the test results.

            The validation set is used for model development and
            decision making, while the final test set is intended to
            provide an independent assessment of generalisation.
            """
        )


# ============================================================
# 10. FOOTER
# ============================================================

st.divider()


footer_left, footer_right = st.columns(
    2
)


with footer_left:

    st.caption(
        "UK Food Hygiene ML  •  Model evaluation dashboard"
    )


with footer_right:

    st.caption(
        "Production model: Tuned XGBoost  •  Calibration: Platt scaling"
    )