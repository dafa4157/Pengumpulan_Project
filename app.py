import streamlit as st
import pandas as pd
from datetime import datetime
import os

CSV_FILE = "data_project.csv"
UPLOAD_FOLDER = "uploads"
BACKUP_FOLDER = "backup"

# Buat folder upload & backup jika belum ada
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(BACKUP_FOLDER, exist_ok=True)

# =============================
# 🔄 LOAD & SIMPAN DATA
# =============================
def load_data():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE, parse_dates=[
            'Tanggal Upload Pertama',
            'Tanggal Update Terakhir',
            'Tanggal Selesai'
        ])
    else:
        df = pd.DataFrame(columns=[
            'Nama Project', 'Status', 'Tanggal Upload Pertama',
            'Tanggal Update Terakhir', 'Tanggal Selesai', 'Selesai'
        ])
        df.to_csv(CSV_FILE, index=False)
        return df

def save_data(df):
    df.to_csv(CSV_FILE, index=False, date_format="%Y-%m-%d %H:%M:%S")
    backup_filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(os.path.join(BACKUP_FOLDER, backup_filename), index=False, date_format="%Y-%m-%d %H:%M:%S")

# =============================
# 🚀 APLIKASI STREAMLIT
# =============================
st.title("📋 Manajemen Project")

df = load_data()

# =============================
# ➕ TAMBAH PROJECT BARU
# =============================
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
            st.success(f"Project '{nama_baru}' berhasil ditambahkan. Silakan refresh halaman.")

# =============================
# 🔧 KELOLA PROJECT
# =============================
st.subheader("🔧 Kelola Project")

