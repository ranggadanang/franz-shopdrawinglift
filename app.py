import streamlit as st
import matplotlib.subplots as plt
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

# Daftar kunci utama penyimpanan data hasil recall dari cloud gsheets
state_keys = [
    "b_nama_project", "b_no_kontrak", "b_lebar_sh", "b_dalam_sh", "b_h_pit", "b_h_headroom", "b_jml_lantai",
    "b_lebar_p", "b_width_doorway", "b_tinggi_p", "b_tinggi_gembosan", "b_tebal_l", "b_dinding_kiri",
    "b_side_tombol", "b_config_sep",
    "k_nama_project", "k_no_kontrak", "k_posisi_cwt", "k_lebar_sh", "k_dalam_sh", "k_h_pit", "k_h_headroom", "k_jml_lantai",
    "k_posisi_rel_kabin", "k_track_gauge_cwt", "k_tebal_rail_cwt", "k_tebal_pintu_luar", "k_celah_daun_pintu", "k_tebal_kolom",
    "k_lebar_p", "k_width_doorway", "k_tinggi_p", "k_tinggi_gembosan", "k_tebal_l", "k_dinding_kiri", "k_side_tombol"
]

# Set nilai default murni bawaan jika session masih kosong saat pertama kali dibuka
for k in state_keys:
    if k not in st.session_state:
        if "nama" in k: st.session_state[k] = "GUNAWAN-JKT"
        elif "no" in k or "kontrak" in k: st.session_state[k] = " "
        elif "side_tombol" in k: st.session_state[k] = "KANAN"
        elif "config_sep" in k: st.session_state[k] = "3-SISI"
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
        elif "rel_kabin" in k: st.session_state[k] = 670
        elif "gauge_cwt" in k: st.session_state[k] = 700
        elif "rail_cwt" in k: st.session_state[k] = 60
        elif "pintu_luar" in k: st.session_state[k] = 110
        elif "daun_pintu" in k: st.session_state[k] = 30
        elif "tebal_kolom" in k: st.session_state[k] = 200

# =========================================================================
# G2. SIDEBAR LOGIC: RECALL PROYEK DROPDOWN (READ)
# =========================================================================
if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", width=200)
st.sidebar.markdown("### 📋 Panggil Riwayat Proyek")

try:
    df_history = conn.read(ttl="5s")
    if df_history is not None and not df_history.empty:
        df_history['label_select'] = df_history['nama_project'].astype(str) + " (" + df_history['no_drawing'].astype(str) + ") [" + df_history['tipe_modul'].astype(str) + "]"
        options_list = ["-- Pilih Data Untuk Auto-Fill --"] + df_history['label_select'].tolist()
        
        selected_project = st.sidebar.selectbox("Pilih Proyek:", options_list)
        
        if selected_project != "-- Pilih Data Untuk Auto-Fill --":
            row = df_history[df_history['label_select'] == selected_project].iloc[0]
            tipe = row['tipe_modul']
            st.sidebar.success(f"Berhasil memuat tipe: {tipe}")
            
            if tipe == "Separator Beam":
                st.session_state.b_nama_project = str(row.get('nama_project', 'GUNAWAN-JKT'))
                st.session_state.b_no_kontrak = str(row.get('no_drawing', ' '))
                st.session_state.b_lebar_sh = int(row.get('lebar_hoistway', 1700))
                st.session_state.b_dalam_sh = int(row.get('dalam_hoistway', 1500))
                st.session_state.b_h_pit = int(row.get('kedalaman_pit', 170))
                st.session_state.b_h_headroom = int(row.get('tinggi_headroom', 3000))
                st.session_state.b_jml_lantai = int(row.get('jml_lantai', 3))
                st.session_state.b_lebar_p = int(row.get('lebar_pintu_bersih', 800))
                st.session_state.b_width_doorway = int(row.get('width_doorway', 950))
                st.session_state.b_tinggi_p = int(row.get('tinggi_p', 2000))
                st.session_state.b_tinggi_gembosan = int(row.get('tinggi_gembosan', 2100))
                st.session_state.b_tebal_l = int(row.get('tebal_l', 300))
                st.session_state.b_dinding_kiri = int(row.get('dinding_kiri', 375))
                st.session_state.b_side_tombol = str(row.get('side_tombol', 'KANAN'))
                st.session_state.b_config_sep = str(row.get('config_sep', '3-SISI'))
                
            elif tipe == "Column Structure":
                st.session_state.k_nama_project = str(row.get('nama_project', 'GUNAWAN-JKT'))
                st.session_state.k_no_kontrak = str(row.get('no_drawing', ' '))
                st.session_state.k_posisi_cwt = str(row.get('posisi_cwt_raw', 'L (KANAN LAYOUT)'))
                st.session_state.k_lebar_sh = int(row.get('lebar_hoistway', 1430))
                st.session_state.k_dalam_sh = int(row.get('dalam_hoistway', 1430))
                st.session_state.k_h_pit = int(row.get('kedalaman_pit', 170))
                st.session_state.k_h_headroom = int(row.get('tinggi_headroom', 3000))
                st.session_state.k_jml_lantai = int(row.get('jml_lantai', 3))
                st.session_state.k_posisi_rel_kabin = int(row.get('posisi_rel_kabin', 670))
                st.session_state.k_track_gauge_cwt = int(row.get('track_gauge_cwt', 700))
                st.session_state.k_tebal_rail_cwt = int(row.get('tebal_rail_cwt', 60))
                st.session_state.k_tebal_pintu_luar = int(row.get('tebal_pintu_luar', 110))
                st.session_state.k_celah_daun_pintu = int(row.get('celah_daun_pintu', 30))
                st.session_state.k_tebal_kolom = int(row.get('tebal_kolom', 200))
                st.session_state.k_lebar_p = int(row.get('lebar_pintu_bersih', 800))
                st.session_state.k_width_doorway = int(row.get('width_doorway', 950))
                st.session_state.k_tinggi_p = int(row.get('tinggi_p', 2000))
                st.session_state.k_tinggi_gembosan = int(row.get('tinggi_gembosan', 2100))
                st.session_state.k_tebal_l = int(row.get('tebal_l', 300))
                st.session_state.k_dinding_kiri = int(row.get('dinding_kiri', 400))
                st.session_state.k_side_tombol = str(row.get('side_tombol', 'KANAN'))
