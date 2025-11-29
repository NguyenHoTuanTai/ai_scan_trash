import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="my_orders",
    layout="wide"
)
st.title("Đơn hàng của bạn")

username = st.session_state.get("Customer Name")
role = st.session_state.get("role")
# --- Kiểm tra login ---
if "role" not in st.session_state or st.session_state["role"] != "user":
    st.warning("Bạn phải đăng nhập bằng tài khoản user để xem trang này.")
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

# --- Đọc từ CSV ---
df = pd.read_csv(
    "data/Global_Superstore2.csv",
    encoding="ISO-8859-1",
    parse_dates=["Order Date", "Ship Date"],
    dayfirst=True
)

# --- Chỉ lọc theo username – KHÔNG GHÉP SESSION_STATE ---
customer_data_display = df[df["Customer Name"] == username]

if customer_data_display.empty:
    st.warning("Bạn chưa mua sản phẩm nào.")
else:
    # Bỏ các cột không cần
    cols_to_drop = ["Quantity", "Discount", "Profit", "Shipping Cost", "Order Priority", "Postal Code"]
    customer_data_display = customer_data_display.drop(
        columns=[c for c in cols_to_drop if c in customer_data_display.columns],
        errors="ignore"
    )

    st.dataframe(customer_data_display, height=600)
