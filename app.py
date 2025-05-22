import streamlit as st
import pandas as pd
from datetime import datetime
import os
import pytz

# Konstanta
CSV_FILE = "data_project.csv"
UPLOAD_FOLDER = "uploads"
LOCAL_TZ = pytz.timezone("Asia/Jakarta")

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def load_data():
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        return df
    else:
        df = pd.DataFrame(columns=[
            'Nama Project', 'Status', 'Tanggal Upload Pertama',
            'Tanggal Update Terakhir', 'Tanggal Selesai', 'Selesai'
        ])
        df.to_csv(CSV_FILE, index=False)
        return df

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

def hapus_file_project(nama_project):
    nama_project_lower = nama_project.lower()
    files_dihapus = []
    for f in os.listdir(UPLOAD_FOLDER):
        if f.lower().startswith(f"{nama_project_lower}__"):
            filepath = os.path.join(UPLOAD_FOLDER, f)
            try:
                os.remove(filepath)
                files_dihapus.append(f)
            except Exception as e:
                st.error(f"Gagal menghapus file '{f}': {e}")
    return files_dihapus

def now_str():
    return datetime.now(LOCAL_TZ).strftime("%Y-%m-%d %H:%M:%S")

def convert_to_datetime(df, col):
    df[col] = pd.to_datetime(df[col], errors='coerce')
    return df

df = load_data()

st.title("📋 Manajemen Project")

# Inisialisasi session state untuk hapus project
if "hapus_dipicu" not in st.session_state:
    st.session_state.hapus_dipicu = False
if "project_hapus" not in st.session_state:
    st.session_state.project_hapus = None
if "index_hapus" not in st.session_state:
    st.session_state.index_hapus = None

# Subheader Kelola Project
st.subheader("🔧 Kelola Project")

if not df.empty:
    selected_index = st.selectbox("Pilih Project", df.index, format_func=lambda i: df.at[i, 'Nama Project'])

    st.write(f"**Nama Project:** {df.at[selected_index, 'Nama Project']}")
    st.write(f"**Status:** {df.at[selected_index, 'Status']}")
    st.write(f"**Tanggal Upload Pertama:** {df.at[selected_index, 'Tanggal Upload Pertama']}")
    st.write(f"**Tanggal Update Terakhir:** {df.at[selected_index, 'Tanggal Update Terakhir']}")
    st.write(f"**Tanggal Selesai:** {df.at[selected_index, 'Tanggal Selesai']}")

    uploaded_files = st.file_uploader("Upload file (boleh lebih dari satu)", key=selected_index, accept_multiple_files=True)
    if uploaded_files:
        nama_project = df.at[selected_index, 'Nama Project']

        duplicate_files = []
        files_to_upload = []
        for file in uploaded_files:
            filename = f"{nama_project}__{file.name}"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.exists(filepath):
                duplicate_files.append(file.name)
            else:
                files_to_upload.append((filename, file))

        if duplicate_files:
            st.error(f"❌ File berikut sudah ada dan tidak diunggah ulang:\n\n{', '.join(duplicate_files)}")

        if files_to_upload:
            now = now_str()
            for filename, file in files_to_upload:
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                with open(filepath, "wb") as f:
                    f.write(file.read())

            if pd.isna(df.at[selected_index, 'Tanggal Upload Pertama']) or df.at[selected_index, 'Tanggal Upload Pertama'] in [None, 'None', 'nan']:
                df.at[selected_index, 'Tanggal Upload Pertama'] = now
            df.at[selected_index, 'Tanggal Update Terakhir'] = now
            if not df.at[selected_index, 'Selesai']:
                df.at[selected_index, 'Status'] = 'Belum Selesai'

            save_data(df)
            st.success(f"{len(files_to_upload)} file berhasil diunggah dan disimpan.")

    # Checkbox selesai project
    if df.at[selected_index, 'Selesai']:
        st.checkbox("✅ Project Telah Selesai", value=True, disabled=True)
    else:
        if df.at[selected_index, 'Tanggal Upload Pertama'] in [None, 'None', 'nan'] or pd.isna(df.at[selected_index, 'Tanggal Upload Pertama']):
            st.info("🔒 Upload file terlebih dahulu sebelum menandai project sebagai selesai.")
        else:
            if st.checkbox("✔️ Tandai sebagai Selesai", key=f"selesai_{selected_index}"):
                now = now_str()
                df.at[selected_index, 'Status'] = "Selesai"
                df.at[selected_index, 'Tanggal Selesai'] = now
                df.at[selected_index, 'Tanggal Update Terakhir'] = now
                df.at[selected_index, 'Selesai'] = True
                save_data(df)
                st.success("✅ Project ditandai sebagai selesai.")

    # Tombol hapus project
    if st.button("🗑 Hapus Project Ini"):
        st.session_state.project_hapus = df.at[selected_index, 'Nama Project']
        st.session_state.index_hapus = selected_index
        st.session_state.hapus_dipicu = True

    # Jika hapus dipicu, lakukan hapus dan rerun
    if st.session_state.hapus_dipicu:
        files_dihapus = hapus_file_project(st.session_state.project_hapus)
        if files_dihapus:
            st.write(f"File yang dihapus: {', '.join(files_dihapus)}")
        else:
            st.info("Tidak ada file terkait project yang ditemukan untuk dihapus.")

        df.drop(index=st.session_state.index_hapus, inplace=True)
        df.reset_index(drop=True, inplace=True)
        save_data(df)
        st.success(f"Project '{st.session_state.project_hapus}' dan file terkait berhasil dihapus.")

        # Reset flag
        st.session_state.hapus_dipicu = False
        st.experimental_rerun()

else:
    st.info("Belum ada project. Tambahkan project terlebih dahulu.")



