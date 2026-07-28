# 🧪 Tạo Nhãn Ống Nghiệm BE

Ứng dụng Streamlit tạo nhãn in cho ống nghiệm trong nghiên cứu tương đương sinh học
(Bioequivalence – BE). Từ các thông số của nghiên cứu (mã nghiên cứu, số người tình
nguyện, số giai đoạn, số thời điểm lấy mẫu), ứng dụng tự động sinh file PDF chứa toàn
bộ nhãn, sẵn sàng để in trên khổ giấy tem Tomy A4 (5 cột × 6 hàng nhãn/tờ).

Mỗi giai đoạn (period) gồm 3 bản nhãn:

- **Ống Tổng** – sắp xếp theo người tình nguyện
- **Ống A** – sắp xếp theo thời điểm lấy mẫu
- **Ống S** – sắp xếp theo thời điểm lấy mẫu

## Tính năng

- **Sinh PDF nhãn** theo đúng khổ giấy 5×6 nhãn/tờ, tự động phân trang.
- **Xem trước nhãn** ngay trên web trước khi tải PDF: chọn số trang để xem bố cục,
  nội dung từng nhãn (bao gồm nhãn tiêu đề của từng giai đoạn/bản) đúng như khi in.
- **Ghi nhớ thông số đã nhập lần cuối**: mã nghiên cứu, số người tình nguyện, số giai
  đoạn, số thời điểm lấy mẫu được lưu vào file `last_params.json` cạnh ứng dụng và tự
  động điền lại ở lần mở sau, giúp không phải nhập lại từ đầu.
  > Lưu ý: nếu chạy trên nền tảng hosting có filesystem tạm thời (ví dụ Streamlit
  > Community Cloud), file này có thể bị xóa khi app khởi động lại/redeploy. Khi chạy
  > trên máy cá nhân (`streamlit run`), thông số sẽ được giữ lại lâu dài.

## Cài đặt & chạy trên máy cá nhân

1. Cài các thư viện cần thiết:

   ```bash
   pip install -r requirements.txt
   ```

2. Chạy ứng dụng:

   ```bash
   streamlit run streamlit_app.py
   ```

3. Mở trình duyệt theo địa chỉ được in ra (mặc định `http://localhost:8501`).

## Cách sử dụng

1. Nhập **Mã nghiên cứu**, **số người tình nguyện**, **số giai đoạn**, **số thời điểm
   lấy mẫu**.
2. Xem thông tin tổng quan (tổng số ống, tổng số nhãn) để kiểm tra số lượng trước khi in.
3. Dùng phần **Xem trước nhãn** để duyệt qua từng trang, kiểm tra nội dung nhãn đúng
   trước khi in giấy tem.
4. Nhấn **Tạo PDF**, sau đó nhấn **Tải xuống PDF** để lấy file in.

## Công nghệ sử dụng

- [Streamlit](https://streamlit.io/) – giao diện web
- [ReportLab](https://www.reportlab.com/) – sinh file PDF
