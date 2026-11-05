---
name: topdown-2d-map-architect
description: トップダウン2Dゲームにおけるマップやステージの設計・生成・自律検証スキル。抽出された素材（タイル、壁、床、プロップ等）からステージを構築し、ユーザーのイメージの有無に応じたハイブリッド型設計、経路到達性（BFS）やタイルの接続整合性を自動テストし、崩れがあれば合格するまで自律的に修正してGodot 4.x TileMapLayerやプレビュー画像を出力する。ユーザーが「トップダウンのマップを作りたい」「ステージを作成して」「ダンジョンを生成して」「マップの構成をテストして」「タイルマップを作って」「/topdown-map」「/map-craft」などに言及した場合は必ずこのスキルを使用すること。また、ステージ完成後はgodot-2d-specialistへ自動連携すること。
---

# Topdown 2D Map Architect (マップ・ステージ設計＆自律検証オーケストレーター)

トップダウン2Dゲーム向けに、用意されたタイル素材からステージやマップを自動／半自動設計し、**「構成の崩れ（経路閉塞・孤立）」** と **「デザインの崩れ（タイルの角・境界不整合）」** を徹底的にテスト検証して、問題があれば自律的にやり直して仕上げるスキルです。

---

## ワークフロー概要

```mermaid
flowchart TD
    Step1["Step 1: マップイメージのヒアリング<br>(game-2d-asset-crafterのタイル素材受領 / イメージ有無確認)"]
    Branch{"イメージの有無"}
    Step1A["イメージあり: ユーザー構想を反映した設計<br>(開始点、大広間、ボス部屋の配置)"]
    Step1B["イメージなし: 素材に応じた3つの推奨レイアウト提示<br>(ダンジョン型 / アリーナ型 / 迷路探索型)"]
    Step2["Step 2: ハイブリッド型マップ構築<br>(build_topdown_map.py / レイヤー別組み立て)"]
    Step3["Step 3: 二大自動テスト検証<br>(validate_map_structure.py + validate_map_design.py)"]
    Step4{"Step 4: テスト合否判定<br>(全チェック合格か？)"}
    Step5["Step 5: パッケージ出力 & プレビュー提示<br>(Godot TileMapLayer + 全体俯瞰プレビューPNG)"]
    Step6["Step 6: godot-2d-specialistへの連携ハンドオーバー<br>(stage_*.tscn をレベルデザインへ引き渡し)"]

    Step1 --> Branch
    Branch -- "あり" --> Step1A --> Step2
    Branch -- "なし" --> Step1B --> Step2
    Step2 --> Step3
    Step3 --> Step4
    Step4 -- "Fail (崩れあり / 最大3-5回)" --> Step2
    Step4 -- "Pass (全合格)" --> Step5
    Step5 --> Step6
```

---

## ワークフローステップ詳細

### Step 1: マップ・ステージのイメージヒアリング
- `game-2d-asset-crafter` 等からタイル素材群を受け取り、イメージの有無（あり: ユーザー構想 / なし: ダンジョン・アリーナ・迷路の3推奨案から選定）を確認します。

### Step 2: ハイブリッド型マップ構築
- `scripts/build_topdown_map.py` を実行して、マップ構造・衝突判定・装飾レイヤーを組み立てます。

### Step 3: 二大自動テスト検証（崩れ検知）
1. **構成の崩れテスト**: `scripts/validate_map_structure.py` でBFS経路到達性100%（スタート〜ゴール/全宝箱）、外周密閉度、孤立床を検査。
2. **デザインの崩れテスト**: `scripts/validate_map_design.py` で孤立壁、壁内穴あき、オブジェクト埋没を検査。

### Step 4: 改善ループ（反復リトライ）
- 崩れ検知時はエラー箇所を特定し、自動修正して Step 2 を再実行（最大3〜5回）。

### Step 5: パッケージ出力 & 節目確認
- **全体俯瞰プレビュー画像 (`map_preview.png`)** を提示し、ユーザーの承認を得ます（**節目確認 2A**）。
- Godot 4.x シーンファイル (`stage_01.tscn`) をエクスポート。

### Step 6: `godot-2d-specialist` への連携ハンドオーバー
- 承認されたステージシーン（`.tscn`）を **`godot-2d-specialist`** のレベル担当サブエージェント（`2d-level-specialist`）へ引き渡し、メインゲームシーンへのインポートとカメラ追従設定を依頼します。

---

## 付属スクリプト一覧
- **`scripts/build_topdown_map.py`**: ハイブリッド型マップ構築、プレビューPNGレンダリング、Godot TSCNエクスポート
- **`scripts/validate_map_structure.py`**: BFS経路探索、外周密閉度、孤立床検出
- **`scripts/validate_map_design.py`**: 壁接続・穴あき・オブジェクト埋没のデザイン整合性検証
