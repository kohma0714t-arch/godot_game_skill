# Godot 4.x 3D Audio & VFX Manager テンプレート
extends Node
class_name AudioVFXManager3D

@onready var bgm_player: AudioStreamPlayer = AudioStreamPlayer.new()

func _ready() -> void:
	add_child(bgm_player)
	bgm_player.bus = "Music"

func play_bgm(stream: AudioStream) -> void:
	if stream and bgm_player.stream != stream:
		bgm_player.stream = stream
		bgm_player.play()

func play_sfx_3d(stream: AudioStream, global_pos: Vector3, parent: Node) -> void:
	if not stream or not parent:
		return
	var player: AudioStreamPlayer3D = AudioStreamPlayer3D.new()
	player.stream = stream
	player.bus = "SFX"
	player.global_position = global_pos
	parent.add_child(player)
	player.play()
	player.finished.connect(player.queue_free)

func spawn_vfx_3d(vfx_scene: PackedScene, global_pos: Vector3, parent: Node) -> void:
	if not vfx_scene or not parent:
		return
	var vfx: GPUParticles3D = vfx_scene.instantiate() as GPUParticles3D
	if vfx:
		vfx.global_position = global_pos
		parent.add_child(vfx)
		vfx.emitting = true
		vfx.finished.connect(vfx.queue_free)

