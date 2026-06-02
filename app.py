import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import ezdxf
import io
import os
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Set Konfigurasi Halaman Web Streamlit
st.set_page_config(page_title="Franz Lift Drawing Generator", layout="wide", page_icon="⚙️")

# =========================================================================
# G1. CONFIG: INITIALIZATION GOOGLE SHEETS & RECALL SESSION STATE SYSTEM
# =========================================================================
conn = st.connection("gsheets", type=GSheetsConnection)

# Daftar kunci state yang harus diamankan agar auto-fill berjalan lancar tanpa interupsi reload
state_keys = [
    "b_project_name", "b_contract_no", "b_w_sh", "b_d_sh", "b_p_h", "b_hr_h", "b_f_num", "b_tr_str",
    "b_cw_door", "b_dw_door", "b_ph_door", "b_gh_door", "b_lt_thick", "b_lwall_dis",
    "k_project_name", "k_contract_no", "k_w_sh", "k_d_sh", "k_p_h", "k_hr_h", "k_f_num", "k_tr_str",
    "k_rel_pos", "k_tg_cwt", "k_th_cwt", "k_th_door", "k_gap_door", "k_th_col",
    "k_cw_door", "k_dw_door", "k_ph_door", "k_gh_door", "k_lt_thick", "k_lwall_dis"
]

# Set nilai default murni bawaan program asli jika session belum terisi
for k in state_keys:
    if k not in st.session_state:
        if "name" in k or "contract" in k or "str" in k:
            st.session_state[k] = "PROJECT REVISI" if "name" in k else ("-" if "contract" in k else "3500, 3500")
        elif "f_num" in k:
            st.session_state[k] = 3
        elif "w_sh" in k:
            st.session_state[k] = 1700
        elif "d_sh" in k:
            st.session_state[k] = 1500
        elif "p_h" in k:
            st.session_state[k] = 1200
        elif "hr_h" in k:
            st.session_state[k] = 4000
        elif "cw_door" in k:
            st.session_state[k] = 800
        elif "dw_door" in k:
            st.session_state[k] = 950
        elif "ph_door" in k:
            st.session_state[k] = 2000
        elif "gh_door" in k:
            st.session_state[k] = 2100
        elif "lt_thick" in k:
            st.session_state[k] = 300
        elif "lwall_dis" in k:
            st.session_state[k] = 400
        elif "rel_pos" in k:
            st.session_state[k] = 750
        elif "tg_cwt" in k:
            st.session_state[k] = 650
        elif "th_cwt" in k:
            st.session_state[k] = 65
        elif "th_door" in k:
            st.session_state[k] = 120
        elif "gap_door" in k:
            st.session_state[k] = 50
        elif "th_col" in k:
            st.session_state[k] = 150

# =========================================================================
# G2. SIDEBAR INTERFACE: DYNAMIC RECALL DROPDOWN (READ)
# =========================================================================
if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", width=220)
else:
    st.sidebar.title("FRANZ HOME LIFT")

st.sidebar.markdown("### 📋 Panggil Riwayat Proyek")

