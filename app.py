import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import os

# ================================
# 🕒 TIMEZONE ASIA/JAKARTA (WIB)
# ================================
LOCAL_TZ = pytz.timezone("Asia/Jakarta")

def now():
    return datetime.now(LOCAL_TZ)

# ================================
# 📂 FOLDER & FILE
# ================================
CSV_FILE = "data_project.csv"
UPLOAD_FOLDER = "uploads"
BACKUP_FOLDER = "backup"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(BACKUP_FOLDER, exist_ok=True)

# ================================
# 🔄 LOAD & SIMPAN DATA
# ================================
def load_data():
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        # Convert kolom tanggal ke datetime dengan timezone lokal
        for col in ['Tanggal Upload Pertama', 'Tanggal Update Terakhir', 'Tanggal Selesai']:
            df[col] = pd.to_datetime(df[col], errors='coerce')
            # Kalau kolom datetime belum aware timezone, lokalize ke Asia/Jakarta
            df[col] = df[col].dt.tz_localize(None).dt.tz_localize(LOCAL_TZ)
        return df
    else:
        df = pd.DataFrame(columns=[
            'Nama Project', 'Status', 'Tanggal Upload Pertama',
            'Tanggal Update Terakhir', 'Tanggal Selesai', 'Selesai'
        ])
        df.to_csv(CSV_FILE, index=False)
        return df

def save_data(df):
    # Simpan kolom tanggal tanpa timezone (naik ke UTC dihapus agar csv clean)
    df_to_save = df.copy()
    for col in ['Tanggal Upload Pertama', 'Tanggal Update Terakhir', 'Tanggal Selesai']:
        df_to_save[col] = df_to_save[col].dt.tz_localize(None)
    df_to_save.to_csv(CSV_FILE, index=False)

    # Backup otomatis dengan timestamp waktu lokal
    backup_filename = f"backup_{now().strftime('%Y%m%d_%H%M%S')}.csv"
    df_to_save.to_csv(os.path.join(BACKUP_FOLDER, backup_filename), index=False)

# ================================
# 🚀 APLIKASI STREAMLIT
# ================================
st.title("📋 Manajemen Project")

df = load_data()

# ================================
# ➕ TAMBAH PROJECT BARU
# ================================
st.subheader("➕ Tambah Project Baru")
with st.form("form_tambah"):
    nama_baru = st.text_input("Nama Project Baru")
    submitted = st.form_submit_button("Tambah")
    if submitted:
        if nama_baru.strip() == "":
            st.warning("Nama project tidak boleh kosong.")
        elif nama_baru in df['Nama Project'].values:
            st.warning("Project sudah ada.")
        else:
            new_row = {
                'Nama Project': nama_baru,
                'Status': 'Belum Selesai',
                'Tanggal Upload Pertama': pd.NaT,
                'Tanggal Update Terakhir': pd.NaT,
                'Tanggal Selesai': pd.NaT,
                'Selesai': False
            }
            df.loc[len(df)] = new_row
            save_data(df)
            st.success(f"Project '{nama_baru}' berhasil ditambahkan. Silakan refresh halaman untuk melihat perubahan.")

# ================================
# 🔧 KELOLA PROJECT
# ================================
st.subheader("🔧 Kelola Project")

