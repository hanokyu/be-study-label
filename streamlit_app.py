import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

def generate_be_full_workflow(study_code, num_subjects, num_timepoints, num_periods, output_pdf):
    all_labels = []
    subjects = range(1, num_subjects + 1)
    
    # Tự động tạo list thời điểm từ 00 đến (num_timepoints - 1)
    timepoints = [f"{i:02d}" for i in range(num_timepoints)]
    
    # Lặp qua các giai đoạn (1, 2, 3...)
    for period in range(1, num_periods + 1):
        
        # ==========================================
        # BẢN 1: TỔNG (SORT THEO NGƯỜI TÌNH NGUYỆN) 
        # ==========================================
        # Chèn nhãn chỉ mục ở đầu
        all_labels.append({
            'is_header': True,
            'line1': f"GIAI DOAN {period}",
            'line2': "ONG TONG",
            'line3': "(Theo doi tuong)"
        })
        
        for sub in subjects:
            for tp in timepoints:
                all_labels.append({
                    'is_header': False,
                    'Study_Code': f"{study_code} - Per {period}",
                    'Subject_Time': f"S{sub:02d} - T{tp}",
                    'Blank line': "\n",  # Dòng trống để tạo khoảng cách giữa các dòng
                    'Tube_ID': f"{period}.{sub:02d}.{tp}"
                })
        
        # Chèn nhãn trống làm đầy trang cuối để Bản 2 bắt đầu ở tờ giấy mới
        while len(all_labels) % 30 != 0:
            all_labels.append(None)
            
        # ==========================================
        # BẢN 2: ỐNG A (SORT THEO THỜI ĐIỂM)
        # ==========================================
        all_labels.append({
            'is_header': True,
            'line1': f"GIAI DOAN {period}",
            'line2': "ONG A",
            'line3': "(Theo thoi diem)"
        })
        
        for tp in timepoints:
            for sub in subjects:
                all_labels.append({
                    'is_header': False,
                    'Study_Code': f"{study_code} - Per {period}",
                    'Subject_Time': f"S{sub:02d} - T{tp}",
                    'Blank line': "\n",  # Dòng trống để tạo khoảng cách giữa các dòng
                    'Tube_ID': f"{period}.{sub:02d}.{tp}_A"
                })
                
        while len(all_labels) % 30 != 0:
            all_labels.append(None)
            
        # ==========================================
        # BẢN 3: ỐNG S (SORT THEO THỜI ĐIỂM)
        # ==========================================
        all_labels.append({
            'is_header': True,
            'line1': f"GIAI DOAN {period}",
            'line2': "ONG S",
            'line3': "(Theo thoi diem)"
        })
        
        for tp in timepoints:
            for sub in subjects:
                all_labels.append({
                    'is_header': False,
                    'Study_Code': f"{study_code} - Per {period}",
                    'Subject_Time': f"S{sub:02d} - T{tp}",
                    'Blank line': "\n",  # Dòng trống để tạo khoảng cách giữa các dòng
                    'Tube_ID': f"{period}.{sub:02d}.{tp}_S"
                })
                
        while len(all_labels) % 30 != 0:
            all_labels.append(None)

    # ==========================================
    # VẼ VÀ XUẤT FILE PDF
    # ==========================================
    c = canvas.Canvas(output_pdf, pagesize=A4)
    width, height = A4
    
    # THÔNG SỐ GIẤY TOMY CHÍNH XÁC TỪ ILLUSTRATOR
    cols = 5
    rows = 6
    label_width = 37 * mm   
    label_height = 25 * mm  
    margin_x = 6 * mm       
    margin_y = 4 * mm       
    spacing_x = 4 * mm      
    spacing_y = 2 * mm      
    
    for i, label in enumerate(all_labels):
        idx_on_page = i % (cols * rows)
        col_idx = idx_on_page % cols
        row_idx = idx_on_page // cols
        
        if label is not None:
            # Tọa độ mép trái và mép trên của nhãn hiện tại
            x = margin_x + col_idx * (label_width + spacing_x)
            y_top = height - margin_y - row_idx * (label_height + spacing_y)
            center_x = x + (label_width / 2)
            
            # Kiểm tra xem đây là nhãn chỉ mục hay nhãn ống nghiệm bình thường
            if label.get('is_header'):
                # VẼ NHÃN PHÂN BIỆT (CHỈ MỤC)
                c.setFont("Times-Bold", 12)
                c.drawCentredString(center_x, y_top - 8 * mm, label['line1'])
                c.drawCentredString(center_x, y_top - 14 * mm, label['line2'])
                
                c.setFont("Times-Italic", 10)
                c.drawCentredString(center_x, y_top - 20 * mm, label['line3'])
            else:
                # VẼ NHÃN ỐNG NGHIỆM BÌNH THƯỜNG
                c.setFont("Times-Roman", 12)
                c.drawCentredString(center_x, y_top - 8 * mm, label['Study_Code'])
                c.drawCentredString(center_x, y_top - 14 * mm, label['Subject_Time'])
                c.drawCentredString(center_x, y_top - 20 * mm, label['Tube_ID'])
        
        # Hết 30 vị trí (1 tờ A4) thì sang trang mới
        if idx_on_page == (cols * rows) - 1:
            c.showPage()
            
    c.save()
    print(f"Đã tạo thành công bộ nhãn. File xuất ra: {output_pdf}")

# ==========================================
# CẤU HÌNH THÔNG SỐ NGHIÊN CỨU
# ==========================================
if __name__ == "__main__":
    STUDY_CODE = "17BE2025"
    NUM_SUBJECTS = 36    # Số lượng người tình nguyện
    NUM_TIMEPOINTS = 15  # Số thời điểm (tự động tạo từ T00 đến T14)
    NUM_PERIODS = 2      # Số giai đoạn (Ví dụ: 3 giai đoạn)
    
    OUTPUT_FILE = f"Nhan_{STUDY_CODE}_{NUM_PERIODS}Periods.pdf"
    
    generate_be_full_workflow(STUDY_CODE, NUM_SUBJECTS, NUM_TIMEPOINTS, NUM_PERIODS, OUTPUT_FILE)