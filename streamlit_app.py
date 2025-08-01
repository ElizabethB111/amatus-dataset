# -----------------------------
# app.py – AMATUS Exploration
# -----------------------------


import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="AMATUS", layout="wide", page_icon="🧮")

# ---------- GLOBAL CSS ----------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif;
        background-color: #ffffff;
        color: #374151;
    }

    .block-container {
        padding-top: 2rem;
        padding-left: 3rem;
        padding-right: 3rem;
    }

    h1, h2, h3, h4 {
        color: #1f4e79;
        font-weight: 600;
    }

    .stRadio > div {
        gap: 0.5rem;
    }

    a {
        color: #3B82F6;
        text-decoration: none;
    }
    a:hover {
        text-decoration: underline;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- THEME & GLOBAL STYLES ----------

def amatus_theme():
    font = "Roboto"
    axis_color = "#374151"  
    return {
        "config": {
            "view": {"continuousWidth": 420, "continuousHeight": 300},
            "axis": {
                "labelFont": font,
                "titleFont": font,
                "labelColor": axis_color,
                "titleColor": axis_color,
                "gridOpacity": 0.1,
                "domainColor": "#D1D5DB",
                "tickColor": "#D1D5DB",
            },
            "legend": {"labelFont": font, "titleFont": font},
            "title": {
                "font": font,
                "fontSize": 18,
                "anchor": "start",
                "color": axis_color,
            },
            "range": {
                "category": [
                    "#3B82F6",  # Blue
                    "#F59E0B",  # Amber
                    "#14B8A6",  # Teal
                    "#9333EA",  # Purple
                    "#EF4444",  # Red
                    "#22C55E",  # Green
                ]
            },
        }
    }

alt.themes.register("amatus", amatus_theme)
alt.themes.enable("amatus")

# ---------- DATA LOADING ----------
DATA_PATH = Path("AMATUS_dataset.txt")

@st.cache_data(show_spinner=False)
def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, sep=";")
    return df[~df["sample"].isin(["german_students"])]

if DATA_PATH.exists():
    df = load_data(DATA_PATH)
else:
    st.error("Dataset not found. Upload the file to proceed.")
    uploaded = st.file_uploader("Upload AMATUS_dataset.txt", type=["txt", "csv"])
    if uploaded is None:
        st.stop()
    df = load_data(uploaded)

# ---------- SIDEBAR ----------
st.sidebar.markdown('<div style="font-size:1.5rem;font-weight:bold;color:#1f4e79;margin-bottom:1rem;">📘 AMATUS Insights</div>', unsafe_allow_html=True)
page = st.sidebar.radio(
    "Navigate",
    ["Overview", "Score Distribution", "Anxiety Triggers", "Student Profiles"]
)

# ---------- PAGES ----------

if page == "Overview":
    st.title("Welcome to the AMATUS Dashboard")
    st.write("This tool helps you explore student anxiety patterns in mathematics learning.")

elif page == "Score Distribution":
    st.header("Score Distribution")
    demo_option = st.selectbox(
        "Filter by demographic (placeholder)",
        ["All students", "Female", "Male", "Other / not reported"]
    )
    amas_scores = [col for col in df.columns if "score_AMAS" in col]
    score_df = df[amas_scores].melt(var_name="Subscale", value_name="Score")
    chart = alt.Chart(score_df).mark_boxplot(extent='min-max').encode(
        x=alt.X("Subscale:N", title="AMAS Subscale"),
        y=alt.Y("Score:Q", title="Score"),
        color=alt.Color("Subscale:N", legend=None)
    ).properties(width=600, height=400)
    st.altair_chart(chart, use_container_width=True)

elif page == "Anxiety Triggers":
    st.header("What tasks cause anxiety while learning math?")
    amas_cols = [col for col in df.columns if "AMAS" in col and "score" not in col]
    corrs = df[amas_cols + ["score_AMAS_learning"]].corr()
    cor_df = corrs.loc[amas_cols, "score_AMAS_learning"].reset_index()
    cor_df.columns = ["item", "corr"]

    chart = (
        alt.Chart(cor_df)
        .mark_bar()
        .encode(
            y=alt.Y("item:N", sort="-x", title="Survey Item"),
            x=alt.X("corr:Q", title="Correlation with Learning Anxiety"),
            color=alt.condition(
                "datum.corr > 0", alt.value("#EF4444"), alt.value("#3B82F6")
            )
        )
        .properties(height=400)
    )

    text = chart.mark_text(
        align="left",
        baseline="middle",
        dx=3
    ).encode(
        text=alt.Text("corr:Q", format=".2f")
    )

    st.altair_chart(chart + text, use_container_width=True)

elif page == "Student Profiles":
    st.header("Clustered Student Profiles")
    st.markdown("""
    This section will provide a clustering-based summary of student anxiety patterns.
    Future iterations will allow filtering by score levels and AMAS profiles.
    """)