try:
    df_history = conn.read(ttl="10s")
    if df_history is not None and not df_history.empty:
        # Menghasilkan label penunjuk unik pada dropdown
        df_history['label_dropdown'] = df_history['nama_project'].astype(str) + " (" + df_history['no_drawing'].astype(str) + ") [" + df_history['tipe_modul'].astype(str) + "]"
        list_pilihan = ["-- Pilih Proyek untuk Di-Recall --"] + df_history['label_dropdown'].tolist()
        
        pilihan_recall = st.sidebar.selectbox("Pilih Proyek Lama:", list_pilihan)
        
        if pilihan_recall != "-- Pilih Proyek untuk Di-Recall --":
            row_data = df_history[df_history['label_dropdown'] == pilihan_recall].iloc[0]
            tipe_terpilih = row_data['tipe_modul']
            
            st.sidebar.success(f"Berhasil memuat parameter: {tipe_terpilih}")
            
            if tipe_terpilih == "Separator Beam":
                st.session_state.b_project_name = str(row_data.get('nama_project', 'PROJECT REVISI'))
                st.session_state.b_contract_no = str(row_data.get('no_drawing', '-'))
                st.session_state.b_w_sh = int(row_data.get('lebar_hoistway', 1700))
                st.session_state.b_d_sh = int(row_data.get('dalam_hoistway', 1500))
                st.session_state.b_p_h = int(row_data.get('kedalaman_pit', 1200))
                st.session_state.b_hr_h = int(row_data.get('tinggi_headroom', 4000))
                st.session_state.b_f_num = int(row_data.get('jml_lantai', 3))
                st.session_state.b_tr_str = str(row_data.get('travel_list_str', '3500, 3500'))
                st.session_state.b_cw_door = int(row_data.get('lebar_pintu_bersih', 800))
                st.session_state.b_dw_door = int(row_data.get('lebar_bobokan_gawang', 950))
                st.session_state.b_ph_door = int(row_data.get('tinggi_pintu_bersih', 2000))
                st.session_state.b_gh_door = int(row_data.get('total_tinggi_gembosan', 2100))
                st.session_state.b_lt_thick = int(row_data.get('tebal_balok_lintel', 300))
                st.session_state.b_lwall_dis = int(row_data.get('jarak_kupingan_kiri', 400))
                
            elif tipe_terpilih == "Column Structure":
                st.session_state.k_project_name = str(row_data.get('nama_project', 'PROJECT REVISI'))
                st.session_state.k_contract_no = str(row_data.get('no_drawing', '-'))
                st.session_state.k_w_sh = int(row_data.get('lebar_hoistway', 1700))
                st.session_state.k_d_sh = int(row_data.get('dalam_hoistway', 1500))
                st.session_state.k_p_h = int(row_data.get('kedalaman_pit', 1200))
                st.session_state.k_hr_h = int(row_data.get('tinggi_headroom', 4000))
                st.session_state.k_f_num = int(row_data.get('jml_lantai', 3))
                st.session_state.k_tr_str = str(row_data.get('travel_list_str', '3500, 3500'))
                st.session_state.k_rel_pos = int(row_data.get('as_rel_kabin', 750))
                st.session_state.k_tg_cwt = int(row_data.get('track_gauge_cwt', 650))
                st.session_state.k_th_cwt = int(row_data.get('tebal_rail_cwt', 65))
                st.session_state.k_th_door = int(row_data.get('tebal_pintu_luar', 120))
                st.session_state.k_gap_door = int(row_data.get('celah_daun_pintu', 50))
                st.session_state.k_th_col = int(row_data.get('tebal_kolom_unp', 150))
                st.session_state.k_cw_door = int(row_data.get('lebar_pintu_bersih', 800))
                st.session_state.k_dw_door = int(row_data.get('lebar_bobokan_gawang', 950))
                st.session_state.k_ph_door = int(row_data.get('tinggi_pintu_bersih', 2000))
                st.session_state.k_gh_door = int(row_data.get('total_tinggi_gembosan', 2100))
                st.session_state.k_lt_thick = int(row_data.get('tebal_balok_lintel', 300))
                st.session_state.k_lwall_dis = int(row_data.get('jarak_kupingan_kiri', 400))
    else:
        st.sidebar.info("Database gsheets terdeteksi kosong.")
except:
    st.sidebar.info("Sistem Cloud History siap dikonfigurasi melalui Secrets Management.")

# FUNGSI EMIT DATA DATA BARU KE GOOGLE SHEETS (WRITE)
def append_history_to_sheets(payload):
    try:
        df_old = conn.read()
        df_new = pd.DataFrame([payload])
        if df_old is not None and not df_old.empty:
            df_merged = pd.concat([df_old, df_new], ignore_index=True)
        else:
            df_merged = df_new
        conn.update(data=df_merged)
        st.success("✨ Seluruh nilai parameter sukses dicatat permanen ke Cloud Database!")
    except Exception as e:
        st.warning("Gagal memperbarui Google Sheets. Periksa kembali kecocokan hak akses editor service account.")

# =========================================================================
# G3. CORE HELPER DRAW: KOP BORDER RESMI & STRUKTURAL LAYOUT LOGIC (ASLI)
# =========================================================================
def draw_rigid_border(ax, x_min, x_max, y_min, y_max, project_name, contract_no, page_title, page_num, total_pages, zoom_logo=0.25):
    ax.add_patch(plt.Rectangle((x_min, y_min), x_max - x_min, y_max - y_min, facecolor='none', edgecolor='black', lw=1.5, zorder=100))
    ax.add_patch(plt.Rectangle((x_min + 15, y_min + 15), (x_max - x_min) - 30, (y_max - y_min) - 30, facecolor='none', edgecolor='black', lw=0.8, zorder=100))
    
    h_kop = 150
    y_kop_start = y_min + 15
    y_kop_end = y_kop_start + h_kop
    x_kop_start = x_min + 15
    x_kop_end = x_max - 15
    
    ax.plot([x_kop_start, x_kop_end], [y_kop_end, y_kop_end], color='black', lw=1.0)
    
    x1 = x_kop_start + 250
    x2 = x_kop_end - 350
    ax.plot([x1, x1], [y_kop_start, y_kop_end], color='black', lw=0.8)
    ax.plot([x2, x2], [y_kop_start, y_kop_end], color='black', lw=0.8)
    
    if os.path.exists("logo.png"):
        try:
            img = mpimg.imread("logo.png")
            imagebox = OffsetImage(img, zoom=zoom_logo)
            x_center_logo = x_kop_start + 125
            y_center_logo = (y_kop_start + y_kop_end) / 2
            ab = AnnotationBbox(imagebox, (x_center_logo, y_center_logo), frameon=False, box_alignment=(0.5, 0.5))
            ax.add_artist(ab)
        except:
            ax.text(x_kop_start + 125, (y_kop_start + y_kop_end) / 2, "FRANZ HOME LIFT", ha='center', va='center', fontweight='bold', fontsize=12)
    else:
        ax.text(x_kop_start + 125, (y_kop_start + y_kop_end) / 2, "FRANZ HOME LIFT", ha='center', va='center', fontweight='bold', fontsize=12)
        
    y_mid = (y_kop_start + y_kop_end) / 2
    ax.text(x1 + 30, y_mid + 25, f"PROYEK / CLIENT : {project_name.upper()}", fontsize=11, fontweight='bold', va='center')
    ax.text(x1 + 30, y_mid - 25, f"NOMOR GAMBAR   : {contract_no.upper()}", fontsize=11, fontweight='bold', va='center')
    
    x_mid_title = (x2 + x_kop_end) / 2
    ax.text(x_mid_title, y_mid + 30, page_title.upper(), fontsize=13, fontweight='bold', ha='center', va='center')
    ax.plot([x2, x_kop_end], [y_mid, y_mid], color='black', lw=0.5)
    ax.text(x_mid_title, y_mid - 30, f"HALAMAN: {page_num} DARI {total_pages}", fontsize=10, ha='center', va='center')


