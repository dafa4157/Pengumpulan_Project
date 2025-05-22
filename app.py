# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ====================
# Konstanta
# ====================
CSV_FILE = "data_project.csv"
UPLOAD_FOLDER = "uploads"
BACKUP_FOLDER = "backup"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(BACKUP_FOLDER, exist_ok=True)

# ====================
# Load & Save Data
# ====================
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
    backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(os.path.join(BACKUP_FOLDER, backup_name), index=False)

# ====================
# Tampilan Aplikasi
# ====================
st.set_page_config(page_title="Manajemen Proyek", layout="wide")
st.title("📋 Manajemen Project")

df = load_data()

# ====================
# Tambah Project Baru
# ====================
st.subheader("➕ Tambah Project Baru")
with st.form("form_tambah"):
    nama_baru = st.text_input("Nama Project Baru")
    submit_tambah = st.form_submit_button("Tambah")
    if submit_tambah:
        if nama_baru.strip() == "":
            st.warning("⚠️ Nama project tidak boleh kosong.")
        elif nama_baru in df['Nama Project'].values:
            st.warning("⚠️ Project sudah ada.")
        else:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            df.loc[len(df)] = {
                'Nama Project': nama_baru,
                'Status': 'Belum Selesai',
                'Tanggal Upload Pertama': None,
                'Tanggal Update Terakhir': None,
                'Tanggal Selesai': None,
                'Selesai': False
            }
            save_data(df)
            st.success(f"✅ Project '{nama_baru}' berhasil ditambahkan. Silakan refresh halaman.")
# ====================
# Kelola Project
# ====================
st.subheader("🔧 Kelola Project")

if not df.empty:
    selected_index = st.selectbox("Pilih Project", df.index, format_func=lambda i: df.at[i, 'Nama Project'])

    project = df.loc[selected_index]
    st.write(f"**Nama:** {project['Nama Project']}")
    st.write(f"**Status:** {project['Status']}")
    st.write(f"**Upload Pertama:** {project['Tanggal Upload Pertama']}")
    st.write(f"**Update Terakhir:** {project['Tanggal Update Terakhir']}")
    st.write(f"**Tanggal Selesai:** {project['Tanggal Selesai']}")

    uploaded_files = st.file_uploader("Upload file", key=f"upload_{selected_index}", accept_multiple_files=True)

    if uploaded_files:
        any_uploaded = False
        for file in uploaded_files:
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ts = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"{project['Nama Project']}__{ts}__{file.name}"
            path = os.path.join(UPLOAD_FOLDER, filename)
            with open(path, "wb") as f:
                f.write(file.read())
            any_uploaded = True

        if any_uploaded:
            if pd.isna(project['Tanggal Upload Pertama']) or str(project['Tanggal Upload Pertama']).strip().lower() in ['none', 'nan', '']:
                df.at[selected_index, 'Tanggal Upload Pertama'] = now_str

            df.at[selected_index, 'Tanggal Update Terakhir'] = now_str

            if not project['Selesai']:
                df.at[selected_index, 'Status'] = "Belum Selesai"

            save_data(df)
            st.success(f"✅ {len(uploaded_files)} file berhasil diunggah.")

    # Checkbox selesai
    if project['Selesai']:
        st.checkbox("✅ Project Telah Selesai", value=True, disabled=True)
    else:
        boleh_selesai = df.at[selected_index, 'Tanggal Upload Pertama'] not in [None, 'None', 'nan', '']
        if not boleh_selesai:
            st.info("📥 Upload file terlebih dahulu sebelum menandai selesai.")
        else:
            if st.checkbox("✔️ Tandai sebagai selesai", key=f"selesai_{selected_index}"):
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                df.at[selected_index, 'Status'] = "Selesai"
                df.at[selected_index, 'Tanggal Selesai'] = now_str
                df.at[selected_index, 'Tanggal Update Terakhir'] = now_str
                df.at[selected_index, 'Selesai'] = True
                save_data(df)
                st.success("✅ Project ditandai sebagai selesai.")

    if st.button("🗑 Hapus Project Ini", key=f"hapus_{selected_index}"):
        nama = df.at[selected_index, 'Nama Project']
        df.drop(index=selected_index, inplace=True)
        df.reset_index(drop=True, inplace=True)
        save_data(df)
        st.success(f"🗑 Project '{nama}' dihapus.")

