import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import io
import os
import base64
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Set Konfigurasi Halaman Web Streamlit
st.set_page_config(page_title="Franz Lift Structure Drawing", layout="wide", page_icon="⚙️")

# =========================================================================
# G1. CONFIG: INITIALIZATION GOOGLE SHEETS & RECALL SESSION STATE SYSTEM
# =========================================================================
conn = st.connection("gsheets", type=GSheetsConnection)

DOOR_CONFIG_OPTIONS = [
    "1 Sisi (Depan)",
    "2 Sisi Berseberangan (Depan & Belakang)",
    "2 Sisi Adjacent (Depan & Kanan)",
    "2 Sisi Adjacent (Depan & Kiri)"
]

state_keys = [
    # Modul Balok
    "b_nama_project", "b_no_kontrak", "b_lebar_sh", "b_dalam_sh", "b_h_pit", "b_h_headroom", "b_jml_lantai",
    "b_lebar_p", "b_width_doorway", "b_tinggi_p", "b_tinggi_gembosan", "b_tebal_l", "b_dinding_kiri",
    "b_side_tombol", "b_config_sep", "b_door_config",
    "b_lebar_p2", "b_width_doorway2", "b_dinding_awal2", "b_side_tombol2", "b_pdf_ref_base64",
    # Modul Kolom
    "k_nama_project", "k_no_kontrak", "k_posisi_cwt", "k_lebar_sh", "k_dalam_sh", "k_h_pit", "k_h_headroom", "k_jml_lantai",
    "k_posisi_rel_kabin", "k_track_gauge_cwt", "k_tebal_rail_cwt", "k_tebal_pintu_luar", "k_celah_daun_pintu", "k_tebal_kolom",
    "k_jarak_rel_ke_cwt", "k_sisa_belakang",
    "k_lebar_p", "k_width_doorway", "k_tinggi_p", "k_tinggi_gembosan", "k_tebal_l", "k_dinding_kiri", "k_side_tombol",
    "k_door_config", "k_lebar_p2", "k_width_doorway2", "k_dinding_awal2", "k_side_tombol2", "k_pdf_ref_base64"
]

for k in state_keys:
    if k not in st.session_state:
        if "pdf_ref_base64" in k: st.session_state[k] = ""
        elif "nama" in k: st.session_state[k] = "GUNAWAN-JKT"
        elif "no" in k or "kontrak" in k: st.session_state[k] = " "
        elif "side_tombol" in k: st.session_state[k] = "KANAN"
        elif "config_sep" in k: st.session_state[k] = "3-SISI"
        elif "door_config" in k: st.session_state[k] = "1 Sisi (Depan)"
        elif "posisi_cwt" in k: st.session_state[k] = "L (KANAN LAYOUT)"
        elif "jml_lantai" in k: st.session_state[k] = 3
        elif "lebar_sh" in k: st.session_state[k] = 1700 if "b_" in k else 1430
        elif "dalam_sh" in k: st.session_state[k] = 1500 if "b_" in k else 1430
        elif "h_pit" in k: st.session_state[k] = 170
        elif "headroom" in k: st.session_state[k] = 3000
        elif "lebar_p" in k: st.session_state[k] = 800
        elif "width_doorway" in k: st.session_state[k] = 950
        elif "tinggi_p" in k: st.session_state[k] = 2000
        elif "gembosan" in k: st.session_state[k] = 2100
        elif "tebal_l" in k: st.session_state[k] = 300
        elif "dinding_kiri" in k: st.session_state[k] = 375 if "b_" in k else 400
        elif "dinding_awal2" in k: st.session_state[k] = 220
        elif "rel_kabin" in k: st.session_state[k] = 670
        elif "gauge_cwt" in k: st.session_state[k] = 700
        elif "rail_cwt" in k: st.session_state[k] = 56
        elif "pintu_luar" in k: st.session_state[k] = 110
        elif "daun_pintu" in k: st.session_state[k] = 30
        elif "tebal_kolom" in k: st.session_state[k] = 200
        elif "jarak_rel_ke_cwt" in k: st.session_state[k] = 630
        elif "sisa_belakang" in k: st.session_state[k] = 165

# =========================================================================
# G2. SIDEBAR LOGIC: CALLBACK FUNCTION UNTUK AUTO-FILL INSTAN SINKRON
# =========================================================================
if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", width=200)
st.sidebar.markdown("### 📋 Panggil Riwayat Proyek")

def trigger_recall_sync():
    if st.session_state.pilihan_proyek_sidebar != "-- Pilih Data Untuk Auto-Fill --":
        row_terpilih = df_history[df_history['label_select'] == st.session_state.pilihan_proyek_sidebar].iloc[0]
        tipe_modul = row_terpilih['tipe_modul']
        
        if tipe_modul == "Separator Beam":
            st.session_state.b_nama_project = str(row_terpilih.get('nama_project', 'GUNAWAN-JKT'))
            st.session_state.b_no_kontrak = str(row_terpilih.get('no_drawing', ' '))
            st.session_state.b_lebar_sh = int(row_terpilih.get('lebar_hoistway', 1700))
            st.session_state.b_dalam_sh = int(row_terpilih.get('dalam_hoistway', 1500))
            st.session_state.b_h_pit = int(row_terpilih.get('kedalaman_pit', 170))
            st.session_state.b_h_headroom = int(row_terpilih.get('tinggi_headroom', 3000))
            st.session_state.b_jml_lantai = int(row_terpilih.get('jml_lantai', 3))
            st.session_state.b_lebar_p = int(row_terpilih.get('lebar_pintu_bersih', 800))
            st.session_state.b_width_doorway = int(row_terpilih.get('width_doorway', 950))
            st.session_state.b_tinggi_p = int(row_terpilih.get('tinggi_p', 2000))
            st.session_state.b_tinggi_gembosan = int(row_terpilih.get('tinggi_gembosan', 2100))
            st.session_state.b_tebal_l = int(row_terpilih.get('tebal_l', 300))
            st.session_state.b_dinding_kiri = int(row_terpilih.get('dinding_kiri', 375))
            st.session_state.b_side_tombol = str(row_terpilih.get('side_tombol', 'KANAN'))
            st.session_state.b_config_sep = str(row_terpilih.get('config_sep', '3-SISI'))
            dc = str(row_terpilih.get('door_config', '1 Sisi (Depan)'))
            st.session_state.b_door_config = dc if dc in DOOR_CONFIG_OPTIONS else "1 Sisi (Depan)"
            st.session_state.b_lebar_p2 = int(row_terpilih.get('lebar_pintu_bersih2', 800))
            st.session_state.b_width_doorway2 = int(row_terpilih.get('width_doorway2', 950))
            st.session_state.b_dinding_awal2 = int(row_terpilih.get('dinding_awal2', 220))
            st.session_state.b_side_tombol2 = str(row_terpilih.get('side_tombol2', 'KANAN'))
            st.session_state.b_pdf_ref_base64 = str(row_terpilih.get('pdf_referensi_data', ''))
            
        elif tipe_modul == "Column Structure":
            st.session_state.k_nama_project = str(row_terpilih.get('nama_project', 'GUNAWAN-JKT'))
            st.session_state.k_no_kontrak = str(row_terpilih.get('no_drawing', ' '))
            st.session_state.k_posisi_cwt = str(row_terpilih.get('posisi_cwt_raw', 'L (KANAN LAYOUT)'))
            st.session_state.k_lebar_sh = int(row_terpilih.get('lebar_hoistway', 1430))
            st.session_state.k_dalam_sh = int(row_terpilih.get('dalam_hoistway', 1430))
            st.session_state.k_h_pit = int(row_terpilih.get('kedalaman_pit', 170))
            st.session_state.k_h_headroom = int(row_terpilih.get('tinggi_headroom', 3000))
            st.session_state.k_jml_lantai = int(row_terpilih.get('jml_lantai', 3))
            st.session_state.k_posisi_rel_kabin = int(row_terpilih.get('posisi_rel_kabin', 670))
            st.session_state.k_track_gauge_cwt = int(row_terpilih.get('track_gauge_cwt', 700))
            st.session_state.k_tebal_rail_cwt = int(row_terpilih.get('tebal_rail_cwt', 56))
            st.session_state.k_tebal_pintu_luar = int(row_terpilih.get('tebal_pintu_luar', 110))
            st.session_state.k_celah_daun_pintu = int(row_terpilih.get('celah_daun_pintu', 30))
            st.session_state.k_tebal_kolom = int(row_terpilih.get('tebal_kolom', 200))
            st.session_state.k_jarak_rel_ke_cwt = int(row_terpilih.get('jarak_rel_ke_cwt', 630))
            st.session_state.k_sisa_belakang = int(row_terpilih.get('sisa_belakang', 165))
            st.session_state.k_lebar_p = int(row_terpilih.get('lebar_pintu_bersih', 800))
            st.session_state.k_width_doorway = int(row_terpilih.get('width_doorway', 950))
            st.session_state.k_tinggi_p = int(row_terpilih.get('tinggi_p', 2000))
            st.session_state.k_tinggi_gembosan = int(row_terpilih.get('tinggi_gembosan', 2100))
            st.session_state.k_tebal_l = int(row_terpilih.get('tebal_l', 300))
            st.session_state.k_dinding_kiri = int(row_terpilih.get('dinding_kiri', 400))
            st.session_state.k_side_tombol = str(row_terpilih.get('side_tombol', 'KANAN'))
            dc = str(row_terpilih.get('door_config', '1 Sisi (Depan)'))
            st.session_state.k_door_config = dc if dc in DOOR_CONFIG_OPTIONS else "1 Sisi (Depan)"
            st.session_state.k_lebar_p2 = int(row_terpilih.get('lebar_pintu_bersih2', 800))
            st.session_state.k_width_doorway2 = int(row_terpilih.get('width_doorway2', 950))
            st.session_state.k_dinding_awal2 = int(row_terpilih.get('dinding_awal2', 220))
            st.session_state.k_side_tombol2 = str(row_terpilih.get('side_tombol2', 'KANAN'))
            st.session_state.k_pdf_ref_base64 = str(row_terpilih.get('pdf_referensi_data', ''))

try:
    df_history = conn.read(ttl="1s")
    if df_history is not None and not df_history.empty:
        df_history['label_select'] = df_history['nama_project'].astype(str) + " (" + df_history['no_drawing'].astype(str) + ") [" + df_history['tipe_modul'].astype(str) + "]"
        options_list = ["-- Pilih Data Untuk Auto-Fill --"] + df_history['label_select'].tolist()
        st.sidebar.selectbox("Pilih Proyek:", options_list, key="pilihan_proyek_sidebar", on_change=trigger_recall_sync)
except:
    st.sidebar.info("Sistem Cloud History siap dikonfigurasi melalui Secrets Management.")

def push_history_to_sheets(payload):
    try:
        df_old = conn.read()
        df_new = pd.DataFrame([payload])
        if df_old is not None and not df_old.empty:
            df_merged = pd.concat([df_old, df_new], ignore_index=True)
        else:
            df_merged = df_new
        conn.update(data=df_merged)
        st.success("✨ Nilai parameter sukses dicatat permanen ke Cloud Database!")
    except:
        st.warning("Catatan: Data gagal dikirim ke Google Sheets, periksa konfigurasi 'Secrets' Anda.")

