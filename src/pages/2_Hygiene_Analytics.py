from io import StringIO
from pathlib import Path

import altair as alt
import pandas as pd
import requests
import streamlit as st


# ============================================================
# 1. PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Food Hygiene Intelligence",
    page_icon="📊",
    layout="wide",
)


# ============================================================
# 2. DATA LOCATION
#
# Works locally and on Streamlit Cloud.
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "app"
    / "fsa_analytics.csv.gz"
)


# ONS Local Authority District to Region lookup
ONS_REGION_CSV = (
    "https://hub.arcgis.com/api/v3/datasets/"
    "ecc34decb1e5465b96bf055b4524edbf_0/"
    "downloads/data"
    "?format=csv"
    "&spatialRefId=4326"
    "&where=1%3D1"
)


# ============================================================
# 3. DASHBOARD CSS
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        max-width: 1500px;
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
            #0e1117;
    }

    [data-testid="stSidebar"] {
        background: #151923;
        border-right: 1px solid rgba(255,255,255,0.06);
    }

    h1 {
        font-size: 2.8rem !important;
        font-weight: 800 !important;
        letter-spacing: -1.4px !important;
    }

    h2 {
        margin-top: 0.5rem !important;
        font-weight: 750 !important;
    }

    h3 {
        font-weight: 700 !important;
    }

    [data-testid="stMetric"] {
        background:
            linear-gradient(
                145deg,
                rgba(24, 34, 52, 0.96),
                rgba(17, 24, 39, 0.96)
            );

        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px;
        padding: 20px 22px;
        min-height: 125px;

        box-shadow:
            0px 8px 28px rgba(0,0,0,0.15);
    }

    [data-testid="stMetricLabel"] {
        color: #91a4bb !important;
        font-weight: 650 !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 800 !important;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        background:
            linear-gradient(
                145deg,
                rgba(24,34,52,0.55),
                rgba(17,24,39,0.55)
            );

        border-radius: 18px !important;
        border-color: rgba(255,255,255,0.08) !important;
    }

    /* ======================================================
       BIG DASHBOARD NAVIGATION
       ====================================================== */

    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        gap: 12px;
        background: rgba(15, 23, 42, 0.72);
        padding: 10px;
        border-radius: 18px;

        border:
            1px solid rgba(255,255,255,0.08);

        margin-top: 8px;
        margin-bottom: 28px;

        box-shadow:
            0px 10px 30px rgba(0,0,0,0.13);
    }

    [data-testid="stTabs"]
    button[data-baseweb="tab"] {
        height: 66px;

        padding-left: 24px;
        padding-right: 24px;

        border-radius: 13px;

        background:
            rgba(30, 41, 59, 0.68);

        border:
            1px solid rgba(255,255,255,0.06);

        font-size: 0.96rem;
        font-weight: 700;
        color: #aebed1;

        transition: all 0.2s ease;
        flex: 1;
    }

    [data-testid="stTabs"]
    button[data-baseweb="tab"]:hover {
        background:
            rgba(56, 189, 248, 0.10);

        border-color:
            rgba(56, 189, 248, 0.35);

        color: white;
        transform: translateY(-1px);
    }

    [data-testid="stTabs"]
    button[data-baseweb="tab"][aria-selected="true"] {
        background:
            linear-gradient(
                135deg,
                rgba(239, 68, 68, 0.20),
                rgba(56, 189, 248, 0.12)
            );

        border:
            1px solid rgba(239, 68, 68, 0.50);

        color: white;

        box-shadow:
            0px 5px 18px rgba(239, 68, 68, 0.10);
    }

    [data-testid="stTabs"]
    [data-baseweb="tab-highlight"] {
        display: none;
    }

    [data-testid="stExpander"] {
        border-radius: 14px;
        border-color: rgba(255,255,255,0.08);
    }

    [data-testid="stDataFrame"] {
        border-radius: 14px;
        overflow: hidden;
    }

    hr {
        border-color: rgba(255,255,255,0.07) !important;
    }

    footer {
        visibility: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 4. HELPERS
# ============================================================

def normalise_authority(value):

    if pd.isna(value):
        return None

    value = str(value).lower().strip()

    replacements = [
        " city council",
        " borough council",
        " metropolitan borough council",
        " district council",
        " county council",
        " council",
    ]

    for text in replacements:
        value = value.replace(text, "")

    return value.strip()


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
# 5. LOAD FSA ANALYTICS DATA
# ============================================================

@st.cache_data
def load_fsa_data():

    if not DATA_PATH.exists():
        return None

    df = pd.read_csv(
        DATA_PATH,
        compression="gzip",
        low_memory=False,
    )

    required_columns = [
        "BusinessType",
        "LocalAuthorityName",
        "RatingValue",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Analytics dataset is missing columns: "
            f"{missing_columns}"
        )

    # Convert hygiene rating to number
    df["rating_numeric"] = pd.to_numeric(
        df["RatingValue"],
        errors="coerce",
    )

    # Keep valid 0 to 5 FHRS ratings
    df = df[
        df["rating_numeric"].isin(
            [0, 1, 2, 3, 4, 5]
        )
    ].copy()

    # Project classification target
    # 0, 1, 2 = low hygiene
    # 3, 4, 5 = not low
    df["low_hygiene"] = (
        df["rating_numeric"] <= 2
    ).astype(int)

    # Normalised authority name for ONS matching
    df["authority_key"] = (
        df["LocalAuthorityName"]
        .apply(normalise_authority)
    )

    return df


# ============================================================
# 6. LOAD ONS REGION LOOKUP
# ============================================================

@st.cache_data(ttl=86400)
def load_region_lookup():

    try:

        response = requests.get(
            ONS_REGION_CSV,
            timeout=20,
        )

        response.raise_for_status()

        lookup = pd.read_csv(
            StringIO(response.text)
        )

        if (
            "LAD23NM" not in lookup.columns
            or
            "RGN23NM" not in lookup.columns
        ):
            return None

        lookup = (
            lookup[
                [
                    "LAD23NM",
                    "RGN23NM",
                ]
            ]
            .drop_duplicates()
            .copy()
        )

        lookup["authority_key"] = (
            lookup["LAD23NM"]
            .apply(normalise_authority)
        )

        return lookup

    except Exception:
        return None


# ============================================================
# 7. LOAD DATA
# ============================================================

try:

    df = load_fsa_data()

except Exception as error:

    st.error(
        f"Could not load analytics dataset: {error}"
    )

    st.stop()


if df is None:

    st.error(
        f"Could not find analytics dataset: {DATA_PATH}"
    )

    st.stop()


FULL_DATA_COUNT = len(df)


# ============================================================
# 8. ADD REGION INFORMATION
# ============================================================

region_lookup = load_region_lookup()


if region_lookup is not None:

    df = df.merge(
        region_lookup[
            [
                "authority_key",
                "RGN23NM",
            ]
        ],
        on="authority_key",
        how="left",
    )

    df = df.rename(
        columns={
            "RGN23NM": "region"
        }
    )

else:

    df["region"] = None


# ============================================================
# 9. HERO SECTION
# ============================================================

with st.container(border=True):

    st.caption(
        "UK FOOD HYGIENE ML  •  ANALYTICS DASHBOARD"
    )

    st.title(
        "📊 Food Hygiene Intelligence"
    )

    st.write(
        """
        Explore food hygiene patterns across the UK, compare
        business categories, investigate local authorities
        and analyse regional differences using Food Standards
        Agency data.
        """
    )

    hero1, hero2, hero3, hero4 = st.columns(4)

    hero1.caption(
        "🏛️ Food Standards Agency"
    )

    hero2.caption(
        "⭐ FHRS ratings 0 to 5"
    )

    hero3.caption(
        "📍 Local and regional analysis"
    )

    hero4.caption(
        "🤖 Machine learning project"
    )


st.write("")


# ============================================================
# 10. DASHBOARD FILTERS
# ============================================================

with st.expander(
    "⚙️ Dashboard filters",
    expanded=False,
):

    filter_col1, filter_col2 = st.columns(
        [2, 1]
    )

    business_types = sorted(
        df["BusinessType"]
        .dropna()
        .unique()
        .tolist()
    )

    with filter_col1:

        selected_businesses = st.multiselect(
            "Business types",
            options=business_types,
            default=[],
            placeholder="All business types",
            key="analytics_business_filter_cloud",
        )

    with filter_col2:

        minimum_sample = st.slider(
            "Minimum establishments per area",
            min_value=50,
            max_value=3000,
            value=500,
            step=50,
            key="analytics_minimum_sample_cloud",
        )


# ============================================================
# 11. APPLY FILTERS
# ============================================================

filtered = df.copy()


if selected_businesses:

    filtered = filtered[
        filtered["BusinessType"].isin(
            selected_businesses
        )
    ].copy()


# ============================================================
# 12. KPIs
# ============================================================

total = len(filtered)

low_count = int(
    filtered["low_hygiene"].sum()
)


if total > 0:

    low_rate = (
        filtered["low_hygiene"].mean()
        * 100
    )

else:

    low_rate = 0


authority_count = (
    filtered["LocalAuthorityName"]
    .nunique()
)


k1, k2, k3, k4 = st.columns(4)


k1.metric(
    label="Rated establishments",
    value=f"{total:,}",
    help=(
        f"Full valid FHRS dataset contains "
        f"{FULL_DATA_COUNT:,} rated establishments."
    ),
)


k2.metric(
    label="Low rated businesses",
    value=f"{low_count:,}",
    help="Businesses with FHRS ratings 0, 1 or 2.",
)


k3.metric(
    label="Low rating rate",
    value=f"{low_rate:.1f}%",
    help=(
        "Share of rated establishments "
        "with ratings 0, 1 or 2."
    ),
)


k4.metric(
    label="Local authorities",
    value=f"{authority_count:,}",
    help=(
        "Number of local authorities "
        "in the current selection."
    ),
)


st.write("")


# ============================================================
# 13. DASHBOARD NAVIGATION
# ============================================================

st.header(
    "Explore the dashboard"
)

st.caption(
    "Select a section below to explore national patterns, "
    "regional differences, local authorities or business categories."
)


(
    overview_tab,
    region_tab,
    authority_tab,
    business_tab,
) = st.tabs(
    [
        "📈 UK Overview",
        "🗺️ Regional Analysis",
        "🏙️ City & Local Analysis",
        "🍽️ Business Categories",
    ]
)


# ============================================================
# TAB 1
# UK OVERVIEW
# ============================================================

with overview_tab:

    st.header(
        "UK hygiene rating landscape"
    )

    st.caption(
        "FHRS ratings 0, 1 and 2 are treated "
        "as low hygiene ratings in this project."
    )


    # --------------------------------------------------------
    # Rating distribution
    # --------------------------------------------------------

    rating_distribution = (
        filtered
        .groupby("rating_numeric")
        .size()
        .reindex(
            [0, 1, 2, 3, 4, 5],
            fill_value=0,
        )
        .reset_index(
            name="establishments"
        )
    )


    rating_distribution["percentage"] = (
        rating_distribution["establishments"]
        /
        rating_distribution["establishments"].sum()
        *
        100
    )


    rating_distribution["rating"] = (
        rating_distribution["rating_numeric"]
        .astype(int)
        .astype(str)
    )


    overview_left, overview_right = st.columns(
        [1.65, 1]
    )


    # --------------------------------------------------------
    # Rating distribution chart
    # --------------------------------------------------------

    with overview_left:

        with st.container(border=True):

            st.subheader(
                "Hygiene rating distribution"
            )

            st.caption(
                "Percentage is used instead of raw count "
                "so rating 5 does not visually dominate the chart."
            )


            rating_chart = (
                alt.Chart(
                    rating_distribution
                )
                .mark_bar(
                    cornerRadiusTopLeft=8,
                    cornerRadiusTopRight=8,
                )
                .encode(

                    x=alt.X(
                        "rating:N",
                        title="Food hygiene rating",
                        sort=[
                            "0",
                            "1",
                            "2",
                            "3",
                            "4",
                            "5",
                        ],
                        axis=alt.Axis(
                            labelAngle=0
                        ),
                    ),

                    y=alt.Y(
                        "percentage:Q",
                        title="Share of establishments (%)",
                    ),

                    color=alt.condition(
                        "datum.rating_numeric <= 2",
                        alt.value("#f87171"),
                        alt.value("#38bdf8"),
                    ),

                    tooltip=[
                        alt.Tooltip(
                            "rating:N",
                            title="Rating",
                        ),

                        alt.Tooltip(
                            "establishments:Q",
                            title="Businesses",
                            format=",",
                        ),

                        alt.Tooltip(
                            "percentage:Q",
                            title="Share",
                            format=".2f",
                        ),
                    ],
                )
                .properties(
                    height=390
                )
            )


            rating_labels = (
                alt.Chart(
                    rating_distribution
                )
                .mark_text(
                    dy=-12,
                    fontSize=13,
                    color="#d1d5db",
                )
                .encode(

                    x=alt.X(
                        "rating:N",
                        sort=[
                            "0",
                            "1",
                            "2",
                            "3",
                            "4",
                            "5",
                        ],
                    ),

                    y="percentage:Q",

                    text=alt.Text(
                        "percentage:Q",
                        format=".1f",
                    ),
                )
            )


            st.altair_chart(
                chart_style(
                    rating_chart
                    +
                    rating_labels
                ),
                use_container_width=True,
            )


    # --------------------------------------------------------
    # Donut chart
    # --------------------------------------------------------

    with overview_right:

        with st.container(border=True):

            st.subheader(
                "Low rating split"
            )

            st.caption(
                "Ratings 0 to 2 compared with ratings 3 to 5."
            )


            risk_split = pd.DataFrame(
                {
                    "Group": [
                        "Ratings 0 to 2",
                        "Ratings 3 to 5",
                    ],

                    "Count": [
                        low_count,
                        total - low_count,
                    ],
                }
            )


            donut = (
                alt.Chart(
                    risk_split
                )
                .mark_arc(
                    innerRadius=90,
                    outerRadius=145,
                    cornerRadius=7,
                )
                .encode(

                    theta=alt.Theta(
                        "Count:Q"
                    ),

                    color=alt.Color(
                        "Group:N",
                        scale=alt.Scale(
                            domain=[
                                "Ratings 0 to 2",
                                "Ratings 3 to 5",
                            ],
                            range=[
                                "#f87171",
                                "#38bdf8",
                            ],
                        ),
                        legend=alt.Legend(
                            title=None,
                            orient="bottom",
                        ),
                    ),

                    tooltip=[
                        alt.Tooltip(
                            "Group:N"
                        ),

                        alt.Tooltip(
                            "Count:Q",
                            format=",",
                        ),
                    ],
                )
                .properties(
                    height=390
                )
            )


            st.altair_chart(
                chart_style(donut),
                use_container_width=True,
            )


    st.write("")


    # --------------------------------------------------------
    # Low rating count by authority
    # --------------------------------------------------------

    with st.container(border=True):

        st.subheader(
            "Areas with the largest number of low rated businesses"
        )

        st.caption(
            f"Only authorities with at least "
            f"{minimum_sample:,} establishments are included."
        )


        authority_low_counts = (
            filtered
            .groupby(
                "LocalAuthorityName"
            )
            .agg(
                establishments=(
                    "low_hygiene",
                    "size",
                ),

                low_rated=(
                    "low_hygiene",
                    "sum",
                ),
            )
            .reset_index()
        )


        authority_low_counts = (
            authority_low_counts[
                authority_low_counts[
                    "establishments"
                ]
                >= minimum_sample
            ]
            .sort_values(
                "low_rated",
                ascending=False,
            )
            .head(15)
        )


        low_count_chart = (
            alt.Chart(
                authority_low_counts
            )
            .mark_bar(
                cornerRadiusEnd=7,
                color="#f87171",
            )
            .encode(

                y=alt.Y(
                    "LocalAuthorityName:N",
                    sort="-x",
                    title=None,
                ),

                x=alt.X(
                    "low_rated:Q",
                    title="Low rated establishments",
                ),

                tooltip=[
                    alt.Tooltip(
                        "LocalAuthorityName:N",
                        title="Authority",
                    ),

                    alt.Tooltip(
                        "low_rated:Q",
                        title="Low rated",
                        format=",",
                    ),

                    alt.Tooltip(
                        "establishments:Q",
                        title="Total",
                        format=",",
                    ),
                ],
            )
            .properties(
                height=500
            )
        )


        st.altair_chart(
            chart_style(
                low_count_chart
            ),
            use_container_width=True,
        )


# ============================================================
# TAB 2
# REGIONAL ANALYSIS
# ============================================================

with region_tab:

    st.header(
        "Regional food hygiene intelligence"
    )

    st.caption(
        "English local authorities are matched "
        "to their corresponding ONS region."
    )


    regional_df = filtered.dropna(
        subset=["region"]
    ).copy()


    if regional_df.empty:

        st.warning(
            "Region matching is currently unavailable. "
            "City and local authority analytics still work."
        )

    else:

        match_rate = (
            len(regional_df)
            /
            len(filtered)
            *
            100
        )


        st.info(
            f"{match_rate:.1f}% of current establishments "
            "matched to an English region."
        )


        region_stats = (
            regional_df
            .groupby("region")
            .agg(
                establishments=(
                    "low_hygiene",
                    "size",
                ),

                low_rated=(
                    "low_hygiene",
                    "sum",
                ),

                low_rating_rate=(
                    "low_hygiene",
                    "mean",
                ),
            )
            .reset_index()
        )


        region_stats["low_rating_rate_pct"] = (
            region_stats["low_rating_rate"]
            * 100
        )


        region_left, region_right = st.columns(2)


        # ----------------------------------------------------
        # Region risk rate
        # ----------------------------------------------------

        with region_left:

            with st.container(border=True):

                st.subheader(
                    "Low rating rate by region"
                )


                region_risk_chart = (
                    alt.Chart(
                        region_stats
                    )
                    .mark_bar(
                        cornerRadiusEnd=7,
                        color="#38bdf8",
                    )
                    .encode(

                        y=alt.Y(
                            "region:N",
                            sort="-x",
                            title=None,
                        ),

                        x=alt.X(
                            "low_rating_rate_pct:Q",
                            title="Low rating rate (%)",
                        ),

                        tooltip=[
                            alt.Tooltip(
                                "region:N",
                                title="Region",
                            ),

                            alt.Tooltip(
                                "low_rating_rate_pct:Q",
                                title="Low rating %",
                                format=".2f",
                            ),

                            alt.Tooltip(
                                "establishments:Q",
                                title="Establishments",
                                format=",",
                            ),

                            alt.Tooltip(
                                "low_rated:Q",
                                title="Low rated",
                                format=",",
                            ),
                        ],
                    )
                    .properties(
                        height=420
                    )
                )


                st.altair_chart(
                    chart_style(
                        region_risk_chart
                    ),
                    use_container_width=True,
                )


        # ----------------------------------------------------
        # Region volume
        # ----------------------------------------------------

        with region_right:

            with st.container(border=True):

                st.subheader(
                    "Rated establishments by region"
                )


                region_volume_chart = (
                    alt.Chart(
                        region_stats
                    )
                    .mark_bar(
                        cornerRadiusEnd=7,
                        color="#818cf8",
                    )
                    .encode(

                        y=alt.Y(
                            "region:N",
                            sort="-x",
                            title=None,
                        ),

                        x=alt.X(
                            "establishments:Q",
                            title="Rated establishments",
                        ),

                        tooltip=[
                            alt.Tooltip(
                                "region:N",
                                title="Region",
                            ),

                            alt.Tooltip(
                                "establishments:Q",
                                title="Establishments",
                                format=",",
                            ),
                        ],
                    )
                    .properties(
                        height=420
                    )
                )


                st.altair_chart(
                    chart_style(
                        region_volume_chart
                    ),
                    use_container_width=True,
                )


        st.write("")


        # ----------------------------------------------------
        # Region explorer
        # ----------------------------------------------------

        with st.container(border=True):

            st.subheader(
                "Explore a region"
            )


            selected_region = st.selectbox(
                "Region",
                sorted(
                    regional_df["region"]
                    .dropna()
                    .unique()
                ),
                key="region_explorer_cloud",
            )


            selected_region_df = regional_df[
                regional_df["region"]
                ==
                selected_region
            ].copy()


            selected_region_total = len(
                selected_region_df
            )


            selected_region_low = int(
                selected_region_df[
                    "low_hygiene"
                ].sum()
            )


            selected_region_rate = (
                selected_region_df[
                    "low_hygiene"
                ].mean()
                *
                100
            )


            r1, r2, r3 = st.columns(3)


            r1.metric(
                "Rated establishments",
                f"{selected_region_total:,}",
            )


            r2.metric(
                "Low rated",
                f"{selected_region_low:,}",
            )


            r3.metric(
                "Low rating rate",
                f"{selected_region_rate:.2f}%",
            )


            region_authority_stats = (
                selected_region_df
                .groupby(
                    "LocalAuthorityName"
                )
                .agg(
                    establishments=(
                        "low_hygiene",
                        "size",
                    ),

                    low_rating_rate=(
                        "low_hygiene",
                        "mean",
                    ),
                )
                .reset_index()
            )


            region_authority_stats = (
                region_authority_stats[
                    region_authority_stats[
                        "establishments"
                    ]
                    >= 100
                ]
                .copy()
            )


            region_authority_stats[
                "low_rating_rate_pct"
            ] = (
                region_authority_stats[
                    "low_rating_rate"
                ]
                *
                100
            )


            region_authority_chart = (
                alt.Chart(
                    region_authority_stats
                )
                .mark_bar(
                    cornerRadiusEnd=6,
                    color="#22d3ee",
                )
                .encode(

                    y=alt.Y(
                        "LocalAuthorityName:N",
                        sort="-x",
                        title=None,
                    ),

                    x=alt.X(
                        "low_rating_rate_pct:Q",
                        title="Low rating rate (%)",
                    ),

                    tooltip=[
                        alt.Tooltip(
                            "LocalAuthorityName:N",
                            title="Authority",
                        ),

                        alt.Tooltip(
                            "low_rating_rate_pct:Q",
                            title="Low rating %",
                            format=".2f",
                        ),

                        alt.Tooltip(
                            "establishments:Q",
                            title="Establishments",
                            format=",",
                        ),
                    ],
                )
                .properties(
                    height=max(
                        350,
                        len(region_authority_stats)
                        * 25,
                    )
                )
            )


            st.altair_chart(
                chart_style(
                    region_authority_chart
                ),
                use_container_width=True,
            )


        st.write("")


        # ----------------------------------------------------
        # Region x business heatmap
        # ----------------------------------------------------

        with st.container(border=True):

            st.subheader(
                "Business type risk across regions"
            )


            heatmap_data = (
                regional_df
                .groupby(
                    [
                        "region",
                        "BusinessType",
                    ]
                )
                .agg(
                    establishments=(
                        "low_hygiene",
                        "size",
                    ),

                    low_rating_rate=(
                        "low_hygiene",
                        "mean",
                    ),
                )
                .reset_index()
            )


            heatmap_data = heatmap_data[
                heatmap_data[
                    "establishments"
                ]
                >= 100
            ].copy()


            heatmap_data["risk_pct"] = (
                heatmap_data[
                    "low_rating_rate"
                ]
                *
                100
            )


            heatmap = (
                alt.Chart(
                    heatmap_data
                )
                .mark_rect(
                    cornerRadius=3
                )
                .encode(

                    x=alt.X(
                        "region:N",
                        title=None,
                        axis=alt.Axis(
                            labelAngle=-35
                        ),
                    ),

                    y=alt.Y(
                        "BusinessType:N",
                        title=None,
                    ),

                    color=alt.Color(
                        "risk_pct:Q",
                        title="Low rating %",
                        scale=alt.Scale(
                            scheme="redyellowblue",
                            reverse=True,
                        ),
                    ),

                    tooltip=[
                        alt.Tooltip(
                            "region:N",
                            title="Region",
                        ),

                        alt.Tooltip(
                            "BusinessType:N",
                            title="Business type",
                        ),

                        alt.Tooltip(
                            "risk_pct:Q",
                            title="Low rating %",
                            format=".2f",
                        ),

                        alt.Tooltip(
                            "establishments:Q",
                            title="Establishments",
                            format=",",
                        ),
                    ],
                )
                .properties(
                    height=560
                )
            )


            st.altair_chart(
                chart_style(heatmap),
                use_container_width=True,
            )


# ============================================================
# TAB 3
# CITY AND LOCAL ANALYSIS
# ============================================================

with authority_tab:

    st.header(
        "Cities and local authorities"
    )

    st.caption(
        "Compare food hygiene patterns across "
        "council areas and major cities."
    )


    authority_stats = (
        filtered
        .groupby(
            "LocalAuthorityName"
        )
        .agg(
            establishments=(
                "low_hygiene",
                "size",
            ),

            low_rated=(
                "low_hygiene",
                "sum",
            ),

            low_rating_rate=(
                "low_hygiene",
                "mean",
            ),
        )
        .reset_index()
    )


    authority_stats[
        "low_rating_rate_pct"
    ] = (
        authority_stats[
            "low_rating_rate"
        ]
        *
        100
    )


    significant_authorities = (
        authority_stats[
            authority_stats[
                "establishments"
            ]
            >= minimum_sample
        ]
        .copy()
    )


    # --------------------------------------------------------
    # Bubble chart
    # --------------------------------------------------------

    with st.container(border=True):

        st.subheader(
            "Risk versus number of food businesses"
        )

        st.caption(
            "Each bubble represents a local authority. "
            "Hover over a bubble to inspect it."
        )


        bubble_chart = (
            alt.Chart(
                significant_authorities
            )
            .mark_circle(
                opacity=0.80,
                stroke="#ffffff",
                strokeWidth=0.35,
            )
            .encode(

                x=alt.X(
                    "establishments:Q",
                    title="Rated establishments",
                ),

                y=alt.Y(
                    "low_rating_rate_pct:Q",
                    title="Low rating rate (%)",
                ),

                size=alt.Size(
                    "low_rated:Q",
                    title="Low rated establishments",
                    scale=alt.Scale(
                        range=[
                            70,
                            1200,
                        ]
                    ),
                ),

                color=alt.Color(
                    "low_rating_rate_pct:Q",
                    title="Low rating %",
                    scale=alt.Scale(
                        scheme="redyellowblue",
                        reverse=True,
                    ),
                ),

                tooltip=[
                    alt.Tooltip(
                        "LocalAuthorityName:N",
                        title="Authority",
                    ),

                    alt.Tooltip(
                        "establishments:Q",
                        title="Rated",
                        format=",",
                    ),

                    alt.Tooltip(
                        "low_rated:Q",
                        title="Low rated",
                        format=",",
                    ),

                    alt.Tooltip(
                        "low_rating_rate_pct:Q",
                        title="Low rating %",
                        format=".2f",
                    ),
                ],
            )
            .properties(
                height=520
            )
            .interactive()
        )


        st.altair_chart(
            chart_style(
                bubble_chart
            ),
            use_container_width=True,
        )


    st.write("")


    authority_left, authority_right = st.columns(2)


    # --------------------------------------------------------
    # Highest rates
    # --------------------------------------------------------

    with authority_left:

        with st.container(border=True):

            st.subheader(
                "Highest low rating rates"
            )


            highest_rate = (
                significant_authorities
                .sort_values(
                    "low_rating_rate_pct",
                    ascending=False,
                )
                .head(15)
            )


            highest_rate_chart = (
                alt.Chart(
                    highest_rate
                )
                .mark_bar(
                    cornerRadiusEnd=7,
                    color="#f87171",
                )
                .encode(

                    y=alt.Y(
                        "LocalAuthorityName:N",
                        sort="-x",
                        title=None,
                    ),

                    x=alt.X(
                        "low_rating_rate_pct:Q",
                        title="Low rating rate (%)",
                    ),

                    tooltip=[
                        alt.Tooltip(
                            "LocalAuthorityName:N",
                            title="Authority",
                        ),

                        alt.Tooltip(
                            "low_rating_rate_pct:Q",
                            title="Low rating %",
                            format=".2f",
                        ),

                        alt.Tooltip(
                            "establishments:Q",
                            title="Establishments",
                            format=",",
                        ),
                    ],
                )
                .properties(
                    height=500
                )
            )


            st.altair_chart(
                chart_style(
                    highest_rate_chart
                ),
                use_container_width=True,
            )


    # --------------------------------------------------------
    # Largest areas
    # --------------------------------------------------------

    with authority_right:

        with st.container(border=True):

            st.subheader(
                "Largest food business areas"
            )


            largest_authorities = (
                authority_stats
                .sort_values(
                    "establishments",
                    ascending=False,
                )
                .head(15)
            )


            largest_chart = (
                alt.Chart(
                    largest_authorities
                )
                .mark_bar(
                    cornerRadiusEnd=7,
                    color="#818cf8",
                )
                .encode(

                    y=alt.Y(
                        "LocalAuthorityName:N",
                        sort="-x",
                        title=None,
                    ),

                    x=alt.X(
                        "establishments:Q",
                        title="Rated establishments",
                    ),

                    tooltip=[
                        alt.Tooltip(
                            "LocalAuthorityName:N",
                            title="Authority",
                        ),

                        alt.Tooltip(
                            "establishments:Q",
                            title="Establishments",
                            format=",",
                        ),
                    ],
                )
                .properties(
                    height=500
                )
            )


            st.altair_chart(
                chart_style(
                    largest_chart
                ),
                use_container_width=True,
            )


    st.write("")


    # --------------------------------------------------------
    # Authority explorer
    # --------------------------------------------------------

    with st.container(border=True):

        st.subheader(
            "Explore a city or local authority"
        )


        selected_authority = st.selectbox(
            "Local authority",
            sorted(
                filtered[
                    "LocalAuthorityName"
                ]
                .dropna()
                .unique()
            ),
            key="authority_explorer_cloud",
        )


        authority_df = filtered[
            filtered[
                "LocalAuthorityName"
            ]
            ==
            selected_authority
        ].copy()


        authority_total = len(
            authority_df
        )


        authority_low = int(
            authority_df[
                "low_hygiene"
            ]
            .sum()
        )


        authority_rate = (
            authority_df[
                "low_hygiene"
            ]
            .mean()
            *
            100
        )


        a1, a2, a3 = st.columns(3)


        a1.metric(
            "Rated establishments",
            f"{authority_total:,}",
        )


        a2.metric(
            "Low rated",
            f"{authority_low:,}",
        )


        a3.metric(
            "Low rating rate",
            f"{authority_rate:.2f}%",
        )


        authority_rating_distribution = (
            authority_df
            .groupby(
                "rating_numeric"
            )
            .size()
            .reindex(
                [0, 1, 2, 3, 4, 5],
                fill_value=0,
            )
            .reset_index(
                name="count"
            )
        )


        authority_rating_chart = (
            alt.Chart(
                authority_rating_distribution
            )
            .mark_bar(
                cornerRadiusTopLeft=7,
                cornerRadiusTopRight=7,
            )
            .encode(

                x=alt.X(
                    "rating_numeric:O",
                    title="Hygiene rating",
                    axis=alt.Axis(
                        labelAngle=0
                    ),
                ),

                y=alt.Y(
                    "count:Q",
                    title="Businesses",
                ),

                color=alt.condition(
                    "datum.rating_numeric <= 2",
                    alt.value("#f87171"),
                    alt.value("#38bdf8"),
                ),

                tooltip=[
                    alt.Tooltip(
                        "rating_numeric:O",
                        title="Rating",
                    ),

                    alt.Tooltip(
                        "count:Q",
                        title="Businesses",
                        format=",",
                    ),
                ],
            )
            .properties(
                height=370
            )
        )


        st.altair_chart(
            chart_style(
                authority_rating_chart
            ),
            use_container_width=True,
        )


# ============================================================
# TAB 4
# BUSINESS CATEGORIES
# ============================================================

with business_tab:

    st.header(
        "Food business category intelligence"
    )

    st.caption(
        "Compare low hygiene rates and establishment "
        "volume across different food business categories."
    )


    business_stats = (
        filtered
        .groupby(
            "BusinessType"
        )
        .agg(
            establishments=(
                "low_hygiene",
                "size",
            ),

            low_rated=(
                "low_hygiene",
                "sum",
            ),

            low_rating_rate=(
                "low_hygiene",
                "mean",
            ),
        )
        .reset_index()
    )


    business_stats[
        "low_rating_rate_pct"
    ] = (
        business_stats[
            "low_rating_rate"
        ]
        *
        100
    )


    business_left, business_right = st.columns(2)


    # --------------------------------------------------------
    # Business type risk
    # --------------------------------------------------------

    with business_left:

        with st.container(border=True):

            st.subheader(
                "Low rating rate by business type"
            )


            business_risk = (
                business_stats[
                    business_stats[
                        "establishments"
                    ]
                    >= 100
                ]
                .sort_values(
                    "low_rating_rate_pct",
                    ascending=False,
                )
            )


            business_risk_chart = (
                alt.Chart(
                    business_risk
                )
                .mark_bar(
                    cornerRadiusEnd=7,
                    color="#f87171",
                )
                .encode(

                    y=alt.Y(
                        "BusinessType:N",
                        sort="-x",
                        title=None,
                    ),

                    x=alt.X(
                        "low_rating_rate_pct:Q",
                        title="Low rating rate (%)",
                    ),

                    tooltip=[
                        alt.Tooltip(
                            "BusinessType:N",
                            title="Business type",
                        ),

                        alt.Tooltip(
                            "low_rating_rate_pct:Q",
                            title="Low rating %",
                            format=".2f",
                        ),

                        alt.Tooltip(
                            "establishments:Q",
                            title="Establishments",
                            format=",",
                        ),
                    ],
                )
                .properties(
                    height=560
                )
            )


            st.altair_chart(
                chart_style(
                    business_risk_chart
                ),
                use_container_width=True,
            )


    # --------------------------------------------------------
    # Business volume
    # --------------------------------------------------------

    with business_right:

        with st.container(border=True):

            st.subheader(
                "Establishments by business type"
            )


            business_volume = (
                business_stats
                .sort_values(
                    "establishments",
                    ascending=False,
                )
            )


            business_volume_chart = (
                alt.Chart(
                    business_volume
                )
                .mark_bar(
                    cornerRadiusEnd=7,
                    color="#38bdf8",
                )
                .encode(

                    y=alt.Y(
                        "BusinessType:N",
                        sort="-x",
                        title=None,
                    ),

                    x=alt.X(
                        "establishments:Q",
                        title="Rated establishments",
                    ),

                    tooltip=[
                        alt.Tooltip(
                            "BusinessType:N",
                            title="Business type",
                        ),

                        alt.Tooltip(
                            "establishments:Q",
                            title="Establishments",
                            format=",",
                        ),
                    ],
                )
                .properties(
                    height=560
                )
            )


            st.altair_chart(
                chart_style(
                    business_volume_chart
                ),
                use_container_width=True,
            )


    st.write("")


    # --------------------------------------------------------
    # Business type table
    # --------------------------------------------------------

    with st.container(border=True):

        st.subheader(
            "Business type summary"
        )


        display_business_stats = (
            business_stats[
                [
                    "BusinessType",
                    "establishments",
                    "low_rated",
                    "low_rating_rate_pct",
                ]
            ]
            .rename(
                columns={
                    "BusinessType":
                        "Business type",

                    "establishments":
                        "Rated establishments",

                    "low_rated":
                        "Low rated",

                    "low_rating_rate_pct":
                        "Low rating rate (%)",
                }
            )
            .sort_values(
                "Low rating rate (%)",
                ascending=False,
            )
        )


        st.dataframe(
            display_business_stats,
            use_container_width=True,
            hide_index=True,
            column_config={

                "Rated establishments":
                    st.column_config.NumberColumn(
                        format="%d"
                    ),

                "Low rated":
                    st.column_config.NumberColumn(
                        format="%d"
                    ),

                "Low rating rate (%)":
                    st.column_config.ProgressColumn(
                        "Low rating rate (%)",
                        format="%.2f%%",
                        min_value=0,
                        max_value=max(
                            10,
                            float(
                                display_business_stats[
                                    "Low rating rate (%)"
                                ]
                                .max()
                            ),
                        ),
                    ),
            },
        )


# ============================================================
# 14. FOOTER
# ============================================================

st.divider()

st.caption(
    "UK Food Hygiene ML  •  Food Standards Agency data  •  "
    "Low hygiene target = FHRS rating 0, 1 or 2"
)