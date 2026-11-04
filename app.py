from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


APP_DIR = Path(__file__).resolve().parent
DATA_PATHS = [APP_DIR / "Breast_Cancer.csv", APP_DIR / "data" / "Breast_Cancer.csv"]
NUMERIC_COLUMNS = [
    "Age",
    "Tumor Size",
    "Regional Node Examined",
    "Reginol Node Positive",
    "Survival Months",
]
CATEGORICAL_COLUMNS = [
    "Race",
    "Marital Status",
    "T Stage",
    "N Stage",
    "6th Stage",
    "differentiate",
    "Grade",
    "A Stage",
    "Estrogen Status",
    "Progesterone Status",
    "Status",
]
COLORS = {"Alive": "#36b7a0", "Dead": "#ef6b78"}
PALETTE = ["#e8678c", "#8057b8", "#39b8a5", "#f1a35b", "#6887d7", "#df7896"]

st.set_page_config(
    page_title="Breast Cancer · Cohort Explorer",
    page_icon="🎗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
    :root { --ink:#282536; --muted:#777486; --pink:#e8678c; --line:#eeeaf1; }
    html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
    .stApp { background:linear-gradient(180deg,#fffafd 0%,#f8f7fb 50%,#f8f7fb 100%); color:var(--ink); }
    h1,h2,h3 { font-family:'Manrope',sans-serif; color:var(--ink); letter-spacing:-.035em; }
    .block-container { padding-top:2rem; padding-bottom:3rem; max-width:1500px; }
    [data-testid="stSidebar"] { background:#fff; border-right:1px solid var(--line); }
    [data-testid="stMetric"] { background:#fff; border:1px solid var(--line); padding:1rem 1.1rem; border-radius:16px; box-shadow:0 5px 18px #38214308; }
    [data-testid="stMetricLabel"] { color:var(--muted); }
    [data-testid="stMetricValue"] { color:var(--ink); font-family:'Manrope',sans-serif; }
    div[data-testid="stTabs"] button { font-weight:600; }
    .hero { padding:1.35rem 1.6rem; border:1px solid #f1dce6; border-radius:22px; background:radial-gradient(circle at 92% 12%,#f8dce7 0,transparent 30%),linear-gradient(115deg,#fff 5%,#fff7fa 100%); margin-bottom:1.2rem; }
    .eyebrow { color:#bb4d77; font-size:.76rem; font-weight:700; letter-spacing:.14em; text-transform:uppercase; }
    .hero h1 { margin:.25rem 0 .35rem; font-size:2rem; }
    .hero p { color:var(--muted); margin:0; max-width:850px; }
    .insight { border-left:4px solid var(--pink); padding:.8rem 1rem; background:#fff; border-radius:0 12px 12px 0; color:#555164; margin:.55rem 0; }
    .note { color:var(--muted); font-size:.83rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def read_csv(file_bytes: bytes) -> pd.DataFrame:
    frame = pd.read_csv(BytesIO(file_bytes))
    frame.columns = frame.columns.astype(str).str.strip()
    frame = frame.rename(
        columns={
            "T Stage ": "T Stage",
            "Reginol Node Positive": "Reginol Node Positive",
        }
    )
    for col in NUMERIC_COLUMNS:
        if col in frame:
            frame[col] = pd.to_numeric(frame[col], errors="coerce")
    for col in CATEGORICAL_COLUMNS:
        if col in frame:
            frame[col] = frame[col].astype("string").str.strip()
    if "Status" in frame:
        frame["Status"] = frame["Status"].str.title()
    return frame


def load_default() -> tuple[pd.DataFrame | None, str | None]:
    for path in DATA_PATHS:
        if path.exists():
            try:
                return read_csv(path.read_bytes()), path.name
            except Exception as exc:
                st.error(f"Could not read {path.name}: {exc}")
    return None, None


def fmt_months(value: float) -> str:
    return f"{value:.1f} mo"


def chart_layout(fig: go.Figure, height: int = 360) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=12, r=12, t=48, b=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", color="#514d5d"),
        title=dict(font=dict(family="Manrope, sans-serif", size=16, color="#282536")),
        legend=dict(title_text="", orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(showgrid=True, gridcolor="#f0edf2", zeroline=False)
    fig.update_yaxes(showgrid=False, zeroline=False)
    return fig


def main() -> None:
    st.markdown(
        """
        <div class="hero">
          <div class="eyebrow">Cohort overview · SEER breast cancer dataset</div>
          <h1>Breast cancer cohort explorer</h1>
          <p>Explore recorded survival status, tumor characteristics, lymph node involvement, and cohort patterns. All charts respond to the filters in the sidebar.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown("## 🎗️ Explore the cohort")
        uploaded = st.file_uploader("Upload the notebook's CSV", type=["csv"], help="Expected columns include Age, Tumor Size, Survival Months, Status, and stage fields.")
        if uploaded is not None:
            try:
                raw = read_csv(uploaded.getvalue())
                source = uploaded.name
            except Exception as exc:
                st.error(f"Could not read uploaded CSV: {exc}")
                st.stop()
        else:
            raw, source = load_default()

        if raw is None:
            st.info("Add `Breast_Cancer.csv` beside `app.py` (or in `data/`), or upload it above. The notebook itself contains only a preview, not the full dataset.")
            st.markdown("**Notebook reference:** 4,024 records · 16 columns · 1 exact duplicate · 0 missing values.")
            st.stop()

        required = {"Age", "Tumor Size", "Survival Months", "Status"}
        missing_required = required.difference(raw.columns)
        if missing_required:
            st.error("Missing required fields: " + ", ".join(sorted(missing_required)))
            st.stop()

        st.caption(f"Data source: {source} · {len(raw):,} rows")
        st.divider()

        view = raw.copy()
        age_min = int(view["Age"].min())
        age_max = int(view["Age"].max())
        age_range = st.slider("Age at diagnosis", age_min, age_max, (age_min, age_max))
        view = view[view["Age"].between(*age_range)]

        for col, label in [("Status", "Survival status"), ("6th Stage", "Stage"), ("Race", "Race"), ("Estrogen Status", "Estrogen receptor"), ("Progesterone Status", "Progesterone receptor")]:
            if col in view.columns:
                options = sorted(view[col].dropna().astype(str).unique().tolist())
                chosen = st.multiselect(label, options, default=options, key=f"filter_{col}")
                view = view[view[col].astype(str).isin(chosen)]

        if "Tumor Size" in view.columns and not view.empty:
            size_min = int(view["Tumor Size"].min())
            size_max = int(view["Tumor Size"].max())
            size_range = st.slider("Tumor size", size_min, size_max, (size_min, size_max), key="tumor_size_slider")
            view = view[view["Tumor Size"].between(*size_range)]

        st.caption(f"Showing {len(view):,} of {len(raw):,} records")

    if view.empty:
        st.warning("No records match the selected filters. Widen a filter to continue.")
        st.stop()

    total = len(view)
    dead_count = int((view["Status"] == "Dead").sum())
    alive_count = int((view["Status"] == "Alive").sum())
    median_tumor = view["Tumor Size"].median()
    median_survival = view["Survival Months"].median()
    death_rate = dead_count / total * 100
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Patients in view", f"{total:,}")
    k2.metric("Recorded alive", f"{alive_count:,}", f"{alive_count / total * 100:.1f}% of view")
    k3.metric("Recorded dead", f"{dead_count:,}", f"{death_rate:.1f}% of view")
    k4.metric("Median tumor size", f"{median_tumor:.0f}")
    k5.metric("Median survival", fmt_months(median_survival))
    st.caption("Status and survival months are the values recorded in this dataset; these summaries are descriptive and do not estimate individual prognosis.")

    overview, tumor_tab, outcomes_tab, data_tab = st.tabs(["Overview", "Tumor & nodes", "Outcomes & cohorts", "Data quality & records"])

    with overview:
        left, right = st.columns([1, 1.35])
        with left:
            counts = view["Status"].value_counts().rename_axis("Status").reset_index(name="Patients")
            fig = px.pie(counts, names="Status", values="Patients", hole=.68, color="Status", color_discrete_map=COLORS)
            fig.update_traces(textposition="inside", textinfo="percent+label", marker=dict(line=dict(color="white", width=3)))
            st.plotly_chart(chart_layout(fig, 360).update_layout(showlegend=False), use_container_width=True)
        with right:
            if "6th Stage" in view:
                stage = view.groupby(["6th Stage", "Status"], observed=True).size().reset_index(name="Patients")
                fig = px.bar(stage, x="6th Stage", y="Patients", color="Status", barmode="group", color_discrete_map=COLORS, category_orders={"6th Stage": [x for x in ["0", "I", "IA", "IB", "IIA", "IIB", "IIIA", "IIIB", "IIIC", "IV"] if x in stage["6th Stage"].astype(str).values]})
                fig.update_layout(title="Patient records by stage and status")
                st.plotly_chart(chart_layout(fig, 360), use_container_width=True)
        st.markdown("#### What stands out in the filtered view")
        if "Survival Months" in view.columns and alive_count and dead_count:
            med = view.groupby("Status")["Survival Months"].median()
            if "Alive" in med and "Dead" in med:
                st.markdown(f'<div class="insight">Median recorded survival is <b>{med["Alive"]:.0f} months</b> among records marked alive and <b>{med["Dead"]:.0f} months</b> among records marked dead.</div>', unsafe_allow_html=True)
        if "Reginol Node Positive" in view.columns:
            node_rate = (view["Reginol Node Positive"] > 0).mean() * 100
            st.markdown(f'<div class="insight"><b>{node_rate:.1f}%</b> of records in this view have at least one positive regional lymph node recorded.</div>', unsafe_allow_html=True)
        st.markdown('<div class="note">These are associations and summaries in the selected records. They do not establish cause or clinical risk.</div>', unsafe_allow_html=True)

    with tumor_tab:
        a, b = st.columns(2)
        with a:
            fig = px.histogram(view, x="Tumor Size", color="Status" if view["Status"].nunique() > 1 else None, marginal="box", nbins=35, opacity=.78, color_discrete_map=COLORS, barmode="overlay")
            fig.update_layout(title="Tumor size distribution", xaxis_title="Tumor size", yaxis_title="Patient records")
            st.plotly_chart(chart_layout(fig, 400), use_container_width=True)
        with b:
            if "Reginol Node Positive" in view and "Regional Node Examined" in view:
                fig = px.scatter(view, x="Regional Node Examined", y="Reginol Node Positive", color="Status", size="Tumor Size", hover_data=[c for c in ["Age", "6th Stage"] if c in view], opacity=.65, color_discrete_map=COLORS)
                fig.update_layout(title="Regional nodes examined vs positive", xaxis_title="Nodes examined", yaxis_title="Positive nodes", yaxis=dict(rangemode="tozero"))
                st.plotly_chart(chart_layout(fig, 400), use_container_width=True)
        if "Tumor Size" in view:
            q1, q3 = view["Tumor Size"].quantile([.25, .75])
            upper = q3 + 1.5 * (q3 - q1)
            outliers = int((view["Tumor Size"] > upper).sum())
            st.markdown(f'<div class="insight">The notebook flagged <b>222 potential tumor-size outliers</b> in the full dataset using the IQR rule. In the current filtered view, <b>{outliers:,}</b> records are above its recalculated upper bound of {upper:.1f}. They remain included in the charts.</div>', unsafe_allow_html=True)
        if "6th Stage" in view:
            fig = px.box(view, x="6th Stage", y="Tumor Size", color="Status", points="outliers", color_discrete_map=COLORS)
            fig.update_layout(title="Tumor size by stage", xaxis_title="Stage", yaxis_title="Tumor size")
            st.plotly_chart(chart_layout(fig, 380), use_container_width=True)

    with outcomes_tab:
        a, b = st.columns(2)
        with a:
            group_options = [c for c in ["6th Stage", "N Stage", "T Stage", "Grade", "Race", "Marital Status", "Estrogen Status", "Progesterone Status"] if c in view.columns]
            if group_options:
                category = st.selectbox("Compare survival months across", group_options, key="survival_group")
                grouped = view.groupby(category, observed=True).agg(Median=("Survival Months", "median"), Records=("Survival Months", "size")).reset_index()
                fig = px.bar(grouped, x=category, y="Median", color="Median", color_continuous_scale=["#f4bfd0", "#8057b8"], hover_data={"Records": True, "Median": ":.1f"})
                fig.update_layout(title=f"Median recorded survival by {category.lower()}", xaxis_title=category, yaxis_title="Median survival months", coloraxis_showscale=False)
                st.plotly_chart(chart_layout(fig, 400), use_container_width=True)
            else:
                st.info("No grouping fields are available in this CSV.")
        with b:
            fig = px.scatter(view, x="Age", y="Survival Months", color="Status", symbol="Status", hover_data=[c for c in ["Tumor Size", "6th Stage", "Reginol Node Positive"] if c in view], opacity=.58, color_discrete_map=COLORS)
            fig.update_layout(title="Age and recorded survival months", xaxis_title="Age at diagnosis", yaxis_title="Survival months")
            st.plotly_chart(chart_layout(fig, 400), use_container_width=True)

        if "Marital Status" in view:
            fig = px.violin(view, x="Marital Status", y="Tumor Size", color="Status", box=True, points=False, color_discrete_map=COLORS)
            fig.update_layout(title="Tumor size by marital status and recorded status", xaxis_title="Marital status", yaxis_title="Tumor size")
            st.plotly_chart(chart_layout(fig, 390), use_container_width=True)

        numeric = view.select_dtypes(include="number")
        if len(numeric.columns) > 1:
            corr = numeric.corr(numeric_only=True)
            fig = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r", zmin=-1, zmax=1, aspect="auto")
            fig.update_layout(title="Numeric feature correlations", coloraxis_colorbar_title="Correlation")
            st.plotly_chart(chart_layout(fig, 470), use_container_width=True)
            st.caption("In the notebook's full data, tumor size and positive nodes had a modest positive correlation (r = 0.24); tumor size and survival months had a weak negative correlation (r = −0.09). Correlation alone does not imply causation.")

    with data_tab:
        duplicates = int(view.duplicated().sum())
        missing_count = int(view.isna().sum().sum())
        q1, q3 = view["Tumor Size"].quantile([.25, .75])
        iqr_upper = q3 + 1.5 * (q3 - q1)
        outlier_count = int((view["Tumor Size"] > iqr_upper).sum())
        q1m, q3m = view["Survival Months"].quantile([.25, .75])
        survival_upper = q3m + 1.5 * (q3m - q1m)
        survival_outliers = int((view["Survival Months"] > survival_upper).sum())
        d1, d2, d3, d4 = st.columns(4)
        d1.metric("Missing cells", f"{missing_count:,}")
        d2.metric("Exact duplicate rows", f"{duplicates:,}")
        d3.metric("Tumor size IQR flags", f"{outlier_count:,}")
        d4.metric("Survival IQR flags", f"{survival_outliers:,}")
        st.caption("Outlier flags use the 1.5×IQR rule and are shown for review; records are not removed automatically. The notebook found 1 duplicate and no missing cells in its 4,024-row source.")
        st.markdown("#### Filtered records")
        st.dataframe(view, use_container_width=True, hide_index=True)
        st.download_button("Download filtered CSV", view.to_csv(index=False).encode("utf-8"), "breast_cancer_filtered.csv", "text/csv", type="primary")


if __name__ == "__main__":
    main()
