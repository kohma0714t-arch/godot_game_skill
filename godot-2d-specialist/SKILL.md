---
name: godot-2d-specialist
description: Godot 4.xでの2Dゲーム（プラットフォーマー、トップダウン、パズル等）の開発を専門に行う親オーケストレータースキル。CharacterBody2D物理、ステートマシン、TileMapLayer、VFX、オーディオ管理、絵文字を排除した洗練されたUI、およびCLI自動検証を統括する。ユーザーが「Godotで2Dゲームを作りたい」「2Dプラットフォーマーを実装して」「2Dの当たり判定や物理を設定して」「/godot-2d」などに言及した場合は必ずこのスキルを使用すること。
---

# Godot 2D Specialist (Godot 2D専門開発オーケストレーター)

Godot 4.x（GDScript）における2Dゲーム開発を専門に担当し、物理、ステートマシン、レベルデザイン、UI、CLI自動検証までを自律的に推進するスキルです。

## ワークフロー

1. **仕様 ＆ アート受領**:
   - `game-spec-architect` の仕様書と `game-art-director` のデザイン規約（絵文字禁止、指定カラーパレット）をインプットにします。
2. **サブエージェント分業による実装**:
   - `2d-logic-specialist`: `CharacterBody2D`、ステートマシン（`references/2d_state_machine.gd`）、入力系。
   - `2d-level-specialist`: タイルマップ、足場配置、カメラ（`Camera2D` スムージング）。
   - `2d-ui-specialist`: 洗練されたベクター/テクスチャHUD、ライフバー、ポーズ画面。
   - `2d-vfx-audio-specialist`: `CPUParticles2D`（土煙、光芒）、オーディオプール（`references/2d_audio_vfx_manager.gd`）。
3. **自律検証（QA）**:
   - `Godot_v4.7.2-stable_win64_console.exe --headless --quit` でパースエラー・読込エラーを検出。
   - エラーがあれば即座に自己修復を行い、Exit code 0 を担保します。
4. **ユーザー節目確認**:
   - 各フェーズの節目で実装内容と起動手順（F5）を報告し、ユーザーの承認を得ます。

