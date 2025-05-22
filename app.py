

import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- Constants ---
CSV_FILE = "data_proyek.csv"
UPLOAD_FOLDER = "uploads" # Define a constant for the upload folder

# --- Data Loading and Saving Functions ---
def load_data():
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        # Convert date columns to datetime objects immediately upon loading
        # This is crucial for consistent type handling
        df['Tanggal Upload Pertama'] = pd.to_datetime(df['Tanggal Upload Pertama'], errors='coerce')
        df['Tanggal Update Terakhir'] = pd.to_datetime(df['Tanggal Update Terakhir'], errors='coerce')
        df['Tanggal Selesai'] = pd.to_datetime(df['Tanggal Selesai'], errors='coerce')
        return df
    else:
        df = pd.DataFrame(columns=[
            'Nama Proyek', 'Status', 'Tanggal Upload Pertama',
            'Tanggal Update Terakhir', 'Tanggal Selesai', 'Selesai'
        ])
        df.to_csv(CSV_FILE, index=False)
        return df

def save_data(df):
    # When saving, convert datetime columns to string format to avoid issues with CSV
    # pd.to_datetime will handle conversion back when loading
    df_to_save = df.copy()
    for col in ['Tanggal Upload Pertama', 'Tanggal Update Terakhir', 'Tanggal Selesai']:
        # Only format if the column contains datetime objects, otherwise leave as is (e.g., None)
        if pd.api.types.is_datetime64_any_dtype(df_to_save[col]):
            df_to_save[col] = df_to_save[col].dt.strftime("%Y-%m-%d %H:%M:%S").replace({pd.NaT: None})
    df_to_save.to_csv(CSV_FILE, index=False)

# --- Streamlit Application ---
st.title("📋 Manajemen Proyek")

# Load data into session state
if 'data_proyek' not in st.session_state:
    st.session_state.data_proyek = load_data()

df = st.session_state.data_proyek

# --- Add New Project ---
st.subheader("➕ Tambah Proyek Baru")
with st.form("form_tambah"):
    nama_baru = st.text_input("Nama Proyek Baru")
    submitted = st.form_submit_button("Tambah")
    if submitted:
        if nama_baru.strip() == "":
            st.warning("Nama proyek tidak boleh kosong.")
        elif nama_baru in df['Nama Proyek'].values:
            st.warning("Proyek sudah ada.")
        else:
            new_row = {
                'Nama Proyek': nama_baru,
                'Status': 'Belum Selesai',
                'Tanggal Upload Pertama': pd.NaT, # Use pd.NaT for missing datetimes
                'Tanggal Update Terakhir': pd.NaT,
                'Tanggal Selesai': pd.NaT,
                'Selesai': False
            }
            # Use pd.concat to add a new row
            st.session_state.data_proyek = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(st.session_state.data_proyek)
            st.success(f"Proyek '{nama_baru}' berhasil ditambahkan.")
            st.rerun() # Use st.rerun() instead of st.experimental_rerun()


# --- Manage/Edit/Delete Projects ---
st.subheader("🔧 Kelola Proyek")

