import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
try:
    import seaborn as sns
except Exception:
    sns = None
    print("Warning: seaborn chưa được cài; sẽ dùng matplotlib để vẽ thay thế.")
import re

try:
    from sklearn.cluster import KMeans
except Exception:
    print("Thiếu thư viện 'scikit-learn' (sklearn). Hãy cài vào môi trường ảo hiện tại:")
    print("  & d:/BT-KHDL/.venv/Scripts/python.exe -m pip install scikit-learn")
    raise SystemExit("Thiếu thư viện scikit-learn")

# =============================================================================
# BƯỚC 1: ĐỌC VÀ TIỀN XỬ LÝ DỮ LIỆU
# =============================================================================
# Đọc file dữ liệu CSV (không dùng hàng đầu làm header vì cấu trúc file phức tạp)
file_path = "TỔNG HỢP ĐIỂM K58KTP.xlsx - Trang tính1.csv"
import os

if os.path.exists(file_path):
    df = pd.read_csv(file_path, header=None)
else:
    candidates = [f for f in os.listdir('.') if f.lower().endswith(('.csv', '.xlsx'))]
    print(f"File '{file_path}' không tìm thấy trong thư mục làm việc: {os.getcwd()}")
    if not candidates:
        print('Không tìm thấy file .csv hoặc .xlsx nào trong thư mục hiện tại.')
        raise SystemExit("Cập nhật biến file_path hoặc đặt file dữ liệu vào thư mục làm việc.")

    # Nếu có file csv ưu tiên đọc csv, nếu không có thì đọc xlsx
    csvs = [c for c in candidates if c.lower().endswith('.csv')]
    xls = [c for c in candidates if c.lower().endswith('.xlsx')]
    if csvs:
        chosen = csvs[0]
        print(f"Sử dụng file CSV tìm thấy: {chosen}")
        df = pd.read_csv(chosen, header=None)
    else:
        chosen = xls[0]
        print(f"Sử dụng file Excel tìm thấy: {chosen}")
        try:
            df = pd.read_excel(chosen, header=None)
        except ImportError:
            print("Để đọc file .xlsx cần cài 'openpyxl'. Hãy chạy: pip install openpyxl")
            raise SystemExit("Thiếu thư viện đọc Excel: openpyxl")

# Trích xuất danh sách Tên Sinh Viên (Hàng số 2, từ cột thứ 3 trở đi)
sinh_vien = df.iloc[2, 3:].values

# Trích xuất bảng điểm của các môn học (Từ hàng số 4 đến 55, từ cột thứ 3 trở đi)
bang_diem = df.iloc[4:56, 3:]


# Làm sạch dữ liệu: Chuyển bảng điểm sang dạng số.
# "x" hoặc chuỗi không phải số sẽ trở thành NaN rồi ta xử lý tiếp
bang_diem_so = bang_diem.apply(pd.to_numeric, errors='coerce')

# Nếu 1 sinh viên hoàn toàn không có điểm (tất cả NaN) -> loại bỏ khỏi danh sách
all_nan_mask = bang_diem_so.isna().all(axis=0)
if all_nan_mask.any():
    removed = list(np.array(sinh_vien)[all_nan_mask.values])
    print('Loại bỏ sinh viên không có điểm (không cần lấy dữ liệu):', removed)
    # Giữ lại chỉ những cột có ít nhất 1 điểm
    bang_diem_so = bang_diem_so.loc[:, ~all_nan_mask]
    # Cập nhật danh sách tên sinh viên tương ứng (dùng tên ban đầu, không lấy chỉ số cột)
    sinh_vien = np.array(sinh_vien)[~all_nan_mask.values]

# Những ô NaN (một vài môn thiếu điểm) -> mặc định là 0
bang_diem_so = bang_diem_so.fillna(0)

# Tính điểm GPA trung bình cho từng sinh viên (tính trung bình theo từng cột)
gpa_sinh_vien = bang_diem_so.mean(axis=0).values

# Tạo một DataFrame mới sạch sẽ để phục vụ phân cụm
df_gpa = pd.DataFrame({
    'Sinh_Vien': sinh_vien,
    'GPA': gpa_sinh_vien
})

# Loại bỏ các dòng nếu có sinh viên bị trống hoàn toàn điểm (nếu có)
df_gpa = df_gpa.dropna().reset_index(drop=True)


# =============================================================================
# BƯỚC 2: ÁP DỤNG THUẬT TOÁN PHÂN CỤM K-MEANS (K=3)
# =============================================================================
# Biến đổi dữ liệu GPA về dạng mảng 2 chiều (N hàng, 1 cột) theo yêu cầu của scikit-learn
X = df_gpa[['GPA']].values

# Khởi tạo mô hình K-Means với số cụm là 3
# random_state=42 giúp cố định kết quả giống nhau ở mọi lần chạy
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)

# Huấn luyện mô hình và gán nhãn cụm (0, 1, 2) cho từng sinh viên
df_gpa['Cluster'] = kmeans.fit_predict(X)


