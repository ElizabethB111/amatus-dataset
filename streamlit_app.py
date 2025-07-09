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

# ---------- THEME & GLOBAL STYLES ----------

def amatus_theme():
    font = "Roboto"
    axis_color = "#4e4e4e"
    return {
        "config": {
            "view": {"continuousWidth": 420, "continuousHeight": 300},
            "axis": {"labelFont": font, "titleFont": font, "labelColor": axis_color, "titleColor": axis_color, "gridOpacity": 0.15},
            "legend": {"labelFont": font, "titleFont": font},
            "title": {"font": font, "fontSize": 18, "anchor": "start", "color": axis_color},
            "range": {"category": ["#4A90E2", "#50E3C2", "#F5A623", "#9013FE", "#D0021B", "#7ED321"]},
        }
    }

alt.themes.register("amatus", amatus_theme)
alt.themes.enable("amatus")

# Minimal CSS
st.markdown(
    """<style>.block-container{padding-top:1rem}h1,h2,h3,h4{color:#1f4e79}</style>""",
    unsafe_allow_html=True,
)

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

# ---------- SIDEBAR NAV ----------
st.sidebar.title("AMATUS Insights")
page = st.sidebar.radio("Navigate", ["Overview", "Anxiety Correlations", "Student Profiles", "Score Distribution"], index=0)

amas_cols = [f"AMAS{i}" for i in range(1, 10)]
amas_labels = {
    "AMAS1": "Using math tables in a book", "AMAS2": "Thinking about a math test (1 day before)", "AMAS3": "Watching algebra on the board", "AMAS4": "Taking a math exam", "AMAS5": "Difficult math homework due next class", "AMAS6": "Listening to a math lecture", "AMAS7": "Listening to a peer explain math", "AMAS8": "Taking a pop quiz in math class", "AMAS9": "Starting a new math chapter",
}

# -------------------- OVERVIEW --------------------
if page == "Overview":
    st.header("AMATUS Insights")
    st.subheader("🧮 Math Learning Anxiety")
    st.markdown(
    """
    Many students experience anxiety when learning math — a challenge that can affect their confidence and performance.  
    This dashboard helps educators and researchers explore key patterns in math learning anxiety and self-concept.  
    By understanding student profiles and anxiety triggers, we can better support learners where they need it most. Click on the left to begin exploring.
    """
)

    st.image("math photo.png", width=300)

    with st.expander("About the dataset"):
        st.markdown("AMATUS stands for **Arithmetic Performance, Mathematics Anxiety and Attitudes in Primary School Teachers and University Students**. [More info](https://osf.io/gszpb/).")
    

# -------------------- ANXIETY CORRELATIONS --------------------
elif page == "Anxiety Correlations":
    st.header("Anxiety Correlations with Learning")
    corrs = df[amas_cols + ["score_AMAS_learning"]].corr()
    cor_df = corrs.loc[amas_cols, "score_AMAS_learning"].reset_index()
    cor_df.columns = ["item", "corr"]
    cor_df["label"] = cor_df["item"].map(amas_labels)
    highlight = st.selectbox("Highlight a task", ["(Show all)"] + list(amas_labels.values()))
    cor_df["hl"] = (cor_df["label"] == highlight) if highlight != "(Show all)" else True
    chart = alt.Chart(cor_df).mark_bar().encode(
        y=alt.Y("label:N", sort="-x", title="Task"), x=alt.X("corr:Q", title="Correlation with Math Learning Anxiety"),
        color=alt.Color("hl:N", scale=alt.Scale(domain=[True, False], range=["#4A90E2", "#d3d3d3"]), legend=None),
        tooltip=["label:N", alt.Tooltip("corr:Q", format=".2f")]).properties(height=420)
    st.altair_chart(chart, use_container_width=True)

