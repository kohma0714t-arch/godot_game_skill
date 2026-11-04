# ゲームアセット命名規約ガイドライン

Godot 4.x および Blender との連携において、アセットファイルの識別と自動インポートを円滑にするための命名規則です。

---

## 1. プレフィックス規約

| アセット種別 | 接頭辞 (Prefix) | 例 |
| :--- | :--- | :--- |
| プレイヤーキャラクター | `player_` | `player_base.blend`, `player_sprite.png` |
| 敵キャラクター | `enemy_` | `enemy_slime.blend`, `enemy_boss_dragon.blend` |
| NPC | `npc_` | `npc_merchant.blend`, `npc_guide.png` |
| 地形・環境メッシュ | `env_` | `env_ground_block.blend`, `env_cliff_wall.blend` |
| アイテム・小道具 | `item_` / `prop_` | `item_coin.blend`, `prop_chest.blend` |
| BGM（音楽） | `bgm_` | `bgm_stage1.ogg`, `bgm_boss_battle.ogg` |
| 効果音 (SE) | `sfx_` | `sfx_jump.wav`, `sfx_hit.wav`, `sfx_coin.wav` |
| UI素材 | `ui_` | `ui_health_bar.tscn`, `ui_dialog_box.tscn` |

---

## 2. 3D（Blender / Godot）コリジョンサフィックス規約

BlenderからGodotへ `.blend` をインポートする際、ノード名に特定のサフィックス（接尾辞）を付与することで、Godotが自動的にコリジョンシェイプを生成します。

- **`-col`**: 静的凹凸コリジョン（`StaticBody3D` + `ConcavePolygonShape3D`）
  - 用途: 地形、床、壁、建物
- **`-colonly`**: コリジョンのみ生成（元のメッシュは非表示）
  - 用途: 見えない壁、落下判定トリガー
- **`-convcol`**: 凸包コリジョン（`StaticBody3D` + `ConvexPolygonShape3D`）
  - 用途: 動く障害物、小道具、樽、岩
- **`-navmesh`**: ナビゲーションメッシュ自動生成

---

## 3. ディレクトリ配置基準

```text
res://
├── assets/
│   ├── models/        # 3Dモデル (.blend)
│   ├── textures/      # テクスチャ・スプライト画像 (.png)
│   ├── audio/
│   │   ├── bgm/       # BGM (.ogg)
│   │   └── sfx/       # 効果音 (.wav)
│   └── fonts/         # フォントファイル (.ttf, .otf)
├── scenes/            # シーンファイル (.tscn)
│   ├── characters/
│   ├── environments/
│   └── ui/
└── scripts/           # GDScript (.gd)
```
