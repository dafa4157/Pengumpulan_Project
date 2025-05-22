import streamlit as st
import pandas as pd
from datetime import datetime
import os

CSV_FILE = "data_proyek.csv"

# =============================
# 🔄 LOAD DATA DARI CSV
# =============================
def load_data():
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        df.fillna("", inplace=True)
        if 'Selesai' in df.columns:
            df['Selesai'] = df['Selesai'].astype(bool)
        else:
            df['Selesai'] = False
        return df
    else:
        df = pd.DataFrame(columns=[
            'Nama Proyek', 'Status', 'Tanggal Upload Pertama',
            'Tanggal Update Terakhir', 'Tanggal Selesai', 'Selesai'
        ])
        df.to_csv(CSV_FILE, index=False)
        return df

# =============================
# 💾 SIMPAN DATA KE CSV
# =============================
def save_data(df):
    df.to_csv(CSV_FILE, index=False)

# =============================
# 🚀 APLIKASI STREAMLIT
# =============================
st.set_page_config(page_title="Manajemen Proyek", layout="wide")
st.title("📋 Manajemen Proyek")

# Load data awal
if 'data_proyek' not in st.session_state:
    st.session_state.data_proyek = load_data()

df = st.session_state.data_proyek

# =============================
# ➕ TAMBAH PROYEK BARU
# =============================
st.subheader("➕ Tambah Proyek Baru")
with st.form("form_tambah"):
    nama_baru = st.text_input("Nama Proyek Baru")
    submitted = st.form_submit_button("Tambah")
    if submitted:
        if nama_baru.strip() == "":
            st.warning("❗ Nama proyek tidak boleh kosong.")
        elif nama_baru in df['Nama Proyek'].values:
            st.warning("⚠️ Proyek sudah ada.")
        else:
            new_row = {
                'Nama Proyek': nama_baru,
                'Status': 'Belum Selesai',
                'Tanggal Upload Pertama': '',
                'Tanggal Update Terakhir': '',
                'Tanggal Selesai': '',
                'Selesai': False
            }
            df.loc[len(df)] = new_row
            save_data(df)
            st.success(f"✅ Proyek '{nama_baru}' berhasil ditambahkan.")
            st.experimental_rerun()

# =============================
# 🔧 KELOLA PROYEK
# =============================
st.subheader("🔧 Kelola Proyek")

if not df.empty:
    selected_index = st.selectbox("Pilih Proyek", df.index, format_func=lambda i: df.at[i, 'Nama Proyek'])

    if 0 <= selected_index < len(df):
        st.markdown("### 📁 Detail Proyek")
        st.write(f"**Nama Proyek:** {df.at[selected_index, 'Nama Proyek']}")
        st.write(f"**Status:** {df.at[selected_index, 'Status']}")
        st.write(f"**Tanggal Upload Pertama:** {df.at[selected_index, 'Tanggal Upload Pertama']}")
        st.write(f"**Tanggal Update Terakhir:** {df.at[selected_index, 'Tanggal Update Terakhir']}")
        st.write(f"**Tanggal Selesai:** {df.at[selected_index, 'Tanggal Selesai']}")

        # Upload file
        uploaded = st.file_uploader("Upload file", key=f"upload_{selected_index}")
        if uploaded:
            safe_folder_name = df.at[selected_index, 'Nama Proyek'].replace(" ", "_")
            upload_dir = os.path.join("uploads", safe_folder_name)
            os.makedirs(upload_dir, exist_ok=True)

            file_path = os.path.join(upload_dir, uploaded.name)
            with open(file_path, "wb") as f:
                f.write(uploaded.getbuffer())

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if df.at[selected_index, 'Tanggal Upload Pertama'] in ["", "nan", None]:
                df.at[selected_index, 'Tanggal Upload Pertama'] = now
            df.at[selected_index, 'Tanggal Update Terakhir'] = now

            if not df.at[selected_index, 'Selesai']:
                df.at[selected_index, 'Status'] = 'Belum Selesai'

            save_data(df)
            st.success(f"📥 File '{uploaded.name}' berhasil disimpan.")
            st.info("📂 File di folder proyek:")
            for f in os.listdir(upload_dir):
                st.write(f"• {f}")

        # Tandai selesai
        if df.at[selected_index, 'Selesai']:
            st.checkbox("✅ Proyek Telah Selesai", value=True, disabled=True)
        else:
            if df.at[selected_index, 'Tanggal Upload Pertama'] == "":
                st.info("🔒 Upload file terlebih dahulu sebelum menandai selesai.")
            else:
                if st.checkbox("✔️ Tandai sebagai Selesai", key=f"selesai_{selected_index}"):
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    df.at[selected_index, 'Status'] = "Selesai"
                    df.at[selected_index, 'Tanggal Selesai'] = now
                    df.at[selected_index, 'Tanggal Update Terakhir'] = now
                    df.at[selected_index, 'Selesai'] = True
                    save_data(df)
                    st.success("✅ Proyek ditandai sebagai selesai.")
                    st.experimental_rerun()

        # Hapus proyek
        if st.button("🗑 Hapus Proyek Ini"):
            hapus_nama = df.at[selected_index, 'Nama Proyek']
            df.drop(index=selected_index, inplace=True)
            df.reset_index(drop=True, inplace=True)
            save_data(df)
            st.success(f"🧹 Proyek '{hapus_nama}' berhasil dihapus.")
            st.experimental_rerun()
else:
    st.info("📭 Belum ada proyek. Tambahkan proyek terlebih dahulu.")

# =============================
# 📊 TABEL SEMUA PROYEK
# =============================
st.subheader("📊 Tabel Semua Proyek")
if df.empty:
    st.write("Belum ada data proyek.")
else:
    st.dataframe(df.drop(columns=["Selesai"]), use_container_width=True)












