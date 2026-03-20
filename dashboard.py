import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# -----------------------------------
# Page Config
# -----------------------------------

st.set_page_config(
    page_title="Coffee Shop Sales Dashboard",
    page_icon="☕",
    layout="wide"
)

st.title("☕ Coffee Shop Sales Dashboard")
st.markdown("Analyze coffee shop performance with interactive insights")

# -----------------------------------
# Load Data with Caching
# -----------------------------------

@st.cache_data
def load_data():

    df = pd.read_csv("data/Coffee Shop Sales.csv")

    df["transaction_time"] = pd.to_datetime(
        df["transaction_time"],
        format="%H:%M:%S"
    )

    df["transaction_date"] = pd.to_datetime(
        df["transaction_date"],
        format="%d-%m-%Y"
    )

    df["hour"] = df["transaction_time"].dt.hour

    df["day"] = df["transaction_date"].dt.day_name()

    df["month"] = df["transaction_date"].dt.to_period("M").astype(str)

    df["revenue"] = df["transaction_qty"] * df["unit_price"]

    df = df[df["transaction_qty"] > 0]
    df = df[df["unit_price"] > 0]

    return df


df = load_data()

# -----------------------------------
# Sidebar
# -----------------------------------

st.sidebar.header("Filters")

date_range = st.sidebar.date_input(
    "Select Date Range",
    [df["transaction_date"].min(), df["transaction_date"].max()]
)

location = st.sidebar.multiselect(
    "Store Location",
    df["store_location"].unique(),
    default=df["store_location"].unique()
)

category = st.sidebar.multiselect(
    "Product Category",
    df["product_category"].unique(),
    default=df["product_category"].unique()
)

df = df[
    (df["transaction_date"] >= pd.to_datetime(date_range[0])) &
    (df["transaction_date"] <= pd.to_datetime(date_range[1])) &
    (df["store_location"].isin(location)) &
    (df["product_category"].isin(category))
]


# -----------------------------------
# KPIs
# -----------------------------------

total_revenue = df["revenue"].sum()
total_transactions = len(df)
avg_transaction = df["revenue"].mean()

col1, col2, col3 = st.columns(3)

col1.metric("💰 Total Revenue", f"${total_revenue:,.2f}")
col2.metric("🧾 Transactions", f"{total_transactions:,}")
col3.metric("💳 Avg Transaction", f"${avg_transaction:,.2f}")


# -----------------------------------
# Extra KPIs (Peak Hour, Best, Worst Product)
# -----------------------------------

# Peak Hour calculation
hourly = df.groupby("hour")["transaction_id"].count()

peak_hour = hourly.idxmax()
peak_transactions = hourly.max()


# Best Product calculation
product_sales = df.groupby("product_detail")["revenue"].sum()

best_product = product_sales.idxmax()
best_product_revenue = product_sales.max()


# Worst Product calculation
worst_product = product_sales.idxmin()
worst_product_revenue = product_sales.min()


# Show in KPI metric boxes
col4, col5, col6 = st.columns(3)

col4.metric(
    "🔥 Peak Hour",
    f"{peak_hour}:00",
    f"{peak_transactions} transactions"
)

with col5:
    st.write("🥇 Best Product")
    st.success(f"{best_product}")
    st.write(f"Revenue: ${best_product_revenue:,.0f}")

with col6:
    st.write("⚠️ Worst Product")
    st.error(f"{worst_product}")
    st.write(f"Revenue: ${worst_product_revenue:,.0f}")
# -----------------------------------
# Highlights
# -----------------------------------

best_store = df.groupby("store_location")["revenue"].sum().idxmax()
best_day = df.groupby("day")["revenue"].sum().idxmax()

st.success(f"🏆 Best Store: {best_store}")
st.info(f"📅 Best Day: {best_day}")



# -----------------------------------
# Tabs
# -----------------------------------

tab1, tab2, tab3, tab4 = st.tabs(
    ["Revenue Trend", "Products", "Stores", "Data"]
)

# -----------------------------------
# Revenue Trend
# -----------------------------------

