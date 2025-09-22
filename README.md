# 2025gsc_RitoYamasaki_ZemiReport
# 🌐 災害看護におけるABAC＋オフライン＋Override検証計画  
**Research Plan for ABAC + Offline + Override in Disaster Nursing**

---

## 📄 要旨 / Abstract

**日本語**  
本研究は，災害看護における医療情報の最小知識開示を実現するため，マイナンバー基盤と属性ベース認可（ABAC）を用いた人間中心設計の有効性を検証する。Geo/Time/Role/PurposeとTriageを核に，許可・拒否の理由と「満たせば許可」の一行ヒントを提示する説明可能性UIを実装し，RBAC／ABAC／ABAC＋UIの3条件でユーザ実験を行う。合成FHIRデータと三つの臨床シナリオを用い，過剰開示・見落とし・タスク達成時間および試行回数・主観評価を指標として定量比較する。本研究は，災害時アクセス制御の過剰×見落とし×時間の同時計測を提示し，臨床現場に適合する最小開示の設計原理を示す。

**English**  
This study evaluates a human-centered approach to minimal-knowledge disclosure for disaster nursing.  
Building on Japan’s My Number–based identity layer, we implement attribute-based access control (ABAC) using Geo/Time/Role/Purpose and triage attributes, together with an explainable UI that shows reasons for permit/deny decisions and one-line counterfactual hints (“what to satisfy to permit”). In a controlled user study with synthetic FHIR scenarios, we compare RBAC, ABAC, and ABAC+XUI across four endpoints: over-disclosure, under-disclosure, decision latency, and attempts, plus subjective clarity. The study contributes a joint measurement of privacy exposure and clinical speed, and provides design guidelines for minimal disclosure in emergency care.

---

## 🎯 研究テーマ / Objective

**日本語**  
災害時に意識不明患者の「クリティカルな個人情報」へ迅速かつ必要最小限でアクセスする仕組みを設計・検証する。  
マイナンバーカード認証＋ABACによる動的アクセス制御、オフライン判定、Override機能を統合し、過剰開示・見落とし・判断時間のトレードオフを定量的に評価する。

**English**  
Design and evaluate a mechanism for rapid, minimal-disclosure access to critical patient data during disasters.  
We integrate My Number–based authentication, ABAC-driven dynamic access control, offline decision-making, and emergency override functions, quantifying the trade-offs between over-disclosure, under-disclosure, and decision latency.

---

## 🔎 背景 / Background

**日本語**  
RBACは役割に依存する静的制御であり、災害時の人員・状況変化に適応しにくい。  
ABACはGeo, Time, Role, Purpose, Triageといった動的属性に基づき、より柔軟な最小知識アクセスを可能にするが、拒否理由が不透明、通信途絶時の判定不能、Override乱用リスクといった課題が残る。

**English**  
RBAC offers static, role-based control, which struggles with dynamic personnel and situational changes during disasters.  
ABAC enables fine-grained, context-aware decisions but faces challenges: opaque denials, network dependency, and potential misuse of emergency overrides.

---

## 🧩 研究の流れ / Research Flow

### 🔹 ゼミ論（実装＋机上実験） / Seminar Thesis
- **ポリシー設計 / Policy Design**  
  JSON-based ABAC rules (G×T×R×P＋Triage, S.T.T. principle)
- **UIプロトタイプ / UI Prototype**  
  Permit/deny reasons, “what to satisfy” hints, red-button override flow
- **オフライン対応 / Offline Mode**  
  Local decision cache + delayed audit log sync
- **机上実験 / Controlled Study**  
  比較：RBAC vs ABAC vs ABAC+Override  
  指標：過剰開示率、見落とし率、タスク時間、Override率、主観評価（SUS）

### 🔹 卒論（現場実験＋分析） / Bachelor Thesis
- 実際の看護師・DMATによる短時間試用
- オフライン/オンライン条件切替
- Override使用ログと救命寄与率分析
- 最適ポリシー曲線（見落とし×過剰開示×時間）の提示

---

## 📅 スケジュール / Timeline (Oct – Jan)

| 月 / Month | 主なタスク / Key Tasks |
|-----------|----------------|
| **10月 / Oct** | 文献レビュー、ポリシー仕様、UIモック作成 |
| **11月 / Nov** | Python実装、FHIR合成データ、オフラインキャッシュ |
| **12月 / Dec** | 倫理審査提出、机上実験、統計解析 |
| **1月 / Jan** | 結果整理、論文執筆、発表 |

---

## 🎯 期待される成果 / Expected Outcomes
- 動作するプロトタイプ（オフライン＋Override＋説明UI）  
- 定量データ：過剰開示率・見落とし率・判断時間  
- 現場UX閾値の提示  
- 卒論に向けた現場実験プロトコル

---

## 🛠 使用ツール / Tools
Python (Streamlit, FastAPI), SQLite, JSON, Matplotlib, Pandas, Figma, Synthetic FHIR data.

---

## 🚀 卒論へのつながり / Link to Bachelor Thesis
Use UX thresholds derived here to design real-world experiments, validating whether ABAC+Override “saves” or “breaks” emergency care, and proposing guidelines for clinical adoption.
