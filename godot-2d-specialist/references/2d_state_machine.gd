# Godot 4.x 2D キャラクター ステートマシン テンプレート
extends CharacterBody2D
class_name Character2DStateMachine

enum State { IDLE, RUN, JUMP, FALL, ATTACK, HURT }

@export var speed: float = 280.0
@export var jump_velocity: float = -420.0

var current_state: State = State.IDLE

@onready var sprite: Sprite2D = $Sprite2D

func _physics_process(delta: float) -> void:
	# 重力適用
	if not is_on_floor():
		velocity += get_gravity() * delta

	# 状態遷移と入力処理
	match current_state:
		State.IDLE:
			_process_idle(delta)
		State.RUN:
			_process_run(delta)
		State.JUMP:
			_process_jump(delta)
		State.FALL:
			_process_fall(delta)
		State.ATTACK:
			_process_attack(delta)
		State.HURT:
			_process_hurt(delta)

	move_and_slide()

func change_state(new_state: State) -> void:
	if current_state == new_state:
		return
	current_state = new_state
	# 状態切り替え時の処理（アニメーション変更等）

func _process_idle(delta: float) -> void:
	velocity.x = move_toward(velocity.x, 0.0, speed * 8.0 * delta)
	if Input.is_action_just_pressed("ui_accept") and is_on_floor():
		velocity.y = jump_velocity
		change_state(State.JUMP)
	elif Input.get_axis("ui_left", "ui_right") != 0.0:
		change_state(State.RUN)

func _process_run(delta: float) -> void:
	var dir: float = Input.get_axis("ui_left", "ui_right")
	if dir != 0.0:
		velocity.x = dir * speed
		sprite.flip_h = dir < 0.0
	else:
		change_state(State.IDLE)
	
	if Input.is_action_just_pressed("ui_accept") and is_on_floor():
		velocity.y = jump_velocity
		change_state(State.JUMP)
	elif not is_on_floor():
		change_state(State.FALL)

func _process_jump(delta: float) -> void:
	var dir: float = Input.get_axis("ui_left", "ui_right")
	if dir != 0.0:
		velocity.x = dir * speed
		sprite.flip_h = dir < 0.0
	if velocity.y >= 0.0:
		change_state(State.FALL)

func _process_fall(delta: float) -> void:
	var dir: float = Input.get_axis("ui_left", "ui_right")
	if dir != 0.0:
		velocity.x = dir * speed
	if is_on_floor():
		change_state(State.RUN if dir != 0.0 else State.IDLE)

func _process_attack(delta: float) -> void:
	pass

func _process_hurt(delta: float) -> void:
	pass

