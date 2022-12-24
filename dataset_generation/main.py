import sys
sys.path.append("D:\\Programmieren\\Blender_Synthetic_Training_Data")
import bpy
import dataset_generation.utils as utils
import mathutils
import yaml

import os
import json
def render(frame_id: int):
    """Renders the frame_id'th frame 

    Args:
        frame_id (int): the frame_id'th frame to render
    """
    bpy.context.scene.frame_set(frame_id)
    bpy.ops.render.render()

def setup_compositing(dataset: str, scene: str = "Scene"):
    #enable crypto mattes
    bpy.context.scene.view_layers["ViewLayer"].use_pass_cryptomatte_object = True
    bpy.context.scene.view_layers["ViewLayer"].pass_cryptomatte_depth = 2

    
    if not "Render Layers" in bpy.data.scenes[scene].node_tree.nodes:
        rl = bpy.data.scenes[scene].node_tree.nodes.new("CompositorNodeRLayers")
        rl.name = "Render Layers"
    else:
        rl = bpy.data.scenes[scene].node_tree.nodes["Render Layers"]

    if not "ImageOutput" in bpy.data.scenes[scene].node_tree.nodes:
        io_node = bpy.data.scenes[scene].node_tree.nodes.new("CompositorNodeOutputFile")
        io_node.name = "ImageOutput"
    else:
        io_node = bpy.data.scenes[scene].node_tree.nodes["ImageOutput"]
    io_node.base_path = os.path.join(dataset, "imgs")
    
    
    if not "CryptoOutput" in bpy.data.scenes[scene].node_tree.nodes:
        co_node = bpy.data.scenes[scene].node_tree.nodes.new("CompositorNodeOutputFile")
        co_node.name = "CryptoOutput"
    else:
        co_node = bpy.data.scenes[scene].node_tree.nodes["CryptoOutput"]
    
    co_node.base_path = os.path.join(dataset, "crypto")
    co_node.format.file_format = 'OPEN_EXR'

    bpy.data.scenes[scene].node_tree.links.new(rl.outputs[2], co_node.inputs[0])
    bpy.data.scenes[scene].node_tree.links.new(rl.outputs[0], io_node.inputs[0])

def render_annotated(frame_id: int, objs: bpy.types.Object, dataset: str, scene: str = "Scene"):
    
    json_path = dataset + "/anns/" + "Image" + "{:04d}".format(frame_id) + ".json"
    render(frame_id)
    with open(json_path, "w+") as jf:
        jf.write(json.dumps(generate_annotations(objs)))
def generate_cam_annotation(camera: bpy.types.Object) -> dict:
    """Generates the annotation data for a camera

    Args:
        camera (bpy.types.Object): The camera to get the annotation for

    Returns:
        dict: a dict containing the world to camera Matrix (K), projektion Matrix (P), position (pos) and rotation (rot) (as a quaternion)   
    """
    K = camera.matrix_world.inverted()
    P = camera.calc_matrix_camera(bpy.context.evaluated_depsgraph_get())
    return {"K": utils.mat2list(K), "P": utils.mat2list(P), "pos": list(camera.location), "rot": list(camera.rotation_quaternion), "name": camera.name}
def generate_obj_annotation(obj: bpy.types.Object, custom_propertys: list[str] = ["category_id"]):
    """Generates annotation data for a generic object

    Args:
        obj (bpy.types.Object): _description_
        custom_propertys
    Returns:
        dict: A dict containing the local to world Matrix (M), position (pos) and rotation (rot) (as a quaternion), scale (scale), name (name), parent's name (parent), [category_id (category_id)]
        category_id is added if it's a custom property of the object
    """
    d = {"M": utils.mat2list(obj.matrix_world), "pos": list(obj.location), "rot": list(obj.rotation_quaternion), "scale": list(obj.scale), "name": obj.name, "name_full": obj.name_full}
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


if __name__ == "__main__":
    dataset = "D:\Programmieren\Blender_Synthetic_Training_Data\datasets\example"
    setup_compositing(dataset, "Scene")
    print(utils.get_objs(["Cube", "Camera"]))
    render_annotated(1, utils.get_objs(["Cube", "Camera"]), dataset)
