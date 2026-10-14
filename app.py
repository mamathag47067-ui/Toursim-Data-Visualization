import re
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Indian Tourism Dashboard",
    page_icon="🧭",
    layout="wide",
)

DATA_FILE = Path(__file__).parent / "Top Indian Places to Visit.csv"

st.title("🧭 Indian Tourism Analytics Dashboard")
st.caption("Explore tourist destinations across India. Sidebar filters update every chart and KPI.")

REQUIRED_COLUMNS = [
    "Zone", "State", "City", "Name", "Type", "Establishment Year",
    "time needed to visit in hrs", "Google review rating",
    "Entrance Fee in INR", "Airport with 50km Radius", "Weekly Off",
    "Significance", "DSLR Allowed", "Number of google review in lakhs",
    "Best Time to visit",
]

@st.cache_data
def load_data(file_path: str) -> pd.DataFrame:
    data = pd.read_csv(file_path)
    data.columns = [str(c).strip() for c in data.columns]

    # Remove the exported row-index column if present.
    data = data.loc[:, ~data.columns.str.match(r"^Unnamed")].copy()

    for col in ["time needed to visit in hrs", "Google review rating",
                "Entrance Fee in INR", "Number of google review in lakhs"]:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")

    # Convert year values such as "1921" to numbers; unparseable values stay missing.
    if "Establishment Year" in data.columns:
        year_text = data["Establishment Year"].astype(str).str.extract(r"(\d{4})", expand=False)
        data["Establishment Year"] = pd.to_numeric(year_text, errors="coerce")

    for col in data.select_dtypes(include="object").columns:
        data[col] = data[col].fillna("Unknown").astype(str).str.strip()
        data.loc[data[col].eq(""), col] = "Unknown"

    return data

if not DATA_FILE.exists():
    st.error(
        "Dataset file not found. Put **Top Indian Places to Visit.csv** in the same "
        "folder as **app.py**, then run the app again."
    )
    st.stop()

df = load_data(str(DATA_FILE))
missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
if missing:
    st.error("The CSV is missing expected columns: " + ", ".join(missing))
    st.stop()

# ---------------- Sidebar filters ----------------
st.sidebar.header("🔎 Dashboard Filters")
st.sidebar.write("Choose one or more options. All charts and KPI cards use the same filtered data.")

def multiselect_filter(label: str, column: str):
    options = sorted(df[column].dropna().astype(str).unique().tolist())
    return st.sidebar.multiselect(label, options, default=options, key=f"filter_{column}")

zones = multiselect_filter("Tourism zone", "Zone")
states = multiselect_filter("State", "State")
types = multiselect_filter("Destination type", "Type")
significance = multiselect_filter("Significance", "Significance")
best_times = multiselect_filter("Best time to visit", "Best Time to visit")
airport_options = sorted(df["Airport with 50km Radius"].dropna().astype(str).unique().tolist())
airport_access = st.sidebar.multiselect(
    "Airport within 50 km", airport_options, default=airport_options
)
dslr_options = sorted(df["DSLR Allowed"].dropna().astype(str).unique().tolist())
dslr = st.sidebar.multiselect("DSLR allowed", dslr_options, default=dslr_options)

valid_fees = df["Entrance Fee in INR"].dropna()
fee_min = float(valid_fees.min()) if not valid_fees.empty else 0.0
fee_max = float(valid_fees.max()) if not valid_fees.empty else 0.0
fee_range = st.sidebar.slider(
    "Entrance fee range (₹)",
    min_value=int(fee_min),
    max_value=max(int(fee_max), int(fee_min)),
    value=(int(fee_min), int(fee_max)),
    step=10 if fee_max >= 100 else 1,
)

rating_col = df["Google review rating"].dropna()
rating_min = float(rating_col.min()) if not rating_col.empty else 0.0
rating_max = float(rating_col.max()) if not rating_col.empty else 5.0
rating_range = st.sidebar.slider(
    "Google rating range",
    min_value=max(0.0, rating_min),
    max_value=min(5.0, rating_max),
    value=(max(0.0, rating_min), min(5.0, rating_max)),
    step=0.1,
)

# Apply all sidebar selections once, then use this same dataframe everywhere.
filtered = df[
    df["Zone"].astype(str).isin(zones)
    & df["State"].astype(str).isin(states)
    & df["Type"].astype(str).isin(types)
    & df["Significance"].astype(str).isin(significance)
    & df["Best Time to visit"].astype(str).isin(best_times)
    & df["Airport with 50km Radius"].astype(str).isin(airport_access)
    & df["DSLR Allowed"].astype(str).isin(dslr)
    & df["Entrance Fee in INR"].between(fee_range[0], fee_range[1], inclusive="both")
    & df["Google review rating"].between(rating_range[0], rating_range[1], inclusive="both")
].copy()

st.sidebar.divider()
if st.sidebar.button("Reset all filters", use_container_width=True):
    st.rerun()

