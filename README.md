#link video đã upleen yt

https://youtu.be/_34wyYkBH70

# Phân lớp sinh viên theo GPA

Tập lệnh: `phanDiem.py`

Mô tả ngắn:
- Đọc file danh sách/điểm sinh viên (CSV hoặc XLSX) trong thư mục làm việc.
- Tính GPA từng sinh viên (giá trị NaN hoặc các kí tự không số như `x` được tính là 0).
- Loại bỏ những sinh viên không có điểm (tất cả ô trống).
- Áp dụng K-Means (k=3) để phân lớp sinh viên thành 3 nhóm.
- Xuất 3 file Excel (mỗi file chứa một nhóm) và ảnh biểu đồ tròn vào thư mục `output`.

Yêu cầu môi trường:

1. Tạo và kích hoạt virtualenv (Windows PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Cài thư viện cần thiết:

```powershell
.venv\Scripts\python.exe -m pip install -U pip
.venv\Scripts\python.exe -m pip install pandas numpy matplotlib seaborn scikit-learn openpyxl
```

Cách chạy:

```powershell
.venv\Scripts\python.exe phanDiem.py
```

Hành vi và đầu ra:
- Nếu không tìm thấy file `TỔNG HỢP ĐIỂM K58KTP.xlsx - Trang tính1.csv`, script sẽ tự tìm file `.csv` hoặc `.xlsx` khác trong thư mục.
- Những sinh viên có tất cả ô điểm trống sẽ bị loại khỏi phân tích.
- Những ô điểm thiếu (NaN) hoặc không hợp lệ được xử lý là `0` khi tính GPA.
- Tạo thư mục `output` và sinh ra:
  - `cluster_0_*.xlsx` (nhóm Giỏi / Xuất sắc)
  - `cluster_1_*.xlsx` (nhóm Khá / Trung bình)
  - `cluster_2_*.xlsx` (nhóm Cần cải thiện / Yếu)
  - `phanloai_bieudo.png` (biểu đồ tròn hiển thị số lượng và phần trăm; màu: đỏ=Yếu, vàng=Khá, xanh=Giỏi)

Biểu Đồ Phân Cụm:

<img width="654" height="620" alt="image" src="https://github.com/user-attachments/assets/b900aff7-1bc6-4917-ba04-446d35f4e10d" />



Ghi chú:
- Tên sheet và tên file được làm sạch để loại bỏ ký tự không hợp lệ.
- Nếu bạn muốn thay đổi ngưỡng hay số cụm, chỉnh tham số `n_clusters` trong `KMeans`.

Vấn đề thường gặp:
- Thiếu `openpyxl`: cài `pip install openpyxl`.
- Thiếu `scikit-learn`: cài `pip install scikit-learn`.

Muốn tôi: chuẩn hóa tên file đầu vào, xuất thêm báo cáo tổng hợp, hoặc commit các thay đổi lên git?
  
