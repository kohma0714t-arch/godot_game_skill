# Godot 4.x TileMapLayer インポート & 実装ガイド

Godot 4.x における `TileMapLayer` を用いたトップダウン2Dステージの実装仕様書です。

---

## 1. Godot 4.x の TileMapLayer 構造

Godot 4.3 以降では、従来の `TileMap` ノードから、個別のレイヤーごとに独立した `TileMapLayer` ノードを重ねる構造が推奨されています。

```
StageRoot (Node2D)
├── GroundLayer (TileMapLayer)       # z_index = 0: 床タイル（コリジョンなし）
├── WallLayer (TileMapLayer)         # z_index = 1: 壁タイル（PhysicsLayer0 コリジョンあり）
├── PropsLayer (TileMapLayer)        # z_index = 2: 樽、松明、障害物（一部コリジョンあり）
├── Entities (Node2D)                # z_index = 3: y_sort 有効化（プレイヤー、敵）
│   ├── Player (CharacterBody2D)
│   └── SpawnPoint (Marker2D)
└── ForegroundLayer (TileMapLayer)   # z_index = 4: 屋根、梁、暗がり
```

---

## 2. 物理コリジョン（Physics Layers）設定

1. `TileSet` リソースのインスペクターで `Physics Layers` を追加（Layer 0: `World`）。
2. 壁タイルのコリジョン形状（Collision Polygon）を設定：
   - 壁の上面ではなく、**壁の前面（足元との接地面）のみにコリジョンを設定**することで、プレイヤーの頭部が壁の上に少し重なり、自然なトップダウンの奥行きが表現されます。

---

## 3. ナビゲーション（Navigation Layers）

敵キャラクターのAI巡回や経路探索（Pathfinding）を行う場合：
1. `TileSet` の `Navigation Layers` を追加。
2. 床タイルのナビゲーションポリゴン（Navigation Polygon）を有効化。
3. `NavigationRegion2D` または `TileMapLayer` から自動ベイクされた経路を利用可能。

