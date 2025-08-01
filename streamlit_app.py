# -----------------------------
# app.py – AMATUS Exploration
# -----------------------------


import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

#----Detect screen width------
import streamlit.components.v1 as components

st.markdown("""
<script>
    const width = window.innerWidth;
    window.parent.postMessage({streamlitSetFrameHeight: true}, "*");
    window.parent.postMessage({type: "streamlit:screenWidth", width: width}, "*");
</script>
""", unsafe_allow_html=True)

# Capture screen width from frontend (via JavaScript event bridge)
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
    # fallback for small devices
    st.session_state["screen_width"] = 768
read_width()


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

#-------Mobile Friendly Version-----#
st.markdown("""
<style>
/* Make all content containers more flexible */
.block-container {
    padding: 1.5rem 2rem;
    max-width: 100%;
}

/* Improve readability and spacing on smaller screens */
@media screen and (max-width: 768px) {
    .block-container {
        padding: 1rem;
    }

    h1, h2, h3, h4 {
        font-size: 1.2rem !important;
    }

    .overview-header {
        font-size: 1.5rem !important;
    }

    .overview-sub {
        font-size: 1rem !important;
    }

    .sidebar-title {
        font-size: 1.2rem !important;
    }

    .dataset-badge {
        font-size: 0.85rem;
    }

    .footer {
        font-size: 0.75rem !important;
        padding: 0.5rem !important;
    }
}

/* Prevent sidebar radio buttons from crowding */
.stRadio > div {
    flex-direction: column;
}
</style>
""", unsafe_allow_html=True)


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

