# NGHIÊN CỨU KHOA HỌC VỀ TÁC ĐỘNG CỦA YẾU TÔ THỜI TIẾT LÊN HOẠT ĐỘNG ỔN ĐỊNH CỦA NGÂN HÀNG

## Overview

Nghiên cứu này nghiên cứu định lượng về tác động của các cú sốc nhiệt độ (HEAT_SHOCK) - đại diện cho rủi ro khí hậu vật lý lên sự ổn định của hoạt động ngân hàng

Nghiên cứu sử dụng dữ liệu vi mô cấp ngân hàng kết hợp với dữ liệu khí tượng thủy văn theo lưới tọa độ để đánh giá xem nhiệt độ cực đoan ảnh hưởng thế nào đến tỷ lệ nợ xấu (NPLs) và rủi ro phá sản (Z-score).

## Tech Stack
- Language: Python
- Data Science: pandas, numpy, scikit-learn, xgboost, shap
- Economic Modeling: statsmodels, linearmodels
- Visualization: matplotlib, seaborn, plotly

## Data Structure

Cấu trúc các biến trong bộ dữ liệu nghiên cứu thực tế (`final_research_panel.csv`) bao gồm:

### 1. Biến phụ thuộc Y (Dependent Variables)
- `NPL_ratio` (Tỷ lệ nợ xấu - %): Được tính bằng công thức:
  $$NPL\_ratio_{i,t} = \frac{NPL\_p9\_annual_{i,t} + NPL\_na\_annual_{i,t}}{ASSET\_avg_{i,t}} \times 100$$
  Trong đó:
  - `NPL_p9_annual`: Khoản cho vay quá hạn 90 ngày trở lên nhưng vẫn tính lãi.
  - `NPL_na_annual`: Tài sản nợ không sinh lời (nonaccrual).
  - `ASSET_avg`: Tổng tài sản bình quân năm của ngân hàng.
- `Z_score` (Chỉ số an toàn): Đo lường khoảng cách đến khả năng vỡ nợ, được tính bằng công thức:
  $$Z\_score_{i,t} = \frac{ROA\_annual_{i,t} + ETA\_ratio_{i,t} \times 100}{ROA\_sd3_{i,t}}$$
  Trong đó:
  - `ROA_annual`: Tỷ suất sinh lời trung bình năm trên tổng tài sản (%).
  - `ETA_ratio`: Tỷ lệ vốn chủ sở hữu trên tổng tài sản dạng thập phân (`EQTOT / ASSET_avg`). **Lưu ý:** đây KHÔNG phải `CAR_ratio` (Capital Adequacy Ratio) — `CAR` được giữ riêng làm biến kiểm soát cấp ngân hàng, không xuất hiện trong công thức Z-score.
  - `ROA_sd3`: Độ lệch chuẩn của ROA tính trên cửa sổ trượt 3 năm gần nhất.
- `ln_Zscore`: Logarit tự nhiên của Z-score để phân phối biến tiệm cận phân phối chuẩn.

### 2. Biến độc lập X (Independent Climate Variables)
- `HEAT_DAYS` (Số ngày sốc nhiệt - tương ứng với `HEAT_SHOCK_DAYS` trong lý thuyết): Số ngày trong năm $t$ có nhiệt độ tối đa vượt ngưỡng phân vị thứ 90 (P90) lịch sử của mã ZIP đặt trụ sở ngân hàng.
- `TMAX_AVG` (Nhiệt độ tối đa trung bình - tương ứng với `HEAT_SHOCK_INTENSITY` trong lý thuyết): Nhiệt độ tối đa trung bình hàng ngày trong năm $t$ (°C).
- `HEAT_SHOCK_DUMMY` (Biến giả sốc nhiệt): Được xác định bằng 1 nếu số ngày sốc nhiệt `HEAT_DAYS` > 0, ngược lại bằng 0 (biến này được tạo động trong quá trình hồi quy/phân tích đặc trưng).
- **Biến trễ (Lagged Climate Variables)**: Được tạo ra trong quá trình hồi quy để đánh giá độ trễ tác động (ví dụ: `HEAT_DAYS_(t-1)` hoặc `HEAT_DAYS_lag1`, `TMAX_AVG_lag1`).