except:
    st.sidebar.info("Sistem Cloud History siap dikonfigurasi melalui Secrets Management.")

# FUNGSI EMIT DATA DATA BARU KE GOOGLE SHEETS (WRITE)
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
# G3. HELPER: BORDER DRAFT KOP RESMI (ASLI)
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
    
    w_col1 = w_kop * 0.28
    w_col2 = w_kop * 0.32
    w_col3 = w_kop * 0.22
    
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
    ax.text(x_c2 + 20, y_kop_start + (h_kop * 0.32), page_title, color='black', fontweight='bold', va='center', ha='left', fontsize=9, zorder=103)
    
    ax.text(x_c3 + 20, y_kop_start + (h_kop * 0.30), "DESIGNED BY: RDP", color='black', va='center', ha='left', fontsize=8, zorder=103)
    ax.text(x_c3 + 20, y_kop_start + (h_kop * 0.15), f"PAGE : {page_num} OF {total_pages}", color='blue', fontweight='bold', va='center', ha='left', fontsize=9.5, zorder=103)

# ==========================================
# G4. BALOK LOGIC ENGINE (SEPARATOR BEAM) (ASLI)
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

def make_balok_pdf(elements, lebar_sh, dalam_sh, total_height, travel_list, floor_y_positions, h_headroom, lebar_p_bersih, width_doorway, tinggi_p, tinggi_gembosan, tebal_l, dinding_kiri, config_sep, nama_project, no_kontrak, side_tombol):
    buffer = io.BytesIO()
    w_wall = 200
    w_sep = 100
    elevasi_lintel = tinggi_gembosan
    dinding_kanan = lebar_sh - (dinding_kiri + width_doorway)
    
    with PdfPages(buffer) as pdf:
        # HALAMAN 1
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
        ax1.text(col1_x + (lebar_sh/2), -220, f"Clear Width: {lebar_sh} mm", color='red', ha='center', va='top', fontweight='bold', fontsize=11)
        
        draw_rigid_border(ax1, x_min + 50, x_max - 50, y_min + 50, y_max - 50, nama_project, no_kontrak, "SEPARATOR BEAM", 1, 3, zoom_logo=0.15)
        plt.tight_layout(); pdf.savefig(fig1, dpi=300); plt.close(fig1)

        # HALAMAN 2
        fig2, ax2 = plt.subplots(figsize=(10, 12))
        x_p2_min, x_p2_max = -500, lebar_sh + 1200
        y_p2_min, y_p2_max = -300, elevasi_lintel + tebal_l + 500  
        ax2.set_xlim(x_p2_min, x_p2_max); ax2.set_ylim(y_p2_min, y_p2_max); ax2.axis('off')
        
        ax2.add_patch(plt.Rectangle((0, -100), lebar_sh, 100, hatch='...', facecolor='lightgray', edgecolor='black', alpha=0.6))
        ax2.plot([0, 0], [-100, elevasi_lintel + tebal_l + 350], 'k-', lw=2.5)
        ax2.plot([lebar_sh, lebar_sh], [-100, elevasi_lintel + tebal_l + 350], 'k-', lw=2.5)
        ax2.plot([dinding_kiri, dinding_kiri], [0, elevasi_lintel], 'k-', lw=2)
        ax2.plot([lebar_sh - dinding_kanan, lebar_sh - dinding_kanan], [0, elevasi_lintel], 'k-', lw=2)
        ax2.plot([dinding_kiri, lebar_sh - dinding_kanan], [elevasi_lintel, elevasi_lintel], 'k-', lw=2)
        
        ax2.add_patch(plt.Rectangle((0, elevasi_lintel), lebar_sh, tebal_l, color='black', alpha=0.9))
        ax2.text(lebar_sh / 2, elevasi_lintel + (tebal_l / 2), "Balok Lintel Beton Cor", color='white', ha='center', va='center', fontweight='bold', fontsize=10)
        ax2.text((dinding_kiri + lebar_sh - dinding_kanan)/2, tinggi_p/2, f"Opening Pintu Sipil (Doorway)\n{width_doorway} x {elevasi_lintel} mm\n(Bukaan Bersih Lift: {lebar_p_bersih} mm)", color='black', va='center', ha='center', fontsize=11, fontweight='bold')
        
        if side_tombol == "KANAN":
            x_hole = (lebar_sh - dinding_kanan) + (dinding_kanan / 2)
            xy_text_pos = (x_hole + 250, 1000); rad_val = -0.15
        else:
            x_hole = dinding_kiri / 2
            xy_text_pos = (x_hole - 250, 1000); rad_val = 0.15
            
        ax2.plot([x_hole - 50, x_hole + 50], [1200, 1200], 'r-', lw=1)
        ax2.plot(x_hole, 1200, 'ko', markersize=10, fillstyle='none', lw=1.5)
        ax2.annotate(f"Lubang Kabel\nTombol Pintu Ø25mm\n(As Tombol)", xy=(x_hole, 1190), xytext=xy_text_pos,
                     arrowprops=dict(arrowstyle="->", color="black", lw=1.2, connectionstyle=f"arc3,rad={rad_val}"),
                     fontsize=9, color='black', fontweight='bold', ha='center', va='top')

        ax2.text(dinding_kiri / 2, 150, f"Dinding Kiri:\n{int(dinding_kiri)} mm", ha='center', va='bottom', fontsize=9.5, color='blue', fontweight='bold')
        ax2.text(lebar_sh - (dinding_kanan/2), 150, f"Dinding Kanan:\n{int(dinding_kanan)} mm", ha='center', va='bottom', fontsize=9.5, color='blue', fontweight='bold')

        x_dim_baseline = lebar_sh + 150 
        ax2.plot([lebar_sh, x_dim_baseline + 120], [0, 0], 'r-', lw=0.8)
        ax2.plot([lebar_sh, x_dim_baseline + 120], [elevasi_lintel, elevasi_lintel], 'r-', lw=0.8)
        ax2.plot([lebar_sh, x_dim_baseline + 120], [elevasi_lintel + tebal_l, elevasi_lintel + tebal_l], 'r-', lw=0.8)
        ax2.plot([x_dim_baseline + 60, x_dim_baseline + 60], [0, elevasi_lintel], 'r-', lw=1.2)
        ax2.plot([x_dim_baseline + 60, x_dim_baseline + 60], [elevasi_lintel, elevasi_lintel + tebal_l], 'r-', lw=1.2)
        
        ax2.text(x_dim_baseline + 90, elevasi_lintel / 2, f"{elevasi_lintel} mm (Gembosan Sipil)", color='red', va='center', ha='left', fontsize=10, fontweight='bold')
        ax2.text(x_dim_baseline + 90, elevasi_lintel + (tebal_l / 2), f"{tebal_l} mm Lintel", color='red', va='center', ha='left', fontsize=10, fontweight='bold')
        
        draw_rigid_border(ax2, x_p2_min + 30, x_p2_max - 30, y_p2_min + 150, y_p2_max - 30, nama_project, no_kontrak, "OPENING PINTU", 2, 3, zoom_logo=0.25)
        plt.tight_layout(); pdf.savefig(fig2, dpi=300); plt.close(fig2)

        # HALAMAN 3
        fig3, ax3 = plt.subplots(figsize=(12, 13))
        ax3.set_aspect('equal', adjustable='box')
        x_p3_min, x_p3_max = -750, lebar_sh + 1750
        y_p3_min, y_p3_max = -1200, dalam_sh + 1100
        ax3.set_xlim(x_p3_min, x_p3_max); ax3.set_ylim(y_p3_min, y_p3_max); ax3.axis('off')
        
        ax3.add_patch(plt.Rectangle((-w_wall, -w_wall), lebar_sh + (2*w_wall), dalam_sh + (2*w_wall), facecolor='none', edgecolor='black', lw=2.5))
        ax3.add_patch(plt.Rectangle((0, 0), lebar_sh, dalam_sh, facecolor='whitesmoke', edgecolor='black', lw=1.5))
        ax3.add_patch(plt.Rectangle((dinding_kiri, -w_wall), width_doorway, w_wall, facecolor='white', edgecolor='none'))
        ax3.plot([dinding_kiri, dinding_kiri], [-w_wall, 0], 'k-', lw=2)
        ax3.plot([lebar_sh - dinding_kanan, lebar_sh - dinding_kanan], [-w_wall, 0], 'k-', lw=2)
        
        ax3.text(dinding_kiri / 2, -w_wall - 160, f"Dinding Kiri:\n{int(dinding_kiri)} mm", ha='center', va='top', fontsize=10, color='blue', fontweight='bold')
        ax3.text(lebar_sh - (dinding_kanan/2), -w_wall - 140, f"Dinding Kanan:\n{int(dinding_kanan)} mm", ha='center', va='top', fontsize=10, color='blue', fontweight='bold')
        ax3.text((dinding_kiri + lebar_sh - dinding_kanan)/2, -60, f"Lebar Pintu / Doorway: {width_doorway} mm", ha='center', va='center', fontsize=10, color='black', fontweight='bold')

        plot_kiri = config_sep in ['KIRI', 'KANAN-KIRI', '3-SISI']
        plot_kanan = config_sep in ['KANAN', 'KANAN-KIRI', '3-SISI']
        plot_belakang = config_sep in ['BELAKANG', '3-SISI']
            
        if plot_kiri: ax3.add_patch(plt.Rectangle((-w_sep, 0), w_sep, dalam_sh, facecolor='black', edgecolor='black', alpha=0.8))
        if plot_kanan: ax3.add_patch(plt.Rectangle((lebar_sh, 0), w_sep, dalam_sh, facecolor='black', edgecolor='black', alpha=0.8))
        if plot_belakang: ax3.add_patch(plt.Rectangle((0, dalam_sh), lebar_sh, w_sep, facecolor='black', edgecolor='black', alpha=0.8))

        ax3.text(-w_sep - 160, dalam_sh/2, "Balok Separator Samping (Outside)", rotation=90, va='center', ha='right', fontsize=10, fontweight='bold')
        ax3.text(lebar_sh + w_sep + 160, dalam_sh/2, "Balok Separator Samping (Outside)", rotation=270, va='center', ha='left', fontsize=10, fontweight='bold')
        ax3.text(lebar_sh/2, dalam_sh/2, f"CLEAR AREA SHAFT\n{lebar_sh} mm x {dalam_sh} mm", color='red', ha='center', va='center', fontweight='bold', fontsize=12)
        ax3.text(lebar_sh/2, dalam_sh + w_sep + 150, "REKOMENDASI POSISI SEPARATOR BEAM DI LUAR CLEAR AREA", color='darkgreen', ha='center', fontweight='bold', fontsize=10)

        y_dim_width = dalam_sh + w_sep + 320
        ax3.plot([0, lebar_sh], [y_dim_width, y_dim_width], 'r-', lw=1.2)
        ax3.plot([0, 0], [dalam_sh, y_dim_width + 40], 'r-', lw=0.6)
        
        ax3.plot([lebar_sh, lebar_sh], [dalam_sh, y_dim_width + 40], 'r-', lw=0.6)
        ax3.text(lebar_sh / 2, y_dim_width + 50, f"Clear Width: {lebar_sh} mm", color='red', ha='center', va='bottom', fontweight='bold', fontsize=11)
        
        x_dim_depth = lebar_sh + w_sep + 320
        ax3.plot([x_dim_depth, x_dim_depth], [0, dalam_sh], 'r-', lw=1.2)
        ax3.plot([lebar_sh, x_dim_depth + 40], [0, 0], 'r-', lw=0.6)
        ax3.plot([lebar_sh, x_dim_depth + 40], [dalam_sh, dalam_sh], 'r-', lw=0.6)
        ax3.text(x_dim_depth + 50, dalam_sh / 2, f"Clear Depth:\n{dalam_sh} mm", color='red', va='center', ha='left', fontweight='bold', fontsize=11)

        draw_rigid_border(ax3, x_p3_min + 30, x_p3_max - 30, y_p3_min + 150, y_p3_max - 30, nama_project, no_kontrak, "HOISTWAY", 3, 3, zoom_logo=0.25)
        plt.tight_layout(); pdf.savefig(fig3, dpi=300); plt.close(fig3)

    buffer.seek(0)
    return buffer