def generate_structural_layout(lebar_sh, dalam_sh, h_pit_bersih, h_headroom, travel_list, jml_lantai):
    elements = []
    current_y = 0
    
    elements.append({'type': 'floor_line', 'y_start': current_y, 'name': 'PIT FLOOR'})
    elements.append({'type': 'pit_space', 'y_start': current_y, 'y_end': current_y + h_pit_bersih})
    current_y += h_pit_bersih
    
    floor_y_positions = [current_y]
    elements.append({'type': 'floor_line', 'y_start': current_y, 'name': '1F (LOBBY)'})
    
    for i in range(jml_lantai - 1):
        h_travel = travel_list[i]
        elements.append({'type': 'travel_space', 'y_start': current_y, 'y_end': current_y + h_travel, 'index': i+1})
        current_y += h_travel
        floor_y_positions.append(current_y)
        elements.append({'type': 'floor_line', 'y_start': current_y, 'name': f'{i+2}F'})
        
    elements.append({'type': 'headroom_space', 'y_start': current_y, 'y_end': current_y + h_headroom})
    current_y += h_headroom
    elements.append({'type': 'floor_line', 'y_start': current_y, 'name': 'TOP HOISTWAY'})
    
    total_height = current_y
    return elements, total_height, floor_y_positions


# =========================================================================
# G4. BACKEND RENDER ENGINE: MODUL A & MODUL B (ASLI TANPA EDIT VISUAL)
# =========================================================================
def make_separator_pdf(lebar_sh, dalam_sh, h_pit_bersih, h_headroom, travel_list, jml_lantai,
                       lebar_p_bersih, width_doorway, tinggi_p, tinggi_gembosan, tebal_l, dinding_kiri, config_sep, nama_project, no_kontrak):
    
    elements, total_height, floor_y_positions = generate_structural_layout(lebar_sh, dalam_sh, h_pit_bersih, h_headroom, travel_list, jml_lantai)
    pdf_buffer = io.BytesIO()
    
    with PdfPages(pdf_buffer) as pdf:
        # PAGE 1: POTONGAN DEPAN GAWANG
        x_p1_min, x_p1_max = -550, lebar_sh + 550
        y_p1_min, y_p1_max = -200, total_height + 500
        fig1, ax1 = plt.subplots(figsize=(7.5, 11))
        ax1.set_xlim(x_p1_min, x_p1_max); ax1.set_ylim(y_p1_min, y_p1_max); ax1.axis('off')
        
        ax1.plot([0, 0], [0, total_height], 'k-', lw=2.0)
        ax1.plot([lebar_sh, lebar_sh], [0, total_height], 'k-', lw=2.0)
        
        for idx, f_y in enumerate(floor_y_positions):
            ax1.plot([-250, lebar_sh + 250], [f_y, f_y], 'g--', lw=1.0)
            ax1.text(-270, f_y, f"FINISH FLOOR {idx+1}F\n(Y = {int(f_y)} mm)", color='green', ha='right', va='center', fontsize=9, fontweight='bold')
            
            y_base_pintu = f_y
            x_gawang_kiri = dinding_kiri
            x_gawang_kanan = dinding_kiri + width_doorway
            
            ax1.plot([x_gawang_kiri, x_gawang_kiri], [y_base_pintu, y_base_pintu + tinggi_p + tinggi_gembosan], 'b-', lw=1.5)
            ax1.plot([x_gawang_kanan, x_gawang_kanan], [y_base_pintu, y_base_pintu + tinggi_p + tinggi_gembosan], 'b-', lw=1.5)
            ax1.plot([x_gawang_kiri, x_gawang_kanan], [y_base_pintu + tinggi_p + tinggi_gembosan, y_base_pintu + tinggi_p + tinggi_gembosan], 'b-', lw=1.5)
            
            y_lintel_bawah = y_base_pintu + tinggi_p + tinggi_gembosan
            y_lintel_atas = y_lintel_bawah + tebal_l
            ax1.add_patch(plt.Rectangle((0, y_lintel_bawah), lebar_sh, tebal_l, facecolor='#EAEAEA', edgecolor='black', lw=1.0, zorder=5))
            ax1.text(lebar_sh/2, (y_lintel_bawah + y_lintel_atas)/2, f"BALOK LINTEL COR t={tebal_l}", color='black', ha='center', va='center', fontsize=8, fontweight='bold')

        # Rekonstruksi Aturan Kaku Pemetaan Posisi Ring Balok Separator H-Beam
        beams_y = []
        beams_y.append(h_pit_bersih / 2)
        for f_y in floor_y_positions:
            beams_y.append(f_y)
        for i in range(len(floor_y_positions) - 1):
            mid_y = (floor_y_positions[i] + floor_y_positions[i+1]) / 2
            beams_y.append(mid_y)
        beams_y.append(floor_y_positions[-1] + (h_headroom / 2))
        
        for b_y in beams_y:
            x_b = 0 if config_sep == 'A' else lebar_sh - 150
            ax1.add_patch(plt.Rectangle((x_b, b_y - 75), 150, 150, facecolor='#D3D3D3', edgecolor='blue', lw=1.2, zorder=10))
            ax1.text(200 if config_sep == 'A' else lebar_sh - 450, b_y, f"S-Beam Y={int(b_y)}", color='blue', fontsize=8, fontweight='bold', va='center')
            
        draw_rigid_border(ax1, x_p1_min + 30, x_p1_max - 30, y_p1_min + 150, y_p1_max - 30, nama_project, no_kontrak, "TAMPAK DEPAN & STRUKTUR SEPARATOR", 1, 3, zoom_logo=0.25)
        plt.tight_layout(); pdf.savefig(fig1, dpi=300); plt.close(fig1)
        
        # PAGE 2: POTONGAN SAMPING
        x_p2_min, x_p2_max = -550, dalam_sh + 550
        y_p2_min, y_p2_max = -200, total_height + 500
        fig2, ax2 = plt.subplots(figsize=(7.5, 11))
        ax2.set_xlim(x_p2_min, x_p2_max); ax2.set_ylim(y_p2_min, y_p2_max); ax2.axis('off')
        
        ax2.plot([0, 0], [0, total_height], 'k-', lw=2.0)
        ax2.plot([dalam_sh, dalam_sh], [0, total_height], 'k-', lw=2.0)
        
        for idx, f_y in enumerate(floor_y_positions):
            ax2.plot([-250, dalam_sh + 250], [f_y, f_y], 'g--', lw=1.0)
            ax2.text(-270, f_y, f"FINISH FLOOR {idx+1}F\n(Y = {int(f_y)} mm)", color='green', ha='right', va='center', fontsize=9, fontweight='bold')
            
        for b_y in beams_y:
            ax2.add_patch(plt.Rectangle((0, b_y - 75), dalam_sh, 150, facecolor='#EAEAEA', edgecolor='blue', lw=1.2, zorder=10))
            ax2.text(dalam_sh / 2, b_y, f"BALOK SEPARATOR MANDIRI Y={int(b_y)} mm", color='blue', fontsize=8, ha='center', va='center', fontweight='bold')
            
        draw_rigid_border(ax2, x_p2_min + 30, x_p2_max - 30, y_p2_min + 150, y_p2_max - 30, nama_project, no_kontrak, "POTONGAN SAMPING SEPARATOR BEAM", 2, 3, zoom_logo=0.25)
        plt.tight_layout(); pdf.savefig(fig2, dpi=300); plt.close(fig2)
        
        # PAGE 3: TAMPAK ATAS
        x_p3_min, x_p3_max = -550, lebar_sh + 550
        y_p3_min, y_p3_max = -400, dalam_sh + 600
        fig3, ax3 = plt.subplots(figsize=(7.5, 11))
        ax3.set_xlim(x_p3_min, x_p3_max); ax3.set_ylim(y_p3_min, y_p3_max); ax3.axis('off')
        
        ax3.add_patch(plt.Rectangle((0, 0), lebar_sh, dalam_sh, facecolor='none', edgecolor='black', lw=2.5))
        
        x_b_p3 = 0 if config_sep == 'A' else lebar_sh - 150
        ax3.add_patch(plt.Rectangle((x_b_p3, 0), 150, dalam_sh, facecolor='#D3D3D3', edgecolor='blue', lw=1.5))
        ax3.text(x_b_p3 + 75, dalam_sh/2, "PROFIL SEPARATOR\nBEAM H-BEAM", color='blue', ha='center', va='center', rotation=90, fontsize=9, fontweight='bold')
        
        y_p_line = -220
        ax3.plot([dinding_kiri, dinding_kiri + width_doorway], [y_p_line, y_p_line], 'b-', lw=2.0)
        ax3.plot([dinding_kiri, dinding_kiri], [0, y_p_line - 30], 'b--', lw=0.7)
        ax3.plot([dinding_kiri + width_doorway, dinding_kiri + width_doorway], [0, y_p_line - 30], 'b--', lw=0.7)
        ax3.text(dinding_kiri + width_doorway/2, y_p_line - 45, f"Bobokan Gawang Pintu: {width_doorway} mm", color='blue', ha='center', va='top', fontweight='bold', fontsize=10)
        
        draw_rigid_border(ax3, x_p3_min + 30, x_p3_max - 30, y_p3_min + 150, y_p3_max - 30, nama_project, no_kontrak, "LAYOUT TAMPAK ATAS HOISTWAY", 3, 3, zoom_logo=0.25)
        plt.tight_layout(); pdf.savefig(fig3, dpi=300); plt.close(fig3)
        
    return pdf_buffer.getvalue()