### 3. Biến kiểm soát (Control Variables)

#### ** BANK LEVEL CONTROL (Kiểm soát cấp ngân hàng) **
- `SIZE` (Quy mô ngân hàng): Logarit tự nhiên của tổng tài sản trung bình quy về đơn vị USD thực tế:
  $$SIZE_{i,t} = \ln(ASSET\_avg_{i,t} \times 1000)$$
  *Lưu ý:* Biến này được Winsorize ở mức 1% - 99% để hạn chế tác động của giá trị ngoại lai cực đoan.
- `CAR` (Capital Adequacy Ratio - %): Tỷ lệ an toàn vốn (Leverage Ratio) thực tế:
  $$CAR_{i,t} = \frac{CAR\_annual_{i,t}}{ASSET\_avg_{i,t}} \times 100$$
- `NIM` (Net Interest Margin - %): Biên tỷ suất lợi nhuận thuần từ lãi ròng:
  $$NIM_{i,t} = \frac{NIM\_annual_{i,t}}{ASSET\_avg_{i,t}} \times 100$$
- `ROA_annual` (Return on Assets - %): Tỷ suất sinh lời trên tổng tài sản.
- `LTD` (Loan-to-Deposit Ratio): Tỷ lệ dư nợ trên huy động vốn (một số năm có thể bị khuyết dữ liệu).
- `LIQ` (Liquidity Ratio): Tỷ lệ thanh khoản của ngân hàng.

#### ** MACRO LEVEL CONTROL (Kiểm soát vĩ mô) **
*Lưu ý:* Các biến kiểm soát vĩ mô không xuất hiện trực tiếp trong bảng dữ liệu thực tế (`final_research_panel.csv`) mà được kiểm soát gián tiếp thông qua việc sử dụng **Time Fixed Effects ($\gamma_t$)** trong mô hình hồi quy bảng (Panel Fixed Effects), hoặc có thể được bổ sung từ nguồn dữ liệu ngoài của ngân hàng trung ương/bang khi phân tích hồi quy nâng cao. Các biến lý thuyết bao gồm:
- `GDP_GROWTH`: Tăng trưởng GDP bang/địa phương đặt trụ sở ngân hàng.
- `UNEMPLOYMENT`: Tỷ lệ thất nghiệp địa phương.
- `INFLATION`: Tỷ lệ lạm phát quốc gia.

## Modeling & Methodology

### 1. Mô hình Kinh tế lượng (Panel Fixed Effects Model - FEM)
Kiểm định mối quan hệ nhân quả và các kênh truyền dẫn ngắn hạn bằng mô hình hồi quy dữ liệu bảng tác động cố định (Panel FEM), kiểm soát các đặc trưng riêng biệt không đổi theo thời gian của ngân hàng và các cú sốc vĩ mô theo năm. Để xử lý hiện tượng tự tương quan chuỗi và phương sai sai số thay đổi, mô hình áp dụng sai số chuẩn phân cụm cấp ngân hàng (Clustered Standard Errors by Bank):

$$Y_{i,t} = \alpha_i + \gamma_t + \beta Climate_{i,t} + \theta Controls_{i,t} + \epsilon_{i,t}$$

Trong đó:
- $Y_{i,t}$: Biến phụ thuộc đo lường sự ổn định ngân hàng (`NPL_ratio` hoặc `ln_Zscore`) của ngân hàng $i$ trong năm $t$.
- $\alpha_i$ (Bank Fixed Effects): Hằng số kiểm soát các đặc trưng nội tại không đổi theo thời gian của từng ngân hàng (như văn hóa quản trị, vị trí địa lý cố định, phân khúc khách hàng).
- $\gamma_t$ (Time Fixed Effects): Hằng số kiểm soát các biến động vĩ mô chung theo năm tác động lên toàn bộ hệ thống ngân hàng (lạm phát quốc gia, chính sách tiền tệ của Fed).
- $Climate_{i,t}$: Vector các biến độc lập khí hậu bao gồm tần suất rủi ro vật lý (`HEAT_DAYS`), cường độ (`TMAX_AVG`), biến giả sốc nhiệt (`HEAT_SHOCK_DUMMY`) và các biến trễ thời gian (`lag1`, `lag2`).
- $Controls_{i,t}$: Vector các biến kiểm soát cấp ngân hàng (`SIZE`, `CAR`, `NIM`, `ROA_annual`, `LTD`, `LIQ`).
- $\epsilon_{i,t}$: Sai số ngẫu nhiên.

