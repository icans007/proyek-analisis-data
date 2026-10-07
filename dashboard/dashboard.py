import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

st.set_page_config(
    page_title="Dashboard Analisis E-Commerce",
    layout="wide"
)

sns.set(style="darkgrid")

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_data():
    df = pd.read_csv("dashboard/main_data.csv")
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
    df["year"] = df["order_purchase_timestamp"].dt.year
    df["month"] = df["order_purchase_timestamp"].dt.month
    df["month_year"] = df["order_purchase_timestamp"].dt.to_period("M").astype(str)
    return df

df = load_data()

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.header("Filter Data")
    st.markdown("Sesuaikan rentang data yang ingin ditampilkan.")

    # Filter tanggal
    min_date = df["order_purchase_timestamp"].min().date()
    max_date = df["order_purchase_timestamp"].max().date()

    date_range = st.date_input(
        "Pilih rentang tanggal",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    if len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

    # Filter tahun
    available_years = sorted(df["year"].dropna().unique().tolist())
    selected_years = st.multiselect("Pilih Tahun", options=available_years, default=available_years)

    # Filter bulan
    month_map = {
        1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
        5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
        9: "September", 10: "Oktober", 11: "November", 12: "Desember"
    }
    available_months = sorted(df["month"].dropna().unique().tolist())
    selected_months = st.multiselect(
        "Pilih Bulan",
        options=available_months,
        default=available_months,
        format_func=lambda x: month_map.get(x, str(x))
    )

    # Filter kategori produk
    if "product_category_name" in df.columns:
        categories = sorted(df["product_category_name"].dropna().unique().tolist())
        selected_categories = st.multiselect(
            "Pilih Kategori Produk",
            options=categories,
            default=categories[:10] if len(categories) > 10 else categories
        )
    else:
        selected_categories = []

    # Filter kota customer
    if "customer_city" in df.columns:
        cities = sorted(df["customer_city"].dropna().unique().tolist())
        selected_cities = st.multiselect(
            "Pilih Kota Customer",
            options=cities,
            default=cities
        )
    else:
        selected_cities = []

    # Filter range payment
    min_payment = float(df["payment_value"].min())
    max_payment = float(df["payment_value"].max())

    payment_range = st.slider(
        "Rentang Payment Value",
        min_value=float(min_payment),
        max_value=float(max_payment),
        value=(float(min_payment), float(max_payment))
    )

    # Pilihan jumlah top data
    top_n = st.slider("Jumlah Top Kategori", min_value=5, max_value=20, value=10)

    st.markdown("---")
    st.info("Gunakan filter di atas untuk melihat data yang lebih spesifik.")

# =========================
# FILTER DATAFRAME
# =========================
filtered_df = df[
    (df["order_purchase_timestamp"].dt.date >= start_date) &
    (df["order_purchase_timestamp"].dt.date <= end_date) &
    (df["year"].isin(selected_years)) &
    (df["month"].isin(selected_months)) &
    (df["payment_value"].between(payment_range[0], payment_range[1]))
]

if "product_category_name" in filtered_df.columns and len(selected_categories) > 0:
    filtered_df = filtered_df[filtered_df["product_category_name"].isin(selected_categories)]

if "customer_city" in filtered_df.columns and len(selected_cities) > 0:
    filtered_df = filtered_df[filtered_df["customer_city"].isin(selected_cities)]

# =========================
# HEADER & METRICS
# =========================
st.title("Dashboard Analisis E-Commerce")
st.markdown("Analisis komprehensif performa transaksi, tren penjualan, dan segmentasi pelanggan.")
st.markdown("---")

if filtered_df.empty:
    st.warning("Tidak ada data yang sesuai dengan filter yang dipilih. Silakan sesuaikan filter di menu *sidebar*.")
    st.stop()

# Menampilkan metrik utama
total_orders = filtered_df["order_id"].nunique()
total_revenue = filtered_df["payment_value"].sum()
total_customers = filtered_df["customer_id"].nunique()
top_category = filtered_df["product_category_name"].mode()[0] if "product_category_name" in filtered_df.columns else "-"

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Orders", f"{total_orders:,}")
with col2:
    st.metric("Total Revenue", f"R$ {total_revenue:,.2f}")
with col3:
    st.metric("Total Customers", f"{total_customers:,}")
with col4:
    st.metric("Top Category", top_category)

st.markdown("<br>", unsafe_allow_html=True)

# =========================
# VISUALISASI UTAMA (MENGGUNAKAN TABS)
# =========================
tab1, tab2, tab3 = st.tabs([" Performa Produk", " Tren Penjualan", " Segmentasi Pelanggan (RFM)"])

with tab1:
    st.subheader(f"Top {top_n} Kategori Produk Terlaris")
    top_products = (
        filtered_df["product_category_name"]
        .value_counts()
        .head(top_n)
    )
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(x=top_products.values, y=top_products.index, ax=ax, palette="viridis")
    ax.set_xlabel("Jumlah Penjualan")
    ax.set_ylabel("Kategori Produk")
    st.pyplot(fig)

with tab2:
    st.subheader("Tren Order dan Revenue Bulanan")
    col_trend1, col_trend2 = st.columns(2)
    
    with col_trend1:
        monthly_orders = (
            filtered_df.groupby("month_year")["order_id"]
            .nunique()
            .sort_index()
        )
        fig, ax = plt.subplots(figsize=(8, 5))
        monthly_orders.plot(marker="o", ax=ax, color="#1f77b4")
        ax.set_title("Tren Order Bulanan")
        ax.set_xlabel("Bulan")
        ax.set_ylabel("Jumlah Order")
        plt.xticks(rotation=45)
        st.pyplot(fig)
        
    with col_trend2:
        monthly_revenue = (
            filtered_df.groupby("month_year")["payment_value"]
            .sum()
            .sort_index()
        )
        fig, ax = plt.subplots(figsize=(8, 5))
        monthly_revenue.plot(marker="o", ax=ax, color="#2ca02c")
        ax.set_title("Revenue Bulanan")
        ax.set_xlabel("Bulan")
        ax.set_ylabel("Total Revenue")
        plt.xticks(rotation=45)
        st.pyplot(fig)

with tab3:
    st.subheader("Distribusi RFM Score")
    snapshot_date = filtered_df["order_purchase_timestamp"].max()

    rfm = filtered_df.groupby("customer_id").agg({
        "order_purchase_timestamp": lambda x: (snapshot_date - x.max()).days,
        "order_id": "nunique",
        "payment_value": "sum"
    }).reset_index()

    rfm.columns = ["customer_id", "Recency", "Frequency", "Monetary"]

    if not rfm.empty and len(rfm) >= 4:
        rfm["R_score"] = pd.qcut(rfm["Recency"], 4, labels=[4, 3, 2, 1], duplicates="drop")
        rfm["F_score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 4, labels=[1, 2, 3, 4], duplicates="drop")
        rfm["M_score"] = pd.qcut(rfm["Monetary"], 4, labels=[1, 2, 3, 4], duplicates="drop")
        rfm["RFM_score"] = (
            rfm["R_score"].astype(int) +
            rfm["F_score"].astype(int) +
            rfm["M_score"].astype(int)
        )

        fig, ax = plt.subplots(figsize=(10, 5))
        rfm["RFM_score"].value_counts().sort_index().plot(kind="bar", ax=ax, color="#ff7f0e")
        ax.set_xlabel("RFM Score")
        ax.set_ylabel("Jumlah Customer")
        plt.xticks(rotation=0)
        st.pyplot(fig)
    else:
        st.warning("Data tidak cukup untuk menampilkan distribusi RFM berdasarkan filter saat ini.")

st.markdown("---")

# =========================
# DATA PREVIEW & INSIGHTS
# =========================
col_data, col_insight = st.columns([1.5, 1])

with col_data:
    with st.expander(" Lihat Data Mentah (Preview)"):
        st.dataframe(filtered_df.head(50), use_container_width=True)

with col_insight:
    st.success("**Insight Utama**")
    st.markdown("""
    - Kategori produk terlaris di menu *Performa Produk* dapat digunakan untuk memandu prioritas restok dan strategi promosi.
    - Pola pada *Tren Penjualan* membantu mengidentifikasi musim ramai (peak season) vs musim sepi.
    - Distribusi *RFM Score* memisahkan pelanggan loyal dari pelanggan yang berisiko *churn*.
    """)