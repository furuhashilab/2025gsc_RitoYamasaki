# Attribute Dictionary v1 (Disaster Nursing ABAC)

> 目的：ABACで用いる属性を S/O/E/P に分類し、定義・権威・鮮度(TTL)・取得方法・欠落時/期限切れ時の扱いを明記する。

| name | class (S/O/E/P) | type | domain / example | authority (権威) | acquisition (取得) | TTL | fallback (欠落/期限切れ時) | audit_note |
|---|---|---|---|---|---|---|---|---|
| role | S | enum | ER_Nurse / ER_Physician / DMAT_Nurse | 病院人事 | 起動時同期（ローカルキャッシュ） | 24h | Deny + Advice「権限不足」 | 値のみ |
| license | S | enum | RN / EMT / MD | 資格台帳（免許） | 起動時同期 | 30d | Deny（Override不可） | 値のみ |
| org | S | enum | Hospital_A / Field_ER | 施設台帳 | 起動時同期 | 24h | Deny（所属不明） | 値のみ |
| on_duty | S | bool | true/false | 勤怠システム | ローカル入力/同期 | 8h | Deny + Advice「勤務中に設定」 | 値のみ |
| data_class | O | enum | blood_type / allergy_category / vital_signs | データ作成時 | 固定 | n/a | Deny（不明データ） | カテゴリのみ保持 |
| sensitivity | O | enum | low / med / high | ポリシー | 固定 | n/a | high の場合は更に厳格（Permit条件加重） | 値のみ |
| geo | E | enum | Shelter_A / ER_200m_radius | 端末測位 | 自動更新 | 5m | **Deny + Advice**「位置を更新」(救命のみ Override 可) | 位置カテゴリのみ |
| time_since_disaster | E | int (sec) | 0–21600 | 管制/時計 | 自動更新 | 10m | Deny + Advice「災害時刻確認」 | 数値のみ |
| network | E | enum | online / offline_weak | 端末 | 自動更新 | 1m | offline: 最小開示のみ/同期遅延 | 値のみ |
| purpose | P | enum | 救命 / 搬送 / 事務 | 利用者 | 毎リクエスト入力 | 1 req | **Deny + モーダル要求** | 必須ログ |
| triage | P | enum | Red / Yellow / Green / Black | トリアージ担当 | 入力 | 15m | 未入力=最小開示のみ | 値のみ |

### メモ
- S/O/E/Pは Subject / Object / Environment / Purpose。
- TTL切れ判定フラグは `*_ttl_expired` としてPDPに渡す。
- オフライン時は「最小開示＋強監査＋再同期後レビュー」。