if not df.empty:
    # Use index as a key for selectbox to avoid issues if project names are not unique
    selected_index = st.selectbox("Pilih Proyek", df.index, format_func=lambda i: df.at[i, 'Nama Proyek'])

    # Display project details
    st.write(f"*Nama Proyek:* {df.at[selected_index, 'Nama Proyek']}")
    st.write(f"*Status:* {df.at[selected_index, 'Status']}")
    st.write(f"*Tanggal Upload Pertama:* {df.at[selected_index, 'Tanggal Upload Pertama'].strftime('%Y-%m-%d %H:%M:%S') if pd.notnull(df.at[selected_index, 'Tanggal Upload Pertama']) else 'N/A'}")
    st.write(f"*Tanggal Update Terakhir:* {df.at[selected_index, 'Tanggal Update Terakhir'].strftime('%Y-%m-%d %H:%M:%S') if pd.notnull(df.at[selected_index, 'Tanggal Update Terakhir']) else 'N/A'}")
    st.write(f"*Tanggal Selesai:* {df.at[selected_index, 'Tanggal Selesai'].strftime('%Y-%m-%d %H:%M:%S') if pd.notnull(df.at[selected_index, 'Tanggal Selesai']) else 'N/A'}")

    # Upload file
    uploaded = st.file_uploader("Upload file", key=f"file_uploader_{selected_index}") # Unique key for file uploader
    if uploaded:
        # Create folder uploads/<nama_proyek> if it doesn't exist
        safe_folder_name = df.at[selected_index, 'Nama Proyek'].replace(" ", "_").replace("/", "_").replace("\\", "_")
        upload_dir = os.path.join(UPLOAD_FOLDER, safe_folder_name)
        os.makedirs(upload_dir, exist_ok=True)

        # Save the file to the folder
        file_path = os.path.join(upload_dir, uploaded.name)
        with open(file_path, "wb") as f:
            f.write(uploaded.getbuffer())

        # Update dates
        now = datetime.now() # Keep it as datetime object
        if pd.isnat(df.at[selected_index, 'Tanggal Upload Pertama']): # Check for pd.NaT
            df.at[selected_index, 'Tanggal Upload Pertama'] = now
        df.at[selected_index, 'Tanggal Update Terakhir'] = now

        # Update status
        if not df.at[selected_index, 'Selesai']:
            df.at[selected_index, 'Status'] = 'Belum Selesai'

        save_data(df)
        st.session_state.data_proyek = df # Update session state
        st.success(f"📁 File '{uploaded.name}' berhasil disimpan di folder '{upload_dir}'.")
        st.rerun()

        # Display uploaded files
        st.info("📂 Daftar file yang sudah diupload:")
        files_uploaded = os.listdir(upload_dir)
        for file in files_uploaded:
            st.write(f"• {file}")

    # Checklist selesai
    if df.at[selected_index, 'Selesai']:
        st.checkbox("✅ Proyek Telah Selesai", value=True, disabled=True, key=f"finished_checkbox_{selected_index}")
    else:
        # Ensure 'Tanggal Upload Pertama' is a datetime object and not NaT before allowing completion
        if pd.isnat(df.at[selected_index, 'Tanggal Upload Pertama']):
            st.info("🔒 Upload file terlebih dahulu sebelum menandai proyek sebagai selesai.")
        else:
            if st.checkbox("✔️ Tandai sebagai Selesai", key=f"mark_complete_{selected_index}"): # Unique key
                now = datetime.now()
                df.at[selected_index, 'Status'] = "Selesai"
                df.at[selected_index, 'Tanggal Selesai'] = now
                df.at[selected_index, 'Tanggal Update Terakhir'] = now
                df.at[selected_index, 'Selesai'] = True
                save_data(df)
                st.session_state.data_proyek = df
                st.success("✅ Proyek ditandai sebagai selesai.")
                st.rerun()

    # Delete project button
    if st.button("🗑 Hapus Proyek Ini", key=f"delete_button_{selected_index}"): # Unique key
        hapus_nama = df.at[selected_index, 'Nama Proyek']
        df.drop(index=selected_index, inplace=True)
        df.reset_index(drop=True, inplace=True)
        save_data(df)
        st.session_state.data_proyek = df
        st.success(f"Proyek '{hapus_nama}' berhasil dihapus.")
        # Attempt to remove the associated upload folder
        safe_folder_name = hapus_nama.replace(" ", "_").replace("/", "_").replace("\\", "_")
        project_upload_dir = os.path.join(UPLOAD_FOLDER, safe_folder_name)
        if os.path.exists(project_upload_dir) and os.path.isdir(project_upload_dir):
            try:
                os.rmdir(project_upload_dir) # Only removes empty directories
                st.info(f"Folder '{project_upload_dir}' dihapus (jika kosong).")
            except OSError as e:
                st.warning(f"Tidak dapat menghapus folder '{project_upload_dir}': {e}. Mungkin masih berisi file.")
        st.rerun()

else:
    st.info("Belum ada proyek. Tambahkan proyek terlebih dahulu.")


# --- All Projects Table ---
st.subheader("📊 Tabel Semua Proyek")
if df.empty:
    st.write("Belum ada data proyek.")
else:
    # Ensure 'Tanggal Upload Pertama' is datetime type (redundant if load_data() works, but harmless)
    df['Tanggal Upload Pertama'] = pd.to_datetime(df['Tanggal Upload Pertama'], errors='coerce')

    # Calculate 'Durasi Hari'
    current_time_pd = pd.Timestamp(datetime.now())
    df['Durasi Hari'] = (current_time_pd - df['Tanggal Upload Pertama']).dt.days

    # Ensure 'Durasi Hari' is None for NaT values in 'Tanggal Upload Pertama'
    df.loc[df['Tanggal Upload Pertama'].isna(), 'Durasi Hari'] = None

    # Display dataframe, excluding the 'Selesai' boolean column if desired
    st.dataframe(df.drop(columns=["Selesai"]), use_container_width=True)