if not df.empty:
    selected_index = st.selectbox("Pilih Project", df.index, format_func=lambda i: df.at[i, 'Nama Project'])

    def tampilkan_waktu(label, waktu):
        if pd.notna(waktu):
            st.write(f"*{label}:* {waktu.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            st.write(f"*{label}:* -")

    st.write(f"*Nama Project:* {df.at[selected_index, 'Nama Project']}")
    st.write(f"*Status:* {df.at[selected_index, 'Status']}")
    tampilkan_waktu("Tanggal Upload Pertama", df.at[selected_index, 'Tanggal Upload Pertama'])
    tampilkan_waktu("Tanggal Update Terakhir", df.at[selected_index, 'Tanggal Update Terakhir'])
    tampilkan_waktu("Tanggal Selesai", df.at[selected_index, 'Tanggal Selesai'])

    uploaded_files = st.file_uploader("Upload file", key=selected_index, accept_multiple_files=True)
    if uploaded_files:
        now = datetime.now()
        for file in uploaded_files:
            timestamp = now.strftime("%Y%m%d%H%M%S")
            filename = f"{df.at[selected_index, 'Nama Project']}__{timestamp}__{file.name}"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            with open(filepath, "wb") as f:
                f.write(file.read())

        if pd.isna(df.at[selected_index, 'Tanggal Upload Pertama']):
            df.at[selected_index, 'Tanggal Upload Pertama'] = now
        df.at[selected_index, 'Tanggal Update Terakhir'] = now

        if not df.at[selected_index, 'Selesai']:
            df.at[selected_index, 'Status'] = 'Belum Selesai'

        save_data(df)
        st.success(f"{len(uploaded_files)} file berhasil diunggah.")

    if df.at[selected_index, 'Selesai']:
        st.checkbox("✅ Project Telah Selesai", value=True, disabled=True)
    else:
        if pd.isna(df.at[selected_index, 'Tanggal Upload Pertama']):
            st.info("🔒 Upload file terlebih dahulu sebelum tandai selesai.")
        else:
            if st.checkbox("✔️ Tandai sebagai Selesai", key=f"selesai_{selected_index}"):
                now = datetime.now()
                df.at[selected_index, 'Status'] = "Selesai"
                df.at[selected_index, 'Tanggal Selesai'] = now
                df.at[selected_index, 'Tanggal Update Terakhir'] = now
                df.at[selected_index, 'Selesai'] = True
                save_data(df)
                st.success("✅ Project ditandai sebagai selesai. Silakan refresh.")

    if st.button("🗑 Hapus Project Ini"):
        hapus_nama = df.at[selected_index, 'Nama Project']
        df.drop(index=selected_index, inplace=True)
        df.reset_index(drop=True, inplace=True)
        save_data(df)
        st.success(f"Project '{hapus_nama}' dihapus.")
else:
    st.info("Belum ada project.")

# =============================
# 📦 CARI & DOWNLOAD FILE
# =============================
st.subheader("🔍 Cari dan Unduh File Project")
search_file = st.text_input("Masukkan nama file atau project")

if search_file:
    matching_files = [f for f in os.listdir(UPLOAD_FOLDER) if search_file.lower() in f.lower()]
    if matching_files:
        for file in matching_files:
            filepath = os.path.join(UPLOAD_FOLDER, file)
            nama_tampil = file.split("__", 2)[-1]
            with open(filepath, "rb") as f:
                st.download_button(f"⬇️ {nama_tampil}", f, file_name=nama_tampil)
    else:
        st.warning("❌ Tidak ada file yang cocok.")

# =============================
# 📊 TABEL PROJECT
# =============================
st.subheader("📊 Tabel Semua Project")
if df.empty:
    st.write("Belum ada data project.")
else:
    tampil_df = df.copy()
    tampil_df['Tanggal Upload Pertama'] = tampil_df['Tanggal Upload Pertama'].dt.strftime("%Y-%m-%d %H:%M:%S")
    tampil_df['Tanggal Update Terakhir'] = tampil_df['Tanggal Update Terakhir'].dt.strftime("%Y-%m-%d %H:%M:%S")
    tampil_df['Tanggal Selesai'] = tampil_df['Tanggal Selesai'].dt.strftime("%Y-%m-%d %H:%M:%S")
    st.dataframe(tampil_df.drop(columns=["Selesai"]), use_container_width=True)

# =============================
# 📈 GRAFIK PROJECT PER HARI
# =============================
st.subheader("📈 Grafik Jumlah Project per Hari")
if not df.empty and df['Tanggal Upload Pertama'].notna().any():
    df_hari = df.dropna(subset=['Tanggal Upload Pertama']).copy()
    df_hari['Tanggal'] = df_hari['Tanggal Upload Pertama'].dt.date
    project_per_day = df_hari.groupby('Tanggal').size().reset_index(name='Jumlah Project')
    project_per_day = project_per_day.sort_values('Tanggal')
    st.line_chart(data=project_per_day, x='Tanggal', y='Jumlah Project', use_container_width=True)
else:
    st.info("Belum ada data project dengan tanggal upload.")

# =============================
# ✅ PROJECT SELESAI > 30 HARI
# =============================
st.subheader("📆 Project Selesai Lebih dari 30 Hari Lalu")
now = datetime.now()
if not df.empty:
    df['Tanggal Selesai'] = pd.to_datetime(df['Tanggal Selesai'], errors='coerce')
    selesai_lama = df[
        (df['Selesai']) & 
        (df['Tanggal Selesai'].notna()) & 
        ((now - df['Tanggal Selesai']).dt.days > 30)
    ]
    if not selesai_lama.empty:
        tampil = selesai_lama[['Nama Project', 'Tanggal Selesai']].copy()
        tampil['Tanggal Selesai'] = tampil['Tanggal Selesai'].dt.strftime("%Y-%m-%d %H:%M:%S")
        st.dataframe(tampil, use_container_width=True)
    else:
        st.info("Tidak ada project yang selesai lebih dari 30 hari lalu.")

st.caption("📌 Catatan: Semua file dan data disimpan permanen kecuali dihapus manual.")







