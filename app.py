import streamlit as st
import pandas as pd
from datetime import datetime
import os

CSV_FILE = "data_project.csv"
UPLOAD_FOLDER = "uploads"
BACKUP_FOLDER = "backup"

# Buat folder jika belum ada
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(BACKUP_FOLDER, exist_ok=True)

# ================================
# 🔄 Load dan Simpan Data
# ================================
def load_data():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    else:
        df = pd.DataFrame(columns=[
            'Nama Project', 'Status', 'Tanggal Upload Pertama',
            'Tanggal Update Terakhir', 'Tanggal Selesai', 'Selesai'
        ])
        df.to_csv(CSV_FILE, index=False)
        return df

def save_data(df):
    df.to_csv(CSV_FILE, index=False)
    backup_filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(os.path.join(BACKUP_FOLDER, backup_filename), index=False)

# ================================
# 🚀 Aplikasi Streamlit
# ================================
st.title("📋 Manajemen Project")

df = load_data()

# ================================
# ➕ Tambah Project Baru
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
                'Tanggal Upload Pertama': None,
                'Tanggal Update Terakhir': None,
                'Tanggal Selesai': None,
                'Selesai': False
            }
            df.loc[len(df)] = new_row
            save_data(df)
            st.success(f"Project '{nama_baru}' berhasil ditambahkan. Silakan refresh halaman.")

# ================================
# 🔧 Kelola Project
# ================================
st.subheader("🔧 Kelola Project")

if not df.empty:
    selected_index = st.selectbox("Pilih Project", df.index, format_func=lambda i: df.at[i, 'Nama Project'])

    st.write(f"*Nama Project:* {df.at[selected_index, 'Nama Project']}")
    st.write(f"*Status:* {df.at[selected_index, 'Status']}")
    st.write(f"*Tanggal Upload Pertama:* {df.at[selected_index, 'Tanggal Upload Pertama']}")
    st.write(f"*Tanggal Update Terakhir:* {df.at[selected_index, 'Tanggal Update Terakhir']}")
    st.write(f"*Tanggal Selesai:* {df.at[selected_index, 'Tanggal Selesai']}")

    uploaded_files = st.file_uploader("Upload file (boleh lebih dari satu)", key=f"uploader_{selected_index}", accept_multiple_files=True)
    if uploaded_files:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for file in uploaded_files:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"{df.at[selected_index, 'Nama Project']}__{timestamp}__{file.name}"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            if file.size > 0:
                with open(filepath, "wb") as f:
                    f.write(file.read())

        if pd.isna(df.at[selected_index, 'Tanggal Upload Pertama']) or df.at[selected_index, 'Tanggal Upload Pertama'] in [None, 'None', 'nan']:
            df.at[selected_index, 'Tanggal Upload Pertama'] = now
        df.at[selected_index, 'Tanggal Update Terakhir'] = now
        if not df.at[selected_index, 'Selesai']:
            df.at[selected_index, 'Status'] = 'Belum Selesai'
        save_data(df)
        st.success(f"{len(uploaded_files)} file berhasil diunggah.")

    if df.at[selected_index, 'Selesai']:
        st.checkbox("✅ Project Telah Selesai", value=True, disabled=True)
    else:
        if df.at[selected_index, 'Tanggal Upload Pertama'] in [None, 'None', 'nan', pd.NaT] or pd.isna(df.at[selected_index, 'Tanggal Upload Pertama']):
            st.info("🔒 Upload file terlebih dahulu sebelum menandai project sebagai selesai.")
        else:
            if st.checkbox("✔️ Tandai sebagai Selesai", key=f"selesai_{selected_index}"):
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                df.at[selected_index, 'Status'] = "Selesai"
                df.at[selected_index, 'Tanggal Selesai'] = now
                df.at[selected_index, 'Tanggal Update Terakhir'] = now
                df.at[selected_index, 'Selesai'] = True
                save_data(df)
                st.success("✅ Project ditandai selesai. Silakan refresh halaman.")

    if st.button("🗑 Hapus Project Ini", key=f"hapus_{selected_index}"):
        hapus_nama = df.at[selected_index, 'Nama Project']
        df.drop(index=selected_index, inplace=True)
        df.reset_index(drop=True, inplace=True)
        save_data(df)
        st.success(f"Project '{hapus_nama}' berhasil dihapus.")
else:
    st.info("Belum ada project. Tambahkan terlebih dahulu.")

# ================================
# 📦 Cari & Download File Project
# ================================
st.subheader("🔍 Cari dan Unduh File Project")
search_file = st.text_input("Masukkan nama file atau project")

if search_file:
    matching_files = []
    for i, f in enumerate(os.listdir(UPLOAD_FOLDER)):
        if search_file.lower() in f.lower():
            matching_files.append((i, f))

    if matching_files:
        for i, file in matching_files:
            filepath = os.path.join(UPLOAD_FOLDER, file)
            nama_tampil = file.split("__", 2)[-1]
            if os.path.exists(filepath):
                with open(filepath, "rb") as f:
                    st.download_button(f"⬇️ {nama_tampil}", f, file_name=nama_tampil, key=f"download_{i}")
    else:
        st.warning("❌ Tidak ditemukan file dengan nama tersebut.")

# ================================
# 📊 Tabel Semua Project
# ================================
st.subheader("📊 Tabel Semua Project")
if df.empty:
    st.write("Belum ada data project.")
else:
    st.dataframe(df.drop(columns=["Selesai"]), use_container_width=True)

# ================================
# 📈 Grafik Jumlah Project per Hari
# ================================
st.subheader("📈 Grafik Jumlah Project per Hari")
if not df.empty and df['Tanggal Upload Pertama'].notna().any():
    df['Tanggal Upload Pertama'] = pd.to_datetime(df['Tanggal Upload Pertama'], errors='coerce')
    df_hari = df.dropna(subset=['Tanggal Upload Pertama']).copy()
    df_hari['Tanggal'] = df_hari['Tanggal Upload Pertama'].dt.date
    project_per_day = df_hari.groupby('Tanggal').size().reset_index(name='Jumlah Project')
    st.line_chart(data=project_per_day, x='Tanggal', y='Jumlah Project', use_container_width=True)
else:
    st.info("Belum ada data upload project untuk grafik.")

# ================================
# ✅ Project Selesai > 30 Hari
# ================================
st.subheader("📆 Project Selesai Lebih dari 30 Hari Lalu")
now = datetime.now()
if not df.empty:
    df['Tanggal Selesai'] = pd.to_datetime(df['Tanggal Selesai'], errors='coerce')
    selesai_lama = df[(df['Selesai']) & (df['Tanggal Selesai'].notna()) & ((now - df['Tanggal Selesai']).dt.days > 30)]
    if not selesai_lama.empty:
        st.dataframe(selesai_lama[['Nama Project', 'Tanggal Selesai']], use_container_width=True)
    else:
        st.info("Tidak ada project yang selesai lebih dari 30 hari lalu.")

st.caption("📌 Catatan: Semua file dan data akan tetap tersimpan selamanya, kecuali kamu menghapus project atau file secara manual.")







