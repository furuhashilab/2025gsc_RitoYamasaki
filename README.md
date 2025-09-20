# 2025gsc_RitoYamasaki_ZemiReport
## 要旨/Abstract
本研究は，災害看護における医療情報の最小知識開示を実現するため，マイナンバー基盤と属性ベース認可（ABAC）を用いた人間中心設計の有効性を検証する。Geo/Time/Role/PurposeとTriageを核に，許可・拒否の理由と「満たせば許可」の一行ヒントを提示する説明可能性UIを実装し，RBAC／ABAC／ABAC＋UIの3条件でユーザ実験を行う。合成FHIRデータと三つの臨床シナリオを用い，過剰開示・見落とし・タスク達成時間および試行回数・主観評価を指標として定量比較する。本研究は，災害時アクセス制御の過剰×見落とし×時間の同時計測を提示し，臨床現場に適合する最小開示の設計原理を示す。

This study evaluates a human-centered approach to minimal-knowledge disclosure for disaster nursing. Building on Japan’s My Number–based identity layer, we implement attribute-based access control (ABAC) using Geo/Time/Role/Purpose and triage attributes, together with an explainable UI that shows reasons for permit/deny decisions and a one-line counterfactual hint (“what to satisfy to permit”). In a controlled user study with synthetic FHIR scenarios, we compare RBAC, ABAC, and ABAC+XUI across four endpoints: over-disclosure, under-disclosure, decision latency (human_ms), and attempts, plus subjective clarity. The study contributes a joint measurement of privacy exposure and clinical speed, and provides design guidelines for minimal disclosure in emergency care. 


# 災害看護における最小知識アクセス制御の検証  
マイナンバー基盤 × ABAC × 説明可能UI

---

## 研究テーマ / 目的
**テーマ**  
災害看護における最小知識アクセス制御：マイナンバー基盤と属性ベース認可（ABAC）＋説明可能UIの有効性検証  

**目的**  
- 災害時に、意識不明の患者に必要な医療情報だけを迅速に開示する仕組みを設計・評価  
- Geo×Time×Role×Purpose＋Triage（G×T×R×P）とS.T.T.原則（Scope/Time/Trace）を活用  
- RBAC／ABAC／ABAC＋説明可能UIの比較実験を通じ、臨床現場に適合する最小開示の設計原理を明らかにする

---

## 背景
- **課題**  
  - 災害時、患者本人が意思表示できず、情報不足による誤処置リスクが高い  
  - 過剰情報開示はプライバシー侵害につながる
- **技術的背景**  
  - マイナンバーカードの普及により、現場でデジタルID認証が可能になりつつある  
  - RBACは静的ロール依存で、災害現場の動的状況に不向き  
  - ABACは時間・場所・目的などの動的属性を使い柔軟に制御できる

---

## 研究の流れ
1. **関連研究レビュー**  
   RBAC・ABAC・災害時情報アクセス・説明可能UIに関する先行研究を整理
2. **ポリシー設計**  
   G×T×R×P＋S.T.T.原則に基づくABACポリシーを設計
3. **UI試作**  
   - ABAC+Explain：許可/拒否理由をUI表示  
   - ABAC+Explain+CF：拒否時に「満たせば許可」の一行ヒントを表示
4. **実験シナリオ作成**  
   合成FHIRデータ＋臨床シナリオ3本を作成
5. **ユーザ実験**  
   看護師・医療従事者に操作してもらい、以下を測定
   - 過剰開示率
   - 見落とし率
   - タスク達成時間・試行回数
   - 主観評価（理解度・納得感）
6. **結果分析・考察**  
   RBAC/ABAC/ABAC+CFを定量比較し、最小開示と迅速性を両立する設計原理を抽出

---

## スケジュール（10月〜1月）
- **10月**：研究設計確定、ポリシー草案、シナリオ作成  
- **11月**：UIプロトタイプ開発、合成データ投入、動作テスト  
- **12月**：ユーザ実験実施、データ収集、一次解析  
- **1月**：分析・考察、論文執筆、指導教員レビュー、最終提出  

---

## 期待される成果
- 災害現場に適した最小知識アクセスのデザインパターン提示  
- 過剰開示・見落とし・時間のトレードオフを可視化  
- 説明可能UI（XAI）の効果を定量評価  

---

## 使用ツール
- **Python + Streamlit**：ABACポリシー検証UI実装  
- **pandas / matplotlib**：データ収集・可視化  
- **FHIR合成データ**：模擬患者情報生成  
- **Google Form**：主観評価アンケート収集  

---

## 卒論へのつながり
- 本研究で得られた「臨床UX閾値」を、卒論で扱う耐量子暗号（PQC）導入時の**遅延許容設計基準**として活用  
- ABAC＋CFが現場で受け入れられる条件を定義し、将来的に**ブロックチェーン監査ログ＋PQC署名**を組み込んだ分散型アクセス制御モデルに発展  

---