*Các kiểm định bổ sung:*
- **Hausman Test:** Kiểm định lựa chọn giữa mô hình Tác động cố định (Fixed Effects - FE) và Tác động ngẫu nhiên (Random Effects - RE).
- **Winsorization:** Xử lý giá trị ngoại lai của các biến liên tục ở mức 1%-99% để loại bỏ nhiễu cực đoan.
- **Phân tích dị thể (Heterogeneity Analysis):** Ước lượng mô hình trên các nhóm mẫu phân chia theo quy mô tài sản (ngân hàng lớn vs nhỏ) và vùng địa lý nhằm đánh giá tính nhạy cảm khác biệt.

### 2. Machine Learning & XAI (Explainable AI)
- **Mục tiêu:** Dự báo phi tuyến tính xác suất một ngân hàng rơi vào trạng thái bất ổn tài chính dựa trên các yếu tố rủi ro khí hậu vật lý và sức khỏe tài chính.
- **Gán nhãn mục tiêu:** Gán nhãn bất ổn định ($1$) nếu chỉ số `Z_score` của ngân hàng nằm dưới ngưỡng phân vị thứ 25 ($25^{th}$ percentile) của mẫu nghiên cứu; ngược lại gán nhãn ổn định ($0$).
- **Thuật toán áp dụng:** Random Forest và XGBoost.
- **Phân chia dữ liệu (Data Splitting):** Áp dụng **Walk-Forward Cross-Validation** (Kiểm định chéo cuộn tiến) để tôn trọng cấu trúc thời gian của dữ liệu bảng, loại bỏ nguy cơ rò rỉ thông tin tương lai (data leakage).
- **Giải thích mô hình phi tuyến (SHAP):** Sử dụng các giá trị Shapley (SHAP values) nhằm bóc tách mức độ đóng góp phi tuyến tính của rủi ro thời tiết so với các biến số tài chính, đồng thời xác định các ngưỡng tới hạn (nonlinear thresholds) thông qua biểu đồ phụ thuộc SHAP (SHAP Dependence Plot).

## Processing
### Biến độc lập X (Khí hậu)
- `HEAT_DAYS`: Tổng số ngày nắng nóng (sốc nhiệt) trong năm $t$. Đại diện cho tần suất xuất hiện cú sốc nhiệt.
- `HEAT_DAYS_lag1` (hoặc `HEAT_DAYS_(t-1)`) & `HEAT_DAYS_lag2` (hoặc `HEAT_DAYS_(t-2)`): Tổng số ngày sốc nhiệt có độ trễ 1 năm và 2 năm.
  *Cơ sở lý thuyết:* Tác động của rủi ro khí hậu vật lý lên hoạt động ngân hàng thường có độ trễ nhất định. Doanh nghiệp vay vốn (ví dụ: nông nghiệp, sản xuất) bị ảnh hưởng bởi thời tiết cực đoan không vỡ nợ ngay lập tức mà sẽ sử dụng các nguồn lực dự trữ để cầm cự từ vài tháng đến 1-2 năm trước khi khoản vay thực sự chuyển thành nợ xấu (`NPL_ratio`) hoặc làm suy giảm an toàn vốn (`Z_score`) của ngân hàng.
