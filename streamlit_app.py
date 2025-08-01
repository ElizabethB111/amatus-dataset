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

# Inserted change: demographic filter dropdown in Score Distribution
if page == "Score Distribution":
    demo_option = st.selectbox(
        "Filter by demographic (static placeholder)",
        ["All students", "Female", "Male", "Other / not reported"],
        index=0
    )

