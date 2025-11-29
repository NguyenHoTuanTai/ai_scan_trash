import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.title("🛒 Giỏ hàng của bạn")





username = st.session_state.get("Customer Name")
role = st.session_state.get("role")

if not username or not role:
    st.warning("Bạn chưa đăng nhập.")
    st.stop()

col1, col2, col3 = st.columns([8, 1, 1])

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


# Ẩn sidebar admin
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

cart_file = "data/cart.csv"

needed_cols = ["Customer Name", "Product Name", "Product ID",
               "Category", "Sub-Category", "Quantity", "Price"]

if os.path.exists(cart_file):
    df_cart = pd.read_csv(cart_file)
    # Đảm bảo các cột cần thiết luôn có
    for col in needed_cols:
        if col not in df_cart.columns:
            df_cart[col] = ""
else:
    df_cart = pd.DataFrame(columns=needed_cols)
    df_cart.to_csv(cart_file, index=False)

# Lấy cart của user hiện tại
cart_items = df_cart[df_cart["Customer Name"] == username].to_dict(orient="records")

if not cart_items:
    st.warning("Giỏ hàng đang trống!")
    st.stop()

# HÀM CẬP NHẬT FILE CART.CSV
def save_cart_to_file(new_items):
    df_existing = pd.read_csv(cart_file) if os.path.exists(cart_file) else pd.DataFrame(columns=needed_cols)
    # Giữ lại sản phẩm của user khác
    df_remaining = df_existing[df_existing["Customer Name"] != username]
    # Thêm cart mới của user hiện tại
    df_new = pd.DataFrame(new_items, columns=needed_cols)
    df_final = pd.concat([df_remaining, df_new], ignore_index=True)
    df_final.to_csv(cart_file, index=False)

# HÀM MUA HÀNG
def process_purchase(product_name, quantity):
    csv_file = "data/Global_Superstore2.csv"
    df_existing = pd.read_csv(csv_file, encoding="ISO-8859-1")
    product_rows = df_existing[df_existing["Product Name"] == product_name]
    today = datetime.now()

    existed_order = df_existing[
        (df_existing["Customer Name"] == username) &
        (df_existing["Product Name"] == product_name)
    ]

    if not existed_order.empty:
        df_existing.loc[existed_order.index[0], ["Order Date", "Ship Date"]] = [today, today]
        df_existing.to_csv(csv_file, index=False, encoding="ISO-8859-1")
        return existed_order.iloc[0].copy()

    row = product_rows.drop_duplicates(subset=["Product Name"]).iloc[0].copy()
    row["Customer Name"] = username
    row["Order ID"] = f"BUY-{today.strftime('%Y%m%d%H%M%S%f')}"
    row["Order Date"] = today
    row["Ship Date"] = today

    df_updated = pd.concat([df_existing, pd.DataFrame([row])], ignore_index=True)
    df_updated.to_csv(csv_file, index=False, encoding="ISO-8859-1")

    return row

# FLAG CHỐNG DOUBLE CLICK
if "processing_purchase" not in st.session_state:
    st.session_state["processing_purchase"] = False

clicked_buy = None
clicked_remove = None



# HIỂN THỊ GIỎ HÀNG
# HIỂN THỊ GIỎ HÀNG
for i, item in enumerate(cart_items):
    with st.container():

        # --- HEADER: Tên sản phẩm ---
        st.write(f"### **{item['Product Name']}**")

        # --- GIÁ ---
        st.write(f"**Giá: ${item.get('Price', 0):,.2f}**")

        # --- 3 NÚT SỐ LƯỢNG SÁT NHAU ---
        qty_left, qty_center, qty_right, qty_trong = st.columns([1, 0.2, 1, 7.8])

        with qty_left:
            if st.button("➖", key=f"minus_{i}", use_container_width=True):
                if item["Quantity"] > 1:
                    item["Quantity"] -= 1
                    save_cart_to_file(cart_items)
                    st.rerun()

        with qty_center:
            st.markdown(
                f"""
                <div style='text-align:center;
                            font-size:20px;
                            padding-top:6px;'>
                    {item['Quantity']}
                </div>
                """,
                unsafe_allow_html=True
            )

        with qty_right:
            if st.button("➕", key=f"plus_{i}", use_container_width=True):
                item["Quantity"] += 1
                save_cart_to_file(cart_items)
                st.rerun()

        # --- HÀNG NÚT MUA & XÓA ---
        btn_left, btn_trong, btn_right, btn_t = st.columns([1, 1, 1, 7])

        with btn_left:
            if st.button("🛒 Mua", key=f"buy_{i}", use_container_width=True):
                clicked_buy = i

        with btn_right:
            if st.button("🗑 Xóa", key=f"del_{i}", use_container_width=True):
                clicked_remove = i

        st.markdown("---")

# XỬ LÝ MUA HÀNG
if clicked_buy is not None:

    if st.session_state["processing_purchase"]:
        st.stop()

    st.session_state["processing_purchase"] = True

    item = cart_items[clicked_buy]
    product_name = item["Product Name"]
    quantity = item["Quantity"]

    purchased_row = process_purchase(product_name, quantity)

    # LƯU VÀO SESSION STATE
    if "purchased" not in st.session_state:
        st.session_state["purchased"] = []
    st.session_state["purchased"].append(purchased_row.to_dict())

    # XÓA KHỎI CART
    new_cart = [item for idx, item in enumerate(cart_items) if idx != clicked_buy]
    save_cart_to_file(new_cart)

    st.session_state["processing_purchase"] = False
    st.switch_page("pages/my_orders.py")


# XỬ LÝ XÓA SẢN PHẨM
if clicked_remove is not None:
    new_cart = [item for idx, item in enumerate(cart_items) if idx != clicked_remove]
    save_cart_to_file(new_cart)
    st.rerun()

# TỔNG TIỀN
total_price = sum(item["Price"] * item["Quantity"] for item in cart_items)
st.markdown(f"**Tổng tiền giỏ hàng: ${total_price:,.2f}**")