# ==========================================
# G3. HELPER: BORDER DRAFT KOP RESMI & ELEVASI PINTU
# ==========================================
def draw_rigid_border(ax, x_min, x_max, y_min, y_max, project_name, contract_no, page_title, page_num, total_pages, zoom_logo=0.25):
    ax.add_patch(plt.Rectangle((x_min, y_min), x_max - x_min, y_max - y_min, facecolor='none', edgecolor='black', lw=1.5, zorder=100))
    ax.add_patch(plt.Rectangle((x_min + 15, y_min + 15), (x_max - x_min) - 30, (y_max - y_min) - 30, facecolor='none', edgecolor='black', lw=0.8, zorder=100))
    
    h_kop = 150
    y_kop_start = y_min + 15
    y_kop_end = y_kop_start + h_kop
    x_kop_start = x_min + 15
    x_kop_end = x_max - 15
    w_kop = x_kop_end - x_kop_start
    
    ax.add_patch(plt.Rectangle((x_kop_start, y_kop_start), w_kop, h_kop, facecolor='#ffffff', edgecolor='black', lw=1.2, zorder=101))
    
    w_col1 = w_kop * 0.25
    w_col2 = w_kop * 0.37
    w_col3 = w_kop * 0.20
    
    x_c1 = x_kop_start + w_col1
    x_c2 = x_c1 + w_col2
    x_c3 = x_c2 + w_col3
    
    ax.plot([x_c1, x_c1], [y_kop_start, y_kop_end], 'k-', lw=1, zorder=102)
    ax.plot([x_c2, x_c2], [y_kop_start, y_kop_end], 'k-', lw=1, zorder=102)
    ax.plot([x_c3, x_c3], [y_kop_start, y_kop_end], 'k-', lw=1, zorder=102)
    
    logo_file = "logo.png"
    if os.path.exists(logo_file):
        try:
            img = mpimg.imread(logo_file)
            imagebox = OffsetImage(img, zoom=zoom_logo)
            ab = AnnotationBbox(imagebox, (x_kop_start + (w_col1 / 2), y_kop_start + (h_kop / 2)), frameon=False, zorder=105)
            ax.add_artist(ab)
        except Exception:
            ax.text(x_kop_start + 20, y_kop_start + (h_kop / 2), "FRANZ HOME LIFT", fontweight='bold', color='#1a73e8', va='center', ha='left', fontsize=11, zorder=103)
    else:
        ax.text(x_kop_start + 20, y_kop_start + (h_kop / 2), "FRANZ HOME LIFT", fontweight='bold', color='#1a73e8', va='center', ha='left', fontsize=11, zorder=103)
        
    ax.text(x_c1 + 20, y_kop_start + (h_kop * 0.65), f"PROJECT : {project_name.replace('_', ' ')}", color='black', fontweight='bold', va='center', ha='left', fontsize=9.5, zorder=103)
    ax.text(x_c1 + 20, y_kop_start + (h_kop * 0.30), f"CONTRACT NO: {contract_no}", color='dimgray', va='center', ha='left', fontsize=9, zorder=103)
    
    ax.text(x_c2 + 20, y_kop_start + (h_kop * 0.68), "DRAWING TITLE :", color='dimgray', va='center', ha='left', fontsize=8, zorder=103)
    ax.text(x_c2 + 20, y_kop_start + (h_kop * 0.32), page_title, color='black', fontweight='bold', va='center', ha='left', fontsize=8.5, zorder=103)
    
    ax.text(x_c3 + 20, y_kop_start + (h_kop * 0.65), "DESIGNED BY: RDP", color='black', va='center', ha='left', fontsize=8, zorder=103)
    ax.text(x_c3 + 20, y_kop_start + (h_kop * 0.30), f"PAGE : {page_num} OF {total_pages}", color='blue', fontweight='bold', va='center', ha='left', fontsize=9.5, zorder=103)


def draw_door_elevation_panel(ax, x_offset, span_dim, d_kiri, w_doorway, l_bersih, elev_lintel, t_lintel, t_pintu, side_btn, panel_title, sub_note="(Tampak dari Luar Hoistway)"):
    """Helper menggambar elevasi tampak depan 1 gawang pintu dilihat dari LUAR hoistway menghadap pintu"""
    d_kanan = span_dim - (d_kiri + w_doorway)
    
    # Judul & Catatan Sudut Pandang Panel
    ax.text(x_offset + span_dim / 2, elev_lintel + t_lintel + 290, panel_title, ha='center', va='bottom', fontsize=11.5, fontweight='bold', color='#1a73e8')
    ax.text(x_offset + span_dim / 2, elev_lintel + t_lintel + 210, sub_note, ha='center', va='bottom', fontsize=9, style='italic', color='dimgray')
    
    # Lantai & Dinding Samping
    ax.add_patch(plt.Rectangle((x_offset, -100), span_dim, 100, hatch='...', facecolor='lightgray', edgecolor='black', alpha=0.6))
    ax.plot([x_offset, x_offset], [-100, elev_lintel + t_lintel + 170], 'k-', lw=2.5)
    ax.plot([x_offset + span_dim, x_offset + span_dim], [-100, elev_lintel + t_lintel + 170], 'k-', lw=2.5)
    
    # Bukaan Doorway
    ax.plot([x_offset + d_kiri, x_offset + d_kiri], [0, elev_lintel], 'k-', lw=2)
    ax.plot([x_offset + span_dim - d_kanan, x_offset + span_dim - d_kanan], [0, elev_lintel], 'k-', lw=2)
    ax.plot([x_offset + d_kiri, x_offset + span_dim - d_kanan], [elev_lintel, elev_lintel], 'k-', lw=2)
    
    # Balok Lintel
    ax.add_patch(plt.Rectangle((x_offset, elev_lintel), span_dim, t_lintel, color='black', alpha=0.9))
    ax.text(x_offset + span_dim / 2, elev_lintel + (t_lintel / 2), "Balok Lintel Beton Cor", color='white', ha='center', va='center', fontweight='bold', fontsize=9.5)
    ax.text(x_offset + (d_kiri + span_dim - d_kanan)/2, t_pintu/2, f"Opening Pintu Sipil (Doorway)\n{w_doorway} x {elev_lintel} mm\n(Bukaan Bersih: {l_bersih} mm)", color='black', va='center', ha='center', fontsize=10, fontweight='bold')
    
    # Lubang Kabel Tombol Ø25mm
    if side_btn == "KANAN":
        x_hole = x_offset + (span_dim - d_kanan) + (d_kanan / 2)
        xy_text_pos = (x_hole + 220, 1000); rad_val = -0.15
    else:
        x_hole = x_offset + (d_kiri / 2)
        xy_text_pos = (x_hole - 220, 1000); rad_val = 0.15
        
    ax.plot([x_hole - 45, x_hole + 45], [1200, 1200], 'r-', lw=1)
    ax.plot(x_hole, 1200, 'ko', markersize=9, fillstyle='none', lw=1.5)
    ax.annotate("Lubang Kabel\nTombol Ø25mm\n(As Tombol)", xy=(x_hole, 1190), xytext=xy_text_pos,
                arrowprops=dict(arrowstyle="->", color="black", lw=1.2, connectionstyle=f"arc3,rad={rad_val}"),
                fontsize=8.5, color='black', fontweight='bold', ha='center', va='top')

    # Label Kupingan Dinding Kiri & Kanan (Perspektif Luar Hoistway)
    ax.text(x_offset + d_kiri / 2, 150, f"Dinding Kiri:\n{int(d_kiri)} mm", ha='center', va='bottom', fontsize=9, color='blue', fontweight='bold')
    ax.text(x_offset + span_dim - (d_kanan/2), 150, f"Dinding Kanan:\n{int(d_kanan)} mm", ha='center', va='bottom', fontsize=9, color='blue', fontweight='bold')

    # Garis Dimensi Vertikal (Elevasi Lintel & Tebal Lintel)
    x_dim_baseline = x_offset + span_dim + 120 
    ax.plot([x_offset + span_dim, x_dim_baseline + 100], [0, 0], 'r-', lw=0.8)
    ax.plot([x_offset + span_dim, x_dim_baseline + 100], [elev_lintel, elev_lintel], 'r-', lw=0.8)
    ax.plot([x_offset + span_dim, x_dim_baseline + 100], [elev_lintel + t_lintel, elev_lintel + t_lintel], 'r-', lw=0.8)
    ax.plot([x_dim_baseline + 50, x_dim_baseline + 50], [0, elev_lintel], 'r-', lw=1.2)
    ax.plot([x_dim_baseline + 50, x_dim_baseline + 50], [elev_lintel, elev_lintel + t_lintel], 'r-', lw=1.2)
    
    ax.text(x_dim_baseline + 75, elev_lintel / 2, f"{elev_lintel} mm\n(Gembosan)", color='red', va='center', ha='left', fontsize=9.5, fontweight='bold')
    ax.text(x_dim_baseline + 75, elev_lintel + (t_lintel / 2), f"{t_lintel} mm\nLintel", color='red', va='center', ha='left', fontsize=9.5, fontweight='bold')