# ---------- SIDEBAR ----------
st.sidebar.markdown("""
<style>
.sidebar-title {
    font-size: 1.5rem;
    font-weight: bold;
    color: #1f4e79;
    margin-bottom: 1rem;
}
.sidebar-nav label {
    font-size: 1.05rem;
    color: #374151;
    margin: 0.25rem 0;
}
.sidebar-nav input[type="radio"]:checked + div {
    font-weight: 600 !important;
    color: #3B82F6 !important;
}
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown('<div class="sidebar-title">📘 AMATUS Insights</div>', unsafe_allow_html=True)

with st.sidebar:
    with st.container():
        page = st.radio(
            "Navigate",
            ["Overview", "Score Distribution", "Anxiety Triggers", "Student Profiles"],
            index=0,
            label_visibility="collapsed",
            key="nav_radio"
        )


amas_cols = [f"AMAS{i}" for i in range(1, 10)]
amas_labels = {
    "AMAS1": "Using math tables in a book", "AMAS2": "Thinking about a math test (1 day before)", "AMAS3": "Watching algebra on the board", "AMAS4": "Taking a math exam", "AMAS5": "Difficult math homework due next class", "AMAS6": "Listening to a math lecture", "AMAS7": "Listening to a peer explain math", "AMAS8": "Taking a pop quiz in math class", "AMAS9": "Starting a new math chapter",
}

# -------------------- OVERVIEW --------------------------------
# -------------------- PAGE SELECTION CONTROL FLOW --------------------

if page == "Overview":
    st.header("AMATUS Insights")
    st.subheader("🧮 What Constitutes Math Learning Anxiety?")
    st.markdown(
        """
        Many students experience anxiety when learning math — a challenge that can affect their confidence and performance.  
        By understanding students and their math anxiety triggers, educators can better support learners where they need it most. 
        
        Click on the left to begin exploring; click below to explore the underlying data.
        """
    )
    st.image("math photo.png", width=300)

    with st.expander("About the underlying dataset"):
        st.markdown(
            "AMATUS stands for **Arithmetic Performance, Mathematics Anxiety and Attitudes in Primary School Teachers and University Students**. [More info](https://osf.io/gszpb/)."
            
            " Data used in this dashboard was obtained from 848 German university students in 2023 (teachers in the study were excluded by dashboard creators)."
            
            " Click link above for full data explanation. Dashboard creators are unaffiliated with dataset collectors."
        )

elif page == "Anxiety Triggers":
    st.markdown("##  Anxiety Triggers: Which math learning tasks correlate with student anxiety?")
    st.markdown(
        """
         
        This chart shows the strength of relationship between **specific math tasks** and students’ math learning anxiety.
        """
    )

    # Compute correlations
    corrs = df[amas_cols + ["score_AMAS_learning"]].corr()
    cor_df = corrs.loc[amas_cols, "score_AMAS_learning"].reset_index()
    cor_df.columns = ["item", "corr"]
    cor_df["label"] = cor_df["item"].map(amas_labels)

    # Exclude test-related items
    exclude_items = ["AMAS2", "AMAS4", "AMAS8"]
    cor_df = cor_df[~cor_df["item"].isin(exclude_items)]

    # Altair click selection
    selection = alt.selection_single(fields=["label"], empty="all")

    chart = (
        alt.Chart(cor_df)
        .mark_bar(size=20)
        .encode(
            y=alt.Y(
                "label:N",
                sort="-x",
                title="Task",
                axis=alt.Axis(labelLimit=1000, labelAlign="right", labelFontSize=12),
            ),
            x=alt.X("corr:Q", title="Correlation with Math Learning Anxiety"),
            color=alt.condition(selection, alt.value("#3B82F6"), alt.value("#d1d5d5")),
            tooltip=["label:N", alt.Tooltip("corr:Q", format=".2f")],
        )
        .add_selection(selection)
        .properties(height=400)
    )
    st.altair_chart(chart, use_container_width=True)

    # Executive Summary with mobile-friendly spacing
    st.markdown("### What This Means for Teachers")
    st.markdown(
        """
        - On a scale of 0-1, with 1 being higher correlation, all of these math learning tasks trigger relatively high anxiety.
        - **Visual tasks** like *watching math on the board* or *starting a new topic* show the strongest anxiety links.  
        - **Passive learning** (e.g., lectures, peer explanations) also trigger higher anxiety.  
        - **Actionable tip:** Minimize passive delivery and include **hands-on, interactive tasks** like narrated examples, mini whiteboard work, and manipulatives.
        - Since most students reported low math learning anxiety (see Score Distributions), these findings suggest that students may experience more anxiety than they report.
        """
    )


#------------------------------#

elif page == "Student Profiles":
    st.header("Student Profiles: What kinds of students are learning math?")
    # Profile explanations
    explanations = {
        "Quietly Struggling": (
            "These students have mild anxiety but still struggle with performance. "
            "They may benefit from targeted academic support or confidence-building."
        ),
        "Stressed & Struggling": (
            "These students experience high anxiety and low performance. "
            "They may feel overwhelmed and need both emotional and academic intervention."
        ),
        "Capable but Cautious": (
            "These students perform well despite some anxiety. "
            "They have a healthy self-concept and might just need reassurance to keep thriving."
        ),
    }

    for profile, summary in explanations.items():
        with st.expander(profile):
            st.write(summary)
    # ---------- helper: cluster students ----------
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

    # Run clustering and prepare dataframes
    prof_df, melt_df = cluster(df)

    # Prepare metric labels
    metric_labels = {
        "score_SDQ_M": "Math Anxiety",
        "score_AMAS_total": "Overall Anxiety",
        "sum_arith_perf": "Test Score",
    }
    melt_df["metric"] = melt_df["metric"].replace(metric_labels)

    # Profile selector
    sel = st.multiselect(
        "Select profiles",
        prof_df["profile"].unique(),
        default=prof_df["profile"].unique(),
    )
    prof_df["hl"] = prof_df["profile"].isin(sel)

    # ---------- LAYOUT: scatter (left) | bars (right) ----------
    if st.session_state.get("screen_width", 1000) < 768:
    # Stack vertically on small screens
        left = right = st.container()
    else:
        left, right = st.columns([3, 2], gap="small")


    # Scatter plot (left)
    with left:
        sc = (
            alt.Chart(prof_df)
            .mark_circle(size=60)
            .encode(
                x=alt.X("score_AMAS_total:Q", title="Math Anxiety"),
                y=alt.Y("sum_arith_perf:Q", title="Arithmetic Performance"),
                color=alt.Color("profile:N"),
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

    # Bar chart (right)
    with right:
        bar = (
            alt.Chart(melt_df)
            .mark_bar()
            .encode(
                y=alt.Y("metric:N", title=""),
                x=alt.X("score:Q", title="Mean Score"),
                color=alt.Color("profile:N", legend=None),
                row=alt.Row(
                    "profile:N",
                    header=alt.Header(labelFontSize=0, title=""),
                ),
                tooltip=[
                    "profile:N",
                    "metric:N",
                    alt.Tooltip("score:Q", format=".2f"),
                ],
            )
            .properties(width=280)
        )
        st.altair_chart(bar, use_container_width=True)

#--------------------------------#
else:  # Score Distribution
    st.markdown("## Overall Score Distribution")
    st.markdown(
        "Explore how German university students in the study scored across various measures, including math anxiety, arithmetic performance, and test-related self-concepts."
    )

    # Score selection
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

    # Caption with context
    st.caption(scale_notes.get(m, ""))

    # One-sentence summary
    distribution_summaries = {
        "score_AMAS_total": "Most students reported low to moderate overall math anxiety.",
        "score_AMAS_learning": "Learning-related math anxiety is low in these students.",
        "score_AMAS_testing": "Test-related math anxiety is higher overall than learning anxiety.",
        "sum_arith_perf": "Arithmetic scores taken during the study are relatively low. Compare to evaluation anxiety.",
        "score_SDQ_M": "Math self‑concept is fairly balanced, with many students rating themselves moderately high.",
        "score_PISA_ME": "Students show moderate to strong beliefs in their math capabilities.",
        "score_GAD": "General anxiety levels are skewed toward lower scores.",
        "score_TAI_short": "Test anxiety shows a moderate bell-shaped distribution, which makes sense in context of the math evaluation anxiety scores.",
    }
    st.markdown(f"**Summary:** {distribution_summaries.get(m, 'No summary available for this measure.')}")
    st.write("Some self-reported measures appear contradictory to themselves or contradictory to performance on the arithmetic test, while other measures stay consistent."


# ---------- FOOTER ----------
st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #f9fafb;
        color: #6b7280;
        text-align: center;
        font-size: 0.85rem;
        padding: 0.6rem 1rem;
        border-top: 1px solid #e5e7eb;
        z-index: 999;
    }
    .footer a {
        color: #3B82F6;
        text-decoration: none;
        font-weight: 500;
    }
    .footer a:hover {
        text-decoration: underline;
    }
    </style>

    <div class="footer">
        Built for class (MESA 8714)  using Streamlit · Data from <a href="https://osf.io/gszpb/" target="_blank">AMATUS Study</a> · Last updated Aug 2025
    </div>
    """,
    unsafe_allow_html=True,
)