- `TMAX_AVG`: Nhiệt độ tối đa trung bình hàng ngày trong năm $t$. Đại diện cho cường độ sốc nhiệt.
- `HEAT_SHOCK_DUMMY`: Biến giả, nhận giá trị 1 nếu trong năm $t$ ngân hàng có chịu sốc nhiệt (`HEAT_DAYS` > 0), ngược lại nhận giá trị 0.
- `HEAT_SHOCK_DUMMY_lag1` & `HEAT_SHOCK_DUMMY_lag2`: Biến giả sốc nhiệt trễ 1 năm và 2 năm.

### Kiểm định giả thuyết - FEM
"Sốc nhiệt có làm suy giảm sự ổn định của hoạt động ngân hàng không, và nếu có thì thông qua cơ chế nào, với độ trễ bao lâu?"
Ta sẽ chạy mô hình với 2 giả thuyết sau:

*GIẢ THUYẾT 1: Tác động của tần suất (Số ngày nóng thêm) và cường độ sốc nhiệt*
Phương trình hồi quy:
$$Y_{i,t} = \alpha_i + \gamma_t + \beta_1 HEAT\_DAYS_{i,t} + \beta_2 TMAX\_AVG_{i,t} + \beta_3 HEAT\_DAYS\_lag1_{i,t} + \beta_4 HEAT\_DAYS\_lag2_{i,t} + \theta Controls_{i,t} + \epsilon_{i,t}$$
- $H1$: Tác động tức thời của tần suất sốc nhiệt ($\beta_1 \neq 0$).
- $H2$: Tác động tức thời của cường độ sốc nhiệt ($\beta_2 \neq 0$).
- $H3$: Tác động trễ 1 năm ($\beta_3 \neq 0$) và trễ 2 năm ($\beta_4 \neq 0$) của tần suất sốc nhiệt.
- $H4$: Kiểm định tổng thể bằng F-test với giả thuyết không: $H_0: \beta_1 = \beta_2 = \beta_3 = \beta_4 = 0$.

*GIẢ THUYẾT 2: Tác động của việc xảy ra sốc nhiệt (Biến giả) và cường độ sốc nhiệt*
Phương trình hồi quy:
$$Y_{i,t} = \alpha_i + \gamma_t + \gamma_1 HEAT\_SHOCK\_DUMMY_{i,t} + \gamma_2 TMAX\_AVG_{i,t} + \gamma_3 HEAT\_SHOCK\_DUMMY\_lag1_{i,t} + \gamma_4 HEAT\_SHOCK\_DUMMY\_lag2_{i,t} + \theta Controls_{i,t} + \epsilon_{i,t}$$
- $H1$: Tác động tức thời của việc xuất hiện sốc nhiệt ($\gamma_1 \neq 0$).
- $H2$: Tác động tức thời của cường độ sốc nhiệt ($\gamma_2 \neq 0$).
- $H3$: Tác động trễ 1 năm ($\gamma_3 \neq 0$) và trễ 2 năm ($\gamma_4 \neq 0$) của việc xuất hiện sốc nhiệt.
- $H4$: Kiểm định tổng thể bằng F-test với giả thuyết không: $H_0: \gamma_1 = \gamma_2 = \gamma_3 = \gamma_4 = 0$.


### Định hướng tích hợp Machine Learning

1. **Xác định ngưỡng phi tuyến tính (Nonlinear Threshold Analysis):**
   Các mô hình hồi quy kinh tế lượng tuyến tính (Fixed Effects) mặc dù chứng minh được mối quan hệ nhân quả nhưng giả định tác động là tuyến tính. Ngược lại, thời tiết cực đoan thường gây hại theo cơ chế ngưỡng (ví dụ: số ngày nắng nóng vượt quá một giới hạn nhất định mới bắt đầu gây ra thiệt hại nghiêm trọng). 
   - **Triển khai:** Xây dựng mô hình Random Forest và XGBoost để học các tương tác phi tuyến.
   - **XAI (SHAP):** Sử dụng đồ thị **SHAP Dependence Plot** cho biến `HEAT_DAYS` để định vị rõ ràng ngưỡng tới hạn phi tuyến tính mà tại đó xác suất ngân hàng rơi vào trạng thái rủi ro tăng vọt.


## Project Structure
```md
# Project Structure

```