# -------------------- STUDENT PROFILES --------------------
elif page == "Student Profiles":
    st.header("Student Profiles: What do students need?")

    @st.cache_resource
    def cluster(df_):
        feats = ["score_AMAS_total", "score_SDQ_M", "sum_arith_perf"]
        clean = df_.dropna(subset=feats).copy()
        km = KMeans(n_clusters=3, random_state=42).fit(
            StandardScaler().fit_transform(clean[feats])
        )
        label_map = {
            0: "Quietly Struggling",
            1: "Stressed & Struggling",
            2: "Capable but Cautious",
        }
        clean["profile"] = pd.Series(km.labels_, index=clean.index).map(label_map)

        melt = (
            clean.groupby("profile")[feats]
                 .mean()
                 .reset_index()
                 .melt("profile", var_name="metric", value_name="score")
        )
        return clean, melt

    prof_df, melt_df = cluster(df)

    #  Replace metric codes with readable labels
    metric_labels = {
        "score_SDQ_M":      "Math Anxiety",
        "score_AMAS_total": "Overall Anxiety",
        "sum_arith_perf":   "Test Score",
    }
    melt_df["metric"] = melt_df["metric"].replace(metric_labels)

    # UI controls
    sel = st.multiselect(
        "Select profiles",
        prof_df["profile"].unique(),
        default=prof_df["profile"].unique(),
    )
    prof_df["hl"] = prof_df["profile"].isin(sel)

    left, right = st.columns([3, 2])

    # Scatter 
    with left:
        sc = (
            alt.Chart(prof_df)
                .mark_circle(size=70)
                .encode(
                    x=alt.X("score_AMAS_total:Q", title="Math Anxiety"),
                    y=alt.Y("sum_arith_perf:Q", title="Arithmetic Performance"),
                    color="profile:N",
                    opacity=alt.condition("datum.hl", alt.value(0.9), alt.value(0.1)),
                    tooltip=["profile:N", "score_SDQ_M:Q"],
                )
                .properties(height=420, width=320)
        )
        st.altair_chart(sc, use_container_width=True)

    with right:
        bar = (
            alt.Chart(melt_df[melt_df["profile"].isin(sel)])
                .mark_bar()
                .encode(
                    y=alt.Y("metric:N", title=""),
                    x=alt.X("score:Q", title="Mean Score"),
                    color="profile:N",
                    row=alt.Row("profile:N", header=alt.Header(labelAngle=0)),
                    tooltip=[
                        "profile:N",
                        "metric:N",
                        alt.Tooltip("score:Q", format=".2f"),
                    ],
                )
                .properties(width=220)
        )
        st.altair_chart(bar, use_container_width=True)



# ---------- PROFILE DESCRIPTIONS ----------
    st.subheader("What does each profile mean?")
    explanations = {
        "Quietly Struggling": 
            "These students have mild anxiety but still struggle with performance. They may benefit from targeted academic support or confidence-building.",
        "Stressed & Struggling": 
            "These students experience high anxiety and low performance. They may feel overwhelmed and need both emotional and academic intervention.",
        "Capable but Cautious": 
            "These students perform well despite some anxiety. They have a healthy self-concept and might just need reassurance to keep thriving.",
    }

    for profile, summary in explanations.items():
        with st.expander(profile):
            st.write(summary)


# -------------------- SCORE DISTRIBUTION --------------------
else:
    st.header("Score Distribution")
    opts = {
        "score_AMAS_total":"Math Anxiety Total","score_AMAS_learning":"Math Anxiety Learning","score_AMAS_testing":"Math Evaluation Anxiety","sum_arith_perf":"Arithmetic Performance","score_SDQ_M":"Math Self‑Concept","score_PISA_ME":"Math Self‑Efficacy","score_GAD":"General Anxiety (GAD‑7)","score_TAI_short":"Test Anxiety (TAI‑S)"}
    m = st.selectbox("Select score", list(opts.keys()), format_func=lambda k:opts[k])
    hist = alt.Chart(df).mark_bar().encode(alt.X(f"{m}:Q", bin=alt.Bin(maxbins=50)), y="count()")
    st.altair_chart(hist, use_container_width=True)