# ==========================================
# G5. KOLOM LOGIC ENGINE (STRUKTUR PILAR) (ASLI)
# ==========================================
def make_kolom_pdf(lebar_sh, dalam_sh, h_pit_bersih, h_headroom, travel_list, posisi_rel_kabin, track_gauge_cwt, tebal_rail_cwt, tebal_pintu_luar, celah_daun_pintu, tebal_kolom, lebar_p_bersih, width_doorway, tinggi_p, tinggi_gembosan, tebal_l, dinding_kiri, nama_project, no_kontrak, posisi_cwt, side_tombol):
    buffer = io.BytesIO()
    elevasi_lintel = tinggi_gembosan
    dinding_kanan = lebar_sh - (dinding_kiri + width_doorway)
    w_wall = 200 
    
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
        # HALAMAN 1
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
        
        if posisi_cwt == 'L':
            ax1.add_patch(plt.Rectangle((x_offset_l + y_start_kabin, 0), tebal_kolom, total_height, facecolor='gray', alpha=0.7, hatch='//'))
            ax1.text(x_offset_l + dalam_sh/2, -100, "TAMPAK SAMPING SISI KIRI\n(STRUKTUR REL KABIN)", ha='center', va='top', fontsize=10, fontweight='bold')
            ax1.add_patch(plt.Rectangle((x_offset_r + y_start_cwt_depan, 0), tebal_kolom, total_height, facecolor='gray', alpha=0.7, hatch='//'))
            ax1.add_patch(plt.Rectangle((x_offset_r + y_start_cwt_belakang, 0), tebal_kolom, total_height, facecolor='gray', alpha=0.7, hatch='//'))
            ax1.text(x_offset_r + dalam_sh/2, -100, "TAMPAK SAMPING SISI KANAN\n(STRUKTUR 2x SISI CWT)", ha='center', va='top', fontsize=10, fontweight='bold')
        else:
            ax1.add_patch(plt.Rectangle((x_offset_l + y_start_cwt_depan, 0), tebal_kolom, total_height, facecolor='gray', alpha=0.7, hatch='//'))
            ax1.add_patch(plt.Rectangle((x_offset_l + y_start_cwt_belakang, 0), tebal_kolom, total_height, facecolor='gray', alpha=0.7, hatch='//'))
            ax1.text(x_offset_l + dalam_sh/2, -100, "TAMPAK SAMPING SISI KIRI\n(STRUKTUR 2x SISI CWT)", ha='center', va='top', fontsize=10, fontweight='bold')
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

        txt_orientasi = "CWT SISI KIRI" if posisi_cwt == 'K' else "CWT SISI KANAN"
        draw_rigid_border(ax1, x_min + 50, x_max - 50, y_min + 50, y_max - 50, nama_project, no_kontrak, f"STRUKTUR LIFT ({txt_orientasi})", 1, 3, zoom_logo=0.15)
        plt.tight_layout(); pdf.savefig(fig1, dpi=300); plt.close(fig1)

        # HALAMAN 2
        fig2, ax2 = plt.subplots(figsize=(10, 12))
        x_p2_min, x_p2_max = -500, lebar_sh + 1200
        y_p2_min, y_p2_max = -300, elevasi_lintel + tebal_l + 500  
        ax2.set_xlim(x_p2_min, x_p2_max); ax2.set_ylim(y_p2_min, y_p2_max); ax2.axis('off')
        
        ax2.add_patch(plt.Rectangle((0, -100), lebar_sh, 100, hatch='...', facecolor='lightgray', edgecolor='black', alpha=0.6))
        ax2.plot([0, 0], [-100, elevasi_lintel + tebal_l + 350], 'k-', lw=2.5)
        ax2.plot([lebar_sh, lebar_sh], [-100, elevasi_lintel + tebal_l + 350], 'k-', lw=2.5)
        ax2.plot([dinter_dk := dinding_kiri, dinding_kiri], [0, elevasi_lintel], 'k-', lw=2)
        ax2.plot([lebar_sh - dinding_kanan, lebar_sh - dinding_kanan], [0, elevasi_lintel], 'k-', lw=2)
        ax2.plot([dinter_dk, lebar_sh - dinding_kanan], [elevasi_lintel, elevasi_lintel], 'k-', lw=2)
        
        ax2.add_patch(plt.Rectangle((0, elevasi_lintel), lebar_sh, tebal_l, color='black', alpha=0.9))
        ax2.text(lebar_sh / 2, elevasi_lintel + (tebal_l / 2), "Balok Lintel Beton Cor", color='white', ha='center', va='center', fontweight='bold', fontsize=10)
        ax2.text((dinter_dk + lebar_sh - dinding_kanan)/2, tinggi_p/2, f"Opening Pintu Sipil (Doorway)\n{width_doorway} x {elevasi_lintel} mm\n(Bukaan Bersih: {lebar_p_bersih} mm)", color='black', va='center', ha='center', fontsize=11, fontweight='bold')
        
        if side_tombol == 'KANAN':
            x_hole = (lebar_sh - dinding_kanan) + (dinding_kanan / 2)
            xy_text_pos = (x_hole + 250, 1000); rad_val = -0.15
        else:
            x_hole = dinding_kiri / 2
            xy_text_pos = (x_hole - 250, 1000); rad_val = 0.15
            
        ax2.plot([x_hole - 50, x_hole + 50], [1200, 1200], 'r-', lw=1)
        ax2.plot(x_hole, 1200, 'ko', markersize=10, fillstyle='none', lw=1.5)
        
        ax2.annotate(f"Lubang Kabel\nTombol Pintu Ø25mm\n(As Tombol)", xy=(x_hole, 1190), xytext=xy_text_pos,
                     arrowprops=dict(arrowstyle="->", color="black", lw=1.2, connectionstyle=f"arc3,rad={rad_val}"),
                     fontsize=9, color='black', fontweight='bold', ha='center', va='top')
        
        ax2.text(dinter_dk / 2, 150, f"Dinding Kiri:\n{int(dinter_dk)} mm", ha='center', va='bottom', fontsize=9.5, color='blue', fontweight='bold')
        ax2.text(lebar_sh - (dinding_kanan/2), 150, f"Dinding Kanan:\n{int(dinding_kanan)} mm", ha='center', va='bottom', fontsize=9.5, color='blue', fontweight='bold')

        x_dim_baseline = lebar_sh + 150 
        ax2.plot([lebar_sh, x_dim_baseline + 120], [0, 0], 'r-', lw=0.8)
        ax2.plot([lebar_sh, x_dim_baseline + 120], [elevasi_lintel, elevasi_lintel], 'r-', lw=0.8)
        ax2.plot([lebar_sh, x_dim_baseline + 120], [elevasi_lintel + tebal_l, elevasi_lintel + tebal_l], 'r-', lw=0.8)
        ax2.plot([x_dim_baseline + 60, x_dim_baseline + 60], [0, elevasi_lintel], 'r-', lw=1.2)
        ax2.plot([x_dim_baseline + 60, x_dim_baseline + 60], [elevasi_lintel, elevasi_lintel + tebal_l], 'r-', lw=1.2)
        
        ax2.text(x_dim_baseline + 90, elevasi_lintel / 2, f"{elevasi_lintel} mm", color='red', va='center', ha='left', fontsize=10, fontweight='bold')
        ax2.text(x_dim_baseline + 90, elevasi_lintel + (tebal_l / 2), f"{tebal_l} mm Lintel", color='red', va='center', ha='left', fontsize=10, fontweight='bold')
        
        draw_rigid_border(ax2, x_p2_min + 30, x_p2_max - 30, y_p2_min + 150, y_p2_max - 30, nama_project, no_kontrak, "OPENING PINTU", 2, 3, zoom_logo=0.25)
        plt.tight_layout(); pdf.savefig(fig2, dpi=300); plt.close(fig2)

        # HALAMAN 3
        fig3, ax3 = plt.subplots(figsize=(14, 15))
        ax3.set_aspect('equal', adjustable='box')  
        x_p3_min, x_p3_max = -1200, lebar_sh + 2100
        y_p3_min, y_p3_max = -1200, dalam_sh + 1100
        ax3.set_xlim(x_p3_min, x_p3_max); ax3.set_ylim(y_p3_min, y_p3_max); ax3.axis('off')
        
        ax3.add_patch(plt.Rectangle((-w_wall, -w_wall), lebar_sh + (2*w_wall), dalam_sh + (2*w_wall), facecolor='none', edgecolor='black', lw=2.5))
        ax3.add_patch(plt.Rectangle((0, 0), lebar_sh, dalam_sh, facecolor='whitesmoke', edgecolor='black', lw=1.5))
        ax3.add_patch(plt.Rectangle((dinter_dk, -w_wall), width_doorway, w_wall, facecolor='white', edgecolor='none'))
        ax3.plot([dinter_dk, dinter_dk], [-w_wall, 0], 'k-', lw=2)
        ax3.plot([lebar_sh - dinding_kanan, lebar_sh - dinding_kanan], [-w_wall, 0], 'k-', lw=2)
        
        ax3.text(dinter_dk / 2, -w_wall - 160, f"Dinding Kiri:\n{int(dinter_dk)} mm", ha='center', va='top', fontsize=10, color='blue', fontweight='bold')
        ax3.text(lebar_sh - (dinding_kanan/2), -w_wall - 140, f"Dinding Kanan:\n{int(dinding_kanan)} mm", ha='center', va='top', fontsize=10, color='blue', fontweight='bold')
        ax3.text((dinter_dk + lebar_sh - dinding_kanan)/2, -60, f"Lebar Doorway: {width_doorway} mm", ha='center', va='center', fontsize=10, color='black', fontweight='bold')
        ax3.text(lebar_sh/2, dalam_sh/2, f"CLEAR AREA SHAFT LIFT \n{lebar_sh} mm x {dalam_sh} mm", color='red', ha='center', va='center', fontweight='bold', fontsize=12)

        x_l1, x_l2 = -260, -550     
        x_r1, x_r2 = lebar_sh + tebal_kolom + 260, lebar_sh + tebal_kolom + 580 

        if posisi_cwt == 'L':
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
            
            ax3.text(x_l2 - 45, dalam_sh / 2, f"Clear Depth: {dalam_sh} mm", color='darkred', va='center', ha='right', fontweight='bold', fontsize=10)
            ax3.text(x_r2 + 45, dalam_sh / 2, f"Clear Depth:\n{dalam_sh} mm", color='darkred', va='center', ha='left', fontweight='bold', fontsize=10)
        else:
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
            
            ax3.text(x_l2 - 45, dalam_sh / 2, f"Clear Depth  Shaft: {dalam_sh} mm", color='darkred', va='center', ha='right', fontweight='bold', fontsize=10)
            ax3.text(x_r2 + 45, dalam_sh / 2, f"Clear Depth:\n{dalam_sh} mm", color='darkred', va='center', ha='left', fontweight='bold', fontsize=10)


        y_w_line = dalam_sh + 320
        ax3.plot([0, lebar_sh], [y_w_line, y_w_line], 'r-', lw=1.2)
        ax3.plot([0, 0], [dalam_sh, y_w_line + 40], 'r-', lw=0.6)
        ax3.plot([lebar_sh, lebar_sh], [dalam_sh, y_w_line + 40], 'r-', lw=0.6)
        ax3.text(lebar_sh / 2, dalam_sh + 370, f"Clear Width of Shaft: {lebar_sh} mm", color='red', ha='center', va='bottom', fontweight='bold', fontsize=11)

        txt_title = "DENAH POTONGAN STRUKTUR KOLOM UTAMA (TAMPAK ATAS)"
        draw_rigid_border(ax3, x_p3_min + 30, x_p3_max - 30, y_p3_min + 150, y_p3_max - 30, nama_project, no_kontrak, txt_title, 3, 3, zoom_logo=0.25)
        plt.tight_layout(); pdf.savefig(fig3, dpi=300); plt.close(fig3)

    buffer.seek(0)
    return buffer