nckh_esg/
│
├── README.md
├── DATABASE.md
├── RULE.md
├── requirements.txt
├── environment.yml
├── .gitignore
│
├── configs/
│   ├── config.yaml
│   ├── paths.yaml
│   └── model_params.yaml
│
├── data/
│   │
│   ├── raw/
│   │   ├── bank_data/
│   │   ├── climate_data/
│   │   │   ├── ERA5/
│   │   │   └── shapefiles/
│   │   ├── macro_data/
│   │   └── external/
│   │
│   ├── interim/
│   │   ├── merged/
│   │   ├── cleaned/
│   │   └── panel_data/
│   │
│   ├── processed/
│   │   ├── econometrics/
│   │   ├── machine_learning/
│   │   └── final_dataset/
│   │
│   └── metadata/
│       ├── variable_dictionary.xlsx
│       ├── data_sources.md
│       └── units.md
│
├── notebooks/
│   │
│   ├── 01_data_collection/
│   ├── 02_data_cleaning/
│   ├── 03_feature_engineering/
│   ├── 04_exploratory_data_analysis/
│   ├── 05_econometric_model/
│   ├── 06_machine_learning/
│   ├── 07_shap_analysis/
│   └── 08_robustness_checks/
│
├── src/
│   │
│   ├── data/
│   │   ├── load_data.py
│   │   ├── clean_bank_data.py
│   │   ├── clean_climate_data.py
│   │   └── merge_data.py
│   │
│   ├── preprocessing/
│   │   ├── winsorize.py
│   │   ├── missing_values.py
│   │   ├── lag_variables.py
│   │   └── standardize.py
│   │
│   ├── feature_engineering/
│   │   ├── heat_shock_days.py
│   │   ├── heat_shock_intensity.py
│   │   ├── heat_shock_dummy.py
│   │   ├── lag_features.py
│   │   ├── climate_features.py
│   │   └── target_variables.py
│   │
│   ├── econometrics/
│   │   ├── fixed_effects.py
│   │   ├── pooled_ols.py
│   │   ├── random_effects.py
│   │   ├── clustered_se.py
│   │   ├── hausman_test.py
│   │   ├── heterogeneity_analysis.py
│   │   └── robustness_check.py
│   │
│   ├── machine_learning/
│   │   ├── walk_forward_cv.py
│   │   ├── xgboost_model.py
│   │   ├── model_evaluation.py
│   │   └── threshold_analysis.py
│   │
│   ├── explainability/
│   │   ├── shap_values.py
│   │   ├── dependence_plot.py
│   │   ├── feature_importance.py
│   │   └── partial_dependence.py
│   │
│   ├── visualization/
│   │   ├── eda_plots.py
│   │   ├── regression_plots.py
│   │   ├── climate_maps.py
│   │   └── shap_plots.py
│   │
│   └── utils/
│       ├── logger.py
│       ├── paths.py
│       ├── constants.py
│       └── helper.py
│
├── models/
│   ├── econometrics/
│   ├── xgboost/
│   └── shap/
│
├── outputs/
│   │
│   ├── tables/
│   │   ├── descriptive_statistics/
│   │   ├── correlation_matrix/
│   │   ├── regression_results/
│   │   ├── heterogeneity_results/
│   │   └── robustness_results/
│   │
│   ├── figures/
│   │   ├── eda/
│   │   ├── climate/
│   │   ├── regression/
│   │   └── shap/
│   │
│   └── reports/
│       ├── hypothesis_1/
│       ├── hypothesis_2/
│       └── final_results/
│
├── paper/
│   ├── proposal/
│   ├── literature_review/
│   ├── methodology/
│   ├── draft/
│   ├── references/
│   └── final_paper/
│
├── presentations/
│   ├── proposal_slide/
│   ├── progress_report/
│   └── defense_slide/
│
├── references/
│   ├── climate_risk/
│   ├── banking_stability/
│   ├── econometrics/
│   └── machine_learning/
│
└── tests/
├── test_data.py
├── test_features.py
├── test_models.py
└── test_utils.py

```
```
