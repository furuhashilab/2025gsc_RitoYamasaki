# 2025gsc_RitoYamasaki_ZemiReport
## 渋谷で歩道の Wi-Fi カバー率を測る / Street Wi-Fi Coverage in Shibuya

---

## 1. 概要 / Overview

### 日本語
本ゼミ論では、Valenzano ら (2016) が提案した **Potential Street Coverage (PSC)** 手法を、東京都渋谷の 500 m × 500 m AOI（センター街周辺）に対して **QGIS のみ** を用いて再現し、Wi-Fi アクセスポイント (AP) の「歩道カバー率」を定量評価する。

WiGLE で取得した AP 点群から半径 $r$ の円バッファを生成し、OpenStreetMap (OSM) の道路ネットワークを 10 m セグメントに分割した上で交差長を計算する。さらに AOI 全体を 25 m メッシュに分割し、各グリッド内の道路被覆率 (coverage ratio) を集計、**ECDF (Empirical Cumulative Distribution Function)** により $r$ の違いによるカバー率の分布変化を解析する。

本リポジトリは、以下を含む：

- QGIS 用 1 本のスクリプトで **「25 m グリッド × $r \in \{5,10,15,20,25,35,45,50\}$」の coverage ratio と ECDF を一括計算**
- 出力 CSV から、Spreadsheet 等で **最適な $r$ (AP カバレッジ半径)** を選定するプロセス

### English
This study replicates the **Potential Street Coverage (PSC)** methodology proposed by Valenzano et al. (2016) in a **500 m × 500 m AOI in Shibuya, Tokyo**, using **QGIS only**.

Wi-Fi access points (APs) collected via WiGLE are buffered with radius $r$, and intersected with 10 m–segmented OpenStreetMap (OSM) roads. The AOI is further divided into a 25 m grid; within each cell, the **road coverage ratio** is computed and summarized as an **Empirical Cumulative Distribution Function (ECDF)** for multiple radii $r \in \{5, 10, 15, 20, 25, 35, 45, 50\}$.

This repository contains:

- A single QGIS Python script that computes **25 m grid–based coverage ratios and ECDFs for all radii in one shot**
- CSV outputs that can be post-processed (e.g., in Google Sheets) to select an **optimal AP coverage radius** for this AOI.

---

## 2. 目的 / Objectives

### 日本語
- Valenzano ら (2016) の PSC 手法を、渋谷 AOI において QGIS 上で再現する
- WiGLE AP 点群・OSM 道路・25 m グリッドを用い、「グリッド内道路のうち、Wi-Fi で実際にカバーされている割合」を算出する
- $r$ の感度分析（5〜50 m）を行い、**ゼロカバー率と高カバー率セルの割合から「現実的な $r$」を決定**する
- 処理はすべて EPSG:6677 上の QGIS GUI + Python コンソールで完結させ、再現可能なスクリプトとフォルダ構成を GitHub に残す

### English
- Reproduce the PSC workflow of Valenzano et al. (2016) in Shibuya AOI using QGIS
- Compute, for each 25 m grid cell, **the fraction of road length covered by AP buffers**
- Perform a sensitivity analysis over radii $r = 5\text{--}50\text{ m}$, and **select a realistic AP coverage radius** based on zero-coverage rate and high-coverage cell proportion
- Keep all processing within EPSG:6677 in QGIS (GUI + Python console), and publish a reproducible script and folder layout on GitHub

---

## 3. データ / Data

### 3.1 使用レイヤ / Layers Used
（この README は、以下の最終加工レイヤが QGIS プロジェクトに読み込まれていることを前提とする）

- **AP points**
  - レイヤ名: `ap_gt_points_6677`
  - 内容: Shibuya AOI 内の WiGLE ログから作成した AP 代表点
  - CRS: EPSG:6677
  - 公開上の注意: BSSID/SSID 等の個人・機器特定情報は削除または秘匿済み

- **Road segments (10 m)**
  - レイヤ名: `roads_10m_seg_src`
  - 内容: AOI 内の OSM 道路を抽出し、10 m セグメントに分割したライン
  - CRS: EPSG:6677
  - 各フィーチャには `$length` ($\approx 10\text{ m}$) が保持される

