if "bpy" in locals():
    import importlib
    importlib.reload(sdg_sampler)
    importlib.reload(yaml)
else:
    from . import sdg_sampler
    from . import yaml
import bpy
import logging
import functools
import os
from typing import Union


def file_parser(val: str) -> Union[str, list] :
    return val
def material_parser(val: str) -> bpy.types.Material:
    return bpy.data.materials[val]
def bool_parser(val: str):
    return val.lower() == "true"
class SetValue():
    def __init__(self, attr: str, val: sdg_sampler.Sampler) -> None:
        self.attr = attr
        self.val = val
    def __call__(self, obj: list[bpy.types.Object]) -> None:
        s = self.val()
        for o in obj:
            setattr(o, self.attr, s)
    def setValFactory(attr):
        return functools.partial(SetValue, attr)
class SetDataValue():
    def __init__(self, attr: str, data_class,  val: sdg_sampler.Sampler) -> None:
        self.attr = attr
        self.data_class = data_class
        self.val = val
    def __call__(self, obj: list[bpy.types.Object]) -> None:
        s = self.val()
        for o in obj:
            if not isinstance(o.data, self.data_class):
                print(f"Object data of tpye {type(obj)} is not instance of {self.data_class}")
            setattr(o.data, self.attr, s)
    def setDataValFactory(attr, data_class):
        return functools.partial(SetDataValue, attr, data_class)

#class SetImgPath():
#    def __init__(self, val: sdg_sampler.Sampler) -> None:
#        self.val = val
#    def __call__(self, obj: bpy.types.Image) -> None:
#        s = self.val()
#        if not isinstance(obj, list):
#            obj.filepath = s
#            obj.reload()
#            return
#        for o in obj:
#            if not isinstance(o, list):
#                o.filepath = s
#                o.reload()
#            else:
#                self.__call__(o)
class SetVisible():
    def __init__(self, val: sdg_sampler.Sampler) -> None:
        self.val = val
    def __call__(self, obj: list[bpy.types.Object]) -> None:
        s = self.val()
        for o in obj:
            o.hide_render = not s
            o.hide_viewport = not s
            
class SetCustomProperty():
    def __init__(self, attr: str, val: sdg_sampler.Sampler) -> None:
        self.attr = attr
        self.val = val
    def __call__(self, obj: list[bpy.types.Object]) -> None:
        s = self.val()
        for o in obj:
                o[self.attr] = s
            
def aplyVelocity(val, vel):
        return tuple([x + y for x, y in zip(val, vel)])
    
class SetVelocity():
    def __init__(self, attr: str, val: sdg_sampler.Sampler) -> None:
        self.attr = attr
        self.val = val
    def setVel(self, velocity, obj: bpy.types.Object):
        cur_val = getattr(obj, self.attr)
        offset_val = aplyVelocity(cur_val, velocity)
        
        obj.keyframe_insert(data_path=self.attr, frame=bpy.context.scene.frame_current)
        
        setattr(obj, self.attr, offset_val)
        obj.keyframe_insert(data_path=self.attr, frame=bpy.context.scene.frame_current+1)

        
    def __call__(self, obj: bpy.types.Object) -> None:
        s = self.val()
        if not isinstance(obj, list):
            self.setVel(s, obj)
            return
        for o in obj:
            if not isinstance(o, list):
                self.setVel(s, o)
            else:
                self.__call__(o)
    def setVelFactory(attr):
        return functools.partial(SetVelocity, attr)       
    

obj_properties = {"location": (float, SetValue.setValFactory("location")),
                  "rotation": (float, SetValue.setValFactory("rotation_euler")),
                  "scale": (float, SetValue.setValFactory("scale")),
                  "delta_location": (float, SetValue.setValFactory("delta_location")),
                  "delta_rotation": (float, SetValue.setValFactory("delta_rotation_euler")),
                  "delta_scale": (float, SetValue.setValFactory("delta_scale")),
                  
                  "color": (float, SetValue.setValFactory("color")),
                  "material": (material_parser, SetValue.setValFactory("active_material")),
                  "velocity": (float, SetVelocity.setVelFactory("location")),
                  "visible": (bool_parser, SetVisible)}

light_properties = {"energy": (float, SetValue.setValFactory("energy")),
                    "color": (float, SetValue.setValFactory("color"))}
image_properties = {"path": (str, SetValue.setValFactory("filepath"))}
camera_properties = {"lens": (float, SetValue.setValFactory("lens"))}

material_properties = {}
scene_properties = {}
collection_properties = {"visible": (bool_parser, SetVisible)}
object_types = {"objects": obj_properties, "images": image_properties, "materials": material_properties, "scenes": scene_properties, "lights": light_properties, "cameras": camera_properties, "collections": collection_properties}

def split_string(s):
    result = []
    start = 0
    open_brackets = 0
    for i, c in enumerate(s):
        if c in ("(", "["):
            open_brackets += 1
        elif c in (")", "]"):
            open_brackets -= 1
        elif c == "," and open_brackets == 0:
            result.append(s[start:i])
            start = i + 1
    result.append(s[start:])
    return result

