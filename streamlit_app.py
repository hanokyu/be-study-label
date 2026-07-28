import streamlit as st
import io
import json
import os
import html
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

LAST_PARAMS_FILE = "last_params.json"

# Khổ nhãn ổn định (mặc định) - KHÔNG thay đổi hành vi hiện tại nếu người dùng
# không bật phần tuỳ chỉnh thử nghiệm bên dưới.
DEFAULT_LAYOUT = {
    "cols": 5,
    "rows": 6,
    "label_width_mm": 37.0,
    "label_height_mm": 25.0,
    "margin_x_mm": 6.0,
    "margin_y_mm": 4.0,
    "spacing_x_mm": 4.0,
    "spacing_y_mm": 2.0,
    "font_header": 12,
    "font_header_sub": 10,
    "font_data": 12,
}


def load_last_params():
    """Load last-used input values from disk, if any."""
    if os.path.exists(LAST_PARAMS_FILE):
        try:
            with open(LAST_PARAMS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_last_params(params):
    """Persist current input values to disk for the next session."""
    try:
        with open(LAST_PARAMS_FILE, "w", encoding="utf-8") as f:
            json.dump(params, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


@st.cache_data
def build_label_data(study_code, num_subjects, num_timepoints, num_periods, page_size):
    """Build the full ordered list of label dicts (headers + data), padded to full pages."""
    all_labels = []
    subjects = range(1, num_subjects + 1)
    timepoints = [f"{i:02d}" for i in range(num_timepoints)]

    for period in range(1, num_periods + 1):

        # BẢN 1: ỐNG TỔNG (sort theo người tình nguyện)
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
                    'Tube_ID': f"{period}.{sub:02d}.{tp}"
                })
        while len(all_labels) % page_size != 0:
            all_labels.append(None)

        # BẢN 2: ỐNG A (sort theo thời điểm)
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
                    'Tube_ID': f"{period}.{sub:02d}.{tp}_A"
                })
        while len(all_labels) % page_size != 0:
            all_labels.append(None)

        # BẢN 3: ỐNG S (sort theo thời điểm)
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
                    'Tube_ID': f"{period}.{sub:02d}.{tp}_S"
                })
        while len(all_labels) % page_size != 0:
            all_labels.append(None)

    return all_labels


def build_preview_sample(study_code, num_subjects, num_timepoints, page_size):
    """Build just enough labels (one page) to check the layout - stops early, no
    need to walk every subject/timepoint like the full PDF data does."""
    labels = [{
        'is_header': True,
        'line1': "GIAI DOAN 1",
        'line2': "ONG TONG",
        'line3': "(Theo doi tuong)"
    }]
    for sub in range(1, num_subjects + 1):
        if len(labels) >= page_size:
            break
        for tp in range(num_timepoints):
            if len(labels) >= page_size:
                break
            labels.append({
                'is_header': False,
                'Study_Code': f"{study_code} - Per 1",
                'Subject_Time': f"S{sub:02d} - T{tp:02d}",
                'Tube_ID': f"1.{sub:02d}.{tp:02d}"
            })
    labels += [None] * (page_size - len(labels))
    return labels[:page_size]


