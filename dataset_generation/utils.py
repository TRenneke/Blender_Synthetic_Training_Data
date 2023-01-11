import bpy
import mathutils
import yaml
import random
import colorsys
from typing import Union
class SetLocation():
    def __init__(self, val) -> None:
        self.val = val
    def __call__(self, obj: bpy.types.Object):
        obj.location = self.val()
class SetRotation(): 
    def __init__(self, val) -> None:
        self.val = val
    def __call__(self, obj: bpy.types.Object):
        obj.rotation_euler = self.val()
class SetScale():
    def __init__(self, val) -> None:
        self.val = val
    def setScale(obj: bpy.types.Object, val):
        obj.scale = val()
class SetColor():
    def setColor(obj: bpy.types.Object, val):
        obj.color = val.sample()
    def setMaterial(obj: bpy.types.Object, val):
        obj.active_material = val.sample()
# Placeholder class for code auto completion only 
class Sampler:
    def __init__(self) -> None:
        pass
    def __call__():
        pass
class ChoiceSampler:
    def __init__(self, values: list) -> None:
        self.values = values
    def __call__(self):
        return random.choice(self.values())() 

class ValueSampler:
    def __init__(self, value: Sampler):
        self.value = value
    def __call__(self):
        if isinstance(self.value, list):
            return [x() for x in self.value]
        if isinstance(self.value, tuple):
            return tuple(x() for x in self.value)        
        return self.value
class HSVSampler:
    def __init__(self, h, s, v) -> None:
        self.color = colorsys.hsv_to_rgb(h, s, v)
    def __call__(self):
        return self.color
class UniformSampler:
    def __init__(self, min: Union[Sampler, tuple[Sampler]], max):
        self.min = min
        self.max = max
    def __call__(self):
        _min = self.min()
        _max = self.max()
        if isinstance(_min, tuple):
            l = min(len(_min), len(_max))
            result = tuple(random.uniform(_min[i], _max[i]) for i in range(l))
            return result
        else:
            return random.uniform(_min, _max)
def float_parser(val: str) -> float:
    return float(val)
def int_parser(val: str) -> int:
    return int(val)
def str_parser(val: str) -> str:
    return val
def file_parser(val: str) -> Union[str, list] :
    return val
def material_parser(val: str) -> bpy.types.Material:
    return bpy.data.materials[val]

def mat2list(mat: mathutils.Matrix) -> list[list[float]]:
    """Converts mathutils.Matrix to list[list[float]]

    Args:
        mat (mathutils.Matrix): Matrix to convert

    Returns:
        list[list[float]]: Matrix in list form
    """
    return [list(row) for row in list(mat)]
def get_objs(objects: list[bpy.types.Object],names: Sampler) -> list[bpy.types.Object]:
    """Get all objects listed, only compares the name until the first point so ["Cube"] will also return objects named ["Cube.001", "Cube.l", "Cube.x.y.z"]

    Args:
        names (list[str]): names of the objects to get

    Returns:
        list[bpy.types.Object]: !
    """
    s = names()
    if not isinstance(s, list):
        s = [s]
    return [obj for obj in bpy.data.objects.values() if obj.name.split(".")[0] in s]

obj_properties = {"location": (float_parser, setLocation), 
                  "roation": (float_parser, setRotation), 
                  "scale": (float_parser, setScale),
                  "color": (float_parser, setColor),
                  "material": (material_parser, setMaterial)}
obj_selectors = {"name": (str_parser, get_objs)}


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

def sampler_from_string(s: str, parser) -> Sampler:
    # Check if the string starts with a class name
    if s[0].isupper() and "(" in s:
        # Split the string into two parts: the name of the class and the list of values
        class_name, values_string = s.split("(", 1)
        class_name = class_name.strip()
        values_string = values_string[:-1]
        values = (sampler_from_string(x.strip(), parser) for x in  split_string(values_string))
        
        # Get the class object using its name
        class_object = globals()[class_name + "Sampler"]

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
        return ValueSampler(value)
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
    def __init__(self, exec, select, subGroup) -> None:
        self.exec = exec
        self.select = select
        self.subGroups = subGroup
    def __call__(self, objs) -> list[bpy.types.Object]:
        os = []
        for selector in self.select
        pass
#def runGroup(group: (, list)):
#    for item in group:
#        item[0](item(1))
def parseObjectGroup(group: dict) -> list(tuple(function, Sampler)):
    result_exec = []
    result_select = []
    result_subgroups = []
    for k, v in group.items():
        if k == "type":
            break
        if k in obj_properties:
            parser, fn = obj_properties[k]
            result_exec.append((fn, sampler_from_string(v, parser)))
            break
        if k in obj_selectors:
            parser, fn = obj_selectors[k]
            result_select.append
        if isinstance(v, dict):
            result_exec.append(parseObjectGroup(v))
            break
        else:
            print(f"unknown Property: {k}")
            break
        

groups = {"Object": parseObjectGroup}
def parse_group(group: dict):
    groups[group["type"]](group)
    
#def parseYaml(file_name: str):
#    with open(file_name, "r") as file:
#        yaml_data: dict = yaml.safe_load(file)
#        if isinstance(yaml_data, dict):
#            for ykey in yaml_data.keys():

if __name__ == "__main__":
    with open("example.yaml", "r") as file:
        y = yaml.safe_load(file)
        print(y)
