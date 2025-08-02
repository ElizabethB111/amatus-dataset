# -----------------------------
# app.py – AMATUS Exploration (Fixed Colors)
# -----------------------------

import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import streamlit.components.v1 as components

# JavaScript to detect screen width
st.markdown("""
<script>
    const width = window.innerWidth;
    window.parent.postMessage({streamlitSetFrameHeight: true}, "*");
    window.parent.postMessage({type: "streamlit:screenWidth", width: width}, "*");
</script>
""", unsafe_allow_html=True)

components.html("""
<script>
    const width = window.innerWidth;
    const streamlitWidth = () => {
        const streamlitWindow = window.parent;
        streamlitWindow.postMessage({type: "streamlit:screenWidth", width: width}, "*");
    };
    window.addEventListener("resize", streamlitWidth);
    streamlitWidth();
</script>
""", height=0)

@st.fragment
def read_width():
    st.session_state["screen_width"] = 768
read_width()

# ---------- THEME CONFIG ----------
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
                    "#3B82F6", "#F59E0B", "#14B8A6", "#9333EA", "#EF4444", "#22C55E"
                ]
            },
        }
    }

alt.themes.register("amatus", amatus_theme)
alt.themes.enable("amatus")

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="AMATUS", layout="wide", page_icon="🧮")

# ---------- LOAD DATA ----------
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

amas_cols = [f"AMAS{i}" for i in range(1, 10)]
amas_labels = {
    "AMAS1": "Using math tables in a book", "AMAS2": "Thinking about a math test (1 day before)",
    "AMAS3": "Watching algebra on the board", "AMAS4": "Taking a math exam",
    "AMAS5": "Difficult math homework due next class", "AMAS6": "Listening to a math lecture",
    "AMAS7": "Listening to a peer explain math", "AMAS8": "Taking a pop quiz in math class",
    "AMAS9": "Starting a new math chapter",
}

# ---------- NAVIGATION ----------
page = st.sidebar.radio("Navigate", ["Overview", "Score Distribution", "Anxiety Triggers", "Student Profiles"])

# ---------- PAGE: ANXIETY TRIGGERS ----------
if page == "Anxiety Triggers":
    st.markdown("## Anxiety Triggers: Which math learning tasks correlate with student anxiety?")
    st.markdown("This chart shows the strength of relationship between **specific math tasks** and students’ math learning anxiety.")

    corrs = df[amas_cols + ["score_AMAS_learning"]].corr()
    cor_df = corrs.loc[amas_cols, "score_AMAS_learning"].reset_index()
    cor_df.columns = ["item", "corr"]
    cor_df["label"] = cor_df["item"].map(amas_labels)
    exclude_items = ["AMAS2", "AMAS4", "AMAS8"]
    cor_df = cor_df[~cor_df["item"].isin(exclude_items)]
    selection = alt.selection_single(fields=["label"], empty="all")

    chart = (
        alt.Chart(cor_df)
        .mark_bar(size=20)
        .encode(
            y=alt.Y("label:N", sort="-x", title="Task", axis=alt.Axis(labelLimit=1000, labelAlign="right", labelFontSize=12)),
            x=alt.X("corr:Q", title="Correlation with Math Learning Anxiety"),
            color=alt.Color("label:N", legend=None),
            tooltip=["label:N", alt.Tooltip("corr:Q", format=".2f")],
        )
        .add_selection(selection)
        .properties(height=400)
    )
    st.altair_chart(chart, use_container_width=True)

