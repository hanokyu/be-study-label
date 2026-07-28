import streamlit as st
import io
import json
import os
import html
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

LABELS_PER_PAGE = 30  # 5 cols x 6 rows
LAST_PARAMS_FILE = "last_params.json"


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
def build_label_data(study_code, num_subjects, num_timepoints, num_periods):
    """Build the ordered list of label dicts (headers + data), padded to full pages."""
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
        while len(all_labels) % LABELS_PER_PAGE != 0:
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
        while len(all_labels) % LABELS_PER_PAGE != 0:
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
        while len(all_labels) % LABELS_PER_PAGE != 0:
            all_labels.append(None)

    return all_labels


def render_pdf(all_labels):
    """Draw the label grid into a PDF and return it as a BytesIO buffer."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

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


def generate_be_labels(study_code, num_subjects, num_timepoints, num_periods):
    """Generate BE labels and return PDF as bytes."""
    all_labels = build_label_data(study_code, num_subjects, num_timepoints, num_periods)
    return render_pdf(all_labels)


def render_label_cell(label):
    """Render a single label as an HTML grid cell, mirroring the PDF layout."""
    if label is None:
        return (
            '<div style="aspect-ratio:37/25;border:1px dashed rgba(150,150,150,0.35);'
            'border-radius:4px;"></div>'
        )

    if label.get('is_header'):
        line1 = html.escape(label['line1'])
        line2 = html.escape(label['line2'])
        line3 = html.escape(label['line3'])
        return f'''
        <div style="aspect-ratio:37/25;border:1px solid rgba(150,150,150,0.6);
            border-radius:4px;display:flex;flex-direction:column;align-items:center;
            justify-content:center;text-align:center;padding:2px;
            background:rgba(255,193,7,0.12);font-family:'Times New Roman',Times,serif;">
            <div style="font-weight:bold;font-size:0.8em;">{line1}</div>
            <div style="font-weight:bold;font-size:0.8em;">{line2}</div>
            <div style="font-style:italic;font-size:0.7em;">{line3}</div>
        </div>'''

    study_code = html.escape(label['Study_Code'])
    subject_time = html.escape(label['Subject_Time'])
    tube_id = html.escape(label['Tube_ID'])
    return f'''
    <div style="aspect-ratio:37/25;border:1px solid rgba(150,150,150,0.6);
        border-radius:4px;display:flex;flex-direction:column;align-items:center;
        justify-content:center;text-align:center;padding:2px;
        font-family:'Times New Roman',Times,serif;">
        <div style="font-size:0.78em;">{study_code}</div>
        <div style="font-size:0.78em;">{subject_time}</div>
        <div style="font-size:0.78em;">{tube_id}</div>
    </div>'''


def render_label_page(page_labels):
    """Render one page (up to 30 labels) as a 5x6 CSS grid, matching the PDF sheet."""
    cells_html = "".join(render_label_cell(label) for label in page_labels)
    st.markdown(
        f'<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:6px;">'
        f'{cells_html}</div>',
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

# Hiển thị preview thông tin
st.divider()
st.subheader("📋 Thông tin tổng quan")

total_tubes = num_subjects * num_timepoints * num_periods
col_a, col_b, col_c = st.columns(3)
col_a.metric("Tổng số ống (mỗi loại)", f"{num_subjects * num_timepoints * num_periods:,}")
col_b.metric("Thời điểm", f"T00 → T{num_timepoints - 1:02d}")
col_c.metric("Tổng nhãn (×3 bản)", f"{total_tubes * 3:,}")

# Xem trước nhãn
st.divider()
st.subheader("👁️ Xem trước nhãn")

preview_code = study_code.strip() if study_code.strip() else "(chưa nhập)"
all_labels = build_label_data(preview_code, num_subjects, num_timepoints, num_periods)
total_pages = (len(all_labels) + LABELS_PER_PAGE - 1) // LABELS_PER_PAGE

preview_page = st.number_input(
    f"Trang xem trước (tổng {total_pages} trang)",
    min_value=1, max_value=total_pages,
    value=1, step=1
)
page_start = (preview_page - 1) * LABELS_PER_PAGE
page_labels = all_labels[page_start:page_start + LABELS_PER_PAGE]
render_label_page(page_labels)
st.caption("Bố cục xem trước tương ứng với khổ giấy Tomy A4 – 5×6 nhãn/tờ khi in PDF.")

st.divider()

# Reset PDF cũ nếu thông số thay đổi
current_key = f"{study_code}_{num_subjects}_{num_timepoints}_{num_periods}"
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
                pdf_buffer = render_pdf(all_labels)
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
st.caption("Mỗi giai đoạn gồm 3 bản nhãn: Ống Tổng (theo đối tượng), Ống A (theo thời điểm), Ống S (theo thời điểm). Khổ giấy: Tomy A4 – 5×6 nhãn/tờ.")