def draw_plan_doorway(ax, wall_side, span_w, span_d, w_wall, d_kiri_luar, w_doorway, label_door):
    """
    Helper melubangi dinding pada denah Halaman 3 dengan sudut pandang KONSISTEN dari LUAR hoistway menghadap masing-masing pintu:
    - DEPAN (menghadap +Y)   : Kiri = X=0,         Kanan = X=span_w
    - BELAKANG (menghadap -Y): Kiri = X=span_w,    Kanan = X=0
    - KANAN (menghadap -X)   : Kiri = Y=0 (Depan), Kanan = Y=span_d (Belakang)
    - KIRI (menghadap +X)    : Kiri = Y=span_d,    Kanan = Y=0 (Depan)
    """
    if wall_side == "DEPAN":
        d_kanan_luar = span_w - (d_kiri_luar + w_doorway)
        x_start = d_kiri_luar
        x_end = d_kiri_luar + w_doorway
        ax.add_patch(plt.Rectangle((x_start, -w_wall), w_doorway, w_wall, facecolor='white', edgecolor='none', zorder=5))
        ax.plot([x_start, x_start], [-w_wall, 0], 'k-', lw=2, zorder=6)
        ax.plot([x_end, x_end], [-w_wall, 0], 'k-', lw=2, zorder=6)
        ax.text(x_start / 2, -w_wall - 140, f"Dinding Kiri:\n{int(d_kiri_luar)} mm", ha='center', va='top', fontsize=9.5, color='blue', fontweight='bold')
        ax.text((x_end + span_w)/2, -w_wall - 140, f"Dinding Kanan:\n{int(d_kanan_luar)} mm", ha='center', va='top', fontsize=9.5, color='blue', fontweight='bold')
        ax.text((x_start + x_end)/2, -65, f"{label_door}: {w_doorway} mm", ha='center', va='center', fontsize=9.5, color='black', fontweight='bold', zorder=7)
        
    elif wall_side == "BELAKANG":
        # Dilihat dari luar sisi belakang menghadap ke dalam: Kiri ada di sisi X=span_w, Kanan ada di sisi X=0
        d_kanan_luar = span_w - (d_kiri_luar + w_doorway)
        x_end = span_w - d_kiri_luar
        x_start = x_end - w_doorway
        ax.add_patch(plt.Rectangle((x_start, span_d), w_doorway, w_wall, facecolor='white', edgecolor='none', zorder=5))
        ax.plot([x_start, x_start], [span_d, span_d + w_wall], 'k-', lw=2, zorder=6)
        ax.plot([x_end, x_end], [span_d, span_d + w_wall], 'k-', lw=2, zorder=6)
        ax.text(x_start / 2, span_d + w_wall + 80, f"Dinding Kanan:\n{int(d_kanan_luar)} mm", ha='center', va='bottom', fontsize=9.5, color='blue', fontweight='bold')
        ax.text((x_end + span_w)/2, span_d + w_wall + 80, f"Dinding Kiri:\n{int(d_kiri_luar)} mm", ha='center', va='bottom', fontsize=9.5, color='blue', fontweight='bold')
        ax.text((x_start + x_end)/2, span_d + 65, f"{label_door}: {w_doorway} mm", ha='center', va='center', fontsize=9.5, color='black', fontweight='bold', zorder=7)

    elif wall_side == "KANAN":
        # Dilihat dari luar sisi kanan menghadap ke dalam: Kiri ada di sisi Y=0 (Depan), Kanan ada di sisi Y=span_d (Belakang)
        d_kanan_luar = span_d - (d_kiri_luar + w_doorway)
        y_start = d_kiri_luar
        y_end = d_kiri_luar + w_doorway
        ax.add_patch(plt.Rectangle((span_w, y_start), w_wall, w_doorway, facecolor='white', edgecolor='none', zorder=5))
        ax.plot([span_w, span_w + w_wall], [y_start, y_start], 'k-', lw=2, zorder=6)
        ax.plot([span_w, span_w + w_wall], [y_end, y_end], 'k-', lw=2, zorder=6)
        ax.text(span_w + w_wall + 80, y_start / 2, f"Dinding Kiri (Depan):\n{int(d_kiri_luar)} mm", ha='left', va='center', fontsize=9, color='blue', fontweight='bold')
        ax.text(span_w + w_wall + 80, (y_end + span_d)/2, f"Dinding Kanan (Blkg):\n{int(d_kanan_luar)} mm", ha='left', va='center', fontsize=9, color='blue', fontweight='bold')
        ax.text(span_w + 75, (y_start + y_end)/2, f"{label_door}:\n{w_doorway} mm", rotation=270, ha='center', va='center', fontsize=9, color='black', fontweight='bold', zorder=7)

    elif wall_side == "KIRI":
        # Dilihat dari luar sisi kiri menghadap ke dalam: Kiri ada di sisi Y=span_d (Belakang), Kanan ada di sisi Y=0 (Depan)
        d_kanan_luar = span_d - (d_kiri_luar + w_doorway)
        y_end = span_d - d_kiri_luar
        y_start = y_end - w_doorway
        ax.add_patch(plt.Rectangle((-w_wall, y_start), w_wall, w_doorway, facecolor='white', edgecolor='none', zorder=5))
        ax.plot([-w_wall, 0], [y_start, y_start], 'k-', lw=2, zorder=6)
        ax.plot([-w_wall, 0], [y_end, y_end], 'k-', lw=2, zorder=6)
        ax.text(-w_wall - 80, y_start / 2, f"Dinding Kanan (Depan):\n{int(d_kanan_luar)} mm", ha='right', va='center', fontsize=9, color='blue', fontweight='bold')
        ax.text(-w_wall - 80, (y_end + span_d)/2, f"Dinding Kiri (Blkg):\n{int(d_kiri_luar)} mm", ha='right', va='center', fontsize=9, color='blue', fontweight='bold')
        ax.text(-75, (y_start + y_end)/2, f"{label_door}:\n{w_doorway} mm", rotation=90, ha='center', va='center', fontsize=9, color='black', fontweight='bold', zorder=7)


# ==========================================
# G4. BALOK LOGIC ENGINE (SEPARATOR BEAM)
# ==========================================
def generate_structural_layout(lebar_sh, dalam_sh, h_pit_bersih, h_headroom, travel_list):
    h_beam = 200       
    max_clear_space = 1800  
    
    floor_y_positions = [h_pit_bersih]
    accumulated_y = h_pit_bersih
    for t_val in travel_list:
        accumulated_y += t_val
        floor_y_positions.append(accumulated_y)
        
    elements = []
    elements.append({'y_start': 0, 'y_end': 400, 'height': 400, 'type': 'space', 'label': 'Ruang Dasar PIT'})
    elements.append({'y_start': 400, 'y_end': 400 + h_beam, 'height': h_beam, 'type': 'beam', 'label': 'Separator 1'})
    
    current_y = 400 + h_beam
    
    for i, y_stop_atas in enumerate(floor_y_positions[1:]):
        y_target_beam_bawah = y_stop_atas - h_beam
        jarak_bersih_total = y_target_beam_bawah - current_y
        
        num_balok_tambahan = 0
        while True:
            sisa_ruang_bersih = jarak_bersih_total - (num_balok_tambahan * h_beam)
            celah_uji = sisa_ruang_bersih / (num_balok_tambahan + 1)
            if celah_uji <= max_clear_space:
                break
            num_balok_tambahan += 1
            
        celah_final = (jarak_bersih_total - (num_balok_tambahan * h_beam)) / (num_balok_tambahan + 1)
        
        for _ in range(num_balok_tambahan):
            elements.append({'y_start': current_y, 'y_end': current_y + celah_final, 'height': round(celah_final, 1), 'type': 'space', 'label': ''})
            current_y += celah_final
            elements.append({'y_start': current_y, 'y_end': current_y + h_beam, 'height': h_beam, 'type': 'beam', 'label': 'Separator Tambahan'})
            current_y += h_beam
            
        elements.append({'y_start': current_y, 'y_end': y_target_beam_bawah, 'height': round(y_target_beam_bawah - current_y, 1), 'type': 'space', 'label': ''})
        elements.append({'y_start': y_target_beam_bawah, 'y_end': y_stop_atas, 'height': h_beam, 'type': 'beam', 'label': f'STOP {i+2}'})
        current_y = y_stop_atas

    y_stop_terakhir = floor_y_positions[-1]
    y_total_hoistway = y_stop_terakhir + h_headroom
    
    y_top_beam_bawah = y_total_hoistway - h_beam
    y_separator_kedua_atas = y_top_beam_bawah - 400
    y_separator_kedua_bawah = y_separator_kedua_atas - h_beam
    jarak_sisa_headroom = y_separator_kedua_bawah - y_stop_terakhir
    
    num_balok_hr = 0
    while True:
        sisa_hr = jarak_sisa_headroom - (num_balok_hr * h_beam)
        celah_hr_uji = sisa_hr / (num_balok_hr + 1)
        if celah_hr_uji <= max_clear_space:
            break
        num_balok_hr += 1
        
    celah_hr_final = (jarak_sisa_headroom - (num_balok_hr * h_beam)) / (num_balok_hr + 1)
    
    for _ in range(num_balok_hr):
        elements.append({'y_start': y_stop_terakhir, 'y_end': y_stop_terakhir + celah_hr_final, 'height': round(celah_hr_final, 1), 'type': 'space', 'label': ''})
        y_stop_terakhir += celah_hr_final
        elements.append({'y_start': y_stop_terakhir, 'y_end': y_stop_terakhir + h_beam, 'height': h_beam, 'type': 'beam', 'label': 'Separator Tambahan Headroom'})
        y_stop_terakhir += h_beam
        
    elements.append({'y_start': y_stop_terakhir, 'y_end': y_separator_kedua_bawah, 'height': round(y_separator_kedua_bawah - y_stop_terakhir, 1), 'type': 'space', 'label': ''})
    elements.append({'y_start': y_separator_kedua_bawah, 'y_end': y_separator_kedua_atas, 'height': h_beam, 'type': 'beam', 'label': 'Separator Kedua (Rule 3)'})
    elements.append({'y_start': y_separator_kedua_atas, 'y_end': y_top_beam_bawah, 'height': 400, 'type': 'space', 'label': 'Celah 400mm Atas'})
    elements.append({'y_start': y_top_beam_bawah, 'y_end': y_total_hoistway, 'height': h_beam, 'type': 'beam', 'label': 'TOP'})

    return elements, y_total_hoistway, floor_y_positions

