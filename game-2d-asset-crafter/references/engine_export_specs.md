# 2Dゲームエンジン向けアセット規格 & インポート仕様書

本スキルで出力されたスプライトシートおよびメタデータを、主要な2Dゲームエンジン（Godot 4.x / Phaser 3）へインポートする際の設定仕様です。

---

## 1. Godot Engine 4.x 向け仕様

### テクスチャインポート設定（必須）
ドット絵（ピクセルアート）をぼやけさせず、くっきりと表示するための設定：
- **Texture Filter**: `Nearest`（デフォルトの `Linear` だとドットがぼやけるため必ず変更）
  - プロジェクト全体: `Project Settings` → `Rendering` → `Textures` → `Default Texture Filter` を `Nearest` に設定。
  - 個別ノード: `CanvasItem` → `Texture` → `Filter` を `Nearest` に設定。

### AnimatedSprite2D / SpriteFrames の適用
`pack_spritesheet.py --format godot` で出力された JSON に基づき、スプライトシートを `SpriteFrames` に読み込みます：
1. `AnimatedSprite2D` ノードを作成
2. `Sprite Frames` プロパティで新規 `SpriteFrames` リソースを作成
3. スプライトシート画像を読み込み、JSONの `cell_size`（例: 32x32）に合わせてグリッド分割アイコンから一括登録

---

## 2. Phaser 3 向け仕様

### アトラス（Texture Atlas）の読み込み
`pack_spritesheet.py --format phaser` で出力された画像と JSON をプリロードします：

```javascript
function preload() {
    // スプライトシート画像とJSONアトラスのロード
    this.load.atlas('hero', 'assets/sprites/hero_sheet.png', 'assets/sprites/hero_sheet.json');
}

function create() {
    // テクスチャフィルタを Nearest に指定（ピクセルアートのボケ防止）
    this.textures.get('hero').setFilter(Phaser.Textures.FilterMode.NEAREST);

    // アニメーションの作成（フレーム名で指定）
    this.anims.create({
        key: 'walk',
        frames: [
            { key: 'hero', frame: 'hero_walk_0' },
            { key: 'hero', frame: 'hero_walk_1' },
            { key: 'hero', frame: 'hero_walk_2' }
        ],
        frameRate: 8,
        repeat: -1
    });

    // スプライトのインスタンス化
    const player = this.physics.add.sprite(100, 100, 'hero', 'hero_idle');
    player.play('walk');
}
```

---

## 3. 推奨命名規則 (Naming Convention)

出力される個別PNGおよびフレーム名は、以下の規則に従います：

| アセット種別 | 命名フォーマット | 例 |
| :--- | :--- | :--- |
| **プレイヤーキャラクター** | `hero_[action]_[frame].png` | `hero_idle_0.png`, `hero_walk_1.png`, `hero_attack_0.png` |
| **敵キャラクター** | `enemy_[type]_[action]_[frame].png` | `enemy_slime_idle_0.png`, `enemy_skeleton_attack_1.png` |
| **アイテム** | `item_[name].png` | `item_potion_red.png`, `item_gold_key.png` |
| **タイル・背景** | `tile_[type]_[variant].png` | `tile_floor_stone.png`, `tile_wall_brick.png` |
| **UIパーツ** | `ui_[element]_[state].png` | `ui_heart_full.png`, `ui_button_hover.png` |