else:
    st.info("Belum ada project yang ditambahkan.")


   

# ====================
# Cari & Download File
# ====================
st.subheader("🔍 Cari dan Unduh File Project")
search_term = st.text_input("Masukkan nama file atau project")
if search_term:
    files = [f for f in os.listdir(UPLOAD_FOLDER) if search_term.lower() in f.lower()]
    if files:
        for i, file in enumerate(files):
            filepath = os.path.join(UPLOAD_FOLDER, file)
            filename_display = file.split("__", 2)[-1]
            with open(filepath, "rb") as f:
                st.download_button(f"⬇️ {filename_display}", f, file_name=filename_display, key=f"dl_{i}")
    else:
        st.warning("❌ File tidak ditemukan.")

# ====================
# Hapus File Project
# ====================
st.subheader("🗑 Hapus File Project")
hapus_term = st.text_input("Masukkan nama file yang ingin dihapus", key="hapus_file")

if hapus_term:
    files_to_delete = [f for f in os.listdir(UPLOAD_FOLDER) if hapus_term.lower() in f.lower()]
    
    if files_to_delete:
        st.write(f"File yang cocok dengan '{hapus_term}':")
        for i, file in enumerate(files_to_delete):
            filepath = os.path.join(UPLOAD_FOLDER, file)
            filename_display = file.split("__", 2)[-1]
            col1, col2 = st.columns([8, 1])
            with col1:
                st.write(filename_display)
            with col2:
                if st.button("Hapus", key=f"hapus_file_{i}"):
                    try:
                        os.remove(filepath)
                        st.success(f"File '{filename_display}' berhasil dihapus.")
                    except Exception as e:
                        st.error(f"Gagal menghapus file: {e}")
    else:
        st.info("Tidak ditemukan file dengan nama tersebut.")

# ====================
# Tabel Semua Project
# ====================
st.subheader("📊 Tabel Semua Project")
if df.empty:
    st.write("Tidak ada data.")
else:
    df_tampil = df.copy()
    df_tampil['Tanggal Upload Pertama'] = df_tampil['Tanggal Upload Pertama'].fillna("-")
    df_tampil['Tanggal Update Terakhir'] = df_tampil['Tanggal Update Terakhir'].fillna("-")
    df_tampil['Tanggal Selesai'] = df_tampil['Tanggal Selesai'].fillna("-")
    st.dataframe(df_tampil.drop(columns=["Selesai"]), use_container_width=True)

# ====================
# Grafik Jumlah Project per Hari
# ====================
st.subheader("📈 Grafik Jumlah Project per Hari")
if df['Tanggal Upload Pertama'].notna().any():
    df['Tanggal Upload Pertama'] = pd.to_datetime(df['Tanggal Upload Pertama'], errors='coerce')
    df_hari = df.dropna(subset=['Tanggal Upload Pertama'])
    df_hari['Tanggal'] = df_hari['Tanggal Upload Pertama'].dt.date
    chart_data = df_hari.groupby('Tanggal').size().reset_index(name='Jumlah Project')
    st.line_chart(chart_data, x='Tanggal', y='Jumlah Project', use_container_width=True)
else:
    st.info("Tidak ada data tanggal upload untuk ditampilkan.")

# ====================
# Project Selesai > 30 Hari
# ====================
st.subheader("📆 Project Selesai Lebih dari 30 Hari")
df['Tanggal Selesai'] = pd.to_datetime(df['Tanggal Selesai'], errors='coerce')
overdue = df[(df['Selesai']) & (df['Tanggal Selesai'].notna()) & ((datetime.now() - df['Tanggal Selesai']).dt.days > 30)]

if not overdue.empty:
    st.dataframe(overdue[['Nama Project', 'Tanggal Selesai']], use_container_width=True)
else:
    st.info("✅ Tidak ada project selesai lebih dari 30 hari lalu.")

st.caption("📌 Catatan: File akan tersimpan otomatis. Hapus manual bila perlu.")