def make_kolom_pdf(lebar_sh, dalam_sh, h_pit_bersih, h_headroom, travel_list, posisi_rel_kabin,
                   track_gauge_cwt, tebal_rail_cwt, tebal_pintu_luar, celah_daun_pintu, tebal_kolom,
                   lebar_p_bersih, width_doorway, tinggi_p, tinggi_gembosan, tebal_l, dinding_kiri, side_tombol, nama_project, no_kontrak, posisi_cwt):
    
    elements, total_height, floor_y_positions = generate_structural_layout(lebar_sh, dalam_sh, h_pit_bersih, h_headroom, travel_list, 3)
    pdf_buffer = io.BytesIO()
    
    with PdfPages(pdf_buffer) as pdf:
        # PAGE 1: POTONGAN DEPAN
        x_p1_min, x_p1_max = -550, lebar_sh + 550
        y_p1_min, y_p1_max = -200, total_height + 500
        fig1, ax1 = plt.subplots(figsize=(7.5, 11))
        ax1.set_xlim(x_p1_min, x_p1_max); ax1.set_ylim(y_p1_min, y_p1_max); ax1.axis('off')
        
        ax1.plot([0, 0], [0, total_height], 'k-', lw=2.0)
        ax1.plot([lebar_sh, lebar_sh], [0, total_height], 'k-', lw=2.0)
        
        for idx, f_y in enumerate(floor_y_positions):
            ax1.plot([-250, lebar_sh + 250], [f_y, f_y], 'g--', lw=1.0)
            ax1.text(-270, f_y, f"FINISH FLOOR {idx+1}F\n(Y = {int(f_y)} mm)", color='green', ha='right', va='center', fontsize=9, fontweight='bold')
            
            ax1.add_patch(plt.Rectangle((0, f_y), tebal_kolom, 300, facecolor='#A9A9A9', edgecolor='black', zorder=15))
            ax1.add_patch(plt.Rectangle((lebar_sh - tebal_kolom, f_y), tebal_kolom, 300, facecolor='#A9A9A9', edgecolor='black', zorder=15))
            
            y_base_pintu = f_y
            x_gawang_kiri = dinding_kiri
            x_gawang_kanan = dinding_kiri + width_doorway
            
            ax1.plot([x_gawang_kiri, x_gawang_kiri], [y_base_pintu, y_base_pintu + tinggi_p + tinggi_gembosan], 'b-', lw=1.5)
            ax1.plot([x_gawang_kanan, x_gawang_kanan], [y_base_pintu, y_base_pintu + tinggi_p + tinggi_gembosan], 'b-', lw=1.5)
            ax1.plot([x_gawang_kiri, x_gawang_kanan], [y_base_pintu + tinggi_p + tinggi_gembosan, y_base_pintu + tinggi_p + tinggi_gembosan], 'b-', lw=1.5)
            
            y_lintel_bawah = y_base_pintu + tinggi_p + tinggi_gembosan
            y_lintel_atas = y_lintel_bawah + tebal_l
            ax1.add_patch(plt.Rectangle((0, y_lintel_bawah), lebar_sh, tebal_l, facecolor='#EAEAEA', edgecolor='black', lw=1.0, zorder=5))
            
            x_box = x_gawang_kanan + 45 if side_tombol == "KANAN" else x_gawang_kiri - 105
            ax1.add_patch(plt.Rectangle((x_box, y_base_pintu + 1100), 60, 120, facecolor='yellow', edgecolor='black', zorder=20))
            ax1.text(x_box + 30, y_base_pintu + 1160, "LOP", color='black', fontsize=7, ha='center', va='center', fontweight='bold')

        draw_rigid_border(ax1, x_p1_min + 30, x_p1_max - 30, y_p1_min + 150, y_p1_max - 30, nama_project, no_kontrak, "TAMPAK FRONT ELEVATION & STRUKTUR KOLOM", 1, 3, zoom_logo=0.25)
        plt.tight_layout(); pdf.savefig(fig1, dpi=300); plt.close(fig1)
        
        # PAGE 2: POTONGAN SAMPING
        fig2, ax2 = plt.subplots(figsize=(7.5, 11))
        x_p2_min, x_p2_max = -550, dalam_sh + 550
        y_p2_min, y_p2_max = -200, total_height + 500
        ax2.set_xlim(x_p2_min, x_p2_max); ax2.set_ylim(y_p2_min, y_p2_max); ax2.axis('off')
        ax2.plot([0, 0], [0, total_height], 'k-', lw=2.0)
        ax2.plot([dalam_sh, dalam_sh], [0, total_height], 'k-', lw=2.0)
        
        for idx, f_y in enumerate(floor_y_positions):
            ax2.plot([-250, dalam_sh + 250], [f_y, f_y], 'g--', lw=1.0)
            ax2.add_patch(plt.Rectangle((0, f_y), dalam_sh, 300, facecolor='#D3D3D3', edgecolor='black', zorder=10))
            
        draw_rigid_border(ax2, x_p2_min + 30, x_p2_max - 30, y_p2_min + 150, y_p2_max - 30, nama_project, no_kontrak, "POTONGAN SAMPING STRUKTUR KOLOM COR", 2, 3, zoom_logo=0.25)
        plt.tight_layout(); pdf.savefig(fig2, dpi=300); plt.close(fig2)
        
        # PAGE 3: TAMPAK ATAS
        x_p3_min, x_p3_max = -550, lebar_sh + 550
        y_p3_min, y_p3_max = -400, dalam_sh + 600
        fig3, ax3 = plt.subplots(figsize=(7.5, 11))
        ax3.set_xlim(x_p3_min, x_p3_max); ax3.set_ylim(y_p3_min, y_p3_max); ax3.axis('off')
        
        ax3.add_patch(plt.Rectangle((0, 0), lebar_sh, dalam_sh, facecolor='none', edgecolor='black', lw=2.5))
        ax3.add_patch(plt.Rectangle((0, 0), tebal_kolom, dalam_sh, facecolor='#A9A9A9', edgecolor='black'))
        ax3.add_patch(plt.Rectangle((lebar_sh - tebal_kolom, 0), tebal_kolom, dalam_sh, facecolor='#A9A9A9', edgecolor='black'))
        
        x_cwt_box = 40 if posisi_cwt == 'K' else lebar_sh - 40 - track_gauge_cwt
        ax3.add_patch(plt.Rectangle((x_cwt_box, dalam_sh/2 - 100), track_gauge_cwt, 200, facecolor='none', edgecolor='black', lw=1.5))
        
        draw_rigid_border(ax3, x_p3_min + 30, x_p3_max - 30, y_p3_min + 150, y_p3_max - 30, nama_project, no_kontrak, "LAYOUT TAMPAK ATAS HOISTWAY", 3, 3, zoom_logo=0.25)
        plt.tight_layout(); pdf.savefig(fig3, dpi=300); plt.close(fig3)
        
    return pdf_buffer.getvalue()


