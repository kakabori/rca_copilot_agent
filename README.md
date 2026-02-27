# RCA Copilot Agent（製造装置向け：根拠付き原因分析支援エージェント）

## 1. Overview（概要）
本プロジェクトは、製造装置の異常イベント（異常度スコア＋寄与特徴）を起点に、
保全エンジニアが「止める／止めない」「どこから切り分けるか」を判断するための 
**根拠付きRCA（Root Cause Analysis）** を提示する **Agentic AI** の最小実装ポートフォリオです。

**重要：本Agentは判断を自動化しません。**代わりに、複数の原因仮説を提示し、それぞれに 
**根拠（Evidence）・弱点（Counter Evidence）・不確実性（Confidence / Uncertainty）** を付与して、
現場の意思決定を強化します（Human-in-the-loop）。

---

## 2. Problem Statement（なぜ作るか）
異常検知／予知保全モデルは「いつもと違う」を定量化できますが、製造現場の意思決定
（特にライン停止のような高コスト判断）に必要なものは、スコア単体ではなく以下です。

- **なぜその結論に至ったか（根拠の束ね方）**
- **どこが不確実で、何を追加確認すべきか（次の一手）**
- **過去履歴や作業履歴、手順書とどう整合するか（文脈）**

そこで本プロジェクトでは、異常イベントを「単一の答え」にせず、
**競合する複数仮説**として扱い、データに基づいた根拠を構造化して提示する 
**RCA Copilot Agent** を設計・実装します。

---

## 3. High-level Architecture（全体構成）
最小構成で「本番運用に耐える設計思想」を表現するため、次のレイヤに分割します。

```text
┌--------------------------------------┐ 
│ UI / API                             │
│ - anomaly view / RCA result view     │
└--------------------------------------┘
                    │
┌------------------▼------------------┐
│ RCA Copilot Agent                    │
│ - Hypothesis Generator               │
│ - Evidence Collector                 │
│ - Hypothesis Evaluator               │
│ - Decision Brief Builde              │
└─────────┬─────────┘
                    │
┌─────────▼─────────┐
│ Context & Data Access Layer          │
│ - time-series query                  │
│ - maintenance/work order query       │
│ - doc search (RAG)                   │
│ - asset relations (graph/edge table) │
└───────────────────┘
```

> 詳細設計は `docs/` に切り出します（READMEでは「導線」重視）。

---

## 4. Agent Responsibilities（Agentの役割：Input / Output / 目的）
### 4.1 Input（入力）
異常検知や監視システムから渡される異常イベント（例）：

```json
{
  "asset_id": "ETCHER_01",
  "timestamp": "2026-02-15T13:05:00Z",
  "anomaly_score": 0.92,
  "top_features": ["vibration", "pressure"]
}
```

### 4.2 What the agent does（Agentがやること）
#### 1. 関連データを自律的に取得する

- 直近／長期の時系列（関連センサー、比較対象を含む）
- 保全履歴・作業履歴（work order / maintenance）
- 関連文書（手順書、過去障害報告、ナレッジ）
- 装置・部位・工程の関係（asset graph / edge table）

#### 2. 複数の原因仮説を立てる（競合仮説）

- 例：センサー起因／作業起因／プロセス条件ドリフト／部品劣化…など

#### 3. 各仮説に「根拠」と「弱点」を付与する

- 支持する兆候（supporting evidence）
- 反証・矛盾（counter evidence）
- 不足している証拠（missing evidence）

#### 4. 判断材料として構造化して提示する（意思決定ブリーフ）

- 仮説の優先順位
- 不確実性
- 次に確認すべき信号・点検（最短で効果が高い順）

### 4.3 Output（出力）
現場がそのまま使える「RCA Decision Brief」（例）：

```json
{
    "ranked_hypotheses": [
        {
            "hypothesis": "Recent maintenance caused sensor misalignment",
            "confidence": 0.68,
            "supporting_evidence": [
                "MaintenanceRecord#3421 (2 days ago)",
                "Vibration spike immediately after maintenance"
            ],
            "counter_evidence": [
                "No similar issue observed after same maintenance type in the past"
            ],
            "missing_evidence": [
                "Sensor calibration result after maintenance"
            ],
            "next_checks": [
                "Recalibrate vibration sensor",
                "Compare with adjacent tool sensors"
            ]
        }
    ],
    "overall_uncertainty": "Medium",
    "agent_policy": {
        "auto_stop": "disabled",
        "human_in_the_loop": true
    }
}
```

---

## 5. Minimal Data Model（最小データモデル：ダミーで再現）
本プロジェクトは大規模データを前提にしませんが、
**製造業の現実に必要な“データの種類”**を揃えます。

- Time-series：vibration / temperature / pressure（Parquet/CSVでも可）
- Registry：asset / sensor（台帳）
- Maintenance：work_order / maintenance_record（履歴）
- Documents：手順書・障害報告（Markdown/PDF→テキスト化）
- Relations：asset↔sensor、asset↔work_order、work_order↔doc（edge table）

---

## 6. Why this matters（このポートフォリオで示したいこと）
本プロジェクトは「高精度モデルの実装」ではなく、以下を示すことを目的とします。

- 異常スコアを“意思決定に耐える根拠”へ変換できる
- 複数仮説・根拠・弱点・不確実性を扱う設計ができる
- Human-in-the-loop を前提に、責任境界と運用を設計できる
- 自作を通じて、Cognite / Databricks 等のデータプラットフォームがどこで効くか（文脈化、評価、運用、スケール）”を説明できる

---

## 7. Use Cases（想定ユースケース）

- 半導体製造装置の異常時：RCA / 初動切り分け支援
- 保全エンジニア向け：根拠付き判断材料の提示
- 誤判断が許されない現場での：説明責任・監査を意識した設計

---

## 8. Positioning（面接・職務経歴書向けの一言）
本プロジェクトは、異常検知の精度改善ではなく、異常を“解釈”して意思決定に耐える根拠を
構造化するRCA Copilot Agent を実装する試みである。
（自動停止は行わず、Human-in-the-loop と説明責任を前提とする。）