with tab1:

    col1, col2 = st.columns(2)

    # Daily
    daily = df.groupby("transaction_date")["revenue"].sum()

    with col1:

        st.subheader("Daily Revenue")

        fig1, ax1 = plt.subplots(figsize=(6,3))

        ax1.plot(daily.index, daily.values)

        ax1.set_xlabel("Date")
        ax1.set_ylabel("Revenue")

        st.pyplot(fig1)
        

    # Monthly
    monthly = df.groupby("month")["revenue"].sum()

    with col2:

        st.subheader("Monthly Revenue")

        fig2, ax2 = plt.subplots(figsize=(6,3))

        ax2.plot(monthly.index, monthly.values)

        ax2.set_xlabel("Month")
        ax2.set_ylabel("Revenue")

        st.pyplot(fig2)
    # -----------------------------------
    # Weekday vs Weekend and Monthly Growth
    # -----------------------------------

    col3, col4 = st.columns(2)

    # Weekday vs Weekend
    with col3:

        st.subheader("Weekday vs Weekend Revenue")

        df["is_weekend"] = df["day"].isin(["Saturday", "Sunday"])

        weekend_sales = df.groupby("is_weekend")["revenue"].sum()

        fig3, ax3 = plt.subplots(figsize=(6,3))

        ax3.bar(
            ["Weekday", "Weekend"],
            weekend_sales.values
        )

        ax3.set_xlabel("Day Type")
        ax3.set_ylabel("Revenue")

        plt.tight_layout()

        st.pyplot(fig3)


    # Monthly Growth %
    with col4:

        st.subheader("Monthly Growth %")

        monthly = df.groupby("month")["revenue"].sum().sort_index()

        monthly_growth = monthly.pct_change() * 100

        fig4, ax4 = plt.subplots(figsize=(6,3))

        ax4.plot(
            monthly_growth.index,
            monthly_growth.values,
            marker='o'
        )

        ax4.set_xlabel("Month")
        ax4.set_ylabel("Growth %")

        plt.xticks(rotation=45)

        plt.tight_layout()

        st.pyplot(fig4)




    st.subheader("Sales Heatmap")

    # Create dropdown filters in small columns
    col1, col2 = st.columns([1, 3])  # first column small, second empty

    with col1:
        heatmap_day = st.selectbox(
            "Select Day",
            ["All"] + list(df["day"].unique()),
            key="heatmap_day"
        )

    col3, col4 = st.columns([1, 3])

    with col3:
        heatmap_month = st.selectbox(
            "Select Month",
            ["All"] + list(df["month"].unique()),
            key="heatmap_month"
        )


    # Apply filters
    heatmap_df = df.copy()

    if heatmap_day != "All":
        heatmap_df = heatmap_df[heatmap_df["day"] == heatmap_day]

    if heatmap_month != "All":
        heatmap_df = heatmap_df[heatmap_df["month"] == heatmap_month]


    # Create pivot table
    pivot = heatmap_df.pivot_table(
        values="revenue",
        index="day",
        columns="hour",
        aggfunc="sum"
    )


    # Plot heatmap
    fig, ax = plt.subplots(figsize=(3,2))

    sns.heatmap(
        pivot,
        cmap="YlOrRd",
        annot=False,   # removes clumsy numbers
        cbar=False,        # removes color bar to save space
        ax=ax
    )

    ax.set_title("Revenue Heatmap")

    st.pyplot(fig, use_container_width=False)   


# -----------------------------------
# Products
# -----------------------------------

with tab2:

    col1, col2 = st.columns(2)

    category_sales = df.groupby("product_category")["revenue"].sum()

    with col1:

        st.subheader("Category Revenue")

        fig3, ax3 = plt.subplots(figsize=(6,3))

        ax3.bar(category_sales.index, category_sales.values)

        plt.xticks(rotation=45)

        st.pyplot(fig3)

    top_products = df.groupby(
        "product_detail"
    )["revenue"].sum().nlargest(10)

    with col2:

      st.subheader("Top 10 Products")

      top_products = df.groupby(
        "product_detail"
      )["revenue"].sum().nlargest(10)

      fig, ax = plt.subplots(figsize=(6,3))

       # Horizontal bar chart
      ax.barh(top_products.index, top_products.values)

      ax.set_title("Top 10 Products")
      ax.set_xlabel("Revenue")
      ax.set_ylabel("Product")

      # Show highest on top
      ax.invert_yaxis()

      plt.tight_layout()

      st.pyplot(fig)

# -----------------------------------
# Stores
# -----------------------------------

with tab3:

    col1, col2 = st.columns(2)

    store_sales = df.groupby("store_location")["revenue"].sum()

    with col1:

        st.subheader("Store Revenue")

        fig5, ax5 = plt.subplots(figsize=(6,3))

        ax5.bar(store_sales.index, store_sales.values)

        st.pyplot(fig5)

    hourly = df.groupby("hour")["transaction_id"].count()

    with col2:

        st.subheader("Transactions per Hour")

        fig6, ax6 = plt.subplots(figsize=(6,3))

        ax6.bar(hourly.index, hourly.values)

        st.pyplot(fig6)


# -----------------------------------
# Data
# -----------------------------------

with tab4:

    st.subheader("Dataset")

    st.dataframe(df)

    st.download_button(

        "Download Data",

        df.to_csv(index=False),

        "coffee_sales_cleaned.csv",

        "text/csv"

    )