def render_pdf(all_labels, layout):
    """Draw the label grid into a PDF and return it as a BytesIO buffer."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    cols = layout["cols"]
    rows = layout["rows"]
    page_size = cols * rows
    label_width = layout["label_width_mm"] * mm
    label_height = layout["label_height_mm"] * mm
    margin_x = layout["margin_x_mm"] * mm
    margin_y = layout["margin_y_mm"] * mm
    spacing_x = layout["spacing_x_mm"] * mm
    spacing_y = layout["spacing_y_mm"] * mm
    font_header = layout["font_header"]
    font_header_sub = layout["font_header_sub"]
    font_data = layout["font_data"]

    for i, label in enumerate(all_labels):
        idx_on_page = i % page_size
        col_idx = idx_on_page % cols
        row_idx = idx_on_page // cols

        if label is not None:
            x = margin_x + col_idx * (label_width + spacing_x)
            y_top = height - margin_y - row_idx * (label_height + spacing_y)
            center_x = x + (label_width / 2)

            if label.get('is_header'):
                c.setFont("Times-Bold", font_header)
                c.drawCentredString(center_x, y_top - 8 * mm, label['line1'])
                c.drawCentredString(center_x, y_top - 14 * mm, label['line2'])
                c.setFont("Times-Italic", font_header_sub)
                c.drawCentredString(center_x, y_top - 20 * mm, label['line3'])
            else:
                c.setFont("Times-Roman", font_data)
                c.drawCentredString(center_x, y_top - 8 * mm, label['Study_Code'])
                c.drawCentredString(center_x, y_top - 14 * mm, label['Subject_Time'])
                c.drawCentredString(center_x, y_top - 20 * mm, label['Tube_ID'])

        if idx_on_page == page_size - 1:
            c.showPage()

    c.save()
    buffer.seek(0)
    return buffer


def generate_be_labels(study_code, num_subjects, num_timepoints, num_periods, layout):
    """Generate BE labels and return PDF as bytes."""
    page_size = layout["cols"] * layout["rows"]
    all_labels = build_label_data(study_code, num_subjects, num_timepoints, num_periods, page_size)
    return render_pdf(all_labels, layout)


def render_label_cell(label, layout):
    """Render a single label as an HTML grid cell, in real mm/pt units so it
    matches the printed PDF and makes text overflow visible during preview."""
    if label is None:
        return '<div style="border:1px dashed rgba(150,150,150,0.35);border-radius:4px;"></div>'

    font_header = layout["font_header"]
    font_header_sub = layout["font_header_sub"]
    font_data = layout["font_data"]

    if label.get('is_header'):
        line1 = html.escape(label['line1'])
        line2 = html.escape(label['line2'])
        line3 = html.escape(label['line3'])
        return f'''
        <div style="border:1px solid rgba(150,150,150,0.6);border-radius:4px;
            display:flex;flex-direction:column;align-items:center;justify-content:center;
            text-align:center;overflow:hidden;padding:1mm;
            background:rgba(255,193,7,0.12);font-family:'Times New Roman',Times,serif;">
            <div style="font-weight:bold;font-size:{font_header}pt;line-height:1.15;">{line1}</div>
            <div style="font-weight:bold;font-size:{font_header}pt;line-height:1.15;">{line2}</div>
            <div style="font-style:italic;font-size:{font_header_sub}pt;line-height:1.15;">{line3}</div>
        </div>'''

    study_code = html.escape(label['Study_Code'])
    subject_time = html.escape(label['Subject_Time'])
    tube_id = html.escape(label['Tube_ID'])
    return f'''
    <div style="border:1px solid rgba(150,150,150,0.6);border-radius:4px;
        display:flex;flex-direction:column;align-items:center;justify-content:center;
        text-align:center;overflow:hidden;padding:1mm;
        font-family:'Times New Roman',Times,serif;">
        <div style="font-size:{font_data}pt;line-height:1.15;">{study_code}</div>
        <div style="font-size:{font_data}pt;line-height:1.15;">{subject_time}</div>
        <div style="font-size:{font_data}pt;line-height:1.15;">{tube_id}</div>
    </div>'''


PREVIEW_MAX_WIDTH_PX = 700  # approx. content width of Streamlit's "centered" layout
MM_TO_PX = 96 / 25.4  # CSS reference pixel definition


def render_label_page(page_labels, layout):
    """Render one page as a CSS grid sized in real mm/pt (so font vs. box
    proportions match the PDF 1:1), scaled down to fit the visible width so
    the whole page is visible without horizontal scrolling."""
    cols = layout["cols"]
    rows_needed = -(-len(page_labels) // cols)
    total_w_mm = cols * layout["label_width_mm"] + (cols - 1) * layout["spacing_x_mm"]
    total_h_mm = rows_needed * layout["label_height_mm"] + (rows_needed - 1) * layout["spacing_y_mm"]
    total_w_px = total_w_mm * MM_TO_PX
    total_h_px = total_h_mm * MM_TO_PX
    scale = min(1.0, PREVIEW_MAX_WIDTH_PX / total_w_px)

    cells_html = "".join(render_label_cell(label, layout) for label in page_labels)
    st.markdown(
        f'<div style="width:{total_w_px * scale:.0f}px;height:{total_h_px * scale:.0f}px;'
        f'max-width:100%;overflow:auto;position:relative;">'
        f'<div style="position:absolute;top:0;left:0;display:grid;'
        f'grid-template-columns:repeat({cols},{layout["label_width_mm"]}mm);'
        f'grid-auto-rows:{layout["label_height_mm"]}mm;'
        f'column-gap:{layout["spacing_x_mm"]}mm;row-gap:{layout["spacing_y_mm"]}mm;'
        f'transform:scale({scale});transform-origin:top left;">'
        f'{cells_html}</div></div>',
        unsafe_allow_html=True
    )


# ==========================================
# GIAO DIỆN STREAMLIT
# ==========================================

st.set_page_config(
    page_title="Tạo Nhãn Ống Nghiệm BE",
    page_icon="🧪",
    layout="centered"
)

# Khởi tạo session_state TRƯỚC tất cả widget
if "pdf_buffer" not in st.session_state:
    st.session_state.pdf_buffer = None
if "pdf_filename" not in st.session_state:
    st.session_state.pdf_filename = None

last_params = load_last_params()

st.title("🧪 Tạo Nhãn Ống Nghiệm BE")
st.markdown("Nhập thông số nghiên cứu bên dưới, sau đó nhấn **Tạo PDF** để tải file về.")

st.divider()

col1, col2 = st.columns(2)

with col1:
    study_code = st.text_input(
        "Mã nghiên cứu (Study Code)",
        value=last_params.get("study_code", "17BE2025"),
        help="Ví dụ: 17BE2025"
    )
    num_subjects = st.number_input(
        "Số người tình nguyện",
        min_value=1, max_value=200,
        value=last_params.get("num_subjects", 36),
        step=1
    )

with col2:
    num_periods = st.number_input(
        "Số giai đoạn (Periods)",
        min_value=1, max_value=10,
        value=last_params.get("num_periods", 2),
        step=1
    )
    num_timepoints = st.number_input(
        "Số thời điểm lấy mẫu",
        min_value=1, max_value=50,
        value=last_params.get("num_timepoints", 15),
        step=1,
        help=f"Tự động tạo từ T00 đến T(n-1)"
    )

# Ghi nhớ thông số hiện tại để lần sau mở app sẽ tự điền lại
save_last_params({
    "study_code": study_code,
    "num_subjects": num_subjects,
    "num_periods": num_periods,
    "num_timepoints": num_timepoints,
})

# Hiển thị thông tin tổng quan
st.divider()
st.subheader("📋 Thông tin tổng quan")

total_tubes = num_subjects * num_timepoints * num_periods
col_a, col_b, col_c = st.columns(3)
col_a.metric("Tổng số ống (mỗi loại)", f"{num_subjects * num_timepoints * num_periods:,}")
col_b.metric("Thời điểm", f"T00 → T{num_timepoints - 1:02d}")
col_c.metric("Tổng nhãn (×3 bản)", f"{total_tubes * 3:,}")

# Khổ nhãn - mặc định ổn định (Tomy A4 5x6), có thể bật tuỳ chỉnh thử nghiệm
st.divider()
with st.expander("🧪 Tuỳ chỉnh khổ nhãn (thử nghiệm)"):
    st.caption(
        "Mặc định dùng khổ ổn định Tomy A4 5×6. Bật tuỳ chỉnh nếu bạn dùng loại "
        "giấy tem khác - dùng phần Xem trước bên dưới để kiểm tra chữ không bị tràn nhãn."
    )
    use_custom_layout = st.checkbox("Dùng khổ nhãn tuỳ chỉnh", value=False)

    if use_custom_layout:
        c1, c2 = st.columns(2)
        with c1:
            cols = st.number_input("Số cột / trang", min_value=1, max_value=12, value=DEFAULT_LAYOUT["cols"])
            label_width_mm = st.number_input("Chiều rộng nhãn (mm)", min_value=10.0, max_value=100.0, value=DEFAULT_LAYOUT["label_width_mm"], step=1.0)
            margin_x_mm = st.number_input("Lề trái/phải (mm)", min_value=0.0, max_value=30.0, value=DEFAULT_LAYOUT["margin_x_mm"], step=0.5)
            spacing_x_mm = st.number_input("Khoảng cách ngang giữa nhãn (mm)", min_value=0.0, max_value=20.0, value=DEFAULT_LAYOUT["spacing_x_mm"], step=0.5)
        with c2:
            rows = st.number_input("Số hàng / trang", min_value=1, max_value=15, value=DEFAULT_LAYOUT["rows"])
            label_height_mm = st.number_input("Chiều cao nhãn (mm)", min_value=10.0, max_value=100.0, value=DEFAULT_LAYOUT["label_height_mm"], step=1.0)
            margin_y_mm = st.number_input("Lề trên/dưới (mm)", min_value=0.0, max_value=30.0, value=DEFAULT_LAYOUT["margin_y_mm"], step=0.5)
            spacing_y_mm = st.number_input("Khoảng cách dọc giữa nhãn (mm)", min_value=0.0, max_value=20.0, value=DEFAULT_LAYOUT["spacing_y_mm"], step=0.5)

        auto_font = st.checkbox(
            "Tự động co cỡ chữ theo kích thước nhãn (khuyến nghị)",
            value=True,
            help="Co giãn cỡ chữ theo tỉ lệ kích thước nhãn so với khổ mặc định để giữ bố cục, tránh tràn chữ."
        )
        scale = min(label_width_mm / DEFAULT_LAYOUT["label_width_mm"], label_height_mm / DEFAULT_LAYOUT["label_height_mm"])
        if auto_font:
            font_header = max(6, round(DEFAULT_LAYOUT["font_header"] * scale))
            font_header_sub = max(6, round(DEFAULT_LAYOUT["font_header_sub"] * scale))
            font_data = max(6, round(DEFAULT_LAYOUT["font_data"] * scale))
            st.caption(f"Cỡ chữ tự động: tiêu đề {font_header}pt · phụ đề {font_header_sub}pt · dữ liệu {font_data}pt")
        else:
            font_header = st.number_input("Cỡ chữ tiêu đề (pt)", min_value=4, max_value=24, value=DEFAULT_LAYOUT["font_header"])
            font_header_sub = st.number_input("Cỡ chữ phụ đề (pt)", min_value=4, max_value=24, value=DEFAULT_LAYOUT["font_header_sub"])
            font_data = st.number_input("Cỡ chữ dữ liệu (pt)", min_value=4, max_value=24, value=DEFAULT_LAYOUT["font_data"])

        layout = {
            "cols": cols, "rows": rows,
            "label_width_mm": label_width_mm, "label_height_mm": label_height_mm,
            "margin_x_mm": margin_x_mm, "margin_y_mm": margin_y_mm,
            "spacing_x_mm": spacing_x_mm, "spacing_y_mm": spacing_y_mm,
            "font_header": font_header, "font_header_sub": font_header_sub, "font_data": font_data,
        }

        total_w = margin_x_mm * 2 + cols * label_width_mm + (cols - 1) * spacing_x_mm
        total_h = margin_y_mm * 2 + rows * label_height_mm + (rows - 1) * spacing_y_mm
        # Cho phép dung sai nhỏ (khổ mặc định 213mm đã dùng ổn định từ trước, sát mép A4 210mm)
        a4_tolerance_mm = 5
        if total_w > 210 + a4_tolerance_mm or total_h > 297 + a4_tolerance_mm:
            st.warning(
                f"⚠️ Bố cục hiện cần khoảng {total_w:.0f}×{total_h:.0f}mm, vượt khổ A4 (210×297mm). "
                "Hãy giảm số cột/hàng hoặc khoảng cách."
            )
    else:
        layout = DEFAULT_LAYOUT

page_size = layout["cols"] * layout["rows"]

# Xem trước nhãn - chỉ trang đầu tiên, đủ để kiểm tra hình dạng và nội dung chữ
st.divider()
st.subheader("👁️ Xem trước nhãn")
st.caption("Xem trang đầu tiên (Ống Tổng - Giai đoạn 1) để kiểm tra bố cục và cỡ chữ trước khi in.")

preview_code = study_code.strip() if study_code.strip() else "(chưa nhập)"
preview_labels = build_preview_sample(preview_code, num_subjects, num_timepoints, page_size)
render_label_page(preview_labels, layout)

st.divider()

# Reset PDF cũ nếu thông số thay đổi
current_key = (
    f"{study_code}_{num_subjects}_{num_timepoints}_{num_periods}_"
    f"{layout['cols']}_{layout['rows']}_{layout['label_width_mm']}_{layout['label_height_mm']}_"
    f"{layout['margin_x_mm']}_{layout['margin_y_mm']}_{layout['spacing_x_mm']}_{layout['spacing_y_mm']}_"
    f"{layout['font_header']}_{layout['font_header_sub']}_{layout['font_data']}"
)
if st.session_state.get("last_key") != current_key:
    st.session_state.pdf_buffer = None
    st.session_state.pdf_filename = None
    st.session_state.last_key = current_key

if st.button("🖨️ Tạo PDF", type="primary", use_container_width=True):
    if not study_code.strip():
        st.error("⚠️ Vui lòng nhập Mã nghiên cứu!")
    else:
        with st.spinner("Đang tạo file PDF..."):
            try:
                pdf_buffer = generate_be_labels(
                    study_code.strip(),
                    num_subjects,
                    num_timepoints,
                    num_periods,
                    layout
                )
                st.session_state.pdf_buffer = pdf_buffer.getvalue()
                st.session_state.pdf_filename = f"Nhan_{study_code.strip()}_{num_periods}Periods.pdf"
            except Exception as e:
                st.error(f"❌ Lỗi khi tạo PDF: {e}")

# Nút tải xuống luôn hiển thị nếu đã có PDF trong session
if st.session_state.pdf_buffer is not None:
    st.success("✅ Tạo PDF thành công! Nhấn nút bên dưới để tải về.")
    st.download_button(
        label="⬇️ Tải xuống PDF",
        data=st.session_state.pdf_buffer,
        file_name=st.session_state.pdf_filename,
        mime="application/pdf",
        use_container_width=True
    )

st.divider()
st.caption("Mỗi giai đoạn gồm 3 bản nhãn: Ống Tổng (theo đối tượng), Ống A (theo thời điểm), Ống S (theo thời điểm). Khổ giấy mặc định: Tomy A4 – 5×6 nhãn/tờ.")
