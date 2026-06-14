import pandas as pd
import numpy as np

def calculate_financial_features(df):
    """
    Hàm tính toán các biến số tài chính, bao gồm biến mục tiêu (Y) và biến kiểm soát.
    Yêu cầu dữ liệu đầu vào đã có các biến thô: ASSET, EQTOT, ROA, P9ASSET, NAASSET.
    """
    df_feat = df.copy()
    
    print("⏳ Đang tính toán các biến tài chính...")
    
    # ---------------------------------------------------------
    # 1. SẮP XẾP DỮ LIỆU 
    # ---------------------------------------------------------
    df_feat = df_feat.sort_values(by=['CERT', 'year']).reset_index(drop=True)
    
    # ---------------------------------------------------------
    # 2. TÍNH CÁC BIẾN KIỂM SOÁT CẤP NGÂN HÀNG 
    # ---------------------------------------------------------
    # Quy mô ngân hàng (SIZE): Log tự nhiên của tổng tài sản quy về USD
    df_feat['SIZE'] = np.log(df_feat['ASSET'] * 1000)
    
    # Tỷ lệ an toàn vốn (CAR): Vốn chủ sở hữu / Tổng tài sản
    df_feat['CAR_ratio'] = df_feat['EQTOT'] / df_feat['ASSET']
    df_feat['CAR'] = df_feat['CAR_ratio'] * 100
    
    df_feat['ROA_annual'] = df_feat['ROA']
    df_feat['NIM_annual'] = df_feat['NIM'] 

    # ---------------------------------------------------------
    # 3. TÍNH BIẾN PHỤ THUỘC
    # ---------------------------------------------------------
    # Tỷ lệ nợ xấu (NPL_ratio): Tổng nợ xấu chia cho tổng tài sản
    df_feat['NPL_ratio'] = ((df_feat['P9ASSET'] + df_feat['NAASSET']) / df_feat['ASSET']) * 100
    
    # Tính Độ lệch chuẩn ROA 3 năm (ROA_sd3)
    df_feat['ROA_sd3'] = df_feat.groupby('CERT')['ROA_annual'].transform(
        lambda x: x.rolling(window=3, min_periods=3).std()
    )
    
    # Chỉ số an toàn (Z_score)
    epsilon = 1e-6
    df_feat['Z_score'] = (df_feat['ROA_annual'] + df_feat['CAR_ratio'] * 100) / (df_feat['ROA_sd3'] + epsilon)
    
    # Logarit tự nhiên của Z-score (ln_Zscore)
    df_feat['ln_Zscore'] = np.log(df_feat['Z_score'].where(df_feat['Z_score'] > 0))
    


    print("Đã tính toán xong các biến tài chính (SIZE, CAR, NPL_ratio, Z_score).")
    
    return df_feat