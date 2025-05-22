import streamlit as st
import pandas as pd
from datetime import datetime
import os

CSV_FILE = "data_project.csv"
UPLOAD_FOLDER = "uploads"

# Buat folder upload kalau belum ada
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def load_data():
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        # Bersihkan data tanggal yang mungkin invalid
        for col in ['Tanggal Upload Pertama', 'Tanggal Update Terakhir', 'Tanggal Selesai']:
            df[col] = pd.to_datetime(df[col], errors='coerce')
        # Pastikan kolom Selesai adalah boolean
        if df['Selesai'].dtype != 'bool':
            df['Selesai'] = df['Selesai'].astype(bool)
        return df
    else:
        df = pd.DataFrame(columns=[
            'Nama Project', 'Status', 'Tanggal Upload Pertama',
            'Tanggal Update Terakhir', 'Tanggal Selesai', 'Selesai'
        ])
        df.to_csv(CSV_FILE, index=False)
        return df

def save_data(df):
    # Simpan dengan format tanggal string agar konsisten
    df_copy = df.copy()
    for col in ['Tanggal Upload Pertama', 'Tanggal Update Terakhir', 'Tanggal Selesai']:
        df_copy[col] = df_copy[col].dt.strftime("%Y-%m-%d %H:%M:%S")
    df_copy.to_csv(CSV_FILE, index=False)

st.title("📋 Manajemen Project")

df = load_data()

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
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df)
            st.success(f"Project '{nama_baru}' berhasil ditambahkan. Silakan refresh halaman untuk melihat perubahan.")

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
            st.error(f"❌ File berikut sudah ada dan tidak diunggah ulang:\n\n{', '.join(duplicate_files)}")

        if files_to_upload:
            now = datetime.now()
            for filename, file in files_to_upload:
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                with open(filepath, "wb") as f:
                    f.write(file.read())

            # Update tanggal upload pertama dan update terakhir
            if pd.isna(df.at[selected_index, 'Tanggal Upload Pertama']):
                df.at[selected_index, 'Tanggal Upload Pertama'] = now
            df.at[selected_index, 'Tanggal Update Terakhir'] = now
            if not df.at[selected_index, 'Selesai']:
                df.at[selected_index, 'Status'] = 'Belum Selesai'

            save_data(df)
            st.success(f"{len(files_to_upload)} file berhasil diunggah dan disimpan.")

    # Checkbox selesai
    if df.at[selected_index, 'Selesai']:
        st.checkbox("✅ Project Telah Selesai", value=True, disabled=True)
    else:
        if pd.isna(df.at[selected_index, 'Tanggal Upload Pertama']):
            st.info("🔒 Upload file terlebih dahulu sebelum menandai project sebagai selesai.")
        else:
            if st.checkbox("✔️ Tandai sebagai Selesai", key=f"selesai_{selected_index}"):
                now = datetime.now()
                df.at[selected_index, 'Status'] = "Selesai"
                df.at[selected_index, 'Tanggal Selesai'] = now
                df.at[selected_index, 'Tanggal Update Terakhir'] = now
                df.at[selected_index, 'Selesai'] = True
                save_data(df)
                st.success("✅ Project ditandai sebagai selesai. Silakan refresh halaman untuk melihat perubahan.")

    # Hapus project
    if st.button("🗑 Hapus Project Ini"):
        hapus_nama = df.at[selected_index, 'Nama Project']

        # Hapus file terkait
        for f in os.listdir(UPLOAD_FOLDER):
            if f.startswith(f"{hapus_nama}__"):
                os.remove(os.path.join(UPLOAD_FOLDER, f))

        df = df.drop(index=selected_index).reset_index(drop=True)
        save_data(df)
        st.success(f"Project '{hapus_nama}' dan file terkait berhasil dihapus.")
else:
    st.info("Belum ada project. Tambahkan project terlebih dahulu.")

st.subheader("🔍 Cari dan Unduh File Project")
search_file = st.text_input("Masukkan nama file atau project")

if search_file:
    matching_files = [f for f in os.listdir(UPLOAD_FOLDER) if search_file.lower() in f.lower()]

    if matching_files:
        for file in matching_files:
            filepath = os.path.join(UPLOAD_FOLDER, file)
            nama_tampil = file.split("__", 1)[-1]
            with open(filepath, "rb") as f:
                st.download_button(f"⬇️ {nama_tampil}", f, file_name=nama_tampil)
    else:
        st.warning("❌ Tidak ditemukan file dengan nama tersebut.")

st.subheader("📊 Tabel Semua Project")
if df.empty:
    st.write("Belum ada data project.")
else:
    st.dataframe(df.drop(columns=["Selesai"]), use_container_width=True)

st.subheader("📈 Grafik Jumlah Project per Hari")
if not df.empty and df['Tanggal Upload Pertama'].notna().any():
    df_hari = df.dropna(subset=['Tanggal Upload Pertama']).copy()
    df_hari['Tanggal'] = df_hari['Tanggal Upload Pertama'].dt.normalize()

    project_per_day = df_hari.groupby('Tanggal').size().reset_index(name='Jumlah Project')
    project_per_day = project_per_day.sort_values('Tanggal')

    # Pastikan tipe datetime konsisten
    project_per_day['Tanggal'] = pd.to_datetime(project_per_day['Tanggal'])
    full_range = pd.DataFrame({'Tanggal': pd.date_range(start=project_per_day['Tanggal'].min(),
                                                       end=pd.Timestamp(datetime.now().date()))})

    merged = full_range.merge(project_per_day, on='Tanggal', how='left').fillna(0)
    merged['Jumlah Project'] = merged['Jumlah Project'].astype(int)

    st.line_chart(data=merged, x='Tanggal', y='Jumlah Project', use_container_width=True)
else:
    st.info("Belum ada data project dengan tanggal upload untuk ditampilkan dalam grafik.")

st.subheader("📆 Project Selesai Lebih dari 30 Hari Lalu")
now = datetime.now()
if not df.empty:
    selesai_lama = df[(df['Selesai']) & (df['Tanggal Selesai'].notna()) & ((now - df['Tanggal Selesai']).dt.days > 30)]
    if not selesai_lama.empty:
        st.dataframe(selesai_lama[['Nama Project', 'Tanggal Selesai']], use_container_width=True)
    else:
        st.info("Tidak ada project yang selesai lebih dari 30 hari lalu.")











