# Godot 4.x 2D Audio & VFX Manager テンプレート
extends Node
class_name AudioVFXManager2D

# BGM & SE プレイヤー
@onready var bgm_player: AudioStreamPlayer = AudioStreamPlayer.new()
@onready var sfx_players: Array[AudioStreamPlayer] = []

const MAX_SFX_CHANNELS: int = 8

func _ready() -> void:
	add_child(bgm_player)
	bgm_player.bus = "Music"
	
	for i in range(MAX_SFX_CHANNELS):
		var p: AudioStreamPlayer = AudioStreamPlayer.new()
		p.bus = "SFX"
		add_child(p)
		sfx_players.append(p)

func play_sfx(stream: AudioStream, pitch_variance: float = 0.05) -> void:
	if not stream:
		return
	for p in sfx_players:
		if not p.playing:
			p.stream = stream
			p.pitch_scale = randf_range(1.0 - pitch_variance, 1.0 + pitch_variance)
			p.play()
			return

func play_bgm(stream: AudioStream, fade_duration: float = 0.5) -> void:
	if not stream or bgm_player.stream == stream:
		return
	var tween: Tween = create_tween()
	tween.tween_property(bgm_player, "volume_db", -40.0, fade_duration)
	tween.tween_callback(func():
		bgm_player.stream = stream
		bgm_player.volume_db = 0.0
		bgm_player.play()
	)

func spawn_particle(particle_scene: PackedScene, pos: Vector2, parent: Node2D) -> void:
	if not particle_scene or not parent:
		return
	var p: CPUParticles2D = particle_scene.instantiate() as CPUParticles2D
	if p:
		p.global_position = pos
		parent.add_child(p)
		p.emitting = true
		p.finished.connect(p.queue_free)

