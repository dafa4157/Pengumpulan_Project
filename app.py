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

# Fungsi bantu: Format tanggal & jam
def format_datetime(value):
    try:
        return pd.to_datetime(value).strftime("%Y-%m-%d %H:%M:%S")
    except:
        return "-"

# =============================
# 🔄 LOAD & SIMPAN DATA
# =============================
def load_data():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE, dtype={'Selesai': bool})
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
                'Tanggal Upload Pertama': '',
                'Tanggal Update Terakhir': '',
                'Tanggal Selesai': '',
                'Selesai': False
            }
            df.loc[len(df)] = new_row
            save_data(df)
            st.success(f"Project '{nama_baru}' berhasil ditambahkan. Silakan refresh halaman untuk melihat perubahan.")

# =============================
# 🔧 KELOLA PROJECT
# =============================
st.subheader("🔧 Kelola Project")

if not df.empty:
    selected_index = st.selectbox("Pilih Project", df.index, format_func=lambda i: df.at[i, 'Nama Project'])

    st.write(f"*Nama Project:* {df.at[selected_index, 'Nama Project']}")
    st.write(f"*Status:* {df.at[selected_index, 'Status']}")
    st.write(f"*Tanggal Upload Pertama:* {format_datetime(df.at[selected_index, 'Tanggal Upload Pertama'])}")
    st.write(f"*Tanggal Update Terakhir:* {format_datetime(df.at[selected_index, 'Tanggal Update Terakhir'])}")
    st.write(f"*Tanggal Selesai:* {format_datetime(df.at[selected_index, 'Tanggal Selesai'])}")

    uploaded_files = st.file_uploader("Upload file (boleh lebih dari satu)", key=selected_index, accept_multiple_files=True)
    if uploaded_files:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for file in uploaded_files:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"{df.at[selected_index, 'Nama Project']}__{timestamp}__{file.name}"
            filepath = os.path.join(UPLOAD_FOLDER, filename)

            with open(filepath, "wb") as f:
                f.write(file.read())

        if not df.at[selected_index, 'Tanggal Upload Pertama']:
            df.at[selected_index, 'Tanggal Upload Pertama'] = now
        df.at[selected_index, 'Tanggal Update Terakhir'] = now
        if not df.at[selected_index, 'Selesai']:
            df.at[selected_index, 'Status'] = 'Belum Selesai'

        save_data(df)
        st.success(f"{len(uploaded_files)} file berhasil diunggah dan disimpan.")

    if df.at[selected_index, 'Selesai']:
        st.checkbox("✅ Project Telah Selesai", value=True, disabled=True)
    else:
        if not df.at[selected_index, 'Tanggal Upload Pertama']:
            st.info("🔒 Upload file terlebih dahulu sebelum menandai project sebagai selesai.")
        else:
            if st.checkbox("✔️ Tandai sebagai Selesai", key=f"selesai_{selected_index}"):
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                df.at[selected_index, 'Status'] = "Selesai"
                df.at[selected_index, 'Tanggal Selesai'] = now
                df.at[selected_index, 'Tanggal Update Terakhir'] = now
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

# =============================
# 📦 CARI & DOWNLOAD FILE PROJECT
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
        st.warning("❌ Tidak ditemukan file dengan nama tersebut.")

# =============================
# 📊 TABEL SEMUA PROJECT
# =============================
st.subheader("📊 Tabel Semua Project")
if df.empty:
    st.write("Belum ada data project.")
else:
    df_tampil = df.copy()
    df_tampil['Tanggal Upload Pertama'] = df_tampil['Tanggal Upload Pertama'].apply(format_datetime)
    df_tampil['Tanggal Update Terakhir'] = df_tampil['Tanggal Update Terakhir'].apply(format_datetime)
    df_tampil['Tanggal Selesai'] = df_tampil['Tanggal Selesai'].apply(format_datetime)
    st.dataframe(df_tampil.drop(columns=["Selesai"]), use_container_width=True)

# =============================
# 📈 GRAFIK PROJECT PER HARI
# =============================
st.subheader("📈 Grafik Jumlah Project per Hari")

if not df.empty and df['Tanggal Upload Pertama'].notna().any():
    df_grafik = df.copy()
    df_grafik['Tanggal Upload Pertama'] = pd.to_datetime(df_grafik['Tanggal Upload Pertama'], errors='coerce')
    df_grafik = df_grafik.dropna(subset=['Tanggal Upload Pertama'])
    df_grafik['Tanggal'] = df_grafik['Tanggal Upload Pertama'].dt.date

    project_per_day = df_grafik.groupby('Tanggal').size().reset_index(name='Jumlah Project')
    st.line_chart(project_per_day, x='Tanggal', y='Jumlah Project', use_container_width=True)
else:
    st.info("Belum ada data project dengan tanggal upload untuk ditampilkan dalam grafik.")

# =============================
# ✅ DAFTAR PROJECT SELESAI > 30 HARI
# =============================
st.subheader("📆 Project Selesai Lebih dari 30 Hari Lalu")
now = datetime.now()
if not df.empty:
    df['Tanggal Selesai'] = pd.to_datetime(df['Tanggal Selesai'], errors='coerce')
    selesai_lama = df[(df['Selesai']) & (df['Tanggal Selesai'].notna()) & ((now - df['Tanggal Selesai']).dt.days > 30)]
    if not selesai_lama.empty:
        df_selesai = selesai_lama[['Nama Project', 'Tanggal Selesai']].copy()
        df_selesai['Tanggal Selesai'] = df_selesai['Tanggal Selesai'].dt.strftime("%Y-%m-%d %H:%M:%S")
        st.dataframe(df_selesai, use_container_width=True)
    else:
        st.info("Tidak ada project yang selesai lebih dari 30 hari lalu.")