- **Area of Interest (AOI)**
  - レイヤ名: `aoi`
  - 内容: 渋谷センター街周辺をおおむね 500 m × 500 m で囲んだポリゴン
  - CRS: EPSG:6677

### 3.2 公開ポリシー / Publication Policy
- 生の WiGLE CSV（BSSID/SSID を含むログ）は**リポジトリには含めない**
- 必要に応じて、匿名化・粗化された AP 点レイヤのみを含める
- 公開の中心は、`grid_coverage_ratio_by_r.csv` や `ecdf_grid_coverage_ratio.csv` といった **集計済み CSV** とする

---

## 4. 実装概要 / Implementation Overview

### 4.1 スクリプト / Script

QGIS Python コンソールから呼び出す 1 本のスクリプト：
`scripts/wifi_grid_coverage_ecdf_25m.py`

内部パラメータ設定（抜粋）：

```python
AP_NAME    = "ap_gt_points_6677"
ROADS_NAME = "roads_10m_seg_src"
AOI_NAME   = "aoi"

CELL_SIZE_M = 25
R_LIST = [5, 10, 15, 20, 25, 35, 45, 50]  # 分析対象 r

TARGET_CRS = QgsCoordinateReferenceSystem("EPSG:6677")
OUT_DIR = os.path.expanduser("~/Downloads/corridor_r_outputs")
処理フローは以下の通り：

1. レイヤ読み込み＆必要に応じて再投影（EPSG:6677 へ）
2. AOI 内に 25 m グリッドを作成
   - `native:creategrid` で矩形ポリゴンを生成
   - `native:clip` で AOI にクリップ
   - `grid_id` フィールドを付与（`$id`）
3. 道路 × グリッドの交差長（総延長）を計算
   - `native:intersection` で `roads_10m_seg_src` とグリッドを交差
   - 各 `grid_id` ごとに道路長 `total_len_m` を集計
4. 各 $r$ について AP バッファと道路の交差長を計算
   - `native:buffer`（DISSOLVE=TRUE）で AP を $r$ m バッファに溶解
   - `native:clip` で道路をバッファ領域内にクリップ (`covered_roads`)
   - `native:intersection` で `covered_roads` × グリッド
   - 各 `grid_id` ごとに被覆道路長 `covered_len_m` を集計
### 4.2 ECDF summary & plots

ECDF の集計指標（ECDF(0), P(coverage>=0.8), median coverage_ratio）は、
QGIS から出力した `data/ecdf_grid_coverage_ratio.csv` を
Google スプレッドシートに読み込み、セルに設定した数式で計算した。

本リポジトリには、上記スプレッドシートで計算済みの結果だけを
`derived/ecdf_summary.csv` として含めている。
（数式はスプレッドシート上で確認可能であり、必要に応じて再利用できる。）

In this repository, the ECDF-based summary metrics  
(ECDF(0), P(coverage>=0.8), median coverage_ratio) are **not**
computed by a Python script.

Instead, `data/ecdf_grid_coverage_ratio.csv` exported from QGIS
is loaded into a Google Spreadsheet, and the metrics are derived
using documented cell formulas.

Only the final aggregated table is stored in this repo
as `derived/ecdf_summary.csv`, which is used to produce the plots
of r–ECDF(0), r–P(coverage>=0.8), and r–median coverage_ratio.

### 4. Outputs / CSV files

`outputs/` には、QGIS スクリプトと Google スプレッドシートで集計した結果を
CSV 形式で保存している。

In the `outputs/` directory, we store CSV files generated from the QGIS script
and post-processing in Google Sheets.

- `ecdf_coverage_ratio_by_r.csv`  
  - **日本語**：各 r ∈ {5,10,15,20,25,35,45,50} について、グリッドごとの  
    `coverage_ratio` とその ECDF を記録した生データ。  
  - **English**: Raw ECDF data of `coverage_ratio` for each grid cell,  
    for r ∈ {5,10,15,20,25,35,45,50}.

- `ecdf_max_by_r.csv`  
  - **日本語**：スプレッドシートの「ecdf(MAX)」シートを書き出したもの。  
    各 r ごとの ECDF の最大値テーブル。  
  - **English**: Export of the “ecdf(MAX)” sheet in Google Sheets;  
    table of maximum ECDF values for each radius r.

- `ecdf_sum_by_r.csv`  
  - **日本語**：スプレッドシートの「ecdf(SUM)」シートを書き出したもの。  
    ECDF の累積件数に基づく集計表。  
  - **English**: Export of the “ecdf(SUM)” sheet;  
    aggregated counts based on the cumulative ECDF.

- `ecdf_summary_r5_50.csv`  
  - **日本語**：r ごとの要約指標をまとめたテーブル。  
    列：`r`, `ECDF(0)`, `P(coverage>=0.8)`, `median_coverage_ratio`。  
  - **English**: Summary table of key indicators for each r.  
    Columns: `r`, `ECDF(0)`, `P(coverage>=0.8)`, `median_coverage_ratio`.



5. Coverage Ratio の算出
   - 各セルについて以下の式を計算（道路が存在するセルのみ）：
     $$coverage\_ratio = \frac{covered\_len\_m}{total\_len\_m}$$
6. ECDF の作成
   - $r$ ごとに `coverage_ratio` のリストをソートし、経験分布 $F(x)$ を計算：
     $$F(x_i) = \frac{i}{N}$$
7. coverage_ratio と ecdf を $r$ ごとに出力

---

## 5. 出力ファイル / Outputs
スクリプト実行後、`OUT_DIR` に以下の 2 つの CSV が生成される：

### `grid_coverage_ratio_by_r.csv`
| column | description |
| :--- | :--- |
| r | AP バッファ半径 [m] (5,10,15,20,25,35,45,50) |
| grid_id | グリッド ID |
| total_len_m | セル内の道路総延長 |
| covered_len_m | AP バッファ内に含まれる道路延長 |
| coverage_ratio | `covered_len_m` / `total_len_m` |

### `ecdf_grid_coverage_ratio.csv`
| column | description |
| :--- | :--- |
| r | AP バッファ半径 [m] |
| coverage_ratio | 横軸 $x$ |
| ecdf | 経験累積分布 $F(x)$ |

---

## 6. 再現手順 / Reproduction Steps

### 日本語
1. QGIS プロジェクトを開き、CRS を **EPSG:6677** に設定する。
2. 以下の 3 レイヤを読み込む：
   - `ap_gt_points_6677`
   - `roads_10m_seg_src`
   - `aoi`
3. QGIS の Python コンソールを開き、次を実行：
   ```python
   exec(open("scripts/wifi_grid_coverage_ecdf_25m.py", encoding="utf-8").read())
