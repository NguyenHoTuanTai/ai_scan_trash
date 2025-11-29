import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Đổi mật khẩu",
    layout="centered",         
    initial_sidebar_state="expanded"
)


st.markdown("""
        <style>
            
            header[data-testid="stHeader"] { display: none !important; }
            [data-testid="stSidebar"] { display: none !important; }
        </style>
    """, unsafe_allow_html=True)

role = st.session_state.get("role", "user")

col1, col2, col3 = st.columns([7, 1, 1])

with col3:
    if st.button("Quay Lai"):
        if role == "admin":
            st.switch_page("pages/app.py")
        elif role == "user":
            st.switch_page("pages/product_view.py")
    

# Kiểm tra login
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("Bạn cần đăng nhập để đổi mật khẩu.")
    st.stop()

st.title("Đổi mật khẩu")

old_pass = st.text_input("Mật khẩu cũ", type="password", key="old_pass")
new_pass = st.text_input("Mật khẩu mới", type="password", key="new_pass")
new_pass2 = st.text_input("Xác nhận mật khẩu mới", type="password", key="new_pass2")

if st.button("Cập nhật mật khẩu"):
    #Load accounts
    accounts = pd.read_csv("data/customers_unique.csv", encoding="utf-8")
    username = st.session_state["Customer Name"]

    # Kiểm tra mật khẩu cũ
    if accounts.loc[accounts["Customer Name"]==username, "password"].values[0] != old_pass:
        st.error("Mật khẩu cũ không đúng!")
    elif new_pass != new_pass2:
        st.error("Mật khẩu mới xác nhận không khớp!")
    else:
        # Cập nhật mật khẩu
        accounts.loc[accounts["Customer Name"]==username, "password"] = new_pass
        accounts.to_csv("data/customers_unique.csv", index=False, encoding="utf-8")
        st.success("Đổi mật khẩu thành công!")