# =============================================================================
# BƯỚC 3: THỐNG KÊ VÀ ĐỊNH NGHĨA CÁC CỤM
# =============================================================================
# Tính toán các chỉ số Thấp nhất, Cao nhất, Trung bình và Số lượng sinh viên của mỗi cụm
thong_ke_cum = df_gpa.groupby('Cluster')['GPA'].agg(['min', 'max', 'mean', 'count'])

print("--- KẾT QUẢ THỐNG KÊ CÁC CỤM TỪ MÁY TÍNH ---")
print(thong_ke_cum)
print("\n" + "="*50 + "\n")

# Tự động gán tên nhóm (Giỏi, Khá, Trung bình) dựa trên điểm GPA trung bình (mean) của cụm
thong_ke_cum = thong_ke_cum.sort_values(by='mean', ascending=False)
mapping_ten_nhom = {
    thong_ke_cum.index[0]: "Năng lực Tốt / Xuất sắc",
    thong_ke_cum.index[1]: "Năng lực Khá / Trung bình",
    thong_ke_cum.index[2]: "Năng lực Cần cải thiện / Yếu"
}

df_gpa['Ten_Nhom'] = df_gpa['Cluster'].map(mapping_ten_nhom)

# In ra danh sách kết quả phân lớp để kiểm tra nhanh
print("--- VÍ DỤ DANH SÁCH SINH VIÊN SAU KHI PHÂN NHÓM ---")
print(df_gpa[['Sinh_Vien', 'GPA', 'Ten_Nhom']].head(15))

# =============================================================================
# XUẤT KẾT QUẢ: TẠO 3 FILE XLSX, MỖI FILE LÀ MỘT CỤM PHÂN LỚP
# =============================================================================
output_dir = 'output'
os.makedirs(output_dir, exist_ok=True)

# Lưu từng cụm thành 1 file riêng
cluster_files = []
for cluster_id, grp in df_gpa.groupby('Cluster'):
    label = mapping_ten_nhom.get(cluster_id, f'Cluster_{cluster_id}')
    safe_label = re.sub(r"[\[\]\:\*\?\/\\\\]", "_", str(label))
    fname = f'cluster_{cluster_id}_{safe_label[:40]}.xlsx'
    path = os.path.join(output_dir, fname)
    grp.to_excel(path, index=False)
    cluster_files.append(path)

print('Đã xuất 3 file phân cụm vào thư mục output:')
for p in cluster_files:
    print(' -', p)


# =============================================================================
# BƯỚC 4: TRỰC QUAN HÓA KẾT QUẢ (VẼ BIỂU ĐỒ)
# =============================================================================
# Cấu hình để hiển thị được tiếng Việt trên biểu đồ (nếu máy bạn thiếu font có thể đổi sang tiếng Anh hoặc bỏ dấu)
plt.rcParams['font.family'] = 'DejaVu Sans' # Hoặc 'Arial' tùy máy

plt.figure(figsize=(8, 8))

# Biểu đồ tròn theo nhóm: màu đỏ=Yếu, vàng=Khá, xanh=Giỏi
categories = [
    "Năng lực Cần cải thiện / Yếu",
    "Năng lực Khá / Trung bình",
    "Năng lực Tốt / Xuất sắc",
]

counts = [int((df_gpa['Ten_Nhom'] == c).sum()) for c in categories]

# Màu: đỏ, vàng, xanh
colors = ['#e74c3c', '#f1c40f', '#2ecc71']

def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        count = int(round(pct * total / 100.0))
        return f"{count}\n({pct:.1f}%)"
    return my_autopct

# Nếu tổng = 0 thì vẽ đồ thị trống
total = sum(counts)
if total == 0:
    plt.text(0.5, 0.5, 'Không có dữ liệu để hiển thị', ha='center', va='center')
else:
    wedges, texts, autotexts = plt.pie(
        counts,
        labels=categories,
        colors=colors,
        autopct=make_autopct(counts),
        startangle=90,
        pctdistance=0.7,
        wedgeprops={'edgecolor': 'white'}
    )
    plt.axis('equal')
    for txt in texts + autotexts:
        txt.set_fontsize(10)

# Trang trí biểu đồ
plt.title('KẾT QUẢ PHÂN CỤM LỚP THÀNH 3 NHÓM THEO NĂNG LỰC HỌC TẬP (GPA)', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Điểm số GPA của Sinh viên', fontsize=12)
plt.yticks([]) # Ẩn trục Y vì các điểm đều nằm trên đường thẳng Y=0
plt.grid(True, axis='x', linestyle='--', alpha=0.6)
plt.legend(title='Phân loại nhóm', loc='upper left')

# Lưu ảnh biểu đồ vào thư mục output
try:
    img_path = os.path.join(output_dir, 'phanloai_bieudo.png')
    plt.tight_layout()
    plt.savefig(img_path, dpi=300, bbox_inches='tight')
    print('Đã lưu ảnh biểu đồ:', img_path)
except Exception as e:
    print('Không thể lưu ảnh biểu đồ:', e)

# Hiển thị biểu đồ lên màn hình
plt.show()