# ---------- PAGE: STUDENT PROFILES ----------
elif page == "Student Profiles":
    st.header("Student Profiles: What kinds of students are learning math?")
    @st.cache_resource
    def cluster(df_):
        feats = ["score_AMAS_total", "score_SDQ_M", "sum_arith_perf"]
        clean = df_.dropna(subset=feats).copy()
        km = KMeans(n_clusters=3, random_state=42).fit(StandardScaler().fit_transform(clean[feats]))
        label_map = {0: "Quietly Struggling", 1: "Stressed & Struggling", 2: "Capable but Cautious"}
        clean["profile"] = pd.Series(km.labels_, index=clean.index).map(label_map)
        melt = (
            clean.groupby("profile")[feats]
            .mean()
            .reset_index()
            .melt("profile", var_name="metric", value_name="score")
        )
        return clean, melt

    prof_df, melt_df = cluster(df)
    metric_labels = {"score_SDQ_M": "Math Anxiety", "score_AMAS_total": "Overall Anxiety", "sum_arith_perf": "Test Score"}
    melt_df["metric"] = melt_df["metric"].replace(metric_labels)
    sel = st.multiselect("Select profiles", prof_df["profile"].unique(), default=prof_df["profile"].unique())
    prof_df["hl"] = prof_df["profile"].isin(sel)

    if st.session_state.get("screen_width", 1000) < 768:
        left = right = st.container()
    else:
        left, right = st.columns([3, 2], gap="small")

    with left:
        sc = (
            alt.Chart(prof_df)
            .mark_circle(size=60)
            .encode(
                x=alt.X("score_AMAS_total:Q", title="Math Anxiety"),
                y=alt.Y("sum_arith_perf:Q", title="Arithmetic Performance"),
                color=alt.Color("profile:N", scale=alt.Scale(scheme="category")),
                opacity=alt.condition("datum.hl", alt.value(0.9), alt.value(0.15)),
                tooltip=[
                    alt.Tooltip("profile:N", title="Profile"),
                    alt.Tooltip("score_AMAS_total:Q", title="Math Anxiety"),
                    alt.Tooltip("sum_arith_perf:Q", title="Arithmetic Performance"),
                    alt.Tooltip("score_SDQ_M:Q", title="Math Self‑Concept"),
                ],
            )
            .properties(height=380)
        )
        st.altair_chart(sc, use_container_width=True)

    with right:
        bar = (
            alt.Chart(melt_df)
            .mark_bar()
            .encode(
                y=alt.Y("metric:N", title=""),
                x=alt.X("score:Q", title="Mean Score"),
                color=alt.Color("profile:N", scale=alt.Scale(scheme="category"), legend=None),
                row=alt.Row("profile:N", header=alt.Header(labelFontSize=0, title="")),
                tooltip=["profile:N", "metric:N", alt.Tooltip("score:Q", format=".2f")],
            )
            .properties(width=280)
        )
        st.altair_chart(bar, use_container_width=True)

# ---------- PAGE: SCORE DISTRIBUTIONS ----------
elif page == "Score Distribution":
    opts = {
        "score_AMAS_total": "Math Anxiety Total",
        "score_AMAS_learning": "Math Anxiety Learning",
        "score_AMAS_testing": "Math Evaluation Anxiety",
        "sum_arith_perf": "Arithmetic Performance",
        "score_SDQ_M": "Math Self‑Concept",
        "score_PISA_ME": "Math Self‑Efficacy",
        "score_GAD": "General Anxiety (GAD‑7)",
        "score_TAI_short": "Test Anxiety (TAI‑S)",
    }
    scale_notes = {
        "score_AMAS_total": "Scale: 9–45. Higher = worse math anxiety.",
        "score_AMAS_learning": "Scale: 5–25. Higher = worse anxiety about learning math.",
        "score_AMAS_testing": "Scale: 4–20. Higher = worse anxiety about math evaluation.",
        "sum_arith_perf": "Scale: 0–40. Higher = better arithmetic performance.",
        "score_SDQ_M": "Scale: 4–16. Higher = stronger math self‑concept.",
        "score_PISA_ME": "Scale: 6–24. Higher = stronger math self‑efficacy.",
        "score_GAD": "Scale: 7–28. Higher = more general anxiety.",
        "score_TAI_short": "Scale: 5–20. Higher = more test anxiety.",
    }
    m = st.selectbox("Select a score to explore", list(opts.keys()), format_func=lambda k: opts[k])
    hist = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X(f"{m}:Q", bin=alt.Bin(maxbins=50), title=opts[m]),
            y=alt.Y("count()", title="Number of Students"),
            tooltip=[alt.Tooltip(f"{m}:Q", title=opts[m])]
        )
        .properties(height=380)
    )
    st.altair_chart(hist, use_container_width=True)
    st.caption(scale_notes.get(m, ""))


