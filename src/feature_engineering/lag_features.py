import pandas as pd

def generate_climate_lag_features(df):
    """
    Tạo các biến trễ (lagged features) khí hậu cho dữ liệu bảng (panel data).
    
    Tham số:
    - df: DataFrame chứa dữ liệu gốc, bắt buộc phải có cột 'CERT' và 'year'.
    
    Trả về:
    - DataFrame mới đã được bổ sung các cột biến trễ.
    """
    # 1. Tạo bản sao
    df_feat = df.copy()
    
    # 2. Sắp xếp dữ liệu (CỰC KỲ QUAN TRỌNG)
    df_feat = df_feat.sort_values(by=['CERT', 'year']).reset_index(drop=True)
    
    # 3. Tạo các biến trễ (shift) theo từng nhóm ngân hàng
    df_feat['HEAT_DAYS_LAG1'] = df_feat.groupby('CERT')['HEAT_DAYS'].shift(1)
    df_feat['HEAT_DAYS_LAG2'] = df_feat.groupby('CERT')['HEAT_DAYS'].shift(2)
    df_feat['TMAX_AVG_LAG1'] = df_feat.groupby('CERT')['TMAX_AVG'].shift(1)
    
    # if 'HEAT_SHOCK_DUMMY' in df_feat.columns:
    #     df_feat['HEAT_SHOCK_DUMMY_LAG1'] = df_feat.groupby('CERT')['HEAT_SHOCK_DUMMY'].shift(1)
    #     df_feat['HEAT_SHOCK_DUMMY_LAG2'] = df_feat.groupby('CERT')['HEAT_SHOCK_DUMMY'].shift(2)
        
    print("✔️ Đã tạo thành công các biến trễ (Lag 1 & Lag 2) cho dữ liệu khí hậu.")
    
    return df_feat