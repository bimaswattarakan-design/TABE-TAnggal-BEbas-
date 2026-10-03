import streamlit as st
import pandas as pd
import datetime

# Konfigurasi Tampilan Halaman Web
st.set_page_config(
    page_title="TABE - Sistem Tanggal Bebas WBP",
    page_icon="⚖️",
    layout="wide"
)

# Styling Tema Navy (#002f71) & Aksen Gold (#d4af37)
st.markdown("""
    <style>
    .main { background-color: #f4f7f6; }
    .stApp header { background-color: #002f71; }
    h1, h2, h3 { color: #002f71; }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 5px solid #d4af37;
        text-align: center;
    }
    .alert-box {
        background-color: #fff3cd;
        border-left: 6px solid #ffc107;
        padding: 20px;
        border-radius: 8px;
        color: #856404;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# ID Google Sheets Anda yang terhubung secara online
SHEET_ID = "18jzU8anZEwk716AO8Dn8oT8dSxsv0EJjYqEW3EjXpG4"
SHEET_NAMES = ["JUNI 2026", "JULI 2026 ", "AGUSTUS 2026", "SEPTEMBERR 2026", "OKTOBERR 2026 "]

@st.cache_data(ttl=300)
def load_data_from_cloud():
    all_data = []
    month_map = {
        'JUNI': 6, 'JULI': 7, 'AGUSTUS': 8, 
        'SEPTEMBERR': 9, 'SEPTEMBER': 9, 'OKTOBER': 10, 'OKTOBERR': 10
    }

    for sheet_name in SHEET_NAMES:
        clean_name = sheet_name.strip()
        csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={clean_name}"
        
        try:
            df = pd.read_csv(csv_url, header=None)
            parts = clean_name.upper().split()
            bulan_str = parts[0]
            tahun_int = int(parts[-1]) if len(parts) > 1 and parts[-1].isdigit() else 2026
            bulan_int = month_map.get(bulan_str, 6)

            for row_idx in range(len(df)):
                row_vals = df.iloc[row_idx, 1:8].values
                has_dates = any(pd.notna(val) and str(val).isdigit() and 1 <= int(val) <= 31 for val in row_vals)
                
                if has_dates:
                    for col_idx in range(1, 8):
                        date_val = df.iloc[row_idx, col_idx]
                        if pd.notna(date_val) and str(date_val).isdigit():
                            day_num = int(date_val)
                            for offset in range(1, 4):
                                if (row_idx + offset) < len(df):
                                    cell_val = df.iloc[row_idx + offset, col_idx]
                                    if pd.notna(cell_val) and str(cell_val).strip() != "":
                                        try:
                                            tgl_bebas = datetime.date(tahun_int, bulan_int, day_num)
                                            text_upper = str(cell_val).upper()
                                            cat = "Lainnya"
                                            if "PB" in text_upper: cat = "Pembebasan Bersyarat (PB)"
                                            elif "CB" in text_upper: cat = "Cuti Bersyarat (CB)"
                                            elif "MURNI" in text_upper: cat = "Bebas Murni"

                                            all_data.append({
                                                'Tanggal Bebas': tgl_bebas,
                                                'Nama WBP & Detail': str(cell_val).strip(),
                                                'Kategori': cat,
                                                'Bulan': clean_name
                                            })
                                        except:
                                            pass
        except Exception:
            continue

    return pd.DataFrame(all_data)

# Header Utama Aplikasi
st.title("⚖️ TABE - Tanggal Bebas WBP")
st.caption("Sistem Pemantau & Peringatan Dini Pembebasan Warga Binaan (Terhubung ke Cloud Database)")

# Load Data dari Google Sheets
with st.spinner("Menarik data terbaru dari Google Sheets..."):
    df_wbp = load_data_from_cloud()

if df_wbp.empty:
    st.warning("⚠️ Data belum terbaca. Pastikan koneksi internet aktif dan format Google Sheets sesuai.")
else:
    df_wbp = df_wbp.sort_values(by='Tanggal Bebas').reset_index(drop=True)

    # Logika Waktu (Hari Ini & Besok untuk Pengingat H-1)
    hari_ini = datetime.date.today()
    besok = hari_ini + datetime.timedelta(days=1)
    
    # Filter H-1 (Bebas Besok)
    df_besok = df_wbp[df_wbp['Tanggal Bebas'] == besok]

    if not df_besok.empty:
        st.markdown(f"""
            <div class="alert-box">
                <h3 style="margin-top:0; color:#856404;">⚠️ PERINGATAN H-1: Pembebasan Esok Hari ({besok.strftime('%d-%m-%Y')})</h3>
                <p>Harap segera siapkan Surat Lepas dan berkas administrasi untuk WBP berikut:</p>
                <ul>
                    {"".join([f"<li><b>{row['Nama WBP & Detail']}</b> — <span style='color:red;'>{row['Kategori']}</span></li>" for _, row in df_besok.iterrows()])}
                </ul>
            </div>
        """, unsafe_allow_html=True)

    # Kotak Statistik Atas
    col1, col2, col3, col4 = st.columns(4)
    total_wbp = len(df_wbp)
    bulan_ini = len(df_wbp[(df_wbp['Tanggal Bebas'].dt.month == hari_ini.month) & (df_wbp['Tanggal Bebas'].dt.year == hari_ini.year)])
    total_murni = len(df_wbp[df_wbp['Kategori'] == 'Bebas Murni'])
    total_pb_cb = len(df_wbp[df_wbp['Kategori'].isin(['Pembebasan Bersyarat (PB)', 'Cuti Bersyarat (CB)'])])

    with col1:
        st.metric("Total WBP Terdaftar", total_wbp)
    with col2:
        st.metric("Bebas Bulan Ini", bulan_ini)
    with col3:
        st.metric("Total Bebas Murni", total_murni)
    with col4:
        st.metric("Total PB / CB", total_pb_cb)

    st.markdown("---")

    # Pencarian & Tabel Interaktif
    st.subheader("📋 Data Jadwal Pembebasan WBP")
    search_query = st.text_input("🔍 Cari Nama WBP, Nomor Register, atau Kategori:", "")

    if search_query:
        filtered_df = df_wbp[df_wbp.astype(str).agg(' '.join, axis=1).str.contains(search_query, case=False, na=False)]
    else:
        filtered_df = df_wbp

    # Format Tampilan Tanggal ke DD-MM-YYYY
    display_df = filtered_df.copy()
    display_df['Tanggal Bebas'] = pd.to_datetime(display_df['Tanggal Bebas']).dt.strftime('%d-%m-%Y')

    st.dataframe(
        display_df[['Tanggal Bebas', 'Nama WBP & Detail', 'Kategori', 'Bulan']],
        use_container_width=True,
        hide_index=True
    )

    st.markdown("<br><p style='text-align: center; color: gray; font-size: 12px;'>Aplikasi TABE • Terintegrasi dengan Google Sheets secara Real-Time</p>", unsafe_allow_html=True)
