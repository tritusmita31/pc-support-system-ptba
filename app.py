import streamlit as st
import pandas as pd
import os
import time
import re
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

# TODO: Replace with your purchased premium 3D character asset URL
AI_PC_SUPPORT_BG_URL = "https://cdn.pixabay.com/photo/2021/08/04/13/06/software-developer-6521720_1280.jpg"

# =========================
# UI CONFIG
# =========================
st.set_page_config(
    page_title="Open Ticket - PC Support",
    page_icon="🔧",
    layout="wide"
)

st.markdown("""
<style>
    .reportview-container .main .block-container { max-width: 95%; }
    div[data-testid="stMarkdownContainer"] p {
        font-size: 13px !important;
    }
    .stButton button {
        font-size: 12px !important;
        padding: 0px 10px !important;
        height: 30px !important;
        min-width: 80px !important;
    }
    div[data-testid="stSelectbox"] div div {
        font-size: 12px !important;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# CUSTOM CSS (UI UPGRADE)
# =========================
is_logged_in = st.session_state.get("login", False)

LOGIN_CSS = """
    /* Centered Glassmorphism Login Card Styling (Semi-transparent white) */
    [data-testid="block-container"] {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(25px);
        -webkit-backdrop-filter: blur(25px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 3rem 4rem;
        border-radius: 20px;
        box-shadow: 0 15px 40px rgba(0,0,0,0.4);
        max-width: 480px !important;
        margin: 8vh auto !important;
    }
    
    /* Center the main headers for login and set bright color for dark background */
    h1, h2, h3 {
        text-align: center !important;
        color: #FFFFFF !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.5);
    }
    
    div[data-testid="stCaptionContainer"] p {
        text-align: center !important;
        margin-bottom: 2rem !important;
        color: #E0E0E0 !important;
        font-weight: 500 !important;
    }
    
    /* Ensure input labels stay left aligned and visible */
    .stTextInput label p {
        text-align: left !important;
        font-weight: 600 !important;
        color: #FFFFFF !important;
    }
    
    /* Input fields inside login */
    .stTextInput input {
        background: rgba(255, 255, 255, 0.2) !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        color: #FFFFFF !important;
    }
    
    .stTextInput input:focus {
        background: rgba(255, 255, 255, 0.3) !important;
        border-color: #FFFFFF !important;
        box-shadow: 0 0 10px rgba(255, 255, 255, 0.5) !important;
    }
""" if not is_logged_in else """
    /* Dashboard Wide Styling */
    [data-testid="block-container"] {
        background: transparent;
        max-width: 1300px !important;
        margin: 0 auto;
        padding-top: 2rem;
    }
    
    /* Set Dashboard headers to dark blue */
    h1, h2, h3 {
        color: #0056b3 !important;
    }
    p {
        color: #333 !important;
    }
    
    .stTextInput label p, .stTextArea label p, .stSelectbox label p {
        color: #0056b3 !important;
        font-weight: bold !important;
    }
"""

if not is_logged_in:
    # Linear gradient overlay to darken the background slightly to ensure white input fields and text still have great contrast
    BG_URL_STYLE = f"linear-gradient(rgba(15, 23, 42, 0.6), rgba(15, 23, 42, 0.8)), url('{AI_PC_SUPPORT_BG_URL}')"
else:
    BG_URL_STYLE = "none"

# Using string concatenation to prevent NameError caused by curly braces in Python f-strings
st.markdown("""
<style>

/* BACKGROUND - Fullscreen Image for Login, Standard background for Dashboard */
[data-testid="stAppViewContainer"] {
    background-color: #F8F9FA;
    background-image: """ + BG_URL_STYLE + """;
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

/* TRANSPARENT OVERLAY (Only if logged out) */
.main {
    background: transparent;
}

""" + LOGIN_CSS + """

/* SIDEBAR MODERNIZATION & SOLID BLUE THEME */
section[data-testid="stSidebar"] {
    background: #001B3A !important;
    border-right: none !important;
}
section[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}
section[data-testid="stSidebar"] h2 {
    font-weight: 800 !important;
    font-size: 26px !important;
    margin-bottom: 20px !important;
}

/* Clean Base Radio Text Styling */
section[data-testid="stSidebar"] .stRadio p {
    font-size: 16px !important;
    font-weight: 600 !important;
    color: #FFFFFF !important;
}

/* SIDEBAR LOGOUT BUTTON (Danger Theme Premium) */
section[data-testid="stSidebar"] .stButton {
    background-color: transparent !important;
    padding: 15px 10px !important;
    margin-top: auto !important; /* Pushes to bottom natively if flexed */
    display: flex;
    justify-content: center;
    box-shadow: none !important;
}
section[data-testid="stSidebar"] .stButton > button {
    background-color: #FF4B4B !important; /* Crimson Red */
    color: #FFFFFF !important; /* White text */
    border: none !important;
    border-radius: 15px !important;
    min-height: 45px !important; 
    height: auto !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 12px rgba(255, 75, 75, 0.3) !important;
    width: 100% !important;
    transition: all 0.3s ease;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background-color: #D32F2F !important; /* Darker red on hover */
    color: #FFFFFF !important;
    transform: translateY(-2px);
    box-shadow: 0 6px 15px rgba(211, 47, 47, 0.4) !important;
}

/* Glassmorphism Panels for Main Content */
.glass-panel {
    background: #FFFFFF;
    border-radius: 15px;
    padding: 24px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.03);
    margin-bottom: 20px;
    border: 1px solid rgba(0,0,0,0.02);
}

/* User Metric Cards */
.user-metric-card {
    border-radius: 15px;
    padding: 20px;
    color: white;
    text-align: center;
    box-shadow: 0 6px 12px rgba(0,0,0,0.08);
    transition: transform 0.2s;
}
.user-metric-card:hover { transform: translateY(-3px); }
.user-metric-title { font-size: 14px; font-weight: 600; text-transform: uppercase; margin-bottom: 8px; opacity: 0.9; }
.user-metric-val { font-size: 38px; font-weight: 800; }

.bg-orange-card { background: linear-gradient(135deg, #FFA726, #F57C00); }
.bg-blue-card { background: linear-gradient(135deg, #42A5F5, #1E88E5); }
.bg-green-card { background: linear-gradient(135deg, #66BB6A, #43A047); }

/* DEFAULT INPUT FIELDS (Dashboard) */
.stTextInput input, .stTextArea textarea, .stSelectbox select {
    background: #FFFFFF !important;
    border: 1px solid #CCCCCC !important;
    color: #000000 !important;
    border-radius: 8px !important;
    padding: 12px !important;
    font-size: 15px !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #FF8C00 !important;
    box-shadow: 0 0 10px rgba(255, 140, 0, 0.3) !important;
}

/* TYPOGRAPHY */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Inter', 'Segoe UI', sans-serif !important;
    font-weight: 700 !important;
}

/* MAIN BUTTON STYLING (Sleek White Cards with Dark Text & Big Target Area) */
.stButton>button {
    background-color: #FFFFFF !important;
    color: #003366 !important;
    border-radius: 12px;
    height: auto;
    min-height: 80px;
    padding: 15px 20px;
    width: 100%;
    font-size: 20px !important;
    font-weight: 700 !important;
    border: 1px solid #EAEAEA !important;
    transition: all 0.3s ease;
    box-shadow: 0 5px 15px rgba(0,0,0,0.06);
}
.stButton>button:hover {
    background-color: #FDFDFD !important;
    border-color: #FF8C00 !important;
    color: #FF8C00 !important;
    box-shadow: 0 8px 25px rgba(255, 140, 0, 0.2);
    transform: translateY(-3px);
}

/* DATA FRAME STYLING */
[data-testid="stDataFrame"] {
    border: 1px solid #DDDDDD;
    border-radius: 10px;
    background: #FFFFFF;
    box-shadow: 0 5px 15px rgba(0,0,0,0.05);
}

/* INFO BOXES */
.info-box {
    background: #EAF4FF;
    border-left: 5px solid #0056b3;
    padding: 15px;
    border-radius: 5px;
    font-size: 15px;
    color: #003366;
    margin-bottom: 20px;
}

/* METRIC CARDS */
div[data-testid="metric-container"] {
    background: #FFFFFF;
    padding: 15px 20px;
    border-radius: 10px;
    border: 1px solid #EAEAEA;
    box-shadow: 0 4px 6px rgba(0,0,0,0.03);
}

</style>
""", unsafe_allow_html=True)

# =========================
# DATABASE & SYSTEM CONFIGURATION
# =========================
ADMIN_NAMA = "Admin IT"
ADMIN_EMAIL_LOGIN = "tritusmita@gmail.com"
ADMIN_PASSWORD = "admin123"

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
ADMIN_EMAIL = "tritusmita@gmail.com"
ADMIN_EMAIL_PASSWORD = "mlsd svaf tkia pqsn"

USER_FILE = "users.csv"
TIKET_FILE = "tiket.csv"

if not os.path.exists(USER_FILE):
    pd.DataFrame(columns=["id","nama","email","password","role"]).to_csv(USER_FILE, index=False)

columns = ['id_tiket', 'user', 'perangkat', 'keluhan', 'urgensi', 'lokasi', 'status', 'tanggal', 'pic', 'updated_at']

if not os.path.exists(TIKET_FILE):
    pd.DataFrame(columns=columns).to_csv(TIKET_FILE, index=False)
else:
    try:
        df_mig = pd.read_csv(TIKET_FILE)
        changed = False
        if "lokasi" not in df_mig.columns:
            df_mig["lokasi"] = "-"
            changed = True
        if "urgensi" not in df_mig.columns:
            df_mig["urgensi"] = "Normal"
            changed = True
        if "pic" not in df_mig.columns:
            df_mig["pic"] = "-"
            changed = True
        if "updated_at" not in df_mig.columns:
            df_mig["updated_at"] = "-"
            changed = True
            
        # Migrate old statuses to exact new workflow
        legacy_statuses = ['Open', 'Closed', 'On Process', 'Completed', 'Finished', 'Proses', 'Selesai']
        if any(stat in df_mig['status'].values for stat in legacy_statuses):
            df_mig.loc[df_mig['status'].isin(['Open']), 'status'] = 'Pending'
            df_mig.loc[df_mig['status'].isin(['Proses', 'On Process']), 'status'] = 'In Progress'
            df_mig.loc[df_mig['status'].isin(['Completed', 'Closed', 'Finished', 'Selesai']), 'status'] = 'Resolved'
            changed = True
            
        # Standardize column order
        if list(df_mig.columns) != columns:
            df_mig = df_mig[columns]
            changed = True
            
        if changed:
            df_mig.to_csv(TIKET_FILE, index=False)
    except:
        pass

def load_users():
    return pd.read_csv(USER_FILE)

def save_users(df):
    df.to_csv(USER_FILE, index=False)

def load_tiket():
    df = pd.read_csv(TIKET_FILE)
    expected = ['id_tiket', 'user', 'perangkat', 'keluhan', 'urgensi', 'lokasi', 'status', 'tanggal', 'pic', 'updated_at']
    for col in expected:
        if col not in df.columns:
            if col in ['lokasi', 'pic', 'updated_at']:
                df[col] = '-'
            elif col == 'urgensi':
                df[col] = 'Normal'
            else:
                df[col] = ''
    return df[expected]

def save_tiket(df):
    df.to_csv(TIKET_FILE, index=False)

# =========================
# EMAIL FUNCTION
# =========================
def send_email_notification(user_email, nama_user, perangkat, ticketing_id, waktu_selesai):
    body = f"""Halo {nama_user},

Kami mengonfirmasi bahwa kendala pada perangkat {perangkat} yang dilaporkan pada sistem PC Support telah berhasil ditangani.

Detail Perbaikan:
- Ticketing ID: {ticketing_id}
- Status: Resolved
- Waktu Penyelesaian: {waktu_selesai}

Silakan melakukan verifikasi pada sistem atau mengambil perangkat Anda pada jam operasional kantor.

Terima kasih,
Tim PC Support
"""
    msg = MIMEText(body)
    msg["Subject"] = f"[NOTIFICATION PC SUPPORT] Ticket {ticketing_id} Status Update: Resolved"
    msg["From"] = ADMIN_EMAIL
    msg["To"] = user_email

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(ADMIN_EMAIL, ADMIN_EMAIL_PASSWORD)
        server.sendmail(ADMIN_EMAIL, user_email, msg.as_string())
        server.quit()
        return True
    except:
        return False

# =========================
# SESSION API
# =========================
if "login" not in st.session_state:
    st.session_state.login = False
    st.session_state.user = ""
    st.session_state.role = ""

if "selected_location" not in st.session_state:
    st.session_state.selected_location = ""

# =========================
# REGISTER & LOGIN VIEWS
# =========================
def validate_password(pwd):
    if len(pwd) < 5 or not re.match(r"^[A-Z]", pwd) or not re.search(r"\d", pwd) or not re.search(r"[!@#$%^&*()_+={}\[\]|\\:;\"'<>,.?/~`\-]", pwd):
        return False, "Password tidak sesuai kriteria: Harus min. 5 karakter, diawali huruf kapital, mengandung angka dan simbol!"
    return True, ""

def register():
    st.markdown("## Buat Akun Baru")
    st.caption("Masukan data diri Anda untuk menggunakan sistem.")

    nama = st.text_input("Name")
    email = st.text_input("Email Address")
    
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Register Now"):
        if password != confirm_password:
            st.error("Konfirmasi password tidak cocok!")
        elif not email.endswith("@gmail.com"):
            st.error("Email must be a valid @gmail.com address")
        else:
            is_valid, error_msg = validate_password(password)
            if not is_valid:
                st.error(error_msg)
            else:
                users = load_users()
                if email in users["email"].values:
                    st.error("Alamat Email sudah terdaftar.")
                else:
                    users.loc[len(users)] = [len(users)+1, nama, email, password, "user"]
                    save_users(users)
                    st.success("Registration successful")

def login():
    st.markdown("## Open Ticket PC Support")
    st.caption("Masuk dan pantau perbaikan perangkat Anda.")

    nama = st.text_input("Name")
    email = st.text_input("Email Address")
    password = st.text_input("Password", type="password")

    if st.button("Login ➡️"):
        if nama == ADMIN_NAMA and email == ADMIN_EMAIL_LOGIN and password == ADMIN_PASSWORD:
            st.session_state.login = True
            st.session_state.user = nama
            st.session_state.role = "ADMIN"
            st.rerun()

        users = load_users()
        user = users[(users.email == email) & (users.password == password) & (users.nama == nama)]

        if not user.empty:
            st.session_state.login = True
            st.session_state.user = nama
            st.session_state.role = "USER"
            st.session_state.menu_user = "Create Ticket" 
            st.rerun()
        else:
            st.error("Kredensial tidak valid.")

# =========================
# USER PAGE (STRICTLY FOR USERS)
# =========================
def user_page():
    tiket = load_tiket()
    df_user = tiket[tiket["user"] == st.session_state.user]
    
    if st.session_state.menu_user == "Dashboard Ticket":
        st.markdown(f"<h2>👋 Halo, {st.session_state.user}</h2>", unsafe_allow_html=True)
        st.markdown('<div class="info-box glass-panel" style="margin-bottom:20px; padding: 15px 20px !important;">Pantau status perangkat Anda di sini</div>', unsafe_allow_html=True)
        
        # User Metrics (Colorful Cards)
        c1, c2, c3 = st.columns(3)
        p_count = len(df_user[df_user.status == "Pending"])
        pr_count = len(df_user[df_user.status == "In Progress"])
        s_count = len(df_user[df_user.status == "Resolved"])
        
        c1.markdown(f'<div class="user-metric-card bg-orange-card"><div class="user-metric-title">Pending</div><div class="user-metric-val">{p_count}</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="user-metric-card bg-blue-card"><div class="user-metric-title">In Progress</div><div class="user-metric-val">{pr_count}</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="user-metric-card bg-green-card"><div class="user-metric-title">Resolved</div><div class="user-metric-val">{s_count}</div></div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
        st.markdown("### Ticket History")
        if df_user.empty:
            st.info("Anda belum memiliki riwayat tiket yang dikirimkan.")
        else:
            # Custom Table Display
            col_widths = [1.5, 1.0, 1.0, 1.8, 1.5, 1.2, 1.0, 1.2]
            cols = st.columns(col_widths)
            fields = ["Ticketing ID", "User", "Device", "Issue", "PIC", "Date", "Status", "Updated"]
            for col, field in zip(cols, fields):
                if field == "Ticketing ID":
                    col.markdown(f"<p style='font-weight:bold; margin-bottom:0; white-space:nowrap;'>{field}</p>", unsafe_allow_html=True)
                else:
                    col.markdown(f"<p style='font-weight:bold; margin-bottom:0;'>{field}</p>", unsafe_allow_html=True)
            st.markdown("---")
            
            for idx, row in df_user.iterrows():
                c = st.columns(col_widths)
                c[0].markdown(f"<div style='white-space: nowrap; font-family: monospace; font-size: 14px;'>{row['id_tiket']}</div>", unsafe_allow_html=True)
                c[1].write(row['user'])
                c[2].write(row['perangkat'])
                c[3].write(row['keluhan'])
                c[4].write(row['pic'])
                
                full_date = str(row['tanggal'])
                date_only = full_date[:10]
                time_only = full_date[11:16] if len(full_date) >= 16 else "-"
                c[5].markdown(f"{date_only}<br><span style='color:gray;'>{time_only}</span>", unsafe_allow_html=True)
                
                s = row['status']
                if s == "Pending":
                    badge = f"<span style='background:#FFE0B2; color:#E65100; padding:4px 8px; border-radius:10px; font-weight:bold; font-size:12px;'>{s}</span>"
                elif s == "In Progress":
                    badge = f"<span style='background:#BBDEFB; color:#1565C0; padding:4px 8px; border-radius:10px; font-weight:bold; font-size:12px;'>{s}</span>"
                else:
                    badge = f"<span style='background:#C8E6C9; color:#2E7D32; padding:4px 8px; border-radius:10px; font-weight:bold; font-size:12px;'>{s}</span>"
                c[6].markdown(badge, unsafe_allow_html=True)
                
                full_updated = str(row['updated_at'])
                if full_updated != "-":
                    up_date = full_updated[:10]
                    up_time = full_updated[11:16] if len(full_updated) >= 16 else ""
                    c[7].markdown(f"{up_date}<br><span style='color:gray;'>{up_time}</span>", unsafe_allow_html=True)
                else:
                    c[7].write("-")
                
                st.markdown("<hr style='margin: 5px 0; border-top: 1px solid #F0F0F0;'>", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    elif st.session_state.menu_user == "Create Ticket":
        st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
        st.markdown("### Form Perbaikan")
        perangkat = st.selectbox("Perangkat", ["Laptop", "PC", "Printer", "Network / Jaringan", "Lainnya"])
        keluhan = st.text_area("Keluhan")
        
        if st.button("Kirim Tiket"):
            if keluhan.strip() == "":
                st.warning("Mohon isi deskripsi keluhan terlebih dahulu!")
            else:
                new_id = f"TCK-{datetime.now().strftime('%d%m')}-{len(tiket)+101}"
                urgensi = "Normal"
                lokasi = "-"
                tiket.loc[len(tiket)] = [
                    new_id, 
                    st.session_state.user, 
                    perangkat, 
                    keluhan, 
                    urgensi, 
                    lokasi, 
                    "Pending", 
                    datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "-",
                    "-"
                ]
                save_tiket(tiket)
                st.success("Tiket Anda Berhasil Terkirim! Status saat ini: Pending.")
        st.markdown("</div>", unsafe_allow_html=True)


# =========================
# ADMIN PAGE (STRICTLY FOR ADMINS)
# =========================
def admin_page():
    # Modern SaaS Dashboard CSS Injection for Admin
    st.markdown("""
    <style>
        .admin-card {
            background: #FFFFFF;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            border: 1px solid #EDEDED;
            text-align: center;
        }
        .admin-card-title {
            color: #666;
            font-size: 14px;
            font-weight: 600;
            text-transform: uppercase;
        }
        .admin-card-value {
            font-size: 36px;
            font-weight: 800;
            color: #111;
            margin-top: 10px;
        }
        .status-badge {
            padding: 5px 12px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 12px;
            text-align: center;
            display: inline-block;
        }
        .bg-orange { background: #FFE0B2; color: #E65100; }
        .bg-blue { background: #BBDEFB; color: #1565C0; }
        .bg-green { background: #C8E6C9; color: #2E7D32; }
        
        .admin-table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0 10px;
        }
        .admin-table th {
            background: #F8F9FA;
            color: #555;
            font-weight: 600;
            padding: 12px 15px;
            text-align: left;
            border-bottom: 2px solid #EEE;
        }
        .admin-table td {
            background: #FFFFFF;
            padding: 15px;
            border-top: 1px solid #EEE;
            border-bottom: 1px solid #EEE;
        }
        .admin-table td:first-child { border-left: 1px solid #EEE; border-top-left-radius: 10px; border-bottom-left-radius: 10px; }
        .admin-table td:last-child { border-right: 1px solid #EEE; border-top-right-radius: 10px; border-bottom-right-radius: 10px; }
        
        div.stButton > button {
            white-space: nowrap !important;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("# Admin Control Panel")
    st.markdown("---")

    df_admin = load_tiket()

    if st.session_state.menu_admin == "Management Dashboard":
        # Metric Master Overview For Admin
        st.markdown("### Management Dashboard")
        col1, col2, col3 = st.columns(3)
        
        pending_count = len(df_admin[df_admin.status == "Pending"])
        proses_count = len(df_admin[df_admin.status == "In Progress"])
        selesai_count = len(df_admin[df_admin.status == "Resolved"])

        col1.markdown(f'<div class="user-metric-card bg-orange-card"><div class="user-metric-title">Pending</div><div class="user-metric-val">{pending_count}</div></div>', unsafe_allow_html=True)
        col2.markdown(f'<div class="user-metric-card bg-blue-card"><div class="user-metric-title">In Progress</div><div class="user-metric-val">{proses_count}</div></div>', unsafe_allow_html=True)
        col3.markdown(f'<div class="user-metric-card bg-green-card"><div class="user-metric-title">Resolved</div><div class="user-metric-val">{selesai_count}</div></div>', unsafe_allow_html=True)

    elif st.session_state.menu_admin == "Manage Tickets":
        st.markdown("### Ticket Management - Semua Tiket")
        
        if df_admin.empty:
            st.info("Data tiket saat ini masih kosong (empty).")
        else:
            # List Header
            cols_ratios = [1.5, 1.0, 1.0, 1.5, 1.2, 1.5, 1.0, 1.5, 3.5]
            cols = st.columns(cols_ratios)
            fields = ["Ticketing ID", "User", "Device", "Issue", "PIC", "Date", "Status", "Updated", "Action"]
            for col, field in zip(cols, fields):
                if field in ["Ticketing ID", "Status", "Action"]:
                    col.markdown(f"<p style='font-weight:bold; margin-bottom:0; white-space:nowrap;'>{field}</p>", unsafe_allow_html=True)
                else:
                    col.markdown(f"<p style='font-weight:bold; margin-bottom:0;'>{field}</p>", unsafe_allow_html=True)
            st.markdown("---")

            for idx, row in df_admin.sort_values("id_tiket", ascending=False).iterrows():
                c = st.columns(cols_ratios)
                c[0].markdown(f"<div style='white-space: nowrap; font-family: monospace; font-size: 14px;'>{row['id_tiket']}</div>", unsafe_allow_html=True)
                c[1].write(row['user'])
                c[2].write(row['perangkat'])
                c[3].write(row['keluhan'])
                
                s = row['status']
                if s != "Resolved":
                    new_pic = c[4].text_input("PIC", value=row['pic'], key=f"pic_{row['id_tiket']}", label_visibility="collapsed")
                else:
                    c[4].write(row['pic'])
                
                full_date = str(row['tanggal'])
                date_only = full_date[:10]
                time_only = full_date[11:16] if len(full_date) >= 16 else "-"
                c[5].markdown(f"{date_only}<br><span style='color:gray;'>{time_only}</span>", unsafe_allow_html=True)
                
                if s == "Pending":
                    badge = f"<span style='background:#FFE0B2; color:#E65100; padding:4px 8px; border-radius:10px; font-weight:bold; font-size:12px; white-space:nowrap;'>{s}</span>"
                elif s == "In Progress":
                    badge = f"<span style='background:#BBDEFB; color:#1565C0; padding:4px 8px; border-radius:10px; font-weight:bold; font-size:12px; white-space:nowrap;'>{s}</span>"
                else:
                    badge = f"<span style='background:#C8E6C9; color:#2E7D32; padding:4px 8px; border-radius:10px; font-weight:bold; font-size:12px; white-space:nowrap;'>{s}</span>"
                c[6].markdown(badge, unsafe_allow_html=True)
                
                full_updated = str(row['updated_at'])
                if full_updated != "-":
                    up_date = full_updated[:10]
                    up_time = full_updated[11:16] if len(full_updated) >= 16 else ""
                    c[7].markdown(f"{up_date}<br><span style='color:gray;'>{up_time}</span>", unsafe_allow_html=True)
                else:
                    c[7].write("-")
                
                with c[8]:
                    if s != "Resolved":
                        sub1, sub2 = st.columns([1.8, 1.2])
                        with sub1:
                            new_status = st.selectbox(
                                "Status Update", 
                                ["Pending", "In Progress", "Resolved"], 
                                index=["Pending", "In Progress", "Resolved"].index(row['status']),
                                key=f"status_{row['id_tiket']}"
                            )
                        with sub2:
                            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                            if st.button("Update", key=f"btn_{row['id_tiket']}", use_container_width=True):
                                if new_status != s or new_pic != row['pic']:
                                    df_admin.loc[df_admin["id_tiket"] == row['id_tiket'], "status"] = new_status
                                    df_admin.loc[df_admin["id_tiket"] == row['id_tiket'], "pic"] = new_pic
                                    if new_status == "Resolved" and s != "Resolved":
                                        df_admin.loc[df_admin["id_tiket"] == row['id_tiket'], "updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                                    save_tiket(df_admin)
                                    
                                    # Trigger email ONLY when changed to Resolved
                                    if new_status == "Resolved":
                                        users = load_users()
                                        user_data = users[users["nama"] == row["user"]]
                                        if not user_data.empty:
                                            user_email = user_data.iloc[0]["email"]
                                            waktu_selesai = datetime.now().strftime("%Y-%m-%d %H:%M")
                                            email_sent = send_email_notification(user_email, row["user"], row["perangkat"], row["id_tiket"], waktu_selesai)
                                            if not email_sent:
                                                st.warning("Successfully")
                                                time.sleep(2)
                                            else:
                                                st.success("Successfully ")
                                                time.sleep(1)
                                    else:
                                        st.success("Status Updated!")
                                        time.sleep(0.5)
                                        
                                    st.rerun()
                    else:
                        st.markdown("<span style='color:green; font-size:13px; font-weight:bold; white-space:nowrap;'>Resolved</span>", unsafe_allow_html=True)
                
                st.markdown("---")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Export standardization
            df_export = df_admin.copy()
            df_export = df_export.rename(columns={
                'id_tiket': 'Ticketing ID',
                'user': 'User',
                'perangkat': 'Device',
                'keluhan': 'Issue',
                'pic': 'PIC',
                'tanggal': 'Date',
                'status': 'Status',
                'updated_at': 'Updated'
            })
            df_export = df_export[['Ticketing ID', 'User', 'Device', 'Issue', 'PIC', 'Date', 'Status', 'Updated']]
            csv = df_export.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Report",
                data=csv,
                file_name=f"ticket_report_global.csv",
                mime="text/csv",
            )


# =========================
# CORE NAVIGATION LOGIC
# =========================
def main():
    if not st.session_state.login:
        # Sidebar completely stripped down for Pre-login
        st.sidebar.markdown("## Account Access")
        menu = st.sidebar.radio("Authentication", ["Login", "Register"])
        if menu == "Login":
            login()
        else:
            register()
    else:
        # Sidebar specifically for Logged-In accounts
        st.sidebar.markdown("""
            <div style="display: flex; flex-direction: column; align-items: center; padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.05); margin-bottom: 20px;">
                <img src="https://ui-avatars.com/api/?name=""" + st.session_state.user.replace(' ','+') + """&background=1A73E8&color=fff&bold=true&size=100" style="border-radius: 50%; width: 85px; height: 85px; margin-bottom: 15px; border: 3px solid rgba(255,255,255,0.2);">
                <div style="font-weight: 700; font-size: 18px; color: white;">""" + st.session_state.user + """</div>
                <div style="font-size: 12px; color: #8AB4F8; font-weight: 600; margin-top: 5px; text-transform: uppercase; margin-bottom: 15px;">""" + st.session_state.role + """</div>
            </div>
        """, unsafe_allow_html=True)
        
        # STRICT ROLE PARSING LOGIC
        if st.session_state.role == "ADMIN":
            if "menu_admin" not in st.session_state:
                st.session_state.menu_admin = "Management Dashboard"
                
            st.session_state.menu_admin = st.sidebar.radio("Navigasi", ["Management Dashboard", "Manage Tickets"], label_visibility="collapsed")
            admin_page()
        elif st.session_state.role == "USER":
            if "menu_user" not in st.session_state:
                st.session_state.menu_user = "Dashboard Ticket"
                
            st.session_state.menu_user = st.sidebar.radio("Navigasi", ["Dashboard Ticket", "Create Ticket"], label_visibility="collapsed")
            user_page()
            
        # Move Logout to the bottom
        st.sidebar.markdown("<br><br><br><br><br><br>", unsafe_allow_html=True)
        if st.sidebar.button("Logout", key="logout_btn", use_container_width=True):
            st.session_state.login = False
            st.session_state.selected_location = ""
            st.session_state.user = ""
            st.session_state.role = ""
            if "menu_user" in st.session_state:
                del st.session_state.menu_user
            if "menu_admin" in st.session_state:
                del st.session_state.menu_admin
            st.rerun()

if __name__ == "__main__":
    main()
