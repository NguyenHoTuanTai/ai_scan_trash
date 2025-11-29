import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

st.set_page_config(
    page_title="Product View",
    layout="wide"   
)


username = st.session_state.get("Customer Name")
role = st.session_state.get("role")

if not username or not role:
    st.warning("Bạn chưa đăng nhập.")
    st.stop()

if role != "user":
    st.error("❌ Trang này chỉ dành cho USER.")
    st.stop()

# File giỏ hàng
cart_file = "data/cart.csv"
os.makedirs("data", exist_ok=True)

# Tạo file cart nếu chưa có
if not os.path.exists(cart_file):
    pd.DataFrame(columns=[
        "Customer Name", "Product Name", "Product ID",
        "Category", "Sub-Category", "Quantity", "Price"
    ]).to_csv(cart_file, index=False)

# Load giỏ hàng của user
cart_df = pd.read_csv(cart_file)
user_cart = cart_df[cart_df["Customer Name"] == username]

st.session_state["cart_items"] = user_cart.to_dict(orient="records")
st.session_state["cart_count"] = user_cart["Quantity"].sum() if not user_cart.empty else 0

# Ẩn sidebar cho user
if role == "user":
    st.markdown("""
        <style>
            [data-testid="stSidebarNav"] ul li:nth-child(1),
            [data-testid="stSidebarNav"] ul li:nth-child(4),
            [data-testid="stSidebarNav"] ul li:nth-child(2)
            {
                display: none !important;
            }
        </style>
    """, unsafe_allow_html=True)

# Giỏ hàng & purchased
if "purchased" not in st.session_state:
    st.session_state["purchased"] = []