if not df.empty:
    selected_index = st.selectbox("Pilih Project", df.index, format_func=lambda i: df.at[i, 'Nama Project'])

    st.write(f"*Nama Project:* {df.at[selected_index, 'Nama Project']}")
    st.write(f"*Status:* {df.at[selected_index, 'Status']}")
    st.write(f"*Tanggal Upload Pertama:* {df.at[selected_index, 'Tanggal Upload Pertama']}")
    st.write(f"*Tanggal Update Terakhir:* {df.at[selected_index, 'Tanggal Update Terakhir']}")
    st.write(f"*Tanggal Selesai:* {df.at[selected_index, 'Tanggal Selesai']}")

    uploaded_files = st.file_uploader("Upload file (boleh lebih dari satu)", key=selected_index, accept_multiple_files=True)
    if uploaded_files:
        now_str = now().strftime("%Y-%m-%d %H:%M:%S")
        for file in uploaded_files:
            timestamp = now().strftime("%Y%m%d%H%M%S")
            filename = f"{df.at[selected_index, 'Nama Project']}__{timestamp}__{file.name}"
            filepath = os.path.join(UPLOAD_FOLDER, filename)

            if file.size > 0:
                with open(filepath, "wb") as f:
                    f.write(file.read())

        if pd.isna(df.at[selected_index, 'Tanggal Upload Pertama']):
            df.at[selected_index, 'Tanggal Upload Pertama'] = now()
        df.at[selected_index, 'Tanggal Update Terakhir'] = now()
        if not df.at[selected_index, 'Selesai']:
            df.at[selected_index, 'Status'] = 'Belum Selesai'

        save_data(df)
        st.success(f"{len(uploaded_files)} file berhasil diunggah dan disimpan.")

    if df.at[selected_index, 'Selesai']:
        st.checkbox("✅ Project Telah Selesai", value=True, disabled=True)
    else:
        if pd.isna(df.at[selected_index, 'Tanggal Upload Pertama']):
            st.info("🔒 Upload file terlebih dahulu sebelum menandai project sebagai selesai.")
        else:
            if st.checkbox("✔️ Tandai sebagai Selesai", key=f"selesai_{selected_index}"):
                now_dt = now()
                df.at[selected_index, 'Status'] = "Selesai"
                df.at[selected_index, 'Tanggal Selesai'] = now_dt
                df.at[selected_index, 'Tanggal Update Terakhir'] = now_dt
                df.at[selected_index, 'Selesai'] = True
                save_data(df)
                st.success("✅ Project ditandai sebagai selesai. Silakan refresh halaman untuk melihat perubahan.")

    if st.button("🗑 Hapus Project Ini"):
        hapus_nama = df.at[selected_index, 'Nama Project']
        df.drop(index=selected_index, inplace=True)
        df.reset_index(drop=True, inplace=True)
        save_data(df)
        st.success(f"Project '{hapus_nama}' berhasil dihapus.")
else:
    st.info("Belum ada project. Tambahkan project terlebih dahulu.")

# ================================
# 📦 CARI & DOWNLOAD FILE PROJECT
# ================================
st.subheader("🔍 Cari dan Unduh File Project")
search_file = st.text_input("Masukkan nama file atau project")

if search_file:
    matching_files = []
    for f in os.listdir(UPLOAD_FOLDER):
        if search_file.lower() in f.lower():
            matching_files.append(f)

    if matching_files:
        for file in matching_files:
            filepath = os.path.join(UPLOAD_FOLDER, file)
            nama_tampil = file.split("__", 2)[-1]
            if os.path.exists(filepath):
                with open(filepath, "rb") as f:
                    st.download_button(f"⬇️ {nama_tampil}", f, file_name=nama_tampil)
    else:
        st.warning("❌ Tidak ditemukan file dengan nama tersebut.")

st.caption("📌 Catatan: Semua file dan data akan tetap tersimpan selamanya, kecuali kamu menghapus project atau file secara manual.")

# ================================
# 📊 TABEL SEMUA PROJECT
# ================================
st.subheader("📊 Tabel Semua Project")
if df.empty:
    st.write("Belum ada data project.")
else:
    st.dataframe(df.drop(columns=["Selesai"]), use_container_width=True)

# ================================
# 📈 GRAFIK PROJECT PER HARI
# ================================
st.subheader("📈 Grafik Jumlah Project per Hari")

if not df.empty and df['Tanggal Upload Pertama'].notna().any():
    df_hari = df.dropna(subset=['Tanggal Upload Pertama']).copy()
    # Pastikan tanggal sudah timezone-aware
    df_hari['Tanggal'] = df_hari['Tanggal Upload Pertama'].dt.date

    project_per_day = df_hari.groupby('Tanggal').size().reset_index(name='Jumlah Project')
    project_per_day = project_per_day.sort_values('Tanggal')

    st.line_chart(data=project_per_day, x='Tanggal', y='Jumlah Project', use_container_width=True)
else:
    st.info("Belum ada data project dengan tanggal upload untuk ditampilkan dalam grafik.")

# ================================
# ✅ DAFTAR PROJECT SELESAI > 30 HARI
# ================================
st.subheader("📆 Project Selesai Lebih dari 30 Hari Lalu")
now_dt = now()

if not df.empty:
    df['Tanggal Selesai'] = pd.to_datetime(df['Tanggal Selesai'], errors='coerce')
    # Lokalize timezone jika belum aware
    df['Tanggal Selesai'] = df['Tanggal Selesai'].dt.tz_localize(None).dt.tz_localize(LOCAL_TZ)
    selesai_lama = df[(df['Selesai']) & (df['Tanggal Selesai'].notna()) & ((now_dt - df['Tanggal Selesai']).dt.days > 30)]
    if not selesai_lama.empty:
        st.dataframe(selesai_lama[['Nama Project', 'Tanggal Selesai']], use_container_width=True)
    else:
        st.info("Tidak ada project yang selesai lebih dari 30 hari lalu.")