def sampler_from_string(s: str, parser) -> sdg_sampler.Sampler:
    # Check if the string starts with a class name
    if not isinstance(s, str):
        s = str(s)
    if s[0].isupper() and "(" in s:
        # Split the string into two parts: the name of the class and the list of values
        class_name, values_string = s.split("(", 1)
        class_name = class_name.strip()
        values_string = values_string[:-1]
        
        # Get the class object using its name
        class_object: sdg_sampler.Sampler = sdg_sampler.Samplers[class_name + "Sampler"]
        values = (sampler_from_string(x.strip(), class_object.getParser(i, parser)) for i, x in  enumerate(split_string(values_string)) if len(x.strip()) > 0)
        # Create and return an instance of the class, passing in the values
        return class_object(*values)
    else:
        # Check if the value is a tuple
        if s[0] == "(":
            assert s[-1] == ")"
            # Extract the value as a tuple of object_from_string
            value = tuple(sampler_from_string(x.strip().strip('"\''), parser) for x in split_string(s[1:-1]))
        elif s[0] == "[":
            assert s[-1] == "]"
            value = [sampler_from_string(x, parser) for x in unpack_assets(split_string(s[1:-1]))]
        elif s.endswith(".txt"):
            value = [sampler_from_string(x, parser) for x in unpack_assets([s])]
        else:
            value = parser(s)
        # Create and return an instance of the ValueSample class, passing in the value
        return sdg_sampler.ValueSampler(value)
def unpack_assets(vals: list[str]):
    r = []
    for val in vals:
        val = val.strip().strip('"\'')
        if val.endswith(".txt"):
            r = r + read_txt_file(val)
        else:
            r.append(val)
    return r

def read_txt_file(file_name):
    with open(file_name, "r") as file:
        lines = file.readlines()
    lines: list[str] = [line.strip() for line in lines]
    r = []
    for line in lines:
        if line.endswith(os.path.sep):
            r = r + [os.path.abspath(os.path.join(line, x)) for x in os.listdir(line)]
        else:
            r.append(line)
    return r
def parseNames(values: list[str]):
    for val in values:
        if val.endswith(".txt"):
            return
    return

class ObjectGroup():
    def __init__(self, exec, select, subGroup, t, includes) -> None:
        self.exec = exec
        self.select = select
        self.subGroups = subGroup
        self.objects = None
        self.type = t
        self.includes = includes
    
    def include_group(self, group):
        self.exec += group.exec
    def from_dict(group: dict, customPropertys, t = None):
        result_exec = []
        result_select = []
        result_subgroups = []
        #object_type = None
        actions = {}
        object_type = t
        includes = sdg_sampler.ValueSampler([])

        for ot, a in object_types.items():
            if ot in group:
                actions = a
                object_type = ot
                result_select.append(sampler_from_string(group[ot], str))
        for k, v in group.items():
            logging.debug(f"Processing property: {k}")
            if k in actions:
                parser, action = actions[k]
                result_exec.append(action(sampler_from_string(v, parser)))
                continue
            elif k in customPropertys and object_type == "objects":
                parser = customPropertys[k]
                action = SetCustomProperty(k, sampler_from_string(v, parser))
                result_exec.append(action)
                continue
            if k in object_types:
                continue
            if isinstance(v, dict):
                result_subgroups.append(ObjectGroup.from_dict(v, customPropertys, object_type))
                continue
            if k == "includes":
                includes = sampler_from_string(v, str)                
            else:
                print(f"unknown Property: {k}")
                continue
        return ObjectGroup(result_exec, result_select, result_subgroups, object_type, includes)
    def __call__(self, objects = None) -> list[bpy.types.Object]:
        if objects is None:
            objects = self.getBaseDict()
        self.objects = self.getObjects(objects)
        for ex in self.exec:
            for obj in self.objects:
                ex(obj)
        for sg in self.subGroups:
            sg(self.objects)
    def getObjects(self, objects):
        objs = []
        for selector in self.select:
            objs = selector(objects)
        return objs
    def getBaseDict(self):
        if self.type == "objects":
            return [bpy.data.objects.values()]
        if self.type == "images":
            return [bpy.data.images.values()]
        if self.type == "materials":
            return [bpy.data.materials.values()]
        if self.type == "cameras":
            return [bpy.data.cameras.values()]
        if self.type == "lights":
            return [bpy.data.lights.values()]
        if self.type == "collections":
            return [bpy.data.collections.values()]
        

def flatten(S):
    if S == []:
        return S
    if isinstance(S[0], list):
        return flatten(S[0]) + flatten(S[1:])
    return S[:1] + flatten(S[1:])
data_type_map = {"str": str, "int": int, "float": float, "bool": bool}
class Randomization():
    def __init__(self, groups: dict[str, ObjectGroup], customPropertys = None) -> None:
        self.groups = groups
        self.customPropertys = customPropertys
    def from_file(file: str):
        r = {}
        print(f"Loading file: {file}!")
        with open(file, "r") as f:
            data: dict = yaml.safe_load(f)
            cp = None
            if "CustomPropertys" in data:
                cp = data["CustomPropertys"]
                for k,v in cp.items():
                    cp[k] = data_type_map[v]
            for k, v in data.items():
                if k == "CustomPropertys":      
                    continue
                r[k] = ObjectGroup.from_dict(v, cp)
            for k, v in r.items():
                for icl in v.includes():
                    v.include_group(r[icl])
        return Randomization(r)
    def __call__(self, objects) -> list[bpy.types.Object]:
        for k, v in self.groups.items():
            v(objects)
