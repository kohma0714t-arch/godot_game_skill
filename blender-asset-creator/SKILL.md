---
name: blender-asset-creator
description: Blender 5.2を活用し、Pythonスクリプトによるヘッドレス3D自動モデリング・マテリアル・アニメーション・Godot用自動コリジョン生成、および手動モデリング支援を行う3Dアセットオーケストレータースキル。ユーザーが「Blenderでモデルを作りたい」「3D素材を生成して」「.blendを作成して」「Blender Pythonで自動モデリング」「3Dアセットを作成して」「/blender-create」「/blender-asset」などに言及した場合は必ずこのスキルを使用すること。
---

# Blender Asset Creator (Blender 3Dアセット制作 ＆ 連携オーケストレーター)

Blender 5.2のPython環境（`bpy`）を活用し、Godot 4.xと完全に互換性のある3Dモデル（`.blend`）を自動生成、または手動モデリングを支援するスキルです。

## ワークフロー

1. **アセット要件の受領**:
   - 仕様書（`spec.md`）および `game-art-director` のカラーパレット・質感定義を受け取ります。
2. **モデリング方式の選択**:
   - **自動生成**: Pythonスクリプトを作成し、`blender.exe -b --python script.py` でヘッドレス実行。
   - **手動支援**: ユーザーがBlender GUIで制作する際のノード構成、ピボット位置、命名規則を案内。
3. **コリジョンサフィックスの付与**:
   - 静的障害物: `-col` または `-colonly`
   - 移動体・軽量物: `-convcol`
4. **Godotプロジェクトへの配置**:
   - `res://assets/models/` 直下に `.blend` ファイルを保存し、Godotの自動インポートを発火させます。

---

## 内蔵サブエージェント ＆ 専門領域

- **`blender-mesh-specialist`**:
  - `scripts/asset_templates.py` を用いた幾何学・プロシージャルメッシュ（小道具、宝箱、木、岩、ステージパーツ）の生成。
  - 接地原点 `(0, 0, 0)`、トランスフォーム適用の徹底。
- **`blender-mat-specialist`**:
  - `game-art-director` 監修パレットに基づくPrincipled BSDFマテリアル（ラフネス、メタリック、エミッション）の設定。
- **`blender-rig-anim-specialist`**:
  - 単純回転、上下浮遊、開閉、ボーン付きアーマチュアのアニメーションデータ構築。

