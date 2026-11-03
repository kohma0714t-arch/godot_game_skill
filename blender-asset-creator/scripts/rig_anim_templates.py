"""
Blender 5.x Simple Rigging & Animation Template
Godot 4.x 向けのアニメーション付き.blendモデル生成
"""

import bpy

def setup_simple_rotation_anim(obj, anim_name="RotateLoop", frames=60):
    """オブジェクトに360度ループ回転キーフレームを付与"""
    obj.animation_data_create()
    action = bpy.data.actions.new(name=anim_name)
    obj.animation_data.action = action

    obj.rotation_euler = (0, 0, 0)
    obj.keyframe_insert(data_path="rotation_euler", frame=1)

    obj.rotation_euler = (0, 0, 6.28318) # 2 * PI
    obj.keyframe_insert(data_path="rotation_euler", frame=frames)

    # リニア補間設定
    for fcurve in action.fcurves:
        for kf in fcurve.keyframe_points:
            kf.interpolation = 'LINEAR'

