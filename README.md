
# 2025gsc_RitoYamasaki_ZemiReport  
# 渋谷で歩道の Wi-Fi カバー率を測る / Street Wi-Fi Coverage in Shibuya


## 概要 / Overview

**日本語**  
本ゼミ論は、Valenzano らの「Potential Street Coverage（PSC）」手法を渋谷で **QGISのみ** で再現することを目標とする。WiGLE で取得した AP 点から r=25/50 m の円バッファ（Dissolve）を作成し、OSM 道路（10 m 分割）と交差長を求め、セル内の被覆比を算出して ECDF 化した。今後は 4 本の回廊で **coverage** と **longest gap** を二軸評価し、暫定最適 *r* を導く。  

**English**  
This thesis replicates the **Potential Street Coverage (PSC)** workflow by Valenzano *et al.* in Shibuya using **QGIS only**. WiGLE AP points → circular buffers (r=25/50 m, dissolved) → intersection with 10 m-segmented OSM roads → per-cell coverage ratio → ECDF. Next, four predefined corridors will be surveyed to pick a tentative *r* by jointly optimizing **coverage** and **longest gap**.

---

##  目的 / Objectives

- 論文の **骨格**（WiGLE → PSC → 道路交差 → セル集計）を **QGIS** で厳密再現  
- 再現可能性：入出力は **GeoPackage**、平面座標は **EPSG:6677** に統一

---

## データ / Data

- **WiGLE CSV**（自採取・渋谷、Wi-Fi のみエクスポート）  
- **OSM 道路**（Shibuya AOI 抽出、10 m セグメント化）  
- **AOI**：研究対象ポリゴン（センター街中心）  
- **座標系**：**EPSG:6677**（平面メートル系、JGD2011 / Japan Plane Rectangular）

---

##  パイプライン / Pipeline (QGIS)

1. **AP 点の読み込み**（WiGLE CSV → 点化、必要に応じて再投影 4326→6677）  
2. **PSC バッファ作成**：`r ∈ {25, 50} m`、**Dissolve=ON** で二値被覆  
3. **道路 10 m 分割**：線を距離で分割（10 m）→ 各セグメントの `$length` を保持  
4. **交差長**：`intersection()` で各セグメントの **len_in_r** を算出  
5. **セル集計**：グリッド（例：100 m 角）で  
   - `sum_len_in_r = sum(len_in_r)`  
   - `sum_len_m   = sum($length)`  
   - `cell_ratio_r = sum_len_in_r / sum_len_m`  

> 過大計上を避けるため、**複数 AP のバッファは先に Dissolve** して「被覆あり/なし」を二値化。
---

## 成果物 / Artifacts（現状）

- `buf_psc_25.gpkg` / `buf_psc_50.gpkg`（Dissolve 済み PSC）  
- `roads_10m_seg_src.gpkg`（10 m セグメント道路）  
- `roads_with_psc_25.gpkg` / `roads_with_psc_50.gpkg`（セグメントごと被覆比）  
- `grid_coverage_25_35_45_50_num.gpkg`（セル被覆の指標列つき）  
- `ecdf_psc_25_50.csv` / `ecdf_from_qgis_25_35_45_50.csv`（ECDF テーブル）  
- **Screenshots**：ECDF グラフ、AOI＋PSC マップ

---

## 再現手順（Quick） / Repro Steps (Quick)

1. **データ配置**：WiGLE CSV を `data/raw/` へ（**Wi-Fi のみ**をエクスポート）  
2. **QGIS** プロジェクトの **CRS=EPSG:6677** を確認  
3. **スクリプト実行**（例；QGIS Python Console）  
   - `build_psc_buffers.py` → `buf_psc_25/50.gpkg`  
   - `roads_intersection_ratio.py` → `roads_with_psc_*.gpkg`  
4. **スプレッドシート**で `ecdf_*.csv` を可視化（中央値/上位10%点/AUC 等を算出）


> 代表点生成（最大 RSSI 採用）の 20 行スクリプトは `scripts/make_representatives.py` を参照。

## 拡張
- **回廊校正** :再現していた論文は実地調査をしていなかったので、実際に私は測って、論文で仮説で適切としているr =50が適切なのかを渋谷で測る

---
## これから取り掛かること
 - **ECDF**：`cell_ratio_r` の分布から ECDF テーブル（CSV）を出力  
 - **可視化**：`ecdf_*.csv` をスプレッドシートでプロット（中央値・p75・p90・AUC 等）  
 - **回廊校正（Next）**：4 回廊で **coverage** と **longest gap** を計測 → *r* 暫定決定


##  回廊実測（r 校正） / Corridor Calibration (Next)

- **Corridors**：  
  C1 井の頭通り入口／C2 旧大山街道〜宮益坂／C3 玉川通り〜西口歩道橋／C4 右下 L 字  
- **端末**：Pixel 7a（Wi-Fi **ON**・未接続で可）、位置情報 **ON**  
- **アプリ**：  
  - **WiGLE**：**Wi-Fi のみ**エクスポート（CSV）  
  - **OsmAnd**：**回廊ごとに**トラック録画（往復、停止→保存）  
- **指標**：  
  - `coverage = covered_length / total_length`  
  - `longest_gap = max(uncovered_run)`  
- **目的**：`r ∈ {25,35,45,50,80}` の **coverage↑ & longest_gap↓** のパレート前面から暫定 *r* を決定
- データは取得済み

---

## 中間所見 / Interim Findings

-渋谷のカバー率は高い
-しかし、一度実験を間違えていた時に測っていた、wifiが使えるか使えないかという結果を見ると、使えるwifiは、表示されているものよりもだいぶ少ない
-再現するためのデータ収集は揃っているので、一気に終わらせたい

---

##  倫理・公開ポリシー / Ethics & Sharing

- **匿名化**：BSSID 非公開／座標は 250 m 粗化して共有  
- **最小公開**：CSV は要約指標中心、原データは非公開 or 制限付き  

---

##  参考 / Reference

- Valenzano, A., Mana, D., Borean, C., & Servetti, A. (2016).  
  *Mapping WiFi measurements on OpenStreetMap data for Wireless Street Coverage Analysis.*  
  PDF: [/mnt/data/FOSS4G_2016_Mapping_WiFi_2017_12_03.pdf](/mnt/data/FOSS4G_2016_Mapping_WiFi_2017_12_03.pdf)

---

##  To-Do（短期）

- [ ] グリッド解像度を上げて **ECDF 計算**（中央値・AUC・上位10%点を報告）  
- [ ] **回廊 4 本 実測** → coverage & longest-gap を算出  
- [ ] *r* 暫定決定 & Sensitivity（25/35/45/50） 
- [ ] 仕上げ図：AOI ヒートマップ、ECDF 図、回廊帯図（モデル vs 実測）
      
## 　単語整理
-理論的な累積分布関数（CDF）の代わり:理論的な分布を仮定せず、実際のデータから計算された関数です。﻿(下の論文ではCDF使用）

## 　使用ツール
-Chat GPT5 Thinking
-Chat GPT5.1 Thinking
-QGIS
-Wigle Wardriving
-Google Pixcel 7a