4. コンソールログに表示されるパス（例: `~/Downloads/corridor_r_outputs`）に CSV が生成される。
5. これらを Google スプレッドシート等に読み込み、以下を集計する（本リポジトリの `summary.csv` に相当）。
   - ECDF(0): `coverage_ratio = 0` のときの ecdf 値
   - P(coverage ≥ 0.8): `coverage_ratio ≥ 0.8` のセル比率
   - median: `ECDF = 0.5` のときの `coverage_ratio`

### English
1. Open a QGIS project and set CRS to EPSG:6677.
2. Load the three layers: `ap_gt_points_6677`, `roads_10m_seg_src`, `aoi`.
3. Open the QGIS Python console and run:
   ```python
   exec(open("scripts/wifi_grid_coverage_ecdf_25m.py", encoding="utf-8").read())
4. The script prints the output directory; CSVs are created there.
5. Import the CSVs into a spreadsheet and compute metrics (ECDF(0), P(coverage ≥ 0.8), median).

## 7. $r$ 感度分析の結果 / Sensitivity Results for $r$
`ecdf_grid_coverage_ratio.csv` から集計した結果（`summary.csv`）は以下の通り：



### 7.1 指標の定義 / Metric Definitions
- ECDF(0): `coverage_ratio = 0` のセル割合（= ゼロカバー率）
- P(coverage ≥ 0.8): `coverage_ratio ≥ 0.8` のセル割合（= 高カバー率セルの比率）
- median coverage_ratio: `ECDF = 0.5` のときの `coverage_ratio`（= 典型的セルのカバー率）

### 7.2 数値結果 / Numerical Results
| r [m] | ECDF(0) (Zero cov.) | P(coverage ≥ 0.8) | median coverage_ratio |
| :---: | :---: | :---: | :---: |
| 5 | 0.2862 | 0.2862 | 0.424 |
| 10 | 0.1484 | 0.6254 | 1.000 |
| 15 | 0.0813 | 0.8092 | 1.000 |
| 20 | 0.0495 | 0.8799 | 1.000 |
| 25 | 0.0177 | 0.9399 | 1.000 |
| 35 | 0.0035 | 0.9894 | 1.000 |
| 45 | 0.0000 | 0.9965 | 1.000 |
| 50 | 0.0000 | 1.0000 | 1.000 |
(Values rounded to 4 decimal places)


## 8. 本研究で採用した $r$ の決定 / Choice of $r$ in This Study

### 8.1 判定条件 / Selection Criteria
本研究では、25 m グリッドに対して AP バッファの半径 $r$ を決める際、以下の 2 条件を「十分なカバー品質」の目安とした：

1. ゼロカバー率 ECDF(0) < 0.02 （未カバーセルを全体の 2% 未満に抑える）
2. P(coverage ≥ 0.8) ≥ 0.9 （セルの 90%以上が 80% 以上カバーされている）

### 8.2 判定結果 / Outcome
- r = 20 m
  - ECDF(0) ≈ 0.0495 → 条件1を満たさない
  - P(coverage ≥ 0.8) ≈ 0.8799 → 条件2ギリギリ未達
- r = 25 m
  - ECDF(0) ≈ 0.0177 < 0.02
  - P(coverage ≥ 0.8) ≈ 0.9399 ≥ 0.9
  - → 両条件を同時に満たす最小の $r$
- r ≥ 35 m
  - ECDF(0) → 0.0, P(coverage ≥ 0.8) → 1.0 へ漸近
  - ただし $r$ を大きくするほど、「別セルに属する細街路」をまとめて塗りつぶす形になり、空間解像度の低下が懸念される

### 8.3 結論 / Conclusion
以上より、渋谷 AOI (500 m × 500 m) における PSC 解析では、

1. ゼロカバーセルを 2% 未満に抑え
2. セルの 94% 程度を十分にカバーしつつ
3. $r$ を過度に大きくしない

というトレードオフの観点から、AP バッファ半径として $r = 25 \text{ m}$ を採用した。

---

## 9. 制約と限界 / Limitations

### 日本語
- WiGLE 由来データの偏り: ログ収集は任意の歩行経路に依存しており、大通りと細街路でサンプリング密度が異なる可能性がある。
- セルサイズ固定 (25 m): 本リポジトリでは 25 m グリッドのみを対象としており、10 m / 50 m グリッドとの比較（セルサイズ感度分析）は実施していない。そのため、セルサイズに依存する効果は今後の課題とする。
- 時間的変動の無視: 全期間の WiGLE ログを 1 つの静的データセットとして扱っており、時間帯や曜日による AP 稼働状況の変化は考慮していない。

### English
- Sampling bias from WiGLE: Data collection depends on arbitrary walking routes; main streets and alleys may have different sampling densities.
- Fixed grid size (25 m): This repository focuses on 25 m grids only; sensitivity to grid size (e.g., 10 m or 50 m) is not analyzed here.
- Temporal aggregation: WiGLE logs are treated as a single static snapshot; temporal variations in AP availability are not modeled.

---

## 10. 参考文献 / Reference
- Valenzano, A., Mana, D., Borean, C., & Servetti, A. (2016). Mapping WiFi measurements on OpenStreetMap data for Wireless Street Coverage Analysis. *FOSS4G 2016*.

## 11. 使用ツール / Tools
- QGIS LTR (macOS)
- WiGLE Wardriving
- Google Pixel 7a (data collection)(os16)
- Google Sheets (ECDF 集計・可視化)
- ChatGPT-5.1 Thinking (Text & Script Refinement)
- ChatGPT-5.2 Thinking (Text & Script Refinement)