def make_balok_pdf(elements, lebar_sh, dalam_sh, total_height, travel_list, floor_y_positions, h_headroom, lebar_p_bersih, width_doorway, tinggi_p, tinggi_gembosan, tebal_l, dinding_kiri, config_sep, nama_project, no_kontrak, side_tombol, door_config, lebar_p2, width_doorway2, dinding_awal2, side_tombol2):
    buffer = io.BytesIO()
    w_wall = 200
    w_sep = 100
    elevasi_lintel = tinggi_gembosan
    is_two_doors = door_config != "1 Sisi (Depan)"
    
    with PdfPages(buffer) as pdf:
        # HALAMAN 1 (TIDAK BERUBAH)
        fig1, ax1 = plt.subplots(figsize=(10, 22))
        x_min, x_max = -1200, lebar_sh + 2300
        y_min, y_max = -600, total_height + 400
        ax1.set_xlim(x_min, x_max); ax1.set_ylim(y_min, y_max); ax1.axis('off')
        
        col1_x = 500
        ax1.plot([col1_x, col1_x], [0, total_height], 'k-', lw=2.5)
        ax1.plot([col1_x + lebar_sh, col1_x + lebar_sh], [0, total_height], 'k-', lw=2.5)
        
        for el in elements:
            if el['type'] == 'beam':
                ax1.add_patch(plt.Rectangle((col1_x, el['y_start']), lebar_sh, el['height'], color='black', alpha=0.9))

        for idx, pos in enumerate(floor_y_positions):
            ax1.text(col1_x - 80, pos, f'STOP {idx + 1}-', color='blue', va='center', ha='right', fontweight='bold', fontsize=11)
            ax1.plot([col1_x - 150, col1_x + lebar_sh + 80], [pos, pos], 'b--', lw=1.2)
        ax1.text(col1_x - 80, total_height, 'TOP-', color='blue', va='center', ha='right', fontweight='bold', fontsize=11)
        ax1.plot([col1_x - 150, col1_x + lebar_sh + 80], [total_height, total_height], 'b--', lw=1.2)

        ax1.plot([200, 350], [0, 0], 'r-', lw=1.2); ax1.plot([275, 275], [0, total_height], 'r-', lw=1.2)
        ax1.text(250, floor_y_positions[0] / 2, f"{int(floor_y_positions[0])} (PIT)", color='red', va='center', ha='right', fontweight='bold', fontsize=10)
        for idx, travel_val in enumerate(travel_list):
            ax1.text(250, (floor_y_positions[idx] + floor_y_positions[idx+1])/2, f"{travel_val}", color='red', va='center', ha='right', fontweight='bold', fontsize=10)
        ax1.text(250, (floor_y_positions[-1] + total_height)/2, f"{int(h_headroom)} (Headroom)", color='red', va='center', ha='right', fontweight='bold', fontsize=10)

        x_right_dim = col1_x + lebar_sh + 200
        ax1.plot([x_right_dim + 50, x_right_dim + 50], [0, total_height], 'r-', lw=1)
        for el in elements:
            if el['height'] < 100 and el['type'] == 'space': continue
            ax1.plot([x_right_dim, x_right_dim + 100], [el['y_end'], el['y_end']], 'r-', lw=0.8)
            mid_y = (el['y_start'] + el['y_end']) / 2
            if el['type'] == 'beam':
                ax1.text(x_right_dim + 130, mid_y, f"{int(el['height'])} (Beam)", color='black', va='center', ha='left', fontsize=10, fontweight='bold')
            else:
                ax1.text(x_right_dim + 130, mid_y, f"{int(el['height'])}", color='dimgray', va='center', ha='left', fontsize=9.5)

        ax1.plot([col1_x, col1_x + lebar_sh], [-180, -180], 'r-', lw=1.5)
        ax1.text(col1_x + (lebar_sh/2), -220, "Sepanjang Shaft", color='red', ha='center', va='top', fontweight='bold', fontsize=11)
        
        draw_rigid_border(ax1, x_min + 50, x_max - 50, y_min + 50, y_max - 50, nama_project, no_kontrak, "SEPARATOR BEAM", 1, 3, zoom_logo=0.15)
        plt.tight_layout(); pdf.savefig(fig1, dpi=300); plt.close(fig1)

        # HALAMAN 2 (ELEVASI OPENING PINTU - SUDUT PANDANG DARI LUAR HOISTWAY)
        if not is_two_doors:
            fig2, ax2 = plt.subplots(figsize=(10, 12))
            x_p2_min, x_p2_max = -400, lebar_sh + 900
            y_p2_min, y_p2_max = -350, elevasi_lintel + tebal_l + 500  
            ax2.set_xlim(x_p2_min, x_p2_max); ax2.set_ylim(y_p2_min, y_p2_max); ax2.axis('off')
            
            draw_door_elevation_panel(
                ax2, 0, lebar_sh, dinding_kiri, width_doorway, lebar_p_bersih,
                elevasi_lintel, tebal_l, tinggi_p, side_tombol, "PINTU UTAMA (SISI DEPAN)"
            )
            draw_rigid_border(ax2, x_p2_min + 30, x_p2_max - 30, y_p2_min + 30, y_p2_max - 30, nama_project, no_kontrak, "OPENING PINTU", 2, 3, zoom_logo=0.25)
            plt.tight_layout(); pdf.savefig(fig2, dpi=300); plt.close(fig2)
        else:
            is_adjacent = "Adjacent" in door_config
            span_door2 = dalam_sh if is_adjacent else lebar_sh
            sisi_p2_nama = "SISI KANAN" if "Kanan" in door_config else ("SISI KIRI" if "Kiri" in door_config else "SISI BELAKANG")
            
            gap_between = 950
            total_span_x = lebar_sh + gap_between + span_door2
            fig2, ax2 = plt.subplots(figsize=(16, 11))
            x_p2_min, x_p2_max = -450, total_span_x + 850
            y_p2_min, y_p2_max = -400, elevasi_lintel + tebal_l + 520
            ax2.set_xlim(x_p2_min, x_p2_max); ax2.set_ylim(y_p2_min, y_p2_max); ax2.axis('off')
            
            draw_door_elevation_panel(
                ax2, 0, lebar_sh, dinding_kiri, width_doorway, lebar_p_bersih,
                elevasi_lintel, tebal_l, tinggi_p, side_tombol, "PINTU 1 (SISI DEPAN)"
            )
            draw_door_elevation_panel(
                ax2, lebar_sh + gap_between, span_door2, dinding_awal2, width_doorway2, lebar_p2,
                elevasi_lintel, tebal_l, tinggi_p, side_tombol2, f"PINTU 2 ({sisi_p2_nama})"
            )
            draw_rigid_border(ax2, x_p2_min + 30, x_p2_max - 30, y_p2_min + 30, y_p2_max - 30, nama_project, no_kontrak, f"OPENING PINTU ({door_config.upper()})", 2, 3, zoom_logo=0.25)
            plt.tight_layout(); pdf.savefig(fig2, dpi=300); plt.close(fig2)

        # HALAMAN 3 (DENAH HOISTWAY & BALOK SEPARATOR)
        fig3, ax3 = plt.subplots(figsize=(12, 13))
        ax3.set_aspect('equal', adjustable='box')
        x_p3_min, x_p3_max = -1150, lebar_sh + 1950
        y_p3_min, y_p3_max = -1200, dalam_sh + 1250
        ax3.set_xlim(x_p3_min, x_p3_max); ax3.set_ylim(y_p3_min, y_p3_max); ax3.axis('off')
        
        ax3.add_patch(plt.Rectangle((-w_wall, -w_wall), lebar_sh + (2*w_wall), dalam_sh + (2*w_wall), facecolor='none', edgecolor='black', lw=2.5))
        ax3.add_patch(plt.Rectangle((0, 0), lebar_sh, dalam_sh, facecolor='whitesmoke', edgecolor='black', lw=1.5))
        
        # Lubang Pintu 1 (Depan) - Sudut pandang dari luar hoistway
        draw_plan_doorway(ax3, "DEPAN", lebar_sh, dalam_sh, w_wall, dinding_kiri, width_doorway, "Pintu 1 (Depan)")
        
        # Lubang Pintu 2 - Sudut pandang dari luar hoistway menghadap masing-masing pintu
        if door_config == "2 Sisi Berseberangan (Depan & Belakang)":
            draw_plan_doorway(ax3, "BELAKANG", lebar_sh, dalam_sh, w_wall, dinding_awal2, width_doorway2, "Pintu 2 (Belakang)")
        elif door_config == "2 Sisi Adjacent (Depan & Kanan)":
            draw_plan_doorway(ax3, "KANAN", lebar_sh, dalam_sh, w_wall, dinding_awal2, width_doorway2, "Pintu 2 (Kanan)")
        elif door_config == "2 Sisi Adjacent (Depan & Kiri)":
            draw_plan_doorway(ax3, "KIRI", lebar_sh, dalam_sh, w_wall, dinding_awal2, width_doorway2, "Pintu 2 (Kiri)")

        # Aturan Penempatan Balok Separator sesuai Konfigurasi Pintu
        if door_config == "2 Sisi Adjacent (Depan & Kanan)":
            plot_kiri = True
            plot_kanan = False
            plot_belakang = config_sep in ['BELAKANG', '3-SISI']
        elif door_config == "2 Sisi Adjacent (Depan & Kiri)":
            plot_kiri = False
            plot_kanan = True
            plot_belakang = config_sep in ['BELAKANG', '3-SISI']
        elif door_config == "2 Sisi Berseberangan (Depan & Belakang)":
            plot_kiri = config_sep in ['KIRI', 'KANAN-KIRI', '3-SISI']
            plot_kanan = config_sep in ['KANAN', 'KANAN-KIRI', '3-SISI']
            plot_belakang = False
        else:
            plot_kiri = config_sep in ['KIRI', 'KANAN-KIRI', '3-SISI']
            plot_kanan = config_sep in ['KANAN', 'KANAN-KIRI', '3-SISI']
            plot_belakang = config_sep in ['BELAKANG', '3-SISI']
            
        if plot_kiri:
            ax3.add_patch(plt.Rectangle((-w_sep, 0), w_sep, dalam_sh, facecolor='black', edgecolor='black', alpha=0.8))
            ax3.text(-w_sep - 220, dalam_sh/2, "Balok Separator Kiri (Outside)", rotation=90, va='center', ha='right', fontsize=9.5, fontweight='bold')
        if plot_kanan:
            ax3.add_patch(plt.Rectangle((lebar_sh, 0), w_sep, dalam_sh, facecolor='black', edgecolor='black', alpha=0.8))
            ax3.text(lebar_sh + w_sep + 220, dalam_sh/2, "Balok Separator Kanan (Outside)", rotation=270, va='center', ha='left', fontsize=9.5, fontweight='bold')
        if plot_belakang:
            ax3.add_patch(plt.Rectangle((0, dalam_sh), lebar_sh, w_sep, facecolor='black', edgecolor='black', alpha=0.8))

        ax3.text(lebar_sh/2, dalam_sh/2, f"CLEAR AREA SHAFT\n{lebar_sh} mm x {dalam_sh} mm\n({door_config})", color='red', ha='center', va='center', fontweight='bold', fontsize=11.5)
        ax3.text(lebar_sh/2, dalam_sh + w_sep + 360, "REKOMENDASI POSISI SEPARATOR BEAM DI LUAR CLEAR AREA", color='darkgreen', ha='center', fontweight='bold', fontsize=10)

        y_dim_width = dalam_sh + w_sep + 540
        ax3.plot([0, lebar_sh], [y_dim_width, y_dim_width], 'r-', lw=1.2)
        ax3.plot([0, 0], [dalam_sh, y_dim_width + 40], 'r-', lw=0.6)
        ax3.plot([lebar_sh, lebar_sh], [dalam_sh, y_dim_width + 40], 'r-', lw=0.6)
        ax3.text(lebar_sh / 2, y_dim_width + 50, f"Clear Width of Shaft: {lebar_sh} mm", color='red', ha='center', va='bottom', fontweight='bold', fontsize=11)
        
        x_dim_depth = lebar_sh + w_sep + 480
        ax3.plot([x_dim_depth, x_dim_depth], [0, dalam_sh], 'r-', lw=1.2)
        ax3.plot([lebar_sh, x_dim_depth + 40], [0, 0], 'r-', lw=0.6)
        ax3.plot([lebar_sh, x_dim_depth + 40], [dalam_sh, dalam_sh], 'r-', lw=0.6)
        ax3.text(x_dim_depth + 50, dalam_sh / 2, f"Clear Depth of Shaft:\n{dalam_sh} mm", color='red', va='center', ha='left', fontweight='bold', fontsize=11)

        draw_rigid_border(ax3, x_p3_min + 30, x_p3_max - 30, y_p3_min + 150, y_p3_max - 30, nama_project, no_kontrak, "HOISTWAY", 3, 3, zoom_logo=0.25)
        plt.tight_layout(); pdf.savefig(fig3, dpi=300); plt.close(fig3)

    buffer.seek(0)
    return buffer

