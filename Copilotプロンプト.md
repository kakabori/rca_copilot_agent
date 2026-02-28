# 次スレッド用：ポートフォリオ構築支援プロンプト（RCA Copilot Agent）

私はPythonとAgentic AIを学びたいエンジニアです。あなたは私（ユーザー）のコーチです。
勉強のためにポートフォリオを構築したいので、その構築を支援してください。  

では、以下の前提・目的・思想・目標・制約に沿って、タスク分解・実装手順・コード雛形・ディレクトリ構成まで具体的に導いてください。  

---

## 1) 私の背景（キャリア・志向）
- 現職：MathWorksのデータ分析系テクニカルコンサルティングエンジニア（主にMATLABを用いたデータサイエンス/アプリ開発/デプロイ支援）。
- 製造業（特に時系列データ）を多く扱ってきた。
- 過去に東京エレクトロン向けに異常検知システムをPoC→MVP→工場稼働まで伴走（約5年）。  
  そのシステムは「自動停止」ではなく、**異常度を可視化して現場常駐エンジニアの判断材料**にするもの。
- 私が最も興奮するのは、現場の高コスト意思決定（ライン停止等）に対して、**客観的な根拠を提示して判断を支える**仕事。
- ディープラーニングの高度なモデル設計/トレーニングは得意ではなく、データサイエンティスト職志望でもない。  
  ただし「データ中心の設計」「モデルの業務適用」「運用・説明責任」は強み。

---

## 2) 目指す職種・方向性（キャリアゴール）
- 将来：Databricks / Cognite のような **データプラットフォームベンダー**で、顧客向け実装寄り（Solution Architect / Resident Architect / Implementation系）のポジションを目指す。
- Agentic AIに強い関心があり、製造業での適用（RCA/復旧領域）に価値があると考えている。
- 特に「RCA/復旧（トラブル対応）」で、現場の判断を強化するエージェントを作りたい。

---

## 3) ポートフォリオの目的（この作品で示したい価値）
このポートフォリオの狙いは「異常検知の精度競争」ではない。  
**異常イベントを起点に、意思決定に耐える根拠（Evidence）を束ねて提示し、現場の初動判断（RCA/切り分け）を加速する**ことを示す。

特に示したい能力は以下：

- 競合する複数仮説（Hypotheses）を立て、根拠・弱点・不足証拠・不確実性を構造化して提示できる
- Human-in-the-loop（自動停止しない、判断は人が行う）という責任境界設計
- 「Agentが自分で関連データを取りに行く」tool-use構造

---

## 4) 作るもの（ポートフォリオの作品定義）
### プロジェクト名（仮）
**RCA Copilot Agent**（製造装置向け：根拠付き原因分析支援エージェント）

### 最小E2Eワークフロー（必須）
1. 異常イベント（JSON）を入力（score + top features）
2. Agentが「関連データを取りに行く」（時系列、保全履歴、文書など）※最初はスタブ/ダミーでOK
3. 競合仮説を複数生成
4. 各仮説に対して
   - supporting evidence（根拠）
   - counter evidence（反証/弱点）
   - missing evidence（不足証拠）
   - confidence / uncertainty（不確実性）
   - next checks（次に見るべき信号・点検）
5. 構造化された「意思決定ブリーフ」をJSONで返す
6. （将来拡張）承認→アクション、監査ログ、評価（Evals）など

### Agentの入出力（必須仕様）
#### Input例

```json
{
  "asset_id": "ETCHER_01",
  "timestamp": "2026-02-15T13:05:00Z",
  "anomaly_score": 0.92,
  "top_features": ["vibration", "pressure"]
}
```

#### Output例（骨格）

```
{
  "ranked_hypotheses": [
    {
      "hypothesis": "...",
      "confidence": 0.68,
      "supporting_evidence": ["..."],
      "counter_evidence": ["..."],
      "missing_evidence": ["..."],
      "next_checks": ["..."]
    }
  ],
  "overall_uncertainty": "Medium",
  "policy": { "auto_stop": false, "human_in_the_loop": true }
}
```

---

## 5) 技術方針（まず動くもの優先）

- **最優先：動く最小実装**（docs整備は後回しでOK）
- ローカルPCで完結（Dockerやクラウドは後で）
- 推奨スタック：Python + FastAPI（APIでデモしやすい）
- LLMは最初は不要。まずはルールベース/テンプレで「Agentらしい構造」を動かす。  
  その後、必要箇所（文章生成や仮説生成）だけLLMに置き換える。
- データは小規模ダミーでよいが、製造業の現実感を出すために「種類」は揃える：
  - time-series（CSV/Parquet）
  - asset/sensor registry
  - maintenance/work orders
  - documents（Markdown）
  - relations（edge table）※最初は固定でも可

---

## 6) 成果物の形（採用向けに必要なもの）

- GitHubリポジトリとして成立する構成
- 少なくとも以下が揃うこと：
  - `README.md`（概要・問題設定・全体構成・Agent責務・ユースケース・一言要約）
  - 動くAPI：`POST /rca` でJSONが返る
  - `requirements.txt` と `run` 手順
- デモは、Swagger UI または curl で見せられればOK

---

## 7) デモシナリオ（必須）

- 半導体製造装置を想定（ETCHER_01）
- 異常特徴：vibration と pressure の異常
- Agentが「時系列/履歴/文書」を参照したように見せ、
  「直近メンテの副作用」「センサーずれ」「真空リーク」など競合仮説を提示し、
  次の確認（leak check, calibration, baseline comparison 等）を提示する。

---

## 8) Copilotへの依頼（具体的にやってほしいこと）
次を順番に進めてください。

1. 最小ディレクトリ構成の提示（すぐ作れる形）
2. FastAPIで `/rca` が動く最小コード一式（app/agent/tools/data）
3. すぐ試せる `curl` コマンドとサンプルレスポンス
4. （余裕があれば）次の拡張ステップ：LLM導入ポイント、Evals、監査ログ、graph/relations強化

---

## 9) 現在の状態（今どこまで進んでいるか）

- FastAPIで動くものは作った。ただしデータは全てダミー。LLMも使っていない。

フォルダ構成は以下の通り

rca_copilot_agent/
- app/
	- agent/
		- rca_agent.py
	- tools/
		- documents.py
		- maintenance.py
		- timeseries.py
	- main.py
- scripts/
	- call_rca.ps1
- README.md
