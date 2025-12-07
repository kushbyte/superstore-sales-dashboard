import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Superstore Sales Dashboard", layout="wide")

# ---- Load Data ----
@st.cache_data
def load_data():
    return pd.read_csv("data/train.csv", parse_dates=["Order Date", "Ship Date"])

df = load_data()

# ---- Sidebar Filters ----
st.sidebar.header("Filter Data")

years = sorted(df["Order Date"].dt.year.unique())
selected_year = st.sidebar.multiselect("Select Year", years, default=years)

segments = df["Segment"].unique()
selected_segment = st.sidebar.multiselect("Select Segment", segments, default=segments)

# Filter the data
filtered_df = df[
    (df["Order Date"].dt.year.isin(selected_year)) &
    (df["Segment"].isin(selected_segment))
]

# ---- KPIs ----
total_sales = filtered_df["Sales"].sum()
total_orders = filtered_df["Order ID"].nunique()
avg_order_value = total_sales / total_orders if total_orders > 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("Total Sales", f"${total_sales:,.0f}")
col2.metric("Total Orders", f"{total_orders:,}")
col3.metric("Avg Order Value", f"${avg_order_value:,.2f}")

st.markdown("---")

# ---- Plot 1: Sales by Category ----
cat_sales = filtered_df.groupby("Category")["Sales"].sum().reset_index()
fig1 = px.bar(cat_sales, x="Category", y="Sales",
              title="Sales by Category", color="Category", text_auto=".2s")
st.plotly_chart(fig1, use_container_width=True)

# ---- Plot 2: Monthly Trend ----
filtered_df["YearMonth"] = filtered_df["Order Date"].dt.to_period("M").astype(str)

month_sales = filtered_df.groupby("YearMonth")["Sales"].sum().reset_index()
fig2 = px.line(month_sales, x="YearMonth", y="Sales",
               title="Monthly Sales Trend", markers=True)
st.plotly_chart(fig2, use_container_width=True)

# ---- Plot 3: Top Cities ----
top_cities = (
    filtered_df.groupby("City")["Sales"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig3 = px.bar(top_cities, x="City", y="Sales",
              title="Top 10 Cities by Sales", color="City", text_auto=".2s")
st.plotly_chart(fig3, use_container_width=True)

# ---- Data Table ----
st.markdown("### 📄 Full Filtered Dataset")
st.dataframe(filtered_df)

# Download button
csv = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Download Filtered Data", csv, "filtered_data.csv", "text/csv")
