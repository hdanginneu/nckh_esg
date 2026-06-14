import pandas as pd
import numpy as np
from scipy.stats import mstats

def apply_winsorization(df, columns_to_winsorize, limits=[00.01, 0.01]):
    """
    Hàm thực hiện Winsorize cho các cột được chỉ định trong DataFrame.
    
    Tham số:
    - df: DataFrame dữ liệu gốc.
    - columns_to_winsorize: Danh sách (list) các tên cột cần xử lý ngoại lai.
    - limits: Danh sách gồm 2 phần tử [tỷ lệ chặn dưới, tỷ lệ chặn trên]. 
              Ví dụ [0.01, 0.01] tương ứng với mức chặn 1% và 99%.
    
    Trả về:
    - Một DataFrame mới đã được xử lý Winsorize.
    """
    df_clean = df.copy()
    
    for col in columns_to_winsorize:
        if col in df_clean.columns:
            if df_clean[col].isnull().all():
                continue
                
            col_data = df_clean[col].values
            
            df_clean[col] = mstats.winsorize(col_data, limits=limits)
            
            print(f"Đã xử lý Winsorize thành công cho cột: {col}")
        else:
            print(f"Cảnh báo: Cột '{col}' không tồn tại trong dữ liệu.")
            
    return df_clean