# ==========================================
# 4. EXECUTOR CONTROLLER (STREAMLIT INTERFACE WEB)
# ==========================================
st.title("Franz Lift Shop Drawing Generator")
st.markdown("Aplikasi Otomatisasi Gambar Kerja Sipil Penempatan Separator Beam & Kolom Struktur Utama Lift by RDP.")
st.write("---")

tab_balok, tab_kolom = st.tabs(["1. Opsi Balok Separator Beam", "2. Opsi Tiang Kolom Struktur"])

with tab_balok:
    st.header("Konfigurasi Gambar Kerja Balok Separator Samping")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Parameter Proyek & Sipil")
        b_nama_project = st.text_input("Nama Proyek / Klien:", value=st.session_state.b_nama_project, key="b_proj_widget")
        b_no_kontrak = st.text_input("Nomor Gambar Kerja:", value=st.session_state.b_no_kontrak, key="b_kontrak_widget")
        b_config_sep = st.selectbox("Pilihan Konfigurasi Separator Beam:", ['3-SISI', 'KANAN-KIRI', 'KIRI', 'KANAN', 'BELAKANG'], index=['3-SISI', 'KANAN-KIRI', 'KIRI', 'KANAN', 'BELAKANG'].index(st.session_state.b_config_sep))

    with col2:
        st.subheader("Dimensi Hoistway Bersih (mm)")
        b_lebar_sh = st.number_input("Lebar Area Lift / Hoistway (mm):", value=st.session_state.b_lebar_sh, key="b_w_widget")
        b_dalam_sh = st.number_input("Kedalaman Area Lift / Hoistway (mm):", value=st.session_state.b_dalam_sh, key="b_d_widget")
        b_h_pit = st.number_input("Kedalaman PIT Bersih (mm):", value=st.session_state.b_h_pit, key="b_pit_widget")
        b_h_headroom = st.number_input("Tinggi Headroom / Overhead (mm):", value=st.session_state.b_h_headroom, key="b_hr_widget")

    with col3:
        st.subheader("Dimensi Gawang & Penempatan")
        b_jml_lantai = st.number_input("Jumlah Lantai (Stop):", min_value=2, max_value=10, value=st.session_state.b_jml_lantai, key="b_floors_widget")
        b_travel_list = []
        for i in range(1, b_jml_lantai):
            t_val = st.number_input(f"Tinggi Travel Lantai {i} ke {i+1} (mm):", value=3500, key=f"b_t_{i}_widget")
            b_travel_list.append(t_val)
            
        b_lebar_p = st.number_input("Lebar Opening Pintu Bersih (mm):", value=st.session_state.b_lebar_p, key="b_pw_widget")
        b_width_doorway = st.number_input("Lebar Kongleong Opening Sipil (mm):", value=st.session_state.b_width_doorway, key="b_dw_widget")
        b_tinggi_p = st.number_input("Tinggi Opening Pintu Bersih (mm):", value=st.session_state.b_tinggi_p, key="b_ph_widget")
        b_tinggi_gembosan = st.number_input("Total Tinggi Gembosan Sipil Gawang (mm):", value=st.session_state.b_tinggi_gembosan, key="b_gh_widget")
        b_tebal_l = st.number_input("Tebal Balok Cor Gawang Pintu (mm):", value=st.session_state.b_tebal_l, key="b_lt_widget")
        b_dinding_kiri = st.number_input("Jarak Dinding Kiri ke Tepi Doorway (mm):", value=st.session_state.b_dinding_kiri, key="b_lwall_widget")
        b_side_tombol = st.radio("Penempatan Posisi Tombol Pintu (Balok):", ["KANAN", "KIRI"], index=["KANAN", "KIRI"].index(st.session_state.b_side_tombol), horizontal=True, key="b_side_btn_widget")

    st.write("---")
    st.subheader("Preview Dokumen Cetak Biru Resmi")
    elements, t_total, floor_y_positions = generate_structural_layout(b_lebar_sh, b_dalam_sh, b_h_pit, b_h_headroom, b_travel_list)
    
    balok_pdf_data = make_balok_pdf(
        elements, b_lebar_sh, b_dalam_sh, t_total, b_travel_list, floor_y_positions, b_h_headroom,
        b_lebar_p, b_width_doorway, b_tinggi_p, b_tinggi_gembosan, b_tebal_l, b_dinding_kiri, b_config_sep, b_nama_project, b_no_kontrak, b_side_tombol
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
            "side_tombol": b_side_tombol, "config_sep": b_config_sep
        }
        push_history_to_sheets(payload_a)

