import pytz

# ... kode lain tetap ...

# Bagian Project selesai > 30 hari

st.subheader("📆 Project Selesai Lebih dari 30 Hari Lalu")

if not df.empty:
    # Pastikan Tanggal Selesai datetime dan timezone-aware
    jakarta_tz = pytz.timezone('Asia/Jakarta')
    
    # Convert ke datetime (coerce error), lalu ubah ke timezone Asia/Jakarta jika belum ada tzinfo
    def to_jakarta_tz(dt):
        if pd.isna(dt):
            return pd.NaT
        if dt.tzinfo is None:
            # Jika naive datetime, beri timezone Jakarta
            return jakarta_tz.localize(dt)
        else:
            # Kalau sudah ada timezone, convert ke Jakarta timezone
            return dt.astimezone(jakarta_tz)

    df['Tanggal Selesai Local'] = df['Tanggal Selesai'].apply(to_jakarta_tz)

    now = pd.Timestamp.now(tz=jakarta_tz)

    selesai_lama = df[
        (df['Selesai']) &
        (df['Tanggal Selesai Local'].notna()) &
        ((now - df['Tanggal Selesai Local']).dt.days > 30)
    ]

    if not selesai_lama.empty:
        st.dataframe(selesai_lama[['Nama Project', 'Tanggal Selesai']], use_container_width=True)
    else:
        st.info("Tidak ada project yang selesai lebih dari 30 hari lalu.")
else:
    st.info("Belum ada data project.")







