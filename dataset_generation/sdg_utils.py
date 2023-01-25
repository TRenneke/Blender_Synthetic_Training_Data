import bpy
import mathutils
import yaml
import logging
from typing import Union
from functools import partial



import json
import os

def mat2list(mat: mathutils.Matrix) -> list[list[float]]:
    return [list(row) for row in list(mat)]
def setup_compositing(dataset: str, scene: bpy.types.Scene):
    #enable crypto mattes
    bpy.context.scene.view_layers["ViewLayer"].use_pass_cryptomatte_object = True
    bpy.context.scene.view_layers["ViewLayer"].pass_cryptomatte_depth = 2

    
    if not "Render Layers" in scene.node_tree.nodes:
        rl = scene.node_tree.nodes.new("CompositorNodeRLayers")
        rl.name = "Render Layers"
    else:
        rl = scene.node_tree.nodes["Render Layers"]
    
    co_node: bpy.types.CompositorNodeOutputFile
    if not "CryptoOutput" in scene.node_tree.nodes:
        co_node = scene.node_tree.nodes.new("CompositorNodeOutputFile")
        co_node.name = "CryptoOutput"
    else:
        co_node = scene.node_tree.nodes["CryptoOutput"]
    
    co_node.base_path = os.path.join(dataset, "crypto")
    co_node.format.file_format = 'OPEN_EXR'
    
    co_node.file_slots[0].path = os.path.sep

    crypto_output = None
    for o in rl.outputs:
        if o.name == "CryptoObject00":
             crypto_output = o
             break

    scene.node_tree.links.new(crypto_output, co_node.inputs[0])
#    scene.node_tree.links.new(rl.outputs[0], io_node.inputs[0])

def save_annotations(frame_id: int, objs: bpy.types.Object, dataset: str):
    json_path = os.path.join(dataset, "anns", "{:04d}".format(frame_id) + ".json")  
    with open(json_path, "w+") as jf:
        jf.write(json.dumps(generate_annotations(objs)))
    print("Saved:", json_path)
def generate_cam_annotation(camera: bpy.types.Object) -> dict:
    """Generates the annotation data for a camera

    Args:
        camera (bpy.types.Object): The camera to get the annotation for

    Returns:
        dict: a dict containing the world to camera Matrix (K), projektion Matrix (P), position (pos) and rotation (rot) (as a quaternion)   
    """
    K = camera.matrix_world.inverted()
    P = camera.calc_matrix_camera(bpy.context.evaluated_depsgraph_get())
    return {"K": mat2list(K), "P": mat2list(P), "pos": list(camera.location), "rot": list(camera.rotation_quaternion), "name": camera.name}
def generate_obj_annotation(obj: bpy.types.Object, custom_propertys: list[str] = ["category_id"]):
    """Generates annotation data for a generic object

    Args:
        obj (bpy.types.Object): _description_
        custom_propertys
    Returns:
        dict: A dict containing the local to world Matrix (M), position (pos) and rotation (rot) (as a quaternion), scale (scale), name (name), parent's name (parent), [category_id (category_id)]
        category_id is added if it's a custom property of the object
    """
    d = {"M": mat2list(obj.matrix_world), "pos": list(obj.location), "rot": list(obj.rotation_quaternion), "scale": list(obj.scale), "name": obj.name, "name_full": obj.name_full}
    if not (obj.parent is None):
        d["parent"] = obj.parent.name
    for c_prop in custom_propertys:
        if c_prop in obj:
            d[c_prop] = obj[c_prop]
    return d
def generate_annotations(objs: list[bpy.types.Object]) -> dict:
    """_summary_

    Args:
        objs (bpy.types.Object): The objects to generate the annortation for.

    Returns:
        dict: returns a dict of objects (objects) and cameras (cameras) for the given objects containing a list of annotation dicts for each object
    """
    r = {"objects": [], "cameras": []}
    for obj in objs:
        if obj.type == "CAMERA":
            r["cameras"].append(generate_cam_annotation(obj))
        else:
            r["objects"].append(generate_obj_annotation(obj))
    return r
def getAppendType(str):
    if str == "Object":
        return bpy.data.objects
    if str == "Material":
        return bpy.data.materials
    if str == "Collection":
        return bpy.data.collections
def getFreeName(objects: dict, name: str):
    i = 0
    n = name
    while n in objects:
        i += 1
        n = name + ".{:0>3}".format(i)
    return n

def append_object(filepath: str):
    p, obj_name = os.path.split(filepath)
    p, obj_type = os.path.split(p)
    assert p.endswith(".blend")
    # Append the object from the file
    name = getFreeName(getAppendType(obj_type), obj_name)
    with bpy.data.libraries.load(p) as (data_from, data_to):
        if obj_type == "Object":
            data_to.objects = [obj_name]
        if obj_type == "Material":
            data_to.materials = [obj_name]
        if obj_type == "Collection":
            data_to.collections = [obj_name]
    if obj_type == "Object":
        obj = data_to.objects[0]
        bpy.context.scene.collection.objects.link(obj)
    if obj_type == "Material":
        return data_to.materials[0]
    if obj_type == "Collection":
        obj = data_to.collections[0]
        bpy.context.scene.collection.children.link(obj)
        return obj
    return None