# Hiển thị giỏ hàng & logout
st.markdown(f"""
<style>
.fixed-top-right {{
    position: fixed;
    top: 15px;
    right: 20px;
    z-index: 999;
    display: flex;
    align-items: center;
    gap: 10px;
}}
.cart-box {{
    font-size: 18px;
    background-color: white;
    padding: 5px 10px;
    border-radius: 5px;
    box-shadow: 1px 1px 5px rgba(0,0,0,0.3);
    white-space: nowrap;
}}
.logout-btn {{
    background-color: #ff4b4b;
    color: white;
    border: none;
    padding: 6px 12px;
    border-radius: 5px;
    cursor: pointer;
    box-shadow: 1px 1px 5px rgba(0,0,0,0.3);
    font-size: 15px;
}}
.logout-btn:hover {{
    background-color: #ff1f1f;
}}
</style>
<div class="fixed-top-right">
    <div class="cart-box">
        🛒 <span style="color:red; font-weight:bold;">{st.session_state['cart_count']}</span>
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([7, 1, 2])
with col2:
    if st.button(f"🛒 {st.session_state['cart_count']}"):
        st.switch_page("pages/cart.py")
with col3:
    if st.button("⚙️"):
        st.session_state.show_menu = not st.session_state.get("show_menu", False)

    if st.session_state.get("show_menu", False):
        st.markdown(f"**Customer ID:** `{st.session_state.get('Customer ID', 'N/A')}`")
        st.markdown(f"**Username :** `{st.session_state.get('Customer Name', 'N/A')}`")
        if st.button("Đổi mật khẩu"):
            st.switch_page("pages/change_password.py")
        if st.button("Đăng xuất"):
            st.session_state.clear()
            st.switch_page("login.py")

# Load dữ liệu sản phẩm
df = pd.read_csv(
    "data/Global_Superstore2.csv",
    encoding="ISO-8859-1",
    parse_dates=["Order Date", "Ship Date"],
    dayfirst=True
)

# Top 20 sản phẩm bán chạy
st.subheader("Top 20 sản phẩm bán chạy nhất")
top_products = (
    df.groupby("Product Name")
    .agg({
        "Sales": "sum",
        "Category": "first",
        "Sub-Category": "first",
        "Product ID": "first"
    })
    .sort_values("Sales", ascending=False)
    .head(20)
    .reset_index()
)
fig = px.bar(
    top_products,
    x="Sales",
    y="Product Name",
    orientation="h",
    text="Sales",
    labels={"Sales": "Tổng Sales", "Product Name": "Tên sản phẩm"},
)
fig.update_layout(yaxis=dict(autorange="reversed"), height=600)
st.plotly_chart(fig, use_container_width=True)

# Search + Filter
st.subheader("Khám phá sản phẩm")
search_query = st.text_input("Tìm sản phẩm bất kỳ", "")
categories = ["Tất cả"] + sorted(df["Category"].unique())
selected_category = st.selectbox("Lọc theo Category", categories)
subcats = df[df["Category"]==selected_category]["Sub-Category"].unique() if selected_category!="Tất cả" else df["Sub-Category"].unique()
subcats = ["Tất cả"] + sorted(subcats)
selected_subcat = st.selectbox("Lọc theo Sub-Category", subcats)

# Lọc sản phẩm
all_products = df.groupby("Product Name").agg({
    "Sales":"sum","Category":"first","Sub-Category":"first","Product ID":"first"
}).reset_index()
if selected_category!="Tất cả":
    all_products = all_products[all_products["Category"]==selected_category]
if selected_subcat!="Tất cả":
    all_products = all_products[all_products["Sub-Category"]==selected_subcat]
if search_query:
    all_products = all_products[all_products["Product Name"].str.contains(search_query, case=False, na=False)]

if not all_products.empty:
    st.dataframe(all_products, height=600)
    selected_product = st.selectbox("Chọn sản phẩm để xem chi tiết", all_products["Product Name"].tolist())
    product_info = all_products[all_products["Product Name"]==selected_product].iloc[0]
    st.info(
        f"**Tên sản phẩm:** {product_info['Product Name']}\n\n"
        f"**Product ID:** {product_info['Product ID']}\n\n"
        f"**Category:** {product_info['Category']}\n\n"
        f"**Sub-Category:** {product_info['Sub-Category']}\n\n"
        f"**Tổng Sales:** ${product_info['Sales']:,.2f}"
    )

    # Thêm vào giỏ & mua ngay
    def add_to_cart():
        cart_df = pd.read_csv(cart_file)
        existed = cart_df[(cart_df["Customer Name"]==username) & (cart_df["Product Name"]==selected_product)]
        row = df[df["Product Name"]==selected_product].iloc[0]
        price = round(row["Sales"]/row["Quantity"] if row["Quantity"]>0 else 0,2)
        if not existed.empty:
            idx = existed.index[0]
            cart_df.loc[idx,"Quantity"] += 1
        else:
            new_item = {
                "Customer Name": username,
                "Product Name": selected_product,
                "Product ID": product_info["Product ID"],
                "Category": product_info["Category"],
                "Sub-Category": product_info["Sub-Category"],
                "Quantity": 1,
                "Price": price
            }
            cart_df = pd.concat([cart_df,pd.DataFrame([new_item])], ignore_index=True)
        cart_df.to_csv(cart_file, index=False)
        st.session_state["cart_items"] = cart_df[cart_df["Customer Name"]==username].to_dict("records")
        st.session_state["cart_count"] = sum([x["Quantity"] for x in st.session_state["cart_items"]])

    def buy_now():
        product_rows = df[df["Product Name"]==selected_product]
        if product_rows.empty: return
        csv_file = "data/Global_Superstore2.csv"
        df_existing = pd.read_csv(csv_file, encoding="ISO-8859-1")
        today = datetime.now()
        existed_order = df_existing[(df_existing["Customer Name"]==username) & (df_existing["Product Name"]==selected_product)]
        if not existed_order.empty:
            df_existing.loc[existed_order.index[0],["Order Date","Ship Date"]] = [today,today]
        else:
            row = product_rows.iloc[0].copy()
            row["Customer Name"] = username
            row["Order ID"] = f"BUY-{today.strftime('%Y%m%d%H%M%S%f')}"
            row["Order Date"] = today
            row["Ship Date"] = today
            df_existing = pd.concat([df_existing,pd.DataFrame([row])], ignore_index=True)
        df_existing.to_csv(csv_file,index=False,encoding="ISO-8859-1")
        st.session_state["purchased"].append(selected_product)

    col1,col2,_ = st.columns([1,2,7])
    with col1: st.button("🛒", on_click=add_to_cart)
    with col2: st.button("Mua ngay", on_click=buy_now)

    #     GỢI Ý SẢN PHẨM DỰA TRÊN LỊCH SỬ MUA
    st.subheader("Gợi ý dành cho bạn")

    # Lấy lịch sử mua hàng thật từ Global_Superstore2
    history_df = df[df["Customer Name"] == username]

    def suggest_from_history(history_df, all_df):
        if history_df.empty:
            return pd.DataFrame()

        cats = history_df["Category"].unique()
        subs = history_df["Sub-Category"].unique()
        purchased_ids = history_df["Product ID"].unique()

        suggestions = all_df[
            (
                (all_df["Category"].isin(cats)) |
                (all_df["Sub-Category"].isin(subs))
            )
            & (~all_df["Product ID"].isin(purchased_ids))
        ]

        return suggestions.drop_duplicates("Product ID").head(8)

    # Lấy suggestions
    all_df = df.groupby("Product Name").agg({
        "Sales": "sum",
        "Category": "first",
        "Sub-Category": "first",
        "Product ID": "first"
    }).reset_index()

    suggestions = suggest_from_history(history_df, all_df)

    if suggestions.empty:
        st.info("Không có gợi ý nào dành cho bạn.")
    else:
        cols = st.columns(4)

        for i, (_, row) in enumerate(suggestions.iterrows()):
            with cols[i % 4]:
                st.markdown(row["Product Name"])
                st.write(f"**Category:** {row['Category']}")
                st.write(f"**Sub-Category:** {row['Sub-Category']}")

                # Nút thêm vào giỏ
                if st.button("🛒 Thêm vào giỏ", key=f"suggest_add_{row['Product ID']}"):
                    # Logic thêm vào giỏ giống phần trên
                    cart_df = pd.read_csv(cart_file)
                    existed = cart_df[(cart_df["Customer Name"] == username) &
                                    (cart_df["Product Name"] == row["Product Name"])]

                    price_row = df[df["Product Name"] == row["Product Name"]].iloc[0]
                    price = round(price_row["Sales"] / price_row["Quantity"] if price_row["Quantity"] > 0 else 0, 2)

                    if not existed.empty:
                        idx = existed.index[0]
                        cart_df.loc[idx, "Quantity"] += 1
                    else:
                        new_item = {
                            "Customer Name": username,
                            "Product Name": row["Product Name"],
                            "Product ID": row["Product ID"],
                            "Category": row["Category"],
                            "Sub-Category": row["Sub-Category"],
                            "Quantity": 1,
                            "Price": price
                        }
                        cart_df = pd.concat([cart_df, pd.DataFrame([new_item])], ignore_index=True)

                    cart_df.to_csv(cart_file, index=False)
                    st.session_state["cart_items"] = cart_df[cart_df["Customer Name"] == username].to_dict("records")

                    st.session_state["cart_count"] = sum([x["Quantity"] for x in st.session_state["cart_items"]])

                    st.rerun()