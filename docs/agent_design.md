# Agent Design: RCA Copilot Agent
（仮説駆動・根拠付きRCAのためのAgent設計）

## 0. 本ドキュメントの位置づけ
本ドキュメントは、`README.md` で概要として示した  
**RCA Copilot Agent** の内部設計を詳細化するものである。

目的は以下の3点：
1. **Agentic AI を「正しく」設計していることを示す**
2. 異常検知モデル単体では到達できない  
   **“意思決定に耐えるRCA”** の構造を明確にする
3. 自作実装を通じて、**Cognite / Databricks 等のプラットフォームが  
   どこで効くかを説明できる状態**を作る

---

## 1. 設計思想（Design Philosophy）

### 1.1 正解を当てない
本Agentの目的は「正解の原因を当てる」ことではない。

製造業のRCAでは、
- 観測できるデータは常に不完全
- 判断には時間制約・安全制約がある
- 誤判断コストが極めて高い

そのため、本Agentは **単一の結論を断定しない**。

### 1.2 仮説を競合させる
代わりに、Agentは以下を行う：
- 複数の **競合する原因仮説** を同時に提示
- 各仮説に **根拠（support）と弱点（counter / missing）** を付与
- **不確実性を明示** し、次の確認行動を示す

これは、人間の熟練エンジニアが行っている  
**思考プロセスの外在化**である。

### 1.3 Human-in-the-loop を前提にする
本Agentは：
- 自動停止を行わない
- 最終判断を下さない

代わりに、
> **「判断に耐える材料」を最短時間で構造化する**

ことに価値を置く。

---

## 2. Agentの責務分解（Functional Decomposition）

RCA Copilot Agentは、以下の4つの内部コンポーネントから構成される。

RCA Copilot Agent
├─ Hypothesis Generator
├─ Evidence Collector
├─ Hypothesis Evaluator
└─ Decision Brief Builder

それぞれの責務を以下に定義する。

---

## 3. Hypothesis Generator（仮説生成）

### 3.1 役割
異常イベントを「1つの原因」に収束させず、  
**構造化された仮説空間**に展開する。

### 3.2 仮説の粒度
仮説は「点」ではなく **カテゴリ＋具体例**で定義する。

例：
- センサー起因
  - センサー劣化
  - センサー取り付けズレ
- 作業起因
  - 直近保全作業の副作用
  - 設定変更ミス
- プロセス起因
  - 条件ドリフト
  - 原材料ばらつき
- 装置・部品起因
  - 初期摩耗
  - 冷却系の性能低下

### 3.3 実装イメージ（疑似コード）

python
def generate_hypotheses(anomaly_event):
    hypotheses = []

    if "vibration" in anomaly_event.top_features:
        hypotheses.append("Sensor degradation or misalignment")

    if recent_maintenance_exists(anomaly_event.asset_id):
        hypotheses.append("Side effect of recent maintenance")

    hypotheses.append("Process condition drift")
    hypotheses.append("Early-stage component wear")

    return hypotheses