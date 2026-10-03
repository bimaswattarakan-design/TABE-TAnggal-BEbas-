import streamlit as st
import pandas as pd
import datetime
import urllib.parse

st.set_page_config(page_title="TABE - Tanggal Bebas WBP", page_icon="⚖️", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f4f7f6; }
    .stApp header { background-color: #002f71; }
    h1, h2, h3 { color: #002f71; }
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

# Ganti ID ini dengan Google Sheets baru Anda yang sudah diisi tabel lurus
SHEET_ID = "18jzU8anZEwk716AO8Dn8oT8dSxsv0EJjYqEW3EjXpG4"
SHEET_NAMES = ["Sheet1", "DATABASE_TABE_BERSIH", "JUNI 2026"] # Sesuaikan nama sheet lurus Anda

@st.cache_data(ttl=60)
def load_clean_data():
    # Coba tarik data langsung dari Google Sheets lurus
    csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"
    try:
        df = pd.read_csv(csv_url)
        # Normalisasi nama kolom
        df.columns = [c.strip().title() for c in df.columns]
        if 'Tanggal Bebas' in df.columns:
            df['Tanggal Bebas'] = pd.to_datetime(df['Tanggal Bebas']).dt.date
        return df
    except Exception as e:
        return pd.DataFrame()

st.title("⚖️ TABE - Tanggal Bebas WBP")
st.caption("Sistem Pemantau & Peringatan Dini Pembebasan Warga Binaan")

df_wbp = load_clean_data()

if df_wbp.empty:
    st.error("⚠️ Gagal membaca data. Pastikan Google Sheets Anda sudah diatur publik ('Anyone with the link can view') dan format tabelnya lurus ke bawah.")
else:
    # Urutkan tanggal
    if 'Tanggal Bebas' in df_wbp.columns:
        df_wbp = df_wbp.sort_values(by='Tanggal Bebas').reset_index(drop=True)

    # Logika Pengingat H-1 (Besok)
    hari_ini = datetime.date.today()
    besok = hari_ini + datetime.timedelta(days=1)
    
    if 'Tanggal Bebas' in df_wbp.columns:
        df_besok = df_wbp[df_wbp['Tanggal Bebas'] == besok]
        if not df_besok.empty:
            st.markdown(f"""
                <div class="alert-box">
                    <h3 style="margin-top:0; color:#856404;">⚠️ PERINGATAN H-1: Pembebasan Esok Hari ({besok.strftime('%d-%m-%Y')})</h3>
                    <p>Segera siapkan Surat Lepas dan berkas administrasi untuk WBP berikut:</p>
                    <ul>
                        {"".join([f"<li><b>{row.get('Nama Wbp & Detail', row.iloc[1])}</b> — <span style='color:red;'>{row.get('Kategori', '')}</span></li>" for _, row in df_besok.iterrows()])}
                    </ul>
                </div>
            """, unsafe_allow_html=True)

    # Statistik Ringkas
    col1, col2, col3 = st.columns(3)
    col1.metric("Total WBP Terdaftar", len(df_wbp))
    if 'Tanggal Bebas' in df_wbp.columns:
        bln_ini = len(df_wbp[(df_wbp['Tanggal Bebas'].apply(lambda x: x.month == hari_ini.month if pd.notnull(x) else False))])
        col2.metric("Bebas Bulan Ini", bln_ini)
    col3.metric("Status Sistem", "Normal & Online ✅")

    st.markdown("---")
    st.subheader("📋 Daftar Jadwal Pembebasan WBP")
    
    search = st.text_input("🔍 Cari Nama WBP / Kategori:", "")
    if search:
        filtered = df_wbp[df_wbp.astype(str).agg(' '.join, axis=1).str.contains(search, case=False, na=False)]
    else:
        filtered = df_wbp

    st.dataframe(filtered, use_container_width=True, hide_index=True)