# ==========================================
# G5. KOLOM LOGIC ENGINE (STRUKTUR PILAR)
# ==========================================
def make_kolom_pdf(lebar_sh, dalam_sh, h_pit_bersih, h_headroom, travel_list, posisi_rel_kabin, track_gauge_cwt, tebal_rail_cwt, tebal_pintu_luar, celah_daun_pintu, tebal_kolom, lebar_p_bersih, width_doorway, tinggi_p, tinggi_gembosan, tebal_l, dinding_kiri, nama_project, no_kontrak, posisi_cwt, side_tombol, jarak_rel_ke_cwt, sisa_belakang, door_config, lebar_p2, width_doorway2, dinding_awal2, side_tombol2):
    buffer = io.BytesIO()
    elevasi_lintel = tinggi_gembosan
    w_wall = 200
    is_two_doors = door_config != "1 Sisi (Depan)"
    is_adjacent = "Adjacent" in door_config

    effective_cwt = posisi_cwt
    if door_config == "2 Sisi Adjacent (Depan & Kanan)" and posisi_cwt == 'K':
        effective_cwt = 'B'
    elif door_config == "2 Sisi Adjacent (Depan & Kiri)" and posisi_cwt == 'L':
        effective_cwt = 'B'

    if effective_cwt == 'B':
        y_pintu_kabin = celah_daun_pintu + tebal_pintu_luar
        as_kabin_dari_depan = y_pintu_kabin + posisi_rel_kabin
        y_start_kabin = as_kabin_dari_depan - (tebal_kolom / 2)
        y_end_kabin = as_kabin_dari_depan + (tebal_kolom / 2)
        sisa_belakang_kabin = dalam_sh - y_end_kabin

        y_start_cwt_belakang = dalam_sh - tebal_kolom
        y_end_cwt_belakang = dalam_sh
        y_start_cwt_depan = y_start_cwt_belakang
        y_end_cwt_depan = y_end_cwt_belakang
        celah_bersih_cwt = 0
        sisa_belakang_cwt = 0
    else:
        as_kabin_dari_depan = posisi_rel_kabin + celah_daun_pintu + tebal_pintu_luar
        y_start_kabin = as_kabin_dari_depan - (tebal_kolom / 2)
        y_end_kabin = as_kabin_dari_depan + (tebal_kolom / 2)
        sisa_belakang_kabin = dalam_sh - y_end_kabin

        as_cwt_depan = as_kabin_dari_depan - ((track_gauge_cwt / 2) + tebal_rail_cwt)
        y_start_cwt_depan = as_cwt_depan - (tebal_kolom / 2)
        y_end_cwt_depan = as_cwt_depan + (tebal_kolom / 2)

        as_cwt_belakang = as_kabin_dari_depan + ((track_gauge_cwt / 2) + tebal_rail_cwt)
        y_start_cwt_belakang = as_cwt_belakang - (tebal_kolom / 2)
        y_end_cwt_belakang = as_cwt_belakang + (tebal_kolom / 2)

        celah_bersih_cwt = y_start_cwt_belakang - y_end_cwt_depan
        sisa_belakang_cwt = dalam_sh - y_end_cwt_belakang

    floor_y_positions = [h_pit_bersih]
    accumulated_y = h_pit_bersih
    for t_val in travel_list:
        accumulated_y += t_val
        floor_y_positions.append(accumulated_y)
    total_height = floor_y_positions[-1] + h_headroom

    with PdfPages(buffer) as pdf:
        # HALAMAN 1 (TIDAK BERUBAH)
        fig1, ax1 = plt.subplots(figsize=(14, 22))
        x_min, x_max = -400, (dalam_sh * 2) + 800
        y_min, y_max = -600, total_height + 400
        ax1.set_xlim(x_min, x_max); ax1.set_ylim(y_min, y_max); ax1.axis('off')
        
        x_offset_l = 0
        ax1.plot([x_offset_l, x_offset_l], [0, total_height], 'k-', lw=2)
        ax1.plot([x_offset_l + dalam_sh, x_offset_l + dalam_sh], [0, total_height], 'k-', lw=2)
        
        x_offset_r = dalam_sh + 400
        ax1.plot([x_offset_r, x_offset_r], [0, total_height], 'k-', lw=2)
        ax1.plot([x_offset_r + dalam_sh, x_offset_r + dalam_sh], [0, total_height], 'k-', lw=2)
        
        if effective_cwt == 'L':
            ax1.add_patch(plt.Rectangle((x_offset_l + y_start_kabin, 0), tebal_kolom, total_height, facecolor='gray', alpha=0.7, hatch='//'))
            ax1.text(x_offset_l + dalam_sh/2, -100, "TAMPAK SAMPING SISI KIRI\n(STRUKTUR REL KABIN)", ha='center', va='top', fontsize=10, fontweight='bold')
            ax1.add_patch(plt.Rectangle((x_offset_r + y_start_cwt_depan, 0), tebal_kolom, total_height, facecolor='gray', alpha=0.7, hatch='//'))
            ax1.add_patch(plt.Rectangle((x_offset_r + y_start_cwt_belakang, 0), tebal_kolom, total_height, facecolor='gray', alpha=0.7, hatch='//'))
            ax1.text(x_offset_r + dalam_sh/2, -100, "TAMPAK SAMPING SISI KANAN\n(STRUKTUR 2x SISI CWT)", ha='center', va='top', fontsize=10, fontweight='bold')
        elif effective_cwt == 'K':
            ax1.add_patch(plt.Rectangle((x_offset_l + y_start_cwt_depan, 0), tebal_kolom, total_height, facecolor='gray', alpha=0.7, hatch='//'))
            ax1.add_patch(plt.Rectangle((x_offset_l + y_start_cwt_belakang, 0), tebal_kolom, total_height, facecolor='gray', alpha=0.7, hatch='//'))
            ax1.text(x_offset_l + dalam_sh/2, -100, "TAMPAK SAMPING SISI KIRI\n(STRUKTUR 2x SISI CWT)", ha='center', va='top', fontsize=10, fontweight='bold')
            ax1.add_patch(plt.Rectangle((x_offset_r + y_start_kabin, 0), tebal_kolom, total_height, facecolor='gray', alpha=0.7, hatch='//'))
            ax1.text(x_offset_r + dalam_sh/2, -100, "TAMPAK SAMPING SISI KANAN\n(STRUKTUR REL KABIN)", ha='center', va='top', fontsize=10, fontweight='bold')
        else:
            ax1.add_patch(plt.Rectangle((x_offset_l + y_start_kabin, 0), tebal_kolom, total_height, facecolor='gray', alpha=0.7, hatch='//'))
            ax1.text(x_offset_l + dalam_sh/2, -100, "TAMPAK SAMPING SISI KIRI\n(STRUKTUR REL KABIN)", ha='center', va='top', fontsize=10, fontweight='bold')
            ax1.add_patch(plt.Rectangle((x_offset_r + y_start_kabin, 0), tebal_kolom, total_height, facecolor='gray', alpha=0.7, hatch='//'))
            ax1.text(x_offset_r + dalam_sh/2, -100, "TAMPAK SAMPING SISI KANAN\n(STRUKTUR REL KABIN)", ha='center', va='top', fontsize=10, fontweight='bold')

        ax1.plot([-50, (dalam_sh * 2) + 500], [0, 0], 'k-', lw=1.5)
        for idx, pos in enumerate(floor_y_positions):
            ax1.text(-70, pos, f'STOP {idx + 1}-', color='blue', va='center', ha='right', fontweight='bold', fontsize=11)
            ax1.plot([-100, (dalam_sh * 2) + 500], [pos, pos], 'b--', lw=1)
        ax1.text(-70, total_height, 'TOP-', color='blue', va='center', ha='right', fontweight='bold', fontsize=11)
        ax1.plot([-100, (dalam_sh * 2) + 500], [total_height, total_height], 'b--', lw=1)

        ax1.plot([-250, -250], [0, total_height], 'r-', lw=1.2)
        ax1.text(-280, floor_y_positions[0] / 2, f"{int(floor_y_positions[0])} (PIT)", color='red', va='center', ha='right', fontweight='bold', fontsize=10)
        for idx, travel_val in enumerate(travel_list):
            ax1.text(-280, (floor_y_positions[idx] + floor_y_positions[idx+1])/2, f"{travel_val}", color='red', va='center', ha='right', fontweight='bold', fontsize=10)
        ax1.text(-280, (floor_y_positions[-1] + total_height)/2, f"{int(h_headroom)} (Overhead)", color='red', va='center', ha='right', fontweight='bold', fontsize=10)

        txt_orientasi = "CWT SISI KIRI" if effective_cwt == 'K' else ("CWT SISI KANAN" if effective_cwt == 'L' else "CWT SISI BELAKANG")
        draw_rigid_border(ax1, x_min + 50, x_max - 50, y_min + 50, y_max - 50, nama_project, no_kontrak, f"STRUKTUR LIFT ({txt_orientasi})", 1, 3, zoom_logo=0.15)
        plt.tight_layout(); pdf.savefig(fig1, dpi=300); plt.close(fig1)

        # HALAMAN 2 (ELEVASI OPENING PINTU - SUDUT PANDANG DARI LUAR HOISTWAY)
        if not is_two_doors:
            fig2, ax2 = plt.subplots(figsize=(10, 12))
            x_p2_min, x_p2_max = -400, lebar_sh + 900
            y_p2_min, y_p2_max = -350, elevasi_lintel + tebal_l + 500  
            ax2.set_xlim(x_p2_min, x_p2_max); ax2.set_ylim(y_p2_min, y_p2_max); ax2.axis('off')
            
            draw_door_elevation_panel(
                ax2, 0, lebar_sh, dinding_kiri, width_doorway, lebar_p_bersih,
                elevasi_lintel, tebal_l, tinggi_p, side_tombol, "PINTU UTAMA (SISI DEPAN)"
            )
            draw_rigid_border(ax2, x_p2_min + 30, x_p2_max - 30, y_p2_min + 30, y_p2_max - 30, nama_project, no_kontrak, "OPENING PINTU", 2, 3, zoom_logo=0.25)
            plt.tight_layout(); pdf.savefig(fig2, dpi=300); plt.close(fig2)
        else:
            span_door2 = dalam_sh if is_adjacent else lebar_sh
            sisi_p2_nama = "SISI KANAN" if "Kanan" in door_config else ("SISI KIRI" if "Kiri" in door_config else "SISI BELAKANG")
            
            gap_between = 950
            total_span_x = lebar_sh + gap_between + span_door2
            fig2, ax2 = plt.subplots(figsize=(16, 11))
            x_p2_min, x_p2_max = -450, total_span_x + 850
            y_p2_min, y_p2_max = -400, elevasi_lintel + tebal_l + 520
            ax2.set_xlim(x_p2_min, x_p2_max); ax2.set_ylim(y_p2_min, y_p2_max); ax2.axis('off')
            
            draw_door_elevation_panel(
                ax2, 0, lebar_sh, dinding_kiri, width_doorway, lebar_p_bersih,
                elevasi_lintel, tebal_l, tinggi_p, side_tombol, "PINTU 1 (SISI DEPAN)"
            )
            draw_door_elevation_panel(
                ax2, lebar_sh + gap_between, span_door2, dinding_awal2, width_doorway2, lebar_p2,
                elevasi_lintel, tebal_l, tinggi_p, side_tombol2, f"PINTU 2 ({sisi_p2_nama})"
            )
            draw_rigid_border(ax2, x_p2_min + 30, x_p2_max - 30, y_p2_min + 30, y_p2_max - 30, nama_project, no_kontrak, f"OPENING PINTU ({door_config.upper()})", 2, 3, zoom_logo=0.25)
            plt.tight_layout(); pdf.savefig(fig2, dpi=300); plt.close(fig2)

        # HALAMAN 3 (DENAH POTONGAN STRUKTUR KOLOM UTAMA - TAMPAK ATAS)
        fig3, ax3 = plt.subplots(figsize=(14, 15))
        ax3.set_aspect('equal', adjustable='box')  
        x_p3_min, x_p3_max = -1350, lebar_sh + 2250
        y_p3_min, y_p3_max = -1250, dalam_sh + 1250
        ax3.set_xlim(x_p3_min, x_p3_max); ax3.set_ylim(y_p3_min, y_p3_max); ax3.axis('off')
        
        ax3.add_patch(plt.Rectangle((-w_wall, -w_wall), lebar_sh + (2*w_wall), dalam_sh + (2*w_wall), facecolor='none', edgecolor='black', lw=2.5))
        ax3.add_patch(plt.Rectangle((0, 0), lebar_sh, dalam_sh, facecolor='whitesmoke', edgecolor='black', lw=1.5))
        
        # Lubang Pintu 1 (Depan) - Sudut pandang dari luar hoistway
        draw_plan_doorway(ax3, "DEPAN", lebar_sh, dalam_sh, w_wall, dinding_kiri, width_doorway, "Doorway 1")
        
        # Lubang Pintu 2 - Sudut pandang dari luar hoistway menghadap masing-masing pintu
        if door_config == "2 Sisi Berseberangan (Depan & Belakang)":
            draw_plan_doorway(ax3, "BELAKANG", lebar_sh, dalam_sh, w_wall, dinding_awal2, width_doorway2, "Doorway 2")
        elif door_config == "2 Sisi Adjacent (Depan & Kanan)":
            draw_plan_doorway(ax3, "KANAN", lebar_sh, dalam_sh, w_wall, dinding_awal2, width_doorway2, "Doorway 2")
        elif door_config == "2 Sisi Adjacent (Depan & Kiri)":
            draw_plan_doorway(ax3, "KIRI", lebar_sh, dalam_sh, w_wall, dinding_awal2, width_doorway2, "Doorway 2")

        ax3.text(lebar_sh/2, dalam_sh/2, f"CLEAR AREA SHAFT LIFT\n{lebar_sh} mm x {dalam_sh} mm\n({door_config})", color='red', ha='center', va='center', fontweight='bold', fontsize=11.5)

        x_l1, x_l2 = -260, -620     
        x_r1, x_r2 = lebar_sh + tebal_kolom + 260, lebar_sh + tebal_kolom + 620 

        if effective_cwt == 'L':
            ax3.add_patch(plt.Rectangle((-tebal_kolom, y_start_kabin), tebal_kolom, tebal_kolom, facecolor='black', edgecolor='black'))
            ax3.add_patch(plt.Rectangle((lebar_sh, y_start_cwt_depan), tebal_kolom, tebal_kolom, facecolor='black', edgecolor='black'))
            ax3.add_patch(plt.Rectangle((lebar_sh, y_start_cwt_belakang), tebal_kolom, tebal_kolom, facecolor='black', edgecolor='black'))
            
            ax3.plot([0, x_l2], [0, 0], 'r-', lw=0.5); ax3.plot([0, x_l1], [y_start_kabin, y_start_kabin], 'r-', lw=0.5)
            ax3.plot([0, x_l1], [y_end_kabin, y_end_kabin], 'r-', lw=0.5); ax3.plot([0, x_l2], [dalam_sh, dalam_sh], 'r-', lw=0.5)
            ax3.plot([x_l1, x_l1], [0, dalam_sh], 'r-', lw=1); ax3.plot([x_l2, x_l2], [0, dalam_sh], 'r-', lw=1)
            
            ax3.text(x_l1 + 35, y_start_kabin / 2, f"{int(y_start_kabin)} mm", color='red', va='center', ha='left', fontweight='bold', fontsize=9.5)
            ax3.text(x_l1 - 35, (y_start_kabin + y_end_kabin)/2, f"{tebal_kolom} mm\n(Kolom Kiri)", color='black', va='center', ha='right', fontweight='bold', fontsize=9)
            ax3.text(x_l1 + 35, y_end_kabin + (sisa_belakang_kabin/2), f"{int(sisa_belakang_kabin)} mm", color='red', va='center', ha='left', fontweight='bold', fontsize=9.5)
            
            ax3.plot([lebar_sh, x_r2], [0, 0], 'r-', lw=0.5); ax3.plot([lebar_sh, x_r1], [y_start_cwt_depan, y_start_cwt_depan], 'r-', lw=0.5)
            ax3.plot([lebar_sh, x_r1], [y_end_cwt_depan, y_end_cwt_depan], 'r-', lw=0.5); ax3.plot([lebar_sh, x_r1], [y_start_cwt_belakang, y_start_cwt_belakang], 'r-', lw=0.5)
            ax3.plot([lebar_sh, x_r1], [y_end_cwt_belakang, y_end_cwt_belakang], 'r-', lw=0.5); ax3.plot([lebar_sh, x_r2], [dalam_sh, dalam_sh], 'r-', lw=0.5)
            ax3.plot([x_r1, x_r1], [0, dalam_sh], 'r-', lw=1); ax3.plot([x_r2, x_r2], [0, dalam_sh], 'r-', lw=1)
            
            ax3.text(x_r1 - 35, y_start_cwt_depan / 2, f"{int(y_start_cwt_depan)} mm\n(Sisa Depan)", color='red', va='center', ha='right', fontweight='bold', fontsize=9.5)
            ax3.text(x_r1 + 35, (y_start_cwt_depan + y_end_cwt_depan)/2, f"{tebal_kolom} mm\n(Kolom CWT 1)", color='black', va='center', ha='left', fontsize=8.5, fontweight='bold')
            ax3.text(x_r1 - 35, (y_end_cwt_depan + y_start_cwt_belakang)/2, f"{int(celah_bersih_cwt)} mm\n(Celah Tengah)", color='darkgreen', va='center', ha='right', fontweight='bold', fontsize=9.5)
            ax3.text(x_r1 + 35, (y_start_cwt_belakang + y_end_cwt_belakang)/2, f"{tebal_kolom} mm\n(Kolom CWT 2)", color='black', va='center', ha='left', fontsize=8.5, fontweight='bold')
            ax3.text(x_r1 - 35, y_end_cwt_belakang + (sisa_belakang_cwt/2), f"{int(sisa_belakang_cwt)} mm\n(Sisa Belakang)", color='red', va='center', ha='right', fontweight='bold', fontsize=9.5)
            
        elif effective_cwt == 'K':
            ax3.add_patch(plt.Rectangle((-tebal_kolom, y_start_cwt_depan), tebal_kolom, tebal_kolom, facecolor='black', edgecolor='black'))
            ax3.add_patch(plt.Rectangle((-tebal_kolom, y_start_cwt_belakang), tebal_kolom, tebal_kolom, facecolor='black', edgecolor='black'))
            ax3.add_patch(plt.Rectangle((lebar_sh, y_start_kabin), tebal_kolom, tebal_kolom, facecolor='black', edgecolor='black'))
            
            ax3.plot([0, x_l2], [0, 0], 'r-', lw=0.5); ax3.plot([0, x_l1], [y_start_cwt_depan, y_start_cwt_depan], 'r-', lw=0.5)
            ax3.plot([0, x_l1], [y_end_cwt_depan, y_end_cwt_depan], 'r-', lw=0.5); ax3.plot([0, x_l1], [y_start_cwt_belakang, y_start_cwt_belakang], 'r-', lw=0.5)
            ax3.plot([0, x_l1], [y_end_cwt_belakang, y_end_cwt_belakang], 'r-', lw=0.5); ax3.plot([0, x_l2], [dalam_sh, dalam_sh], 'r-', lw=0.5)
            ax3.plot([x_l1, x_l1], [0, dalam_sh], 'r-', lw=1); ax3.plot([x_l2, x_l2], [0, dalam_sh], 'r-', lw=1)
            
            ax3.text(x_l1 + 35, y_start_cwt_depan / 2, f"{int(y_start_cwt_depan)} mm\n(Sisa Depan)", color='red', va='center', ha='left', fontweight='bold', fontsize=9.5)
            ax3.text(x_l1 - 35, (y_start_cwt_depan + y_end_cwt_depan)/2, f"{tebal_kolom} mm\n(Kolom CWT 1)", color='black', va='center', ha='right', fontsize=8.5, fontweight='bold')
            ax3.text(x_l1 + 35, (y_end_cwt_depan + y_start_cwt_belakang)/2, f"{int(celah_bersih_cwt)} mm\n(Celah Tengah)", color='darkgreen', va='center', ha='left', fontweight='bold', fontsize=9.5)
            ax3.text(x_l1 - 35, (y_start_cwt_belakang + y_end_cwt_belakang)/2, f"{tebal_kolom} mm\n(Kolom CWT 2)", color='black', va='center', ha='right', fontsize=8.5, fontweight='bold')
            ax3.text(x_l1 + 35, y_end_cwt_belakang + (sisa_belakang_cwt/2), f"{int(sisa_belakang_cwt)} mm\n(Sisa Belakang)", color='red', va='center', ha='left', fontweight='bold', fontsize=9.5)
            
            ax3.plot([lebar_sh, x_r2], [0, 0], 'r-', lw=0.5); ax3.plot([lebar_sh, x_r1], [y_start_kabin, y_start_kabin], 'r-', lw=0.5)
            ax3.plot([lebar_sh, x_r1], [y_end_kabin, y_end_kabin], 'r-', lw=0.5); ax3.plot([lebar_sh, x_r2], [dalam_sh, dalam_sh], 'r-', lw=0.5)
            ax3.plot([x_r1, x_r1], [0, dalam_sh], 'r-', lw=1); ax3.plot([x_r2, x_r2], [0, dalam_sh], 'r-', lw=1)
            
            ax3.text(x_r1 - 35, y_start_kabin / 2, f"{int(y_start_kabin)} mm", color='red', va='center', ha='right', fontweight='bold', fontsize=9.5)
            ax3.text(x_r1 + 35, (y_start_kabin + y_end_kabin)/2, f"{tebal_kolom} mm\n(Kolom Kanan)", color='black', va='center', ha='left', fontsize=9)
            ax3.text(x_r1 - 35, y_end_kabin + (sisa_belakang_kabin/2), f"{int(sisa_belakang_kabin)} mm", color='red', va='center', ha='right', fontweight='bold', fontsize=9.5)
            
        else:
            has_left_col = door_config != "2 Sisi Adjacent (Depan & Kiri)"
            has_right_col = door_config != "2 Sisi Adjacent (Depan & Kanan)"
            
            x_tengah = lebar_sh / 2
            x_start_cwt_l = x_tengah - (track_gauge_cwt / 2) - tebal_kolom
            x_start_cwt_r = x_tengah + (track_gauge_cwt / 2)
            
            if has_left_col:
                ax3.add_patch(plt.Rectangle((-tebal_kolom, y_start_kabin), tebal_kolom, tebal_kolom, facecolor='black', edgecolor='black'))
                ax3.plot([0, x_l1], [y_start_kabin, y_start_kabin], 'r-', lw=0.5)
                ax3.plot([0, x_l1], [y_end_kabin, y_end_kabin], 'r-', lw=0.5)
                ax3.plot([x_l1, x_l1], [0, dalam_sh], 'r-', lw=1)
                ax3.text(x_l1 - 35, (y_start_kabin + y_end_kabin)/2, f"{tebal_kolom} mm\n(Kolom Kiri)", color='black', va='center', ha='right', fontsize=9, fontweight='bold')
                ax3.text(x_l1 + 35, y_start_kabin / 2, f"{int(y_start_kabin)} mm", color='red', va='center', ha='left', fontweight='bold', fontsize=9.5)
                ax3.text(x_l1 + 35, y_end_kabin + (sisa_belakang_kabin/2), f"{int(sisa_belakang_kabin)} mm", color='red', va='center', ha='left', fontweight='bold', fontsize=9.5)
                
            if has_right_col:
                ax3.add_patch(plt.Rectangle((lebar_sh, y_start_kabin), tebal_kolom, tebal_kolom, facecolor='black', edgecolor='black'))
                if not has_left_col:
                    ax3.plot([lebar_sh, x_r1], [y_start_kabin, y_start_kabin], 'r-', lw=0.5)
                    ax3.plot([lebar_sh, x_r1], [y_end_kabin, y_end_kabin], 'r-', lw=0.5)
                    ax3.plot([x_r1, x_r1], [0, dalam_sh], 'r-', lw=1)
                    ax3.text(x_r1 + 35, (y_start_kabin + y_end_kabin)/2, f"{tebal_kolom} mm\n(Kolom Kanan)", color='black', va='center', ha='left', fontsize=9, fontweight='bold')
                    ax3.text(x_r1 - 35, y_start_kabin / 2, f"{int(y_start_kabin)} mm", color='red', va='center', ha='right', fontweight='bold', fontsize=9.5)
                    ax3.text(x_r1 - 35, y_end_kabin + (sisa_belakang_kabin/2), f"{int(sisa_belakang_kabin)} mm", color='red', va='center', ha='right', fontweight='bold', fontsize=9.5)

            ax3.add_patch(plt.Rectangle((x_start_cwt_l, y_start_cwt_belakang), tebal_kolom, tebal_kolom, facecolor='black', edgecolor='black'))
            ax3.add_patch(plt.Rectangle((x_start_cwt_r, y_start_cwt_belakang), tebal_kolom, tebal_kolom, facecolor='black', edgecolor='black'))
            
            y_dim_belakang = dalam_sh + 260
            ax3.plot([0, 0], [dalam_sh, y_dim_belakang + 40], 'r-', lw=0.5)
            ax3.plot([lebar_sh, lebar_sh], [dalam_sh, y_dim_belakang + 40], 'r-', lw=0.5)
            ax3.plot([x_start_cwt_l, x_start_cwt_l], [dalam_sh, y_dim_belakang + 40], 'r-', lw=0.5)
            ax3.plot([x_start_cwt_l + tebal_kolom, x_start_cwt_l + tebal_kolom], [dalam_sh, y_dim_belakang + 40], 'r-', lw=0.5)
            ax3.plot([x_start_cwt_r, x_start_cwt_r], [dalam_sh, y_dim_belakang + 40], 'r-', lw=0.5)
            ax3.plot([x_start_cwt_r + tebal_kolom, x_start_cwt_r + tebal_kolom], [dalam_sh, y_dim_belakang + 40], 'r-', lw=0.5)
            ax3.plot([0, lebar_sh], [y_dim_belakang, y_dim_belakang], 'r-', lw=1)
            
            ax3.text(x_start_cwt_l / 2, y_dim_belakang + 40, f"{int(x_start_cwt_l)}", color='blue', ha='center', va='bottom', fontsize=9, fontweight='bold')
            ax3.text(x_start_cwt_l + (tebal_kolom/2), y_dim_belakang - 40, f"{tebal_kolom}", color='black', ha='center', va='top', fontsize=8, fontweight='bold')
            ax3.text(x_tengah, y_dim_belakang + 40, f"{int(track_gauge_cwt)}\n(Gauge)", color='darkgreen', ha='center', va='bottom', fontsize=9.5, fontweight='bold')
            ax3.text(x_start_cwt_r + (tebal_kolom/2), y_dim_belakang - 40, f"{tebal_kolom}", color='black', ha='center', va='top', fontsize=8, fontweight='bold')
            ax3.text((x_start_cwt_r + tebal_kolom + lebar_sh)/2, y_dim_belakang + 40, f"{int(lebar_sh - (x_start_cwt_r + tebal_kolom))}", color='blue', ha='center', va='bottom', fontweight='bold', fontsize=9)

        ax3.text(-680, dalam_sh / 2, f"Clear Depth:\n{dalam_sh} mm", color='darkred', va='center', ha='right', fontweight='bold', fontsize=10)
        ax3.text(lebar_sh + 680, dalam_sh / 2, f"Clear Depth:\n{dalam_sh} mm", color='darkred', va='center', ha='left', fontweight='bold', fontsize=10)

        y_w_line = dalam_sh + 480 if effective_cwt == 'B' else dalam_sh + 380
        ax3.plot([0, lebar_sh], [y_w_line, y_w_line], 'r-', lw=1.2)
        ax3.plot([0, 0], [dalam_sh, y_w_line + 40], 'r-', lw=0.6)
        ax3.plot([lebar_sh, lebar_sh], [dalam_sh, y_w_line + 40], 'r-', lw=0.6)
        ax3.text(lebar_sh / 2, y_w_line + 50, f"Clear Width of Shaft: {lebar_sh} mm", color='red', ha='center', va='bottom', fontweight='bold', fontsize=11)

        txt_title = "DENAH POTONGAN STRUKTUR KOLOM UTAMA (TAMPAK ATAS)"
        draw_rigid_border(ax3, x_p3_min + 30, x_p3_max - 30, y_p3_min + 150, y_p3_max - 30, nama_project, no_kontrak, txt_title, 3, 3, zoom_logo=0.25)
        plt.tight_layout(); pdf.savefig(fig3, dpi=300); plt.close(fig3)

    buffer.seek(0)
    return buffer

