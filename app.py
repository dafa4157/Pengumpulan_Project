import streamlit as st
import pandas as pd
from datetime import datetime
import os
import pytz

# Konstanta
CSV_FILE = "data_project.csv"
UPLOAD_FOLDER = "uploads"
LOCAL_TZ = pytz.timezone("Asia/Jakarta")

# Buat folder upload kalau belum ada
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Fungsi load data CSV atau buat baru jika belum ada
def load_data():
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        # Tambahkan kolom jika belum ada
        expected_cols = [
            'Nama Project', 'Status', 'Tanggal Upload Pertama',
            'Tanggal Update Terakhir', 'Tanggal Selesai', 'Selesai'
        ]
        for col in expected_cols:
            if col not in df.columns:
                df[col] = None
        return df[expected_cols]  # pastikan urutan kolom
    else:
        df = pd.DataFrame(columns=[
            'Nama Project', 'Status', 'Tanggal Upload Pertama',
            'Tanggal Update Terakhir', 'Tanggal Selesai', 'Selesai'
        ])
        df.to_csv(CSV_FILE, index=False)
        return df

# Fungsi simpan data CSV
def save_data(df):
    df.to_csv(CSV_FILE, index=False)

# Fungsi hapus file terkait project berdasarkan prefix nama project
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

# Format waktu sekarang sesuai timezone lokal dalam string
def now_str():
    return datetime.now(LOCAL_TZ).strftime("%Y-%m-%d %H:%M:%S")

# Konversi kolom tanggal ke datetime dengan timezone lokal
def convert_to_datetime_tz(df, col):
    df[col] = pd.to_datetime(df[col], errors='coerce')
    df[col] = df[col].dt.tz_localize(None)
    df[col] = df[col].dt.tz_localize(LOCAL_TZ, ambiguous='NaT', nonexistent='NaT')
    return df

# Load data awal
df = load_data()

st.title("\ud83d\udccb Manajemen Project")

# Form tambah project baru
st.subheader("\u2795 Tambah Project Baru")
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
            st.success(f"Project '{nama_baru}' berhasil ditambahkan. Silakan refresh halaman untuk melihat perubahan.")

# Kelola project
st.subheader("\ud83d\udd27 Kelola Project")

if not df.empty:
    selected_index = st.selectbox("Pilih Project", df.index, format_func=lambda i: df.at[i, 'Nama Project'])

    st.write(f"**Nama Project:** {df.at[selected_index, 'Nama Project']}")
    st.write(f"**Status:** {df.at[selected_index, 'Status']}")
    st.write(f"**Tanggal Upload Pertama:** {df.at[selected_index, 'Tanggal Upload Pertama']}")
    st.write(f"**Tanggal Update Terakhir:** {df.at[selected_index, 'Tanggal Update Terakhir']}")
    st.write(f"**Tanggal Selesai:** {df.at[selected_index, 'Tanggal Selesai']}")

    uploaded_files = st.file_uploader("Upload file (boleh lebih dari satu)", key=selected_index, accept_multiple_files=True)
    if uploaded_files:
        existing_files = os.listdir(UPLOAD_FOLDER)
        nama_project = df.at[selected_index, 'Nama Project']

        duplicate_files = []
        files_to_upload = []
        for file in uploaded_files:
            filename = f"{nama_project}__{file.name}"
            if filename in existing_files:
                duplicate_files.append(file.name)
            else:
                files_to_upload.append((filename, file))

        if duplicate_files:
            st.error(f"\u274c File berikut sudah ada dan tidak diunggah ulang:\n\n{', '.join(duplicate_files)}")

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

    if df.at[selected_index, 'Selesai']:
        st.checkbox("\u2705 Project Telah Selesai", value=True, disabled=True)
    else:
        if df.at[selected_index, 'Tanggal Upload Pertama'] in [None, 'None', 'nan'] or pd.isna(df.at[selected_index, 'Tanggal Upload Pertama']):
            st.info("\ud83d\udd12 Upload file terlebih dahulu sebelum menandai project sebagai selesai.")
        else:
            if st.checkbox("\u2714\ufe0f Tandai sebagai Selesai", key=f"selesai_{selected_index}"):
                now = now_str()
                df.at[selected_index, 'Status'] = "Selesai"
                df.at[selected_index, 'Tanggal Selesai'] = now
                df.at[selected_index, 'Tanggal Update Terakhir'] = now
                df.at[selected_index, 'Selesai'] = True
                save_data(df)
                st.success("\u2705 Project ditandai sebagai selesai. Silakan refresh halaman untuk melihat perubahan.")

    if st.button("\ud83d\uddd1 Hapus Project Ini"):
        hapus_nama = df.at[selected_index, 'Nama Project']
        files_dihapus = hapus_file_project(hapus_nama)
        if files_dihapus:
            st.write(f"File yang dihapus: {', '.join(files_dihapus)}")
        else:
            st.info("Tidak ada file terkait project yang ditemukan untuk dihapus.")

        df.drop(index=selected_index, inplace=True)
        df.reset_index(drop=True, inplace=True)
        save_data(df)
        st.success(f"Project '{hapus_nama}' dan file terkait berhasil dihapus.")
        st.experimental_rerun()