# =========================================================================
# G5. CONTROLLER INTERFACE TAB NAVIGATION
# =========================================================================
st.title("⚙️ Franz Lift Shop Drawing Generator")
st.markdown("Aplikasi Otomatisasi Gambar Kerja Sipil Penempatan Separator Beam & Kolom Struktur Utama Lift.")
st.write("---")

tab_balok, tab_kolom = st.tabs(["🏗️ 1. Opsi Balok Separator Beam", "🏛️ 2. Opsi Tiang Kolom Struktur"])

with tab_balok:
    st.header("Konfigurasi Gambar Kerja Balok Separator Samping")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Parameter Proyek & Sipil")
        b_project_name = st.text_input("Nama Proyek / Klien:", value=st.session_state.b_project_name, key="b_proj_input")
        b_contract_no = st.text_input("Nomor Gambar Kerja / Kontrak Requisition:", value=st.session_state.b_contract_no, key="b_cont_input")
        b_config_sep = st.radio("Penempatan Posisi Sisi Balok Separator:", ["KIRI", "KANAN"], horizontal=True)

    with col2:
        st.subheader("Dimensi Hoistway Bersih (mm)")
        b_w_sh = st.number_input("Lebar Ruang Shaft Lift (Clear Width):", value=st.session_state.b_w_sh, step=50)
        b_d_sh = st.number_input("Kedalaman Ruang Shaft Lift (Clear Depth):", value=st.session_state.b_d_sh, step=50)
        b_p_h = st.number_input("Kedalaman Batas PIT Lift:", value=st.session_state.b_p_h, step=50)
        b_hr_h = st.number_input("Tinggi Ruang Atas Headroom Lantai Top:", value=st.session_state.b_hr_h, step=50)

    with col3:
        st.subheader("Dimensi Lantai & Bukaan Gawang Sipil")
        b_f_num = st.number_input("Jumlah Lantai Berhenti:", min_value=2, max_value=12, value=st.session_state.b_f_num)
        b_tr_str = st.text_input("Jarak Lantai / Travel List (mm, pisahkan dengan koma):", value=st.session_state.b_tr_str)
        
        try:
            b_travel_list = [int(x.strip()) for x in b_tr_str.split(",")]
        except:
            b_travel_list = [3500] * (b_f_num - 1)
            
        b_cw_door = st.number_input("Lebar Bukaan Pintu Bersih (Clear Opening):", value=st.session_state.b_cw_door)
        b_dw_door = st.number_input("Lebar Bobokan Gawang Pintu (Doorway Opening):", value=st.session_state.b_dw_door)
        b_ph_door = st.number_input("Tinggi Opening Pintu Bersih:", value=st.session_state.b_ph_door)
        b_gh_door = st.number_input("Total Tinggi Gembosan Sipil Gawang Pintu:", value=st.session_state.b_gh_door)
        b_lt_thick = st.number_input("Tebal Balok Cor Lintel di atas pintu:", value=st.session_state.b_lt_thick)
        b_lwall_dis = st.number_input("Jarak asimetris dinding kiri KUPINGAN OPENING:", value=st.session_state.b_lwall_dis)

    with col2:
        st.subheader("Preview Dokumen Cetak Biru Resmi")
        
        # Eksekusi Render Gambar PDF Langsung ke Memori Server
        sep_pdf_data = make_separator_pdf(
            b_w_sh, b_d_sh, b_p_h, b_hr_h, b_travel_list, b_f_num,
            b_cw_door, b_dw_door, b_ph_door, b_gh_door, b_lt_thick, b_lwall_dis,
            ('A' if b_config_sep == "KIRI" else 'B'), b_project_name, b_contract_no
        )
        
        # Kirim data parameter ke baris baru Google Sheets Cloud
        payload_a = {
            "nama_project": b_project_name, "no_drawing": b_contract_no, "tipe_modul": "Separator Beam",
            "lebar_hoistway": b_w_sh, "dalam_hoistway": b_d_sh, "kedalaman_pit": b_p_h, "tinggi_headroom": b_hr_h,
            "jml_lantai": b_f_num, "travel_list_str": b_tr_str, "lebar_pintu_bersih": b_cw_door, "lebar_bobokan_gawang": b_dw_door,
            "tinggi_pintu_bersih": b_ph_door, "total_tinggi_gembosan": b_gh_door, "tebal_balok_lintel": b_lt_thick, "jarak_kupingan_kiri": b_lwall_dis
        }
        
        st.success(f"Gambar Kerja Resmi Untuk {b_project_name} Berhasil Di-kalkulasi.")
        st.download_button(
            label="💾 Unduh Gambar Kerja Resmi Balok Separator (PDF)", 
            data=sep_pdf_data, 
            file_name=f"Shop_Drawing_{b_project_name.replace(' ', '_')}_Separator_Beam.pdf", 
            mime="application/pdf"
        )
        
        if st.button("💾 Simpan Log Parameter ke Google Sheets", key="save_sep"):
            append_history_to_sheets(payload_a)

