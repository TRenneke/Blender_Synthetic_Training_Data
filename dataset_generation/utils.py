import bpy
import mathutils
import yaml
import random

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

def create_object_from_string(s: str):
    # Check if the string starts with a class name
    if s[0].isupper():
        # Split the string into two parts: the name of the class and the list of values
        class_name, values_string = s.split("(")
        class_name = class_name.strip()
        values_string = values_string[:-1]

        # Check if the values are a tuple
        if values_string[0] == "(":
            # Extract the values as a tuple of floats
            values = tuple(float(x) for x in values_string[1:-1].split(", "))
        else:
            # Extract the values as a list of floats
            values = [float(x) for x in values_string.split(", ")]

        # Get the class object using its name
        class_object = globals()[class_name + "Sampler"]

        # Create and return an instance of the class, passing in the values
        return class_object(*values)
    else:
        # Check if the value is a tuple
        if s[0] == "(":
            # Extract the value as a tuple of floats
            value = tuple(float(x) for x in s[1:-1].split(", "))
        else:
            # Extract the value as a float
            value = float(s.split(" = ")[1])

        # Create and return an instance of the ValueSample class, passing in the value
        return ValueSampler(value)
def parseNames(values: list[str]):
    for val in values:
        if values.endswith(".txt"):
            return
    return

class ValueSampler:
    def __init__(self, value):
        self.value = value
    def sample(self):
        return self.value
class UniformSampler:
    def __init__(self, min, max):
        self.min = min
        self.max = max
    def sample(self):
        if isinstance(self.min, tuple):
            l = min(len(self.min), len(self.max))
            result = tuple(random.uniform(self.min[i], self.max[i]) for i in range(l))
            return result
        else:
            return random.uniform(self.min, self.max)