# ==========================================
# 4. EXECUTOR CONTROLLER (STREAMLIT INTERFACE WEB)
# ==========================================
st.title("Franz Lift Structure Drawing")
st.markdown("Aplikasi Otomatis Gambar Kerja Sipil Penempatan Separator Beam & Kolom Struktur Utama Lift by RDP.")
st.write("---")

# MENU PANGGIL KEMBALI FILE REFERENSI BASE64
if "pilihan_proyek_sidebar" in st.session_state and st.session_state.pilihan_proyek_sidebar != "-- Pilih Data Untuk Auto-Fill --":
    current_ref_base64 = st.session_state.get("b_pdf_ref_base64", "") if "Beam" in st.session_state.pilihan_proyek_sidebar else st.session_state.get("k_pdf_ref_base64", "")
    if current_ref_base64 and current_ref_base64 != "nan":
        st.sidebar.markdown("---")
        st.sidebar.markdown("📂 **Arsip File Referensi Proyek Ini:**")
        try:
            pdf_bytes = base64.b64decode(current_ref_base64)
            st.sidebar.download_button(label="📥 Download PDF Referensi Lama", data=pdf_bytes, file_name="File_Referensi_Sipil.pdf", mime="application/pdf")
        except Exception:
            pass

tab_balok, tab_kolom = st.tabs(["1. Opsi Balok Separator Beam", "2. Opsi Tiang Kolom Struktur"])

