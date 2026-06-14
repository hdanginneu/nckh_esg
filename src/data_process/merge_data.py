import pandas as pd
from pathlib import Path

def merge_data(data_dir):
    """
    Hàm đọc báo cáo tài chính thô hàng quý, gộp theo năm, 
    và join với dữ liệu không gian, khí hậu.
    """
    data_dir = Path(data_dir)
    
    print("Đang đọc và gộp dữ liệu tài chính từ 2008 đến 2024...")
    # 1. ĐỌC VÀ GỘP DỮ LIỆU TÀI CHÍNH TỪ NHIỀU FILE
    fin_list = []
    for year in range(2008, 2025):
        # Bạn cần trỏ đúng vào thư mục chứa 17 file csv này
        file_path = data_dir / "raw" / f"fdic_financials_{year}.csv" 
        
        if file_path.exists():
            df_temp = pd.read_csv(file_path)
            fin_list.append(df_temp)
        else:
            print(f"Cảnh báo: Không tìm thấy file {file_path}")
            
    # Nối tất cả các năm thành một bảng duy nhất
    df_fin = pd.concat(fin_list, ignore_index=True)
    
    # 2. XỬ LÝ THỜI GIAN VÀ THƯỜNG NIÊN HÓA
    # Tách lấy năm từ định dạng YYYYMMDD (Ví dụ: 20190331 // 10000 = 2019)
    df_fin['year'] = (df_fin['REPDTE'] // 10000).astype(int)

    # Do dữ liệu là cấp quý, ta nhóm theo Ngân hàng và Năm, sau đó lấy trung bình 
    df_fin_annual = df_fin.groupby(['CERT', 'year']).mean(numeric_only=True).reset_index()
    
    # 3. ĐỌC DỮ LIỆU ĐỊA LÝ VÀ KHÍ HẬU
    df_coords = pd.read_csv(data_dir / "raw" / "bank_coordinates.csv")[['CERT', 'ZIP', 'STALP', 'NAME', 'CITY', 'latitude', 'longitude']]
    df_climate = pd.read_csv(data_dir / "raw" / "climate_heat_shock.csv")
    
    # 4. JOIN CÁC BẢNG LẠI VỚI NHAU
    # Merge dữ liệu tài chính với địa lý (CERT)
    df_merged = pd.merge(df_fin_annual, df_coords, on='CERT', how='inner')
    
    # Merge với thời tiết (ZIP và year)
    df_final = pd.merge(df_merged, df_climate, on=['ZIP', 'year'], how='inner')
    
    # 5. TẠO BIẾN GIẢ SỐC NHIỆT
    if 'HEAT_DAYS' in df_final.columns:
        df_final['HEAT_SHOCK_DUMMY'] = (df_final['HEAT_DAYS'] > 0).astype(int)
        
    # 6. CHỈ GIỮ LẠI CÁC CỘT CẦN THIẾT
    columns_to_keep = [
        # Thông tin định danh
        'CERT', 'year', 'ZIP', 'STALP', 'NAME', 'CITY',
        
        # Biến khí hậu (X)
        'HEAT_DAYS', 'TMAX_AVG', 'HEAT_SHOCK_DUMMY',
        
        # Các biến tài chính thô cần để tính Z-score, NPL, SIZE, CAR sau này
        'ASSET', 'EQTOT', 'LNLSNET', 'NIM', 'ROA', 'RBCT1J', 
        'NAASSET', 'P9ASSET', 'P3ASSET', 'NONII', 'NONIX',

        # Vị trí địa lí
        'latitude', 'longitude'
    ]
    
    existing_cols = [col for col in columns_to_keep if col in df_final.columns]
    df_final = df_final[existing_cols]
    
    # Lưu ra folder interim 
    output_path = data_dir / "interim" / "merged_raw_panel.csv"
    
    # Tạo folder
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_final.to_csv(output_path, index=False)
    print(f"Đã merge thành công! Dữ liệu lưu tại: {output_path}")
    
    return df_final