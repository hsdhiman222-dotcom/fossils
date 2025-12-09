import streamlit as st
import pandas as pd
import plotly.express as px

# =========================================================
# STREAMLIT DASHBOARD
# =========================================================

st.set_page_config(
    page_title="Customer Analytics Dashboard",
    layout="wide",
    page_icon="📊"
)

st.title("📊 Customer Orders Dashboard")

st.write("Upload your dataset to begin analysis.")

# =========================================================
# FILE UPLOADER
# =========================================================
uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

if uploaded_file is not None:

    # =========================================================
    # 1. Load data
    # =========================================================
    df = pd.read_csv(uploaded_file)

    # =========================================================
    # 2. Clean "Customer Type"
    # =========================================================
    df['Customer Type'] = (
        df['Customer Type']
        .astype(str)
        .str.strip()
        .replace({'': 'Not Defined', 'nan': 'Not Defined', 'NaN': 'Not Defined'})
    )
    df['Customer Type'] = df['Customer Type'].fillna('Not Defined')

    # =========================================================
    # 3. Parse dates
    # =========================================================
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    # Subset only 2025 data
    df_year = df[df['Date'].dt.year == 2025].copy()
    df_year['Month'] = df_year['Date'].dt.to_period('M').dt.to_timestamp()

    # =========================================================
    # 4. Color maps
    # =========================================================
    custom_colors = {
        "Retail Collector": "#b38f00",
        "Gallery": "#cca300",
        "Museum": "#ffcc00",
        "Not Defined": "#ffdb4d",
        "Wholesaler": "#ffe680",
        "Interior Designer": "#fff5cc",
    }

    color_map = {
        "Gallery": "#732626",
        "Interior Designer": "#ff1a1a",
        "Museum": "#cc5200",
        "Not Defined": "#0047b3",
        "Retail Collector": "#ffff66",
        "Wholesaler": "#2db300",
    }

    # =========================================================
    # 5. Base aggregations
    # =========================================================
    customer_counts = (
        df['Customer Type'].value_counts()
        .rename_axis('Customer Type')
        .reset_index(name='Count')
        .sort_values('Count', ascending=True)
    )

    customer_counts['All'] = 'All Customers'

    time_series = (
        df_year.groupby(['Month', 'Customer Type'])
        .size()
        .reset_index(name='Count')
    )

    # =========================================================
    # DASHBOARD VISUALS
    # =========================================================

    st.header("📦 Total Orders by Customer Type (All Years)")
    stack_fig = px.bar(
        customer_counts,
        x='All',
        y='Count',
        color='Customer Type',
        text='Count',
        color_discrete_map=custom_colors,
        height=500,
    )
    st.plotly_chart(stack_fig, use_container_width=True)

    st.header("📈 Monthly Sales Performance (2025)")
    line_fig = px.line(
        time_series, x='Month', y='Count', color='Customer Type',
        markers=True, color_discrete_map=color_map
    )
    st.plotly_chart(line_fig, use_container_width=True)

    st.header("🟡 Customer Share of Total Orders (Donut Chart)")
    donut_fig = px.pie(
        customer_counts,
        names='Customer Type',
        values='Count',
        hole=0.45,
        color='Customer Type',
        color_discrete_map=custom_colors
    )
    st.plotly_chart(donut_fig, use_container_width=True)

    st.header("🔥 Heatmap — Orders by Month and Customer Type (2025)")
    heatmap_data = time_series.pivot(index='Customer Type', columns='Month', values='Count').fillna(0)
    heat_fig = px.imshow(heatmap_data, aspect="auto")
    st.plotly_chart(heat_fig, use_container_width=True)

    st.header("📊 Monthly Share of Orders by Segment (2025)")
    share_ts = time_series.copy()
    share_ts['Month_Total'] = share_ts.groupby('Month')['Count'].transform('sum')
    share_ts['Share'] = share_ts['Count'] / share_ts['Month_Total']

    area_fig = px.area(
        share_ts, x='Month', y='Share', color='Customer Type',
        color_discrete_map=color_map
    )
    st.plotly_chart(area_fig, use_container_width=True)

    st.header("📉 Cumulative Orders by Customer Type (2025)")
    cum_ts = time_series.sort_values(['Customer Type', 'Month']).copy()
    cum_ts['Cumulative Orders'] = cum_ts.groupby('Customer Type')['Count'].cumsum()

    cum_fig = px.line(
        cum_ts, x='Month', y='Cumulative Orders',
        color='Customer Type', markers=True,
        color_discrete_map=color_map
    )
    st.plotly_chart(cum_fig, use_container_width=True)

    st.header("🎯 Bubble Chart — Monthly Order Intensity (2025)")
    bubble_fig = px.scatter(
        time_series, x='Month', y='Customer Type',
        size='Count', color='Customer Type',
        color_discrete_map=color_map
    )
    st.plotly_chart(bubble_fig, use_container_width=True)

    st.header("🏆 Ranking — Total Orders by Segment (2025)")
    segment_rank_2025 = (
        df_year.groupby('Customer Type')
        .size()
        .reset_index(name='Total Orders 2025')
        .sort_values('Total Orders 2025', ascending=True)
    )

    rank_fig = px.bar(
        segment_rank_2025,
        x='Total Orders 2025',
        y='Customer Type',
        orientation='h',
        color='Customer Type',
        color_discrete_map=color_map
    )
    st.plotly_chart(rank_fig, use_container_width=True)

    # =========================================================
    # CUSTOMER ID ANALYSIS (OPTIONAL)
    # =========================================================
    candidate_cols = ['Customer ID', 'Customer_Id', 'Customer Name', 'Customer']
    customer_id_col = next((c for c in candidate_cols if c in df_year.columns), None)

    if customer_id_col:
        st.header("👤 Per-Customer Behavior (2025)")

        cust_seg = (
            df_year.groupby(['Customer Type', customer_id_col])
            .size()
            .reset_index(name='Orders per Customer')
        )

        seg_customer_stats = (
            cust_seg.groupby('Customer Type')['Orders per Customer']
            .agg(['mean', 'max', 'count'])
            .reset_index()
            .rename(columns={
                'mean': 'Avg Orders per Customer',
                'max': 'Max Orders (Single Customer)',
                'count': 'Number of Customers'
            })
        )

        cust_bar_fig = px.bar(
            seg_customer_stats,
            x='Customer Type',
            y='Avg Orders per Customer',
            color='Customer Type',
            color_discrete_map=color_map,
            text='Avg Orders per Customer'
        )

        st.plotly_chart(cust_bar_fig, use_container_width=True)

else:
    st.info("⬆️ Upload your CSV file to generate the dashboard.")

