# Godot 4.x AnimatedSprite2D 実装ガイド

本スキルで出力された `SpriteFrames` リソース（`.tres`）を、Godot 4.x の 2Dキャラクター（`CharacterBody2D`）へ組み込む手順です。

---

## 1. シーン構成 (Scene Hierarchy)

```
Player (CharacterBody2D)
├── AnimatedSprite2D    # SpriteFrames (.tres) をアタッチ
├── CollisionShape2D   # 足元のカプセル/円コリジョン
└── AnimationPlayer    # (任意) より詳細なプロパティ連携用
```

---

## 2. AnimatedSprite2D のインスペクター設定

1. `AnimatedSprite2D` の `Sprite Frames` プロパティに、出力された `[char]_frames.tres` をドラッグ＆ドロップ。
2. `Texture Filter`: `Nearest` に設定（ドット絵のボケ防止）。

---

## 3. 4方向ステートマシン切り替えスクリプト例 (GDScript)

```gdscript
extends CharacterBody2D

@onready var animated_sprite = $AnimatedSprite2D
var current_dir = "down"
var current_state = "idle"

func _physics_process(delta):
    var input_vector = Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
    
    # 方向の更新
    if input_vector.x > 0:
        current_dir = "right"
    elif input_vector.x < 0:
        current_dir = "left"
    elif input_vector.y > 0:
        current_dir = "down"
    elif input_vector.y < 0:
        current_dir = "up"
        
    # ステート判定
    if Input.is_action_just_pressed("attack"):
        current_state = "attack_light"
    elif input_vector != Vector2.ZERO:
        current_state = "dash" if Input.is_action_pressed("dash") else "walk"
    else:
        current_state = "idle"
        
    # アニメーション再生（例: walk_down, idle_right, attack_light_up）
    var anim_name = current_state + "_" + current_dir
    if animated_sprite.animation != anim_name:
        animated_sprite.play(anim_name)

    velocity = input_vector * 120.0
    move_and_slide()
```

