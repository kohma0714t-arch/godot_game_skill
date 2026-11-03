"""
Blender 5.x Python Asset Generation Templates
Godot 4.x 向けのコリジョンサフィックス付き3Dモデル生成スクリプト
"""

import bpy
import os
import math

def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def create_mat(name, color_rgba, roughness=0.6, metallic=0.0, emission_rgba=None):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color_rgba
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
        if emission_rgba:
            bsdf.inputs["Emission Color"].default_value = emission_rgba
            bsdf.inputs["Emission Strength"].default_value = 1.0
    return mat

def build_lowpoly_tree(filepath):
    clear_scene()
    wood_mat = create_mat("WoodMat", (0.45, 0.28, 0.15, 1.0), roughness=0.8)
    leaf_mat = create_mat("LeafMat", (0.22, 0.65, 0.32, 1.0), roughness=0.6)

    # 幹 (Trunk) - 底面原点
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.25, depth=1.5, location=(0, 0, 0.75))
    trunk = bpy.context.active_object
    trunk.name = "TreeTrunk"
    trunk.data.materials.append(wood_mat)

    # 葉 (Leaves) - 3段のコーン
    for i, z_pos in enumerate([1.6, 2.2, 2.7]):
        scale = 1.0 - (i * 0.2)
        bpy.ops.mesh.primitive_cone_add(vertices=7, radius1=1.0 * scale, depth=1.2 * scale, location=(0, 0, z_pos))
        foliage = bpy.context.active_object
        foliage.name = f"Leaves_{i}"
        foliage.data.materials.append(leaf_mat)

    # 当たり判定（幹部分にコリジョン）
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.3, depth=1.5, location=(0, 0, 0.75))
    col = bpy.context.active_object
    col.name = "TreeCol-colonly"

    bpy.ops.wm.save_as_mainfile(filepath=filepath)
    print(f"Tree saved to {filepath}")

def build_lowpoly_rock(filepath):
    clear_scene()
    rock_mat = create_mat("RockMat", (0.4, 0.42, 0.48, 1.0), roughness=0.9)

    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.9, location=(0, 0, 0.7))
    rock = bpy.context.active_object
    rock.name = "RockMesh-convcol" # 凸型コリジョン自動生成
    rock.scale = (1.2, 0.9, 0.8)
    bpy.ops.object.transform_apply(scale=True)
    rock.data.materials.append(rock_mat)

    bpy.ops.wm.save_as_mainfile(filepath=filepath)
    print(f"Rock saved to {filepath}")