if filtered.empty:
    st.warning("No destinations match these filters. Expand or reset the sidebar selections.")
    st.stop()

# ---------------- KPI cards ----------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Destinations", f"{len(filtered):,}")
mean_rating = filtered["Google review rating"].mean()
c2.metric("Average Google rating", f"{mean_rating:.2f} / 5" if pd.notna(mean_rating) else "N/A")
mean_fee = filtered["Entrance Fee in INR"].mean()
c3.metric("Average entrance fee", f"₹{mean_fee:,.0f}" if pd.notna(mean_fee) else "N/A")
mean_duration = filtered["time needed to visit in hrs"].mean()
c4.metric("Average visit time", f"{mean_duration:.1f} hrs" if pd.notna(mean_duration) else "N/A")

st.divider()

# Every chart below is built from `filtered`, so all sidebar filters apply to all charts.
left, right = st.columns(2)

with left:
    st.subheader("1. Top destinations by Google rating")
    top_rated = (
        filtered.dropna(subset=["Google review rating"])
        .sort_values(["Google review rating", "Number of google review in lakhs"], ascending=False)
        .head(15)
    )
    if not top_rated.empty:
        fig = px.bar(
            top_rated.sort_values("Google review rating"),
            x="Google review rating", y="Name", orientation="h",
            color="Google review rating",
            hover_data=["State", "City", "Type", "Entrance Fee in INR"],
            labels={"Name": "Destination", "Google review rating": "Google rating"},
            title="Top 15 rated destinations in the current selection",
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No rating data available for this selection.")

with right:
    st.subheader("2. Destination type distribution")
    type_counts = filtered["Type"].value_counts().rename_axis("Type").reset_index(name="Destinations")
    fig = px.pie(
        type_counts, names="Type", values="Destinations", hole=0.35,
        title="Share of destination types",
    )
    st.plotly_chart(fig, use_container_width=True)

left, right = st.columns(2)

with left:
    st.subheader("3. Average rating by establishment year")
    year_data = filtered.dropna(subset=["Establishment Year", "Google review rating"])
    if not year_data.empty:
        # Group years into decades to make the line chart easier to read.
        year_data = year_data.copy()
        year_data["Decade"] = (year_data["Establishment Year"] // 10 * 10).astype(int)
        trend = year_data.groupby("Decade", as_index=False)["Google review rating"].mean()
        trend = trend.sort_values("Decade")
        fig = px.line(
            trend, x="Decade", y="Google review rating", markers=True,
            labels={"Decade": "Establishment decade", "Google review rating": "Average rating"},
            title="Average Google rating by establishment decade",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No usable establishment-year and rating data for this selection.")

with right:
    st.subheader("4. Entrance fee vs. Google rating")
    scatter_data = filtered.dropna(subset=["Entrance Fee in INR", "Google review rating"])
    if not scatter_data.empty:
        fig = px.scatter(
            scatter_data, x="Entrance Fee in INR", y="Google review rating",
            color="Type", size="Number of google review in lakhs",
            size_max=24, hover_name="Name",
            hover_data=["State", "City", "Significance"],
            labels={"Entrance Fee in INR": "Entrance fee (₹)", "Google review rating": "Google rating"},
            title="Cost and visitor ratings",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No usable entrance-fee and rating data for this selection.")

left, right = st.columns(2)

with left:
    st.subheader("5. Entrance fee distribution")
    fee_data = filtered.dropna(subset=["Entrance Fee in INR"])
    if not fee_data.empty:
        fig = px.histogram(
            fee_data, x="Entrance Fee in INR", nbins=20,
            labels={"Entrance Fee in INR": "Entrance fee (₹)", "count": "Destinations"},
            title="How entrance fees are distributed",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No entrance-fee data for this selection.")

with right:
    st.subheader("6. Destinations by state")
    state_counts = filtered["State"].value_counts().head(15).rename_axis("State").reset_index(name="Destinations")
    fig = px.bar(
        state_counts.sort_values("Destinations"), x="Destinations", y="State",
        orientation="h", color="Destinations",
        title="States with the most destinations in this selection",
    )
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Filtered destination data")
st.caption(f"Showing {len(filtered):,} of {len(df):,} rows after applying the sidebar filters.")
display_columns = [
    "Zone", "State", "City", "Name", "Type", "Establishment Year",
    "Google review rating", "Entrance Fee in INR", "Significance",
    "Best Time to visit", "time needed to visit in hrs",
]
st.dataframe(
    filtered[display_columns].sort_values(["State", "Name"]),
    use_container_width=True,
    hide_index=True,
)
csv_bytes = filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download filtered data as CSV",
    data=csv_bytes,
    file_name="filtered_tourism_destinations.csv",
    mime="text/csv",
)
st.caption("Data source: Top Indian Places to Visit dataset supplied for this project.")