with tab_kolom:
    st.header("Konfigurasi Gambar Kerja Pilar / Kolom Struktur Utama Vertikal")
    col_k1, col_k2, col_k3 = st.columns(3)
    
    with col_k1:
        st.subheader("Parameter Proyek & Sipil")
        k_nama_project = st.text_input("Nama Proyek / Klien:", value=st.session_state.k_nama_project, key="k_proj_widget")
        k_no_kontrak = st.text_input("Nomor Gambar Kerja:", value=st.session_state.k_no_kontrak, key="k_kontrak_widget")
        k_posisi_cwt = st.radio("Posisi Penempatan CWT Mekanikal:", ["L (KANAN LAYOUT)", "K (KIRI LAYOUT)"], index=["L (KANAN LAYOUT)", "K (KIRI LAYOUT)"].index(st.session_state.k_posisi_cwt), horizontal=True, key="k_cwt_pos_widget")
        cwt_char = k_posisi_cwt[0]
        
        k_lebar_sh = st.number_input("Lebar Area Lift / Hoistway Luar Murni (mm):", value=st.session_state.k_lebar_sh, key="k_w_widget")
        k_dalam_sh = st.number_input("Kedalaman Area Lift / Hoistway Luar Murni (mm):", value=st.session_state.k_dalam_sh, key="k_d_widget")
        k_h_pit = st.number_input("Kedalaman PIT Bersih (mm):", value=st.session_state.k_h_pit, key="k_pit_widget")
        k_h_headroom = st.number_input("Tinggi Headroom / Overhead (mm):", value=st.session_state.k_h_headroom, key="k_hr_widget")
        
    with col_k2:
        st.subheader("Parameter Mekanikal Rel Kunci")
        k_posisi_rel_kabin = st.number_input("Jarak AS REL Kabin ke bibir depan car / kabin (mm):", value=st.session_state.k_posisi_rel_kabin, key="k_rail_pos_widget")
        k_track_gauge_cwt = st.number_input("Jarak antar rel CWT / Secondary Track Gauge (mm):", value=st.session_state.k_track_gauge_cwt, key="k_stg_widget")
        k_tebal_rail_cwt = st.number_input("Ketebalan fisik profil rel CWT (mm):", value=st.session_state.k_tebal_rail_cwt, key="k_tr_widget")
        k_tebal_pintu_luar = st.number_input("Ketebalan mekanisme pintu luar (mm):", value=st.session_state.k_tebal_pintu_luar, key="k_out_door_widget")
        k_celah_daun_pintu = st.number_input("Celah bebas ruang gerak pintu / clearance (mm):", value=st.session_state.k_celah_daun_pintu, key="k_pclear_widget")
        k_tebal_kolom = st.number_input("Ketebalan/Dimensi Kolom Struktur Yang Diinginkan (mm):", value=st.session_state.k_tebal_kolom, key="k_tk_widget")

    with col_k3:
        st.subheader("Dimensi Gawang Opening Depan")
        k_jml_lantai = st.number_input("Jumlah Lantai (Stop):", min_value=2, max_value=10, value=st.session_state.k_jml_lantai, key="k_floors_widget")
        k_travel_list = []
        for i in range(1, k_jml_lantai):
            t_val = st.number_input(f"Tinggi Travel Lantai {i} ke {i+1} (mm):", value=3500, key=f"k_t_{i}_widget")
            k_travel_list.append(t_val)
            
        k_lebar_p = st.number_input("Lebar Opening Pintu Bersih (mm):", value=st.session_state.k_lebar_p, key="k_pw_col_widget")
        k_width_doorway = st.number_input("Lebar Kongleong Sipil Opening (mm):", value=st.session_state.k_width_doorway, key="k_dw_col_widget")
        k_tinggi_p = st.number_input("Tinggi Opening Pintu Bersih (mm):", value=st.session_state.k_tinggi_p, key="k_ph_col_widget")
        k_tinggi_gembosan = st.number_input("Total Tinggi Gembosan Sipil Gawang Pintu (mm):", value=st.session_state.k_tinggi_gembosan, key="k_gh_col_widget")
        k_tebal_l = st.number_input("Tebal Balok Cor Lintel di atas pintu (mm):", value=st.session_state.k_tebal_l, key="k_lt_col_widget")
        k_dinding_kiri = st.number_input("Jarak asimetris dinding kiri KUPINGAN OPENING (mm):", value=st.session_state.k_dinding_kiri, key="k_lwall_col_widget")
        k_side_tombol = st.radio("Penempatan Posisi Tombol Pintu (Kolom):", ["KANAN", "KIRI"], index=["KANAN", "KIRI"].index(st.session_state.k_side_tombol), horizontal=True, key="k_side_btn_widget")

    st.write("---")
    st.subheader("Preview Dokumen Cetak Biru Resmi")
    
    kolom_pdf_data = make_kolom_pdf(
        k_lebar_sh, k_dalam_sh, k_h_pit, k_h_headroom, k_travel_list, k_posisi_rel_kabin,
        k_track_gauge_cwt, k_tebal_rail_cwt, k_tebal_pintu_luar, k_celah_daun_pintu, k_tebal_kolom,
        k_lebar_p, k_width_doorway, k_tinggi_p, k_tinggi_gembosan, k_tebal_l, k_dinding_kiri, k_nama_project, k_no_kontrak, cwt_char, k_side_tombol
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
            "jml_lantai": k_f_num, "lebar_pintu_bersih": k_lebar_p, "width_doorway": k_width_doorway,
            "tinggi_p": k_tinggi_p, "tinggi_gembosan": k_tinggi_gembosan, "tebal_l": k_tebal_l, "dinding_kiri": k_dinding_kiri,
            "side_tombol": k_side_tombol, "posisi_cwt_raw": k_posisi_cwt, "posisi_rel_kabin": k_posisi_rel_kabin,
            "track_gauge_cwt": k_track_gauge_cwt, "tebal_rail_cwt": k_tebal_rail_cwt, "tebal_pintu_luar": k_tebal_pintu_luar,
            "celah_daun_pintu": k_celah_daun_pintu, "tebal_kolom": k_tebal_kolom
        }
        push_history_to_sheets(payload_b)