else:
    st.info("Belum ada project. Tambahkan project terlebih dahulu.")

# Cari dan download file project
st.subheader("\ud83d\udd0d Cari dan Unduh File Project")
search_file = st.text_input("Masukkan nama file atau project")

if search_file:
    matching_files = [f for f in os.listdir(UPLOAD_FOLDER) if search_file.lower() in f.lower()]
    if matching_files:
        for file in matching_files:
            filepath = os.path.join(UPLOAD_FOLDER, file)
            nama_tampil = file.split("__", 1)[-1]
            with open(filepath, "rb") as f:
                st.download_button(f"\u2b07\ufe0f {nama_tampil}", f, file_name=nama_tampil)
    else:
        st.warning("\u274c Tidak ditemukan file dengan nama tersebut.")

# Tabel semua project
st.subheader("\ud83d\udcca Tabel Semua Project")
if df.empty:
    st.write("Belum ada data project.")
else:
    if "Selesai" in df.columns:
        st.dataframe(df.drop(columns=["Selesai"]), use_container_width=True)
    else:
        st.dataframe(df, use_container_width=True)

# Grafik project per hari
st.subheader("\ud83d\udcc8 Grafik Jumlah Project per Hari")

if not df.empty and df['Tanggal Upload Pertama'].notna().any():
    df = convert_to_datetime_tz(df, 'Tanggal Upload Pertama')
    df_hari = df.dropna(subset=['Tanggal Upload Pertama']).copy()
    df_hari['Tanggal'] = df_hari['Tanggal Upload Pertama'].dt.date

    project_per_day = df_hari.groupby('Tanggal').size().reset_index(name='Jumlah Project')
    project_per_day = project_per_day.sort_values('Tanggal')

    full_range = pd.DataFrame({'Tanggal': pd.date_range(start=project_per_day['Tanggal'].min(),
                                                       end=datetime.now(LOCAL_TZ).date())})
    full_range['Tanggal'] = full_range['Tanggal'].dt.date

    merged = full_range.merge(project_per_day, on='Tanggal', how='left').fillna(0)
    merged['Jumlah Project'] = merged['Jumlah Project'].astype(int)

    st.line_chart(data=merged, x='Tanggal', y='Jumlah Project', use_container_width=True)
else:
    st.info("Belum ada data project dengan tanggal upload untuk ditampilkan dalam grafik.")

# Daftar project selesai > 30 hari
st.subheader("\ud83d\udcc6 Project Selesai Lebih dari 30 Hari Lalu")

if not df.empty:
    df = convert_to_datetime_tz(df, 'Tanggal Selesai')
    now_dt = datetime.now(LOCAL_TZ)
    selesai_lama = df[
        (df['Selesai']) &
        (df['Tanggal Selesai'].notna()) &
        ((now_dt - df['Tanggal Selesai']).dt.days > 30)
    ]
    if not selesai_lama.empty:
        st.dataframe(selesai_lama[['Nama Project', 'Tanggal Selesai']], use_container_width=True)
    else:
        st.info("Tidak ada project yang selesai lebih dari 30 hari lalu.")

# Hapus file manual
st.subheader("\ud83d\udd91 Hapus File Manual dari Folder Uploads")
files = os.listdir(UPLOAD_FOLDER)
if files:
    selected_files = st.multiselect("Pilih file yang ingin dihapus:", files)
    if st.button("Hapus File Terpilih"):
        if not selected_files:
            st.warning("Silakan pilih minimal satu file untuk dihapus.")
        else:
            for f in selected_files:
                try:
                    os.remove(os.path.join(UPLOAD_FOLDER, f))
                    st.success(f"File '{f}' berhasil dihapus.")
                except Exception as e:
                    st.error(f"Gagal menghapus file '{f}': {e}")
else:
    st.info("Tidak ada file di folder upload untuk dihapus.")








