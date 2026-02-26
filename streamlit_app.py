import streamlit as st
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

st.set_page_config(page_title="Tạo Nhãn Ống Nghiệm BE", page_icon="🧪", layout="centered")
st.title("🧪 Phần Mềm Tạo Nhãn Ống Nghiệm BE")
st.markdown("Nhập thông số nghiên cứu bên dưới để tự động tạo file PDF in nhãn.")

def generate_be_pdf(study_code, num_subjects, num_timepoints, num_periods):
    buffer = io.BytesIO()
    all_labels = []
    subjects = range(1, num_subjects + 1)
    timepoints = [f"{i:02d}" for i in range(num_timepoints)]
    
    for period in range(1, num_periods + 1):
        # BẢN 1: TỔNG
        all_labels.append({'is_header': True, 'line1': f"GIAI DOAN {period}", 'line2': "ONG TONG", 'line3': "(Theo doi tuong)"})
        for sub in subjects:
            for tp in timepoints:
                all_labels.append({'is_header': False, 'Study_Code': f"{study_code} - Per {period}", 'Subject_Time': f"S{sub:02d} - T{tp}", 'Tube_ID': f"{period}.{sub:02d}.{tp}_Tong"})
        while len(all_labels) % 30 != 0:
            all_labels.append(None)
            
        # BẢN 2: ỐNG A
        all_labels.append({'is_header': True, 'line1': f"GIAI DOAN {period}", 'line2': "ONG A", 'line3': "(Theo thoi diem)"})
        for tp in timepoints:
            for sub in subjects:
                all_labels.append({'is_header': False, 'Study_Code': f"{study_code} - Per {period}", 'Subject_Time': f"S{sub:02d} - T{tp}", 'Tube_ID': f"{period}.{sub:02d}.{tp}_A"})
        while len(all_labels) % 30 != 0:
            all_labels.append(None)
            
        # BẢN 3: ỐNG S
        all_labels.append({'is_header': True, 'line1': f"GIAI DOAN {period}", 'line2': "ONG S", 'line3': "(Theo thoi diem)"})
        for tp in timepoints:
            for sub in subjects:
                all_labels.append({'is_header': False, 'Study_Code': f"{study_code} - Per {period}", 'Subject_Time': f"S{sub:02d} - T{tp}", 'Tube_ID': f"{period}.{sub:02d}.{tp}_S"})
        while len(all_labels) % 30 != 0:
            all_labels.append(None)

    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    cols, rows = 5, 6
    label_width, label_height = 37 * mm, 25 * mm  
    margin_x, margin_y = 6 * mm, 4 * mm       
    spacing_x, spacing_y = 4 * mm, 2 * mm      
    
    for i, label in enumerate(all_labels):
        idx_on_page = i % (cols * rows)
        col_idx = idx_on_page % cols
        row_idx = idx_on_page // cols
        
        if label is not None:
            x = margin_x + col_idx * (label_width + spacing_x)
            y_top = height - margin_y - row_idx * (label_height + spacing_y)
            center_x = x + (label_width / 2)
            
            if label.get('is_header'):
                c.setFont("Times-Bold", 12)
                c.drawCentredString(center_x, y_top - 8 * mm, label['line1'])
                c.drawCentredString(center_x, y_top - 14 * mm, label['line2'])
                c.setFont("Times-Italic", 10)
                c.drawCentredString(center_x, y_top - 20 * mm, label['line3'])
            else:
                c.setFont("Times-Roman", 12)
                c.drawCentredString(center_x, y_top - 8 * mm, label['Study_Code'])
                c.drawCentredString(center_x, y_top - 14 * mm, label['Subject_Time'])
                c.drawCentredString(center_x, y_top - 20 * mm, label['Tube_ID'])
        
        if idx_on_page == (cols * rows) - 1:
            c.showPage()
            
    c.save()
    buffer.seek(0)
    return buffer

# ==========================================
# 3. GIAO DIỆN NHẬP LIỆU
# ==========================================
with st.form("input_form"):
    col1, col2 = st.columns(2)
    with col1:
        # Sửa lại value thành chữ "18BE2025" thay vì gọi session_state
        study_code = st.text_input("Mã Nghiên Cứu (VD: 18BE2025)", value="18BE2025")
        num_subjects = st.number_input("Số Tình Nguyện Viên", min_value=1, value=10, step=1)
    with col2:
        num_timepoints = st.number_input("Số Thời Điểm Lấy Mẫu", min_value=1, value=15, step=1)
        num_periods = st.number_input("Số Giai Đoạn (Periods)", min_value=1, value=2, step=1)
        
    submit_btn = st.form_submit_button("⚙️ Tạo File Nhãn PDF")

# ==========================================
# 4. LƯU FILE VÀO BỘ NHỚ TẠM (SESSION STATE)
# ==========================================
if submit_btn:
    with st.spinner("Đang xử lý dữ liệu..."):
        pdf_buffer = generate_be_pdf(study_code, num_subjects, num_timepoints, num_periods)
        
        # Lưu file và tên file vào session_state
        st.session_state['pdf_buffer'] = pdf_buffer
        st.session_state['file_name'] = f"Nhan_{study_code}_{num_periods}Periods.pdf"

# ==========================================
# 5. HIỂN THỊ NÚT TẢI
# ==========================================
if 'pdf_buffer' in st.session_state:
    st.success("✅ File đã sẵn sàng! Bấm nút bên dưới để tải về.")
    st.download_button(
        label="⬇️ TẢI FILE PDF VỀ MÁY",
        data=st.session_state['pdf_buffer'],
        file_name=st.session_state['file_name'],
        mime="application/pdf"
    )
