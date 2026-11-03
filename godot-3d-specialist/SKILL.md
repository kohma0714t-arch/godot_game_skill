---
name: godot-3d-specialist
description: Godot 4.xでの3Dゲーム（3Dアクション、TPS、探索、アリーナ等）の開発を専門に行う親オーケストレータースキル。CharacterBody3D、三人称追従カメラ（SpringArm3D）、3D物理、Blender（.blend）直接統合、WorldEnvironment・ライティング、3D VFX・音響、絵文字を排除した洗練されたUI、およびCLI自動検証を統括する。ユーザーが「Godotで3Dゲームを作りたい」「3Dアクションを実装して」「BlenderモデルをGodotの3D空間に配置して」「/godot-3d」などに言及した場合は必ずこのスキルを使用すること。
---

# Godot 3D Specialist (Godot 3D専門開発オーケストレーター)

Godot 4.x（Forward Plus / D3D12 / GDScript）における3Dゲーム開発を専門に担当し、物理、ステートマシン、Blenderアセット統合、レベル構築、3D VFX・音響、CLI自動検証までを自律的に推進するスキルです。

## ワークフロー

1. **仕様 ＆ デザイン受領**:
   - `game-spec-architect` の仕様書および `game-art-director` のデザイン規約（絵文字禁止、3〜5色パレット、トーンマッピング指針）を受け取ります。
2. **サブエージェント分業による実装**:
   - `3d-logic-specialist`: `CharacterBody3D`、三人称追従カメラ（`Camera3D` + `SpringArm3D`）、ステートマシン（`references/3d_state_machine.gd`）。
   - `3d-level-specialist`: Blenderの `.blend` ファイル（`-col` 自動コリジョン付）のシーンインスタンス化、足場、ライティング（`DirectionalLight3D` + 影）。
   - `3d-ui-specialist`: 3D空間と親和性の高いモダンなHUD、クリア・リザルト演出。
   - `3d-vfx-audio-specialist`: `GPUParticles3D`（衝撃波、煙、光）、3D位置指定オーディオ（`references/3d_audio_vfx_manager.gd`）。
3. **自律検証（QA）**:
   - `Godot_v4.7.2-stable_win64_console.exe --headless --quit` を実行。
   - インポート漏れやパースエラーを自動検知・即座に自己修復（Exit code 0 保証）。
4. **ユーザー節目確認**:
   - 各フェーズの節目で実機確認手順（F5）を報告し、ユーザーのフィードバックと承認を得て次のステップに進みます。