with tab_balok:
    st.header("Konfigurasi Gambar Kerja Balok Separator")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Parameter Proyek & Sipil")
        b_nama_project = st.text_input("Nama Proyek / Klien:", value=st.session_state.b_nama_project)
        b_no_kontrak = st.text_input("Nomor Gambar Kerja:", value=st.session_state.b_no_kontrak)
        b_door_config = st.selectbox("Konfigurasi Sisi Pintu Lift:", DOOR_CONFIG_OPTIONS, index=DOOR_CONFIG_OPTIONS.index(st.session_state.b_door_config), key="b_door_cfg_sel")
        
        if "Adjacent" in b_door_config:
            st.info("ℹ️ Pintu 2-sisi Adjacent aktif: Balok separator samping otomatis hanya dipasang pada 1 sisi dinding yang tertutup.")
        b_config_sep = st.selectbox("Pilihan Konfigurasi Separator Beam:", ['3-SISI', 'KANAN-KIRI', 'KIRI', 'KANAN', 'BELAKANG'], index=['3-SISI', 'KANAN-KIRI', 'KIRI', 'KANAN', 'BELAKANG'].index(st.session_state.b_config_sep))

        st.markdown("---")
        uploaded_pdf_a = st.file_uploader("Upload File Referensi Tambahan (PDF):", type=["pdf"], key="upload_ref_a")
        b_encoded_string = st.session_state.get("b_pdf_ref_base64", "")
        if uploaded_pdf_a is not None:
            b_encoded_string = base64.b64encode(uploaded_pdf_a.read()).decode('utf-8')
            st.session_state.b_pdf_ref_base64 = b_encoded_string
            st.info("File referensi siap disimpan ke Google Sheets.")

    with col2:
        st.subheader("Dimensi Hoistway & Lantai (mm)")
        b_lebar_sh = st.number_input("Lebar Area Lift / Hoistway (mm):", value=st.session_state.b_lebar_sh)
        b_dalam_sh = st.number_input("Kedalaman Area Lift / Hoistway (mm):", value=st.session_state.b_dalam_sh)
        b_h_pit = st.number_input("Kedalaman PIT Bersih (mm):", value=st.session_state.b_h_pit)
        b_h_headroom = st.number_input("Tinggi Headroom / Overhead (mm):", value=st.session_state.b_h_headroom)
        
        b_jml_lantai = st.number_input("Jumlah Lantai (Stop):", min_value=2, max_value=10, value=st.session_state.b_jml_lantai)
        b_travel_list = []
        for i in range(1, b_jml_lantai):
            t_val = st.number_input(f"Tinggi Travel Lantai {i} ke {i+1} (mm):", value=3500, key=f"b_travel_loop_{i}")
            b_travel_list.append(t_val)

    with col3:
        st.subheader("Dimensi Opening Pintu 1 (Depan)")
        st.caption("📐 Ukuran Dinding Kiri/Kanan dilihat dari LUAR hoistway menghadap pintu.")
        b_lebar_p = st.number_input("Lebar Opening Pintu 1 Bersih (mm):", value=st.session_state.b_lebar_p)
        b_width_doorway = st.number_input("Lebar Doorway Sipil Pintu 1 (mm):", value=st.session_state.b_width_doorway)
        b_dinding_kiri = st.number_input("Jarak Dinding Kiri ke Tepi Doorway 1 (mm):", value=st.session_state.b_dinding_kiri)
        b_side_tombol = st.radio("Posisi Tombol Pintu 1 (Balok):", ["KANAN", "KIRI"], index=["KANAN", "KIRI"].index(st.session_state.b_side_tombol), horizontal=True)
        
        st.markdown("**Dimensi Tinggi Gawang (Berlaku Semua Pintu)**")
        b_tinggi_p = st.number_input("Tinggi Opening Pintu Bersih (mm):", value=st.session_state.b_tinggi_p)
        b_tinggi_gembosan = st.number_input("Total Tinggi Opening Pintu Sipil (mm):", value=st.session_state.b_tinggi_gembosan)
        b_tebal_l = st.number_input("Tebal Balok Cor Opening Pintu (mm):", value=st.session_state.b_tebal_l)

        b_lebar_p2 = st.session_state.b_lebar_p2
        b_width_doorway2 = st.session_state.b_width_doorway2
        b_dinding_awal2 = st.session_state.b_dinding_awal2
        b_side_tombol2 = st.session_state.b_side_tombol2
        
        if b_door_config != "1 Sisi (Depan)":
            st.markdown("---")
            st.subheader("Dimensi Opening Pintu 2")
            st.caption("📐 Ukuran Dinding Kiri/Kanan dilihat dari LUAR hoistway menghadap Pintu 2.")
            b_lebar_p2 = st.number_input("Lebar Opening Pintu 2 Bersih (mm):", value=st.session_state.b_lebar_p2, key="b_pw2")
            b_width_doorway2 = st.number_input("Lebar Doorway Sipil Pintu 2 (mm):", value=st.session_state.b_width_doorway2, key="b_dw2")
            b_dinding_awal2 = st.number_input("Jarak Dinding Kiri ke Tepi Doorway 2 (mm):", value=st.session_state.b_dinding_awal2, key="b_wall2")
            b_side_tombol2 = st.radio("Posisi Tombol Pintu 2 (Balok):", ["KANAN", "KIRI"], index=["KANAN", "KIRI"].index(st.session_state.b_side_tombol2), horizontal=True, key="b_btn2")

    st.write("---")
    st.subheader("Preview Dokumen Cetak Biru Resmi")
    elements, t_total, floor_y_positions = generate_structural_layout(b_lebar_sh, b_dalam_sh, b_h_pit, b_h_headroom, b_travel_list)
    
    balok_pdf_data = make_balok_pdf(
        elements, b_lebar_sh, b_dalam_sh, t_total, b_travel_list, floor_y_positions, b_h_headroom,
        b_lebar_p, b_width_doorway, b_tinggi_p, b_tinggi_gembosan, b_tebal_l, b_dinding_kiri, b_config_sep,
        b_nama_project, b_no_kontrak, b_side_tombol, b_door_config, b_lebar_p2, b_width_doorway2, b_dinding_awal2, b_side_tombol2
    )
    
    st.success(f"Gambar Kerja Resmi Untuk {b_nama_project} Berhasil Di-kalkulasi.")
    st.download_button(
        label="💾 Unduh Gambar Kerja Resmi Balok Separator (PDF)",
        data=balok_pdf_data,
        file_name=f"Shop_Drawing_{b_nama_project.replace(' ', '_')}_Separator_Beam.pdf",
        mime="application/pdf"
    )
    
    if st.button("💾 Simpan Log Parameter Balok ke Google Sheets", key="save_sep"):
        payload_a = {
            "nama_project": b_nama_project, "no_drawing": b_no_kontrak, "tipe_modul": "Separator Beam",
            "lebar_hoistway": b_lebar_sh, "dalam_hoistway": b_dalam_sh, "kedalaman_pit": b_h_pit, "tinggi_headroom": b_h_headroom,
            "jml_lantai": b_jml_lantai, "lebar_pintu_bersih": b_lebar_p, "width_doorway": b_width_doorway,
            "tinggi_p": b_tinggi_p, "tinggi_gembosan": b_tinggi_gembosan, "tebal_l": b_tebal_l, "dinding_kiri": b_dinding_kiri,
            "side_tombol": b_side_tombol, "config_sep": b_config_sep, "door_config": b_door_config,
            "lebar_pintu_bersih2": b_lebar_p2, "width_doorway2": b_width_doorway2, "dinding_awal2": b_dinding_awal2,
            "side_tombol2": b_side_tombol2, "pdf_referensi_data": b_encoded_string
        }
        push_history_to_sheets(payload_a)

