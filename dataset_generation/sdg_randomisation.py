if "bpy" in locals():
    import importlib
    importlib.reload(sdg_sampler)
else:
    from . import sdg_sampler

import bpy
import mathutils
import yaml
import logging
import sys
import functools
from typing import Union

def file_parser(val: str) -> Union[str, list] :
    return val
def material_parser(val: str) -> bpy.types.Material:
    return bpy.data.materials[val]
class SetValue():
    def __init__(self, attr: str, val: sdg_sampler.Sampler) -> None:
        self.attr = attr
        self.val = val
    def __call__(self, obj: bpy.types.Object) -> None:
        s = self.val()
        if not isinstance(obj, list):
            setattr(obj, self.attr, s)
            return
        for o in obj:
            if not isinstance(o, list):
                setattr(o, self.attr, s)
            else:
                self.__call__(o)
    def setValFactory(attr):
        return functools.partial(SetValue, attr)
class SetDataValue():
    def __init__(self, attr: str, val: sdg_sampler.Sampler) -> None:
        self.attr = attr
        self.val = val
    def __call__(self, obj: bpy.types.Object) -> None:
        s = self.val()
        if not isinstance(obj, list):
            setattr(obj.data, self.attr, s)
            return
        for o in obj:
            if not isinstance(o, list):
                setattr(o.data, self.attr, s)
            else:
                self.__call__(o)
    def setDataValFactory(attr):
        return functools.partial(SetDataValue, attr)

class SetImgPath():
    def __init__(self, val: sdg_sampler.Sampler) -> None:
        self.val = val
    def __call__(self, obj: bpy.types.Image) -> None:
        s = self.val()
        if not isinstance(obj, list):
            obj.filepath = s
            obj.reload()
            return
        for o in obj:
            if not isinstance(o, list):
                o.filepath = s
                o.reload()
            else:
                self.__call__(o)
class SetVisible():
    def __init__(self, val: sdg_sampler.Sampler) -> None:
        self.val = val
    def __call__(self, obj: bpy.types.Object) -> None:
        s = self.val()
        if not isinstance(obj, list):
            obj.hide_render = not s
            obj.hide_viewport = not s
            return
        for o in obj:
            if not isinstance(o, list):
                o.hide_render = not s
                o.hide_viewport = not s
            else:
                self.__call__(o)

class SetCustomProperty():
    def __init__(self, attr: str, val: sdg_sampler.Sampler) -> None:
        self.attr = attr
        self.val = val
    def __call__(self, obj: bpy.types.Object) -> None:
        s = self.val()
        if not isinstance(obj, list):
            obj[self.attr] = s
            return
        for o in obj:
            if not isinstance(o, list):
                o[self.attr] = s
            else:
                self.__call__(o)

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
                  "color": (float, SetValue.setValFactory("color")),
                  "material": (material_parser, SetValue.setValFactory("active_material")),
                  "velocity": (float, SetVelocity.setVelFactory("location")),
                  "visible": (bool, SetVisible),
                  "energy": (float, SetDataValue.setDataValFactory("energy")),
                  "light_color": (float, SetDataValue.setDataValFactory("color"))}
image_properties = {"path": (str, SetImgPath)}
material_properties = {}
scene_properties = {}
object_types = {"objects": obj_properties, "images": image_properties, "materials": material_properties, "scenes": scene_properties}

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
        return sdg_sampler.ValueSampler(s)
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
            # Extract the value as a tuple of object_from_string
            value = tuple(sampler_from_string(x.strip(), parser) for x in split_string(s[1:-1]))
        elif s[0] == "[":
            value = [sampler_from_string(x.strip(), parser) for x in split_string(s[1:-1])]
        else:
            # Extract the value as a float
            value = parser(s)

        # Create and return an instance of the ValueSample class, passing in the value
        return sdg_sampler.ValueSampler(value)
def read_txt_file(file_name):
  with open(file_name, "r") as file:
    lines = file.readlines()
  lines = [line.strip() for line in lines]

  return lines
def parseNames(values: list[str]):
    for val in values:
        if val.endswith(".txt"):
            return
    return

class ObjectGroup():
    def __init__(self, exec, select, subGroup, t) -> None:
        self.exec = exec
        self.select = select
        self.subGroups = subGroup
        self.objects = None
        self.type = t
    def from_dict(group: dict, customPropertys, t = None):
        result_exec = []
        result_select = []
        result_subgroups = []
        #object_type = None
        actions = {}
        object_type = None
        for ot, a in object_types.items():
            if ot in group:
                actions = a
                object_type = ot
                result_select.append(sampler_from_string(group[ot], str))
        if t != None and object_type != t:
            print(f"Subgroup object type is: {object_type} which is unequal to main group object type: {t}")
            assert False
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
                #result_select.append(sampler_from_string(v, str))
                continue
            if isinstance(v, dict):
                result_exec.append(ObjectGroup.from_dict(v, customPropertys, object_type))
                continue
            else:
                print(f"unknown Property: {k}")
                continue
        return ObjectGroup(result_exec, result_select, result_subgroups, object_type)
    def __call__(self, objects = None) -> list[bpy.types.Object]:
        if objects is None:
            objects = self.getBaseDict()
        self.objects = self.getObjects(objects)
        if self.type == "images":
            print(self.objects)
        for ex in self.exec:
            for obj in self.objects:
                ex(obj)
        for sg in self.subGroups:
            sg(self.objects)
    def getObjects(self, objects):
        objs = []
        for selector in self.select:
            objs = objs + selector(objects)
        return objs
    def getBaseDict(self):
        if self.type == "objects":
            return bpy.data.objects.values()
        if self.type == "images":
            return bpy.data.images.values()
        if self.type == "materials":
            return bpy.data.materials.values()
        

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
        return Randomization(r)   
    def __call__(self, objects) -> list[bpy.types.Object]:
        for k, v in self.groups.items():
            print(f"Running group: {k}")
            v(objects)
