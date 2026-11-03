# Godot 4.x 3D キャラクター ステートマシン テンプレート
extends CharacterBody3D
class_name Character3DStateMachine

enum State { IDLE, WALK, JUMP, FALL, ATTACK }

@export var speed: float = 6.0
@export var jump_velocity: float = 7.5
@export var rotation_speed: float = 12.0

var current_state: State = State.IDLE

@onready var visual: Node3D = $Visual

func _physics_process(delta: float) -> void:
	if not is_on_floor():
		velocity += get_gravity() * delta

	match current_state:
		State.IDLE:
			_process_idle(delta)
		State.WALK:
			_process_walk(delta)
		State.JUMP:
			_process_jump(delta)
		State.FALL:
			_process_fall(delta)
		State.ATTACK:
			_process_attack(delta)

	move_and_slide()

func change_state(new_state: State) -> void:
	if current_state == new_state:
		return
	current_state = new_state

func _get_movement_direction() -> Vector3:
	var input: Vector2 = Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
	return Vector3(input.x, 0.0, input.y).normalized()

func _rotate_visual_towards(dir: Vector3, delta: float) -> void:
	if dir != Vector3.ZERO and visual:
		var target_angle: float = atan2(dir.x, dir.z)
		visual.rotation.y = lerp_angle(visual.rotation.y, target_angle, rotation_speed * delta)

func _process_idle(delta: float) -> void:
	velocity.x = move_toward(velocity.x, 0.0, speed * 8.0 * delta)
	velocity.z = move_toward(velocity.z, 0.0, speed * 8.0 * delta)
	
	if Input.is_action_just_pressed("ui_accept") and is_on_floor():
		velocity.y = jump_velocity
		change_state(State.JUMP)
	elif _get_movement_direction() != Vector3.ZERO:
		change_state(State.WALK)

func _process_walk(delta: float) -> void:
	var dir: Vector3 = _get_movement_direction()
	if dir != Vector3.ZERO:
		velocity.x = dir.x * speed
		velocity.z = dir.z * speed
		_rotate_visual_towards(dir, delta)
	else:
		change_state(State.IDLE)

	if Input.is_action_just_pressed("ui_accept") and is_on_floor():
		velocity.y = jump_velocity
		change_state(State.JUMP)
	elif not is_on_floor():
		change_state(State.FALL)

func _process_jump(delta: float) -> void:
	var dir: Vector3 = _get_movement_direction()
	if dir != Vector3.ZERO:
		velocity.x = dir.x * speed
		velocity.z = dir.z * speed
		_rotate_visual_towards(dir, delta)
	if velocity.y <= 0.0:
		change_state(State.FALL)

func _process_fall(delta: float) -> void:
	var dir: Vector3 = _get_movement_direction()
	if dir != Vector3.ZERO:
		velocity.x = dir.x * speed
		velocity.z = dir.z * speed
	if is_on_floor():
		change_state(State.WALK if dir != Vector3.ZERO else State.IDLE)

func _process_attack(delta: float) -> void:
	pass