with tab_kolom:
    st.header("Konfigurasi Gambar Kerja Pilar / Kolom Struktur Utama Vertikal")
    col_k1, col_k2, col_k3 = st.columns(3)
    
    with col_k1:
        st.subheader("Parameter Proyek & Sipil")
        k_nama_project = st.text_input("Nama Proyek / Klien: ", value=st.session_state.k_nama_project)
        k_no_kontrak = st.text_input("Nomor Gambar Kerja: ", value=st.session_state.k_no_kontrak)
        k_door_config = st.selectbox("Konfigurasi Sisi Pintu Lift: ", DOOR_CONFIG_OPTIONS, index=DOOR_CONFIG_OPTIONS.index(st.session_state.k_door_config), key="k_door_cfg_sel")
        
        cwt_options = ["L (KANAN LAYOUT)", "K (KIRI LAYOUT)", "B (BELAKANG LAYOUT)"]
        default_cwt_idx = cwt_options.index(st.session_state.k_posisi_cwt) if st.session_state.k_posisi_cwt in cwt_options else 0
        k_posisi_cwt = st.radio("Posisi Penempatan CWT Mekanikal: ", cwt_options, index=default_cwt_idx, horizontal=True)
        cwt_char = k_posisi_cwt[0]
        if "Adjacent" in k_door_config and cwt_char != 'B':
            st.info("ℹ️ Pintu 2-sisi Adjacent aktif: Kolom rel kabin otomatis hanya dipasang pada 1 sisi dinding tertutup, dan kolom CWT ditempatkan di sisi belakang.")
        
        k_lebar_sh = st.number_input("Lebar Area Lift / Hoistway Luar Murni (mm): ", value=st.session_state.k_lebar_sh)
        k_dalam_sh = st.number_input("Kedalaman Area Lift / Hoistway Luar Murni (mm): ", value=st.session_state.k_dalam_sh)
        k_h_pit = st.number_input("Kedalaman PIT Bersih (mm): ", value=st.session_state.k_h_pit)
        k_h_headroom = st.number_input("Tinggi Headroom / Overhead (mm): ", value=st.session_state.k_h_headroom)

        st.markdown("---")
        uploaded_pdf_k = st.file_uploader("Upload File Referensi Tambahan (PDF): ", type=["pdf"], key="upload_ref_k")
        k_encoded_string = st.session_state.get("k_pdf_ref_base64", "")
        if uploaded_pdf_k is not None:
            k_encoded_string = base64.b64encode(uploaded_pdf_k.read()).decode('utf-8')
            st.session_state.k_pdf_ref_base64 = k_encoded_string
            st.info("File referensi siap disimpan ke Google Sheets.")
        
    with col_k2:
        st.subheader("Parameter Mekanikal Rel Kunci")
        k_posisi_rel_kabin = st.number_input("Jarak AS REL Kabin ke bibir depan car / kabin (mm):", value=st.session_state.k_posisi_rel_kabin)
        k_jarak_rel_ke_cwt = st.number_input("Jarak AS REL Kabin ke AS REL CWT (Opsi Belakang) (mm):", value=st.session_state.k_jarak_rel_ke_cwt)
        k_sisa_belakang = st.number_input("Jarak AS REL CWT ke dinding belakang (Opsi Belakang) (mm):", value=st.session_state.k_sisa_belakang)
        k_track_gauge_cwt = st.number_input("Jarak antar rel CWT / Secondary Track Gauge (mm):", value=st.session_state.k_track_gauge_cwt)
        k_tebal_rail_cwt = st.number_input("Ketebalan fisik profil rel CWT (mm):", value=st.session_state.k_tebal_rail_cwt)
        k_tebal_pintu_luar = st.number_input("Ketebalan mekanisme pintu luar (mm):", value=st.session_state.k_tebal_pintu_luar)
        k_celah_daun_pintu = st.number_input("Celah bebas ruang gerak pintu / clearance (mm):", value=st.session_state.k_celah_daun_pintu)
        k_tebal_kolom = st.number_input("Ketebalan/Dimensi Kolom Struktur UNP (mm):", value=st.session_state.k_tebal_kolom)

    with col_k3:
        st.subheader("Dimensi Opening Pintu 1 & Lantai")
        st.caption("📐 Ukuran Dinding Kiri/Kanan dilihat dari LUAR hoistway menghadap pintu.")
        k_jml_lantai = st.number_input("Jumlah Lantai (Stop): ", min_value=2, max_value=10, value=st.session_state.k_jml_lantai)
        k_travel_list = []
        for i in range(1, k_jml_lantai):
            t_val = st.number_input(f"Tinggi Travel Lantai {i} ke {i+1} (mm): ", value=3500, key=f"k_travel_loop_{i}")
            k_travel_list.append(t_val)
            
        k_lebar_p = st.number_input("Lebar Opening Pintu 1 Bersih (mm): ", value=st.session_state.k_lebar_p)
        k_width_doorway = st.number_input("Lebar Doorway Sipil Pintu 1 (mm): ", value=st.session_state.k_width_doorway)
        k_dinding_kiri = st.number_input("Jarak Dinding Kiri ke Tepi Doorway 1 (mm): ", value=st.session_state.k_dinding_kiri)
        k_side_tombol = st.radio("Posisi Tombol Pintu 1 (Kolom): ", ["KANAN", "KIRI"], index=["KANAN", "KIRI"].index(st.session_state.k_side_tombol), horizontal=True)
        
        st.markdown("**Dimensi Tinggi Gawang (Berlaku Semua Pintu)**")
        k_tinggi_p = st.number_input("Tinggi Opening Pintu Bersih (mm): ", value=st.session_state.k_tinggi_p)
        k_tinggi_gembosan = st.number_input("Total Tinggi Opening Pintu Sipil (mm): ", value=st.session_state.k_tinggi_gembosan)
        k_tebal_l = st.number_input("Tebal Balok Cor Lintel di atas pintu (mm): ", value=st.session_state.k_tebal_l)

        k_lebar_p2 = st.session_state.k_lebar_p2
        k_width_doorway2 = st.session_state.k_width_doorway2
        k_dinding_awal2 = st.session_state.k_dinding_awal2
        k_side_tombol2 = st.session_state.k_side_tombol2
        
        if k_door_config != "1 Sisi (Depan)":
            st.markdown("---")
            st.subheader("Dimensi Opening Pintu 2")
            st.caption("📐 Ukuran Dinding Kiri/Kanan dilihat dari LUAR hoistway menghadap Pintu 2.")
            k_lebar_p2 = st.number_input("Lebar Opening Pintu 2 Bersih (mm):", value=st.session_state.k_lebar_p2, key="k_pw2")
            k_width_doorway2 = st.number_input("Lebar Doorway Sipil Pintu 2 (mm):", value=st.session_state.k_width_doorway2, key="k_dw2")
            k_dinding_awal2 = st.number_input("Jarak Dinding Kiri ke Tepi Doorway 2 (mm):", value=st.session_state.k_dinding_awal2, key="k_wall2")
            k_side_tombol2 = st.radio("Posisi Tombol Pintu 2 (Kolom):", ["KANAN", "KIRI"], index=["KANAN", "KIRI"].index(st.session_state.k_side_tombol2), horizontal=True, key="k_btn2")

    st.write("---")
    st.subheader("Preview Dokumen Cetak Biru Resmi")
    
    kolom_pdf_data = make_kolom_pdf(
        k_lebar_sh, k_dalam_sh, k_h_pit, k_h_headroom, k_travel_list, k_posisi_rel_kabin,
        k_track_gauge_cwt, k_tebal_rail_cwt, k_tebal_pintu_luar, k_celah_daun_pintu, k_tebal_kolom,
        k_lebar_p, k_width_doorway, k_tinggi_p, k_tinggi_gembosan, k_tebal_l, k_dinding_kiri, k_nama_project, k_no_kontrak, cwt_char, k_side_tombol,
        k_jarak_rel_ke_cwt, k_sisa_belakang, k_door_config, k_lebar_p2, k_width_doorway2, k_dinding_awal2, k_side_tombol2
    )
    
    st.success(f"Gambar Kerja Resmi Tiang Kolom Struktur Untuk {k_nama_project} Berhasil Di-kalkulasi.")
    st.download_button(
        label="💾 Unduh Gambar Kerja Resmi Kolom Struktur (PDF)",
        data=kolom_pdf_data,
        file_name=f"Shop_Drawing_{k_nama_project.replace(' ', '_')}_Struktur_Kolom.pdf",
        mime="application/pdf"
    )
    
    if st.button("💾 Simpan Log Parameter Kolom ke Google Sheets", key="save_col"):
        payload_b = {
            "nama_project": k_nama_project, "no_drawing": k_no_kontrak, "tipe_modul": "Column Structure",
            "lebar_hoistway": k_lebar_sh, "dalam_hoistway": k_dalam_sh, "kedalaman_pit": k_h_pit, "tinggi_headroom": k_h_headroom,
            "jml_lantai": k_jml_lantai, "lebar_pintu_bersih": k_lebar_p, "width_doorway": k_width_doorway,
            "tinggi_p": k_tinggi_p, "tinggi_gembosan": k_tinggi_gembosan, "tebal_l": k_tebal_l, "dinding_kiri": k_dinding_kiri,
            "side_tombol": k_side_tombol, "posisi_cwt_raw": k_posisi_cwt, "posisi_rel_kabin": k_posisi_rel_kabin,
            "track_gauge_cwt": k_track_gauge_cwt, "tebal_rail_cwt": k_tebal_rail_cwt, "tebal_pintu_luar": k_tebal_pintu_luar,
            "celah_daun_pintu": k_celah_daun_pintu, "tebal_kolom": k_tebal_kolom,
            "jarak_rel_ke_cwt": k_jarak_rel_ke_cwt, "sisa_belakang": k_sisa_belakang,
            "door_config": k_door_config, "lebar_pintu_bersih2": k_lebar_p2, "width_doorway2": k_width_doorway2,
            "dinding_awal2": k_dinding_awal2, "side_tombol2": k_side_tombol2, "pdf_referensi_data": k_encoded_string
        }
        push_history_to_sheets(payload_b)