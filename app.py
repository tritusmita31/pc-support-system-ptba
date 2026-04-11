import streamlit as st
import pandas as pd
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

# =========================
# UI CONFIG
# =========================
st.set_page_config(
    page_title="PC Support System",
    page_icon="💻",
    layout="wide"
)

# =========================
# CUSTOM CSS (FINAL UI)
# =========================
st.markdown("""
<style>

/* BACKGROUND */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #eef2f7, #dfe9f3);
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1e3c72, #2a5298);
}
section[data-testid="stSidebar"] * {
    color: white !important;
}

/* TITLE */
h1 {
    font-size: 38px;
    font-weight: 700;
    color: #1e3c72;
}

h2 {
    font-size: 26px;
    font-weight: 600;
}

h3 {
    font-size: 20px;
}

/* CARD */
.card {
    background: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 6px 20px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}

/* METRIC */
.stMetric {
    background: white;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0px 6px 15px rgba(0,0,0,0.08);
}

/* BUTTON */
.stButton>button {
    background: linear-gradient(90deg, #4CAF50, #2ecc71);
    color: white;
    border-radius: 12px;
    height: 45px;
    font-size: 16px;
    border: none;
}

/* INPUT */
.stTextInput>div>div>input,
.stTextArea textarea,
.stSelectbox>div {
    border-radius: 10px;
}

/* INFO BOX */
.info-box {
    background: linear-gradient(90deg, #e3f2fd, #ffffff);
    padding: 18px;
    border-left: 5px solid #1e88e5;
    border-radius: 10px;
    margin-bottom: 15px;
}

</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================
st.markdown("# 💻 PC Support System")
st.caption("Monitoring perbaikan perangkat secara real-time")

# =========================
# ADMIN
# =========================
ADMIN_NAMA = "Admin IT"
ADMIN_EMAIL = "tritusmita@gmail.com"
ADMIN_PASSWORD = "admin123"

# =========================
# EMAIL
# =========================
SENDER_EMAIL = "tritusmita@gmail.com"
SENDER_PASSWORD = "mlsd svaf tkia pqsn"

# =========================
# DATABASE
# =========================
USER_FILE = "users.csv"
TIKET_FILE = "tiket.csv"

if not os.path.exists(USER_FILE):
    pd.DataFrame(columns=["id","nama","email","password","role"]).to_csv(USER_FILE,index=False)

if not os.path.exists(TIKET_FILE):
    pd.DataFrame(columns=["id_tiket","user","perangkat","keluhan","status","tanggal"]).to_csv(TIKET_FILE,index=False)

def load_users():
    return pd.read_csv(USER_FILE)

def save_users(df):
    df.to_csv(USER_FILE,index=False)

def load_tiket():
    return pd.read_csv(TIKET_FILE)

def save_tiket(df):
    df.to_csv(TIKET_FILE,index=False)

# =========================
# EMAIL FUNCTION
# =========================
def kirim_email(penerima, nama_user, id_tiket, perangkat):
    jam = datetime.now().hour
    salam = "Selamat pagi" if jam<12 else "Selamat siang" if jam<15 else "Selamat sore" if jam<18 else "Selamat malam"

    body = f"""{salam} {nama_user},

Perangkat Anda ({perangkat}) dengan ID Tiket {id_tiket} telah SELESAI diperbaiki.

Silakan ambil di IT Support.

Terima kasih.
"""

    msg = MIMEText(body)
    msg["Subject"] = "Status Perbaikan"
    msg["From"] = SENDER_EMAIL
    msg["To"] = penerima

    try:
        server = smtplib.SMTP("smtp.gmail.com",587)
        server.starttls()
        server.login(SENDER_EMAIL,SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL,penerima,msg.as_string())
        server.quit()
        return True
    except:
        return False

# =========================
# SESSION
# =========================
if "login" not in st.session_state:
    st.session_state.login=False
    st.session_state.user=""
    st.session_state.role=""

# =========================
# REGISTER
# =========================
def register():
    st.markdown("## 📝 Register")

    nama=st.text_input("Nama")
    email=st.text_input("Email")
    password=st.text_input("Password",type="password")

    if st.button("Daftar"):
        users=load_users()
        if email in users["email"].values:
            st.error("Email sudah ada")
        else:
            users.loc[len(users)] = [len(users)+1,nama,email,password,"user"]
            save_users(users)
            st.success("Berhasil daftar")

# =========================
# LOGIN
# =========================
def login():
    st.markdown("## 🔐 Login")

    nama=st.text_input("Nama")
    email=st.text_input("Email")
    password=st.text_input("Password",type="password")

    if st.button("Login"):

        if nama==ADMIN_NAMA and email==ADMIN_EMAIL and password==ADMIN_PASSWORD:
            st.session_state.login=True
            st.session_state.user=nama
            st.session_state.role="admin"
            return

        users=load_users()
        user=users[(users.email==email)&(users.password==password)&(users.nama==nama)]

        if not user.empty:
            st.session_state.login=True
            st.session_state.user=nama
            st.session_state.role="user"
        else:
            st.error("Login gagal")

# =========================
# USER PAGE
# =========================
def user_page():
    st.markdown(f"# 👋 Halo, {st.session_state.user}")

    st.markdown('<div class="info-box">Pantau status perangkat Anda secara real-time</div>', unsafe_allow_html=True)

    tiket=load_tiket()
    user_tiket=tiket[tiket["user"]==st.session_state.user]

    st.markdown("## 📊 Ringkasan Status")

    col1,col2,col3=st.columns(3)
    col1.metric("🕒 Pending",len(user_tiket[user_tiket.status=="Pending"]))
    col2.metric("⚙️ Proses",len(user_tiket[user_tiket.status=="Proses"]))
    col3.metric("✅ Selesai",len(user_tiket[user_tiket.status=="Selesai"]))

    st.markdown("---")

    if st.session_state.menu_user=="📝 Buat Tiket":
        st.markdown("## 📝 Ajukan Perbaikan")

        st.markdown('<div class="card">', unsafe_allow_html=True)

        perangkat=st.selectbox("Perangkat",["Laptop","PC","Printer","Lainnya"])
        keluhan=st.text_area("Keluhan")

        if st.button("Kirim Tiket"):
            tiket.loc[len(tiket)] = [len(tiket)+1,st.session_state.user,perangkat,keluhan,"Pending",datetime.now()]
            save_tiket(tiket)
            st.success("Tiket dikirim!")

        st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.menu_user=="📋 Riwayat":
        st.markdown("## 📋 Riwayat Perbaikan")

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.dataframe(user_tiket, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# =========================
# ADMIN PAGE
# =========================
def admin_page():
    st.markdown("# Admin Dashboard")

    tiket=load_tiket()

    st.markdown("## 📋 Semua Tiket")

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.dataframe(tiket, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if not tiket.empty:
        st.markdown("## 🔄 Update Status")

        col1,col2=st.columns(2)
        with col1:
            id_tiket=st.selectbox("ID Tiket",tiket["id_tiket"])
        with col2:
            status=st.selectbox("Status",["Pending","Proses","Selesai"])

        if st.button("✅ Update"):
            tiket.loc[tiket["id_tiket"]==id_tiket,"status"]=status
            save_tiket(tiket)

            data=tiket[tiket["id_tiket"]==id_tiket].iloc[0]
            users=load_users()
            user_data=users[users["nama"]==data["user"]]

            if not user_data.empty and status=="Selesai":
                kirim_email(user_data.iloc[0]["email"],data["user"],id_tiket,data["perangkat"])

            st.success("Status berhasil diperbarui!")

# =========================
# SIDEBAR
# =========================
st.sidebar.markdown("## 🖥️ PC Support")

if not st.session_state.login:
    menu=st.sidebar.selectbox("Menu",["Login","Register"])
    login() if menu=="Login" else register()

else:
    st.sidebar.markdown(f"👤 {st.session_state.user}")
    st.sidebar.markdown(f"🔑 {st.session_state.role}")

    if st.session_state.role=="user":
        st.session_state.menu_user=st.sidebar.radio(
            "Menu",
            ["📊 Dashboard","📝 Buat Tiket","📋 Riwayat"]
        )

        if st.sidebar.button("Logout"):
            st.session_state.login=False

        user_page()

    else:
        st.sidebar.radio("Menu Admin",["Dashboard"])

        if st.sidebar.button("Logout"):
            st.session_state.login=False

        admin_page()