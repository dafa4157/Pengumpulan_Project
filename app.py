import streamlit as st
import pandas as pd
from datetime import datetime
import os
import pytz

CSV_FILE = "data_project.csv"
UPLOAD_FOLDER = "uploads"

# Buat folder upload kalau belum ada
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# =============================
# 🔄 LOAD & SIMPAN DATA
# =============================
def load_data():
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        # Parsing kolom waktu jadi datetime dengan timezone lokal Asia/Jakarta
        for col in ['Tanggal Upload Pertama', 'Tanggal Update Terakhir', 'Tanggal Selesai']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        return df
    else:
        df = pd.DataFrame(columns=[
            'Nama Project', 'Status', 'Tanggal Upload Pertama',
            'Tanggal Update Terakhir', 'Tanggal Selesai', 'Selesai'
        ])
        df.to_csv(CSV_FILE, index=False)
        return df

def save_data(df):
    df_copy = df.copy()
    for col in ['Tanggal Upload Pertama', 'Tanggal Update Terakhir', 'Tanggal Selesai']:
        if col in df_copy.columns:
            df_copy[col] = df_copy[col].apply(lambda x: x.isoformat() if pd.notnull(x) else None)
    df_copy.to_csv(CSV_FILE, index=False)

# =============================
# Format waktu untuk ditampilkan
def format_datetime_local(dt):
    if pd.isna(dt):
        return "-"
    return dt.strftime("%Y-%m-%d %H:%M:%S")

# =============================
# 🚀 APLIKASI STREAMLIT
# =============================
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

# =============================
# 🔧 KELOLA PROJECT
# =============================
st.subheader("🔧 Kelola Project")

if not df.empty:
    selected_index = st.selectbox("Pilih Project", df.index, format_func=lambda i: df.at[i, 'Nama Project'])

    st.write(f"*Nama Project:* {df.at[selected_index, 'Nama Project']}")
    st.write(f"*Status:* {df.at[selected_index, 'Status']}")
    st.write(f"*Tanggal Upload Pertama:* {format_datetime_local(df.at[selected_index, 'Tanggal Upload Pertama'])}")
    st.write(f"*Tanggal Update Terakhir:* {format_datetime_local(df.at[selected_index, 'Tanggal Update Terakhir'])}")
    st.write(f"*Tanggal Selesai:* {format_datetime_local(df.at[selected_index, 'Tanggal Selesai'])}")

    uploaded_files = st.file_uploader("Upload file (boleh lebih dari satu)", key=selected_index, accept_multiple_files=True)
    if uploaded_files:
        now = datetime.now(pytz.timezone('Asia/Jakarta'))  # waktu lokal Asia/Jakarta saat upload
        for file in uploaded_files:
            filename = f"{df.at[selected_index, 'Nama Project']}__{file.name}"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            with open(filepath, "wb") as f:
                f.write(file.read())

        if pd.isna(df.at[selected_index, 'Tanggal Upload Pertama']) or df.at[selected_index, 'Tanggal Upload Pertama'] in ['None', 'nan']:
            df.at[selected_index, 'Tanggal Upload Pertama'] = now
        df.at[selected_index, 'Tanggal Update Terakhir'] = now
        if not df.at[selected_index, 'Selesai']:
            df.at[selected_index, 'Status'] = 'Belum Selesai'

        save_data(df)
        st.success(f"{len(uploaded_files)} file berhasil diunggah dan disimpan.")

    if df.at[selected_index, 'Selesai']:
        st.checkbox("✅ Project Telah Selesai", value=True, disabled=True)
    else:
        if df.at[selected_index, 'Tanggal Upload Pertama'] in [None, 'None', 'nan'] or pd.isna(df.at[selected_index, 'Tanggal Upload Pertama']):
            st.info("🔒 Upload file terlebih dahulu sebelum menandai project sebagai selesai.")
        else:
            if st.checkbox("✔️ Tandai sebagai Selesai", key=f"selesai_{selected_index}"):
                now = datetime.now(pytz.timezone('Asia/Jakarta'))
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
# 📦 CARI & DOWNLOAD FILE PROJECT + HAPUS FILE
# =============================
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
            nama_tampil = file.split("__", 1)[-1]
            col1, col2 = st.columns([3,1])
            with col1:
                with open(filepath, "rb") as f:
                    st.download_button(f"⬇️ {nama_tampil}", f, file_name=nama_tampil)
            with col2:
                if st.button(f"🗑 Hapus", key=f"hapus_{file}"):
                    try:
                        os.remove(filepath)
                        st.success(f"File '{nama_tampil}' berhasil dihapus.")
                    except Exception as e:
                        st.error(f"Gagal menghapus file: {e}")
    else:
        st.warning("❌ Tidak ditemukan file dengan nama tersebut.")

# =============================
# 📊 TABEL SEMUA PROJECT
# =============================
st.subheader("📊 Tabel Semua Project")
if df.empty:
    st.write("Belum ada data project.")
else:
    st.dataframe(df.drop(columns=["Selesai"]), use_container_width=True)

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
    st.info("Belum ada data project dengan tanggal upload untuk ditampilkan dalam grafik.")

# =============================
# ✅ DAFTAR PROJECT SELESAI > 30 HARI
# =============================
st.subheader("📆 Project Selesai Lebih dari 30 Hari Lalu")
now = datetime.now(pytz.timezone('Asia/Jakarta'))
if not df.empty:
    df['Tanggal Selesai'] = pd.to_datetime(df['Tanggal Selesai'], errors='coerce')
    selesai_lama = df[(df['Selesai']) & (df['Tanggal Selesai'].notna()) & ((now - df['Tanggal Selesai']).dt.days > 30)]
    if not selesai_lama.empty:
        st.dataframe(selesai_lama[['Nama Project', 'Tanggal Selesai']], use_container_width=True)
    else:
        st.info("Tidak ada project yang selesai lebih dari 30 hari lalu.")







