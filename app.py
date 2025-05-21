import streamlit as st
import pandas as pd
from datetime import datetime
import os

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
                'Tanggal Upload Pertama': None,
                'Tanggal Update Terakhir': None,
                'Tanggal Selesai': None,
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
    st.write(f"*Tanggal Upload Pertama:* {df.at[selected_index, 'Tanggal Upload Pertama']}")
    st.write(f"*Tanggal Update Terakhir:* {df.at[selected_index, 'Tanggal Update Terakhir']}")
    st.write(f"*Tanggal Selesai:* {df.at[selected_index, 'Tanggal Selesai']}")

    uploaded_files = st.file_uploader("Upload file (boleh lebih dari satu)", key=selected_index, accept_multiple_files=True)
    if uploaded_files:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
    df['Tanggal Upload Pertama'] = pd.to_datetime(df['Tanggal Upload Pertama'], errors='coerce')
    df_hari = df.dropna(subset=['Tanggal Upload Pertama']).copy()
    df_hari['Tanggal'] = df_hari['Tanggal Upload Pertama'].dt.date

    project_per_day = df_hari.groupby('Tanggal').size().reset_index(name='Jumlah Project')
    project_per_day = project_per_day.sort_values('Tanggal')

    st.line_chart(data=project_per_day, x='Tanggal', y='Jumlah Project', use_container_width=True)
else:
    st.info("Belum ada data project dengan tanggal upload untuk ditampilkan dalam grafik.")




