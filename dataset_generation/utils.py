import bpy
import mathutils
import yaml
import random
from typing import Union

class Sampler:
    def __init__(self) -> None:
        pass
    def sample():
        pass
class ChoiceSampler:
    def __init__(self, values: list) -> None:
        self.values = values
    def sample(self):
        return random.choice(self.values.sample()).sample() 

class ValueSampler:
    def __init__(self, value: Sampler):
        self.value = value
    def sample(self):
        if isinstance(self.value, list):
            return [x.sample() for x in self.value]
        if isinstance(self.value, tuple):
            return tuple(x.sample() for x in self.value)        
        return self.value
class UniformSampler:
    def __init__(self, min: Union[Sampler, tuple[Sampler]], max):
        self.min = min
        self.max = max
    def sample(self):
        _min = self.min.sample()
        _max = self.max.sample()
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
    return float(val)


def mat2list(mat: mathutils.Matrix) -> list[list[float]]:
    """Converts mathutils.Matrix to list[list[float]]

    Args:
        mat (mathutils.Matrix): Matrix to convert

    Returns:
        list[list[float]]: Matrix in list form
    """
    return [list(row) for row in list(mat)]
def get_objs(names: list[str]) -> list[bpy.types.Object]:
    """Get all objects listed, only compares the name until the first point so ["Cube"] will also return objects named ["Cube.001", "Cube.l", "Cube.x.y.z"]

    Args:
        names (list[str]): names of the objects to get

    Returns:
        list[bpy.types.Object]: !
    """
    return [obj for obj in bpy.data.objects.values() if obj.name.split(".")[0] in names]

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