with tab_kolom:
    st.header("Konfigurasi Gambar Kerja Pilar / Kolom Struktur Utama Vertikal")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Parameter Proyek & Sipil")
        k_project_name = st.text_input("Nama Proyek / Klien :", value=st.session_state.k_project_name, key="k_proj_input")
        k_contract_no = st.text_input("Nomor Gambar Kerja / Kontrak Requisition :", value=st.session_state.k_contract_no, key="k_cont_input")
        k_posisi_cwt = st.radio("Penempatan Posisi Sisi Mekanikal CWT Lift:", ["KIRI", "KANAN"], horizontal=True, key="k_cwt_side")
        cwt_char = k_posisi_cwt[0]

        st.subheader("Dimensi Hoistway & Internal Rail Mekanikal (mm)")
        k_w_sh = st.number_input("Lebar Ruang Shaft Lift (Clear Width) :", value=st.session_state.k_w_sh, step=50, key="k_w_sh_inp")
        k_d_sh = st.number_input("Kedalaman Ruang Shaft Lift (Clear Depth) :", value=st.session_state.k_d_sh, step=50, key="k_d_sh_inp")
        k_p_h = st.number_input("Kedalaman Batas PIT Lift :", value=st.session_state.k_p_h, step=50, key="k_p_h_inp")
        k_hr_h = st.number_input("Tinggi Ruang Atas Headroom Lantai Top :", value=st.session_state.k_hr_h, step=50, key="k_hr_h_inp")
        k_rel_pos = st.number_input("As Jarak Posisi Center Rel Kabin:", value=st.session_state.k_rel_pos, key="k_rel_inp")
        k_tg_cwt = st.number_input("Track Gauge CWT Mekanikal (mm):", value=st.session_state.k_tg_cwt, key="k_tg_inp")
        k_th_cwt = st.number_input("Ketebalan Ukuran Profil Rail CWT:", value=st.session_state.k_th_cwt, key="k_th_cwt_inp")
        k_th_door = st.number_input("Tebal Profil Pintu Luar (Front Door Mech):", value=st.session_state.k_th_door, key="k_th_door_inp")
        k_gap_door = st.number_input("Celah Toleransi Bebas Daun Pintu (Clearance):", value=st.session_state.k_gap_door, key="k_gap_inp")
        k_th_col = st.number_input("Ketebalan Profil Ukuran Baja Kolom UNP Utama:", value=st.session_state.k_th_col, key="k_th_col_inp")

        st.subheader("Dimensi Elevasi Lantai & Bukaan Pintu")
        k_f_num = st.number_input("Jumlah Lantai Berhenti :", min_value=2, max_value=12, value=st.session_state.k_f_num, key="k_f_num_inp")
        k_tr_str = st.text_input("Jarak Lantai / Travel List (mm, pisahkan dengan koma) :", value=st.session_state.k_tr_str, key="k_tr_inp")
        
        try:
            k_travel_list = [int(x.strip()) for x in k_tr_str.split(",")]
        except:
            k_travel_list = [3500] * (k_f_num - 1)
            
        k_cw_door = st.number_input("Lebar Bukaan Pintu Bersih (Clear Opening) :", value=st.session_state.k_cw_door, key="k_cw_inp")
        k_dw_door = st.number_input("Lebar Bobokan Gawang Pintu (Doorway Opening) :", value=st.session_state.k_dw_door, key="k_dw_inp")
        k_ph_door = st.number_input("Tinggi Opening Pintu Bersih :", value=st.session_state.k_ph_door, key="k_ph_inp")
        k_gh_door = st.number_input("Total Tinggi Gembosan Sipil Gawang Pintu :", value=st.session_state.k_gh_door, key="k_gh_inp")
        k_lt_thick = st.number_input("Tebal Balok Cor Lintel di atas pintu :", value=st.session_state.k_lt_thick, key="k_lt_inp")
        k_lwall_dis = st.number_input("Jarak asimetris dinding kiri KUPINGAN OPENING :", value=st.session_state.k_lwall_dis, key="k_lw_inp")
        k_side_tombol = st.radio("Penempatan Sisi Kotak Tombol LOP Pintu:", ["KANAN", "KIRI"], horizontal=True)

    with col2:
        st.subheader("Preview Dokumen Cetak Biru Resmi")
        
        kolom_pdf_data = make_kolom_pdf(
            k_w_sh, k_d_sh, k_p_h, k_hr_h, k_travel_list, k_rel_pos, k_tg_cwt, k_th_cwt,
            k_th_door, k_gap_door, k_th_col, k_cw_door, k_dw_door, k_ph_door, k_gh_door,
            k_lt_thick, k_lwall_dis, k_side_tombol, k_project_name, k_contract_no,
            ('K' if k_posisi_cwt == "KIRI" else 'L')
        )
        
        # Kirim data parameter ke baris baru Google Sheets Cloud
        payload_b = {
            "nama_project": k_project_name, "no_drawing": k_contract_no, "tipe_modul": "Column Structure",
            "lebar_hoistway": k_w_sh, "dalam_hoistway": k_d_sh, "kedalaman_pit": k_p_h, "tinggi_headroom": k_hr_h,
            "jml_lantai": k_f_num, "travel_list_str": k_tr_str, "lebar_pintu_bersih": k_cw_door, "lebar_bobokan_gawang": k_dw_door,
            "tinggi_pintu_bersih": k_ph_door, "total_tinggi_gembosan": k_gh_door, "tebal_balok_lintel": k_lt_thick, "jarak_kupingan_kiri": k_lwall_dis,
            "as_rel_kabin": k_rel_pos, "track_gauge_cwt": k_tg_cwt, "tebal_rail_cwt": k_th_cwt, "tebal_pintu_luar": k_th_door, "celah_daun_pintu": k_gap_door, "tebal_kolom_unp": k_th_col
        }
        
        st.success(f"Gambar Kerja Resmi Tiang Kolom Struktur Untuk {k_project_name} Berhasil Di-kalkulasi.")
        st.download_button(
            label="💾 Unduh Gambar Kerja Resmi Kolom Struktur (PDF)", 
            data=kolom_pdf_data, 
            file_name=f"Shop_Drawing_{k_project_name.replace(' ', '_')}_Struktur_Kolom.pdf", 
            mime="application/pdf"
        )
        
        if st.button("💾 Simpan Log Parameter ke Google Sheets", key="save_col"):
            append_history_to_sheets(payload_b)