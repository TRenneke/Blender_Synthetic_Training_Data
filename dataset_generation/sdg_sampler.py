if "bpy" in locals():
    import importlib
    importlib.reload(sdg_utils)
else:
    from . import sdg_utils


import bpy
import random
import colorsys
import numpy as np
from typing import Union
from mathutils import Vector, Matrix

class Sampler:
    def __init__(self, parser) -> None:
        pass
    def __call__(self):
        pass
    def getParser(parameter: int, resultType) -> any:
        return resultType

class ValueSampler(Sampler):
    def __init__(self, value: Sampler):
        self.value = value
    def __call__(self):
        if isinstance(self.value, list):
            return [x() for x in self.value]
        if isinstance(self.value, tuple):
            return tuple(x() for x in self.value)        
        return self.value
    def getParser(parameter: int, resultType):
        return resultType

class ChoiceSampler(Sampler):
    def __init__(self, values: list[Sampler], ammount: Sampler =  ValueSampler(1)) -> None:
        self.values = values
        self.ammount = ammount
    def __call__(self):
        if self.ammount() == 1:
            return random.choice(self.values()) 
        return [random.choice(self.values()) for i in range(self.ammount())]
    def getParser(parameter: int, resultType):
        if parameter == 1:
            return int
        return resultType
class BoolSampler(Sampler):
    def __init__(self, value: Sampler) -> None:
        self.value = value
    def __call__(self):
        return random.random() < self.value()
    def getParser(parameter: int, resultType):
        return float

        
class HSVSampler(Sampler):
    def __init__(self, val: Sampler) -> None:
        self.val = val
    def __call__(self):
        v = self.val()
        if len(v) == 3:
            return colorsys.hsv_to_rgb(*v)
        else:
            h, s, v, a = v
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            return (r, g, b, a)
    def getParser(parameter: int, resultType):
        assert resultType == float
        return float
class UniformSampler(Sampler):
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
    def getParser(parameter: int, resultType):
        assert resultType == float or resultType == int
        return resultType

class CameraLocationSampler():
    def __init__(self, camera: Sampler, val: Sampler) -> None:
        self.val = val
        self.camera = camera
    def __call__(self) -> None:
        cam = bpy.data.objects[self.camera()]
        cam_mat = cam.matrix_world.inverted()
        proj_mat = cam.calc_matrix_camera(bpy.context.evaluated_depsgraph_get())
        mat = proj_mat @ cam_mat
        x, y, z = self.val()
        zpos = Vector((0, 0, -z, 1))
        zpos = proj_mat @ zpos
        z = zpos[2] / zpos[3]
        pos = Vector((x, y, z, 1))
        pos = mat.inverted() @ pos
        x, y, z, w = pos
        return x/w, y/w, z/w
    def getParser(parameter: int, resultType):
        if parameter == 0:
            return str
        return float
#### ------------------------------------ Object Sampler ------------------------------------ #### 
class SelectSampler(Sampler):
    def __init__(self, val: Sampler) -> None:
        self.val = val
    def __call__(self, objects: list[list[bpy.types.Object]]) -> list[list[bpy.types.Object]]:
        s = self.val()
        if not isinstance(s, list):
            s = [s]
        r = []
        for objs in objects:
            objs = [x for x in objs if x.name.split(".")[0] in s]
            if len(objs) > 0:
                r.append(objs)
        return r
    def getParser(parameter: id, resultType):
        return resultType
class CollectionSampler(Sampler):
    def __init__(self, val: Sampler) -> None:
        self.val = val
    def __call__(self, objects: list[bpy.types.Object]) -> list[bpy.types.Object]:
        s = self.val()
        if not isinstance(s, list):
            s = [s]
        return [col.all_objects.values() for col in bpy.data.collections if col.name.split(".")[0] in s]
    def getParser(parameter: id, resultType):
        return resultType
class MergeSampler(Sampler):
    def __init__(self, val: Sampler) -> None:
        pass
    def __call__(self, objects: list[list[bpy.types.Object]]) -> list[list[bpy.types.Object]]:
        r = []
        for objl in objects:
            r += objl
        return [r]
    def getParser(parameter: id, resultType):
        return resultType
class RootSampler():
    def __init__(self) -> None:
        pass
    def __call__(self, objects: list) -> list:
        if isinstance(objects, list):
            return [self.__call__(objs) for objs in objects if isinstance(objs, list) or objs.parent is None]
        return objects
    def getParser(parameter: id, resultType):
        return resultType
class LightSampler():
    def __init__(self) -> None:
        pass
    def __call__(self, objects: list) -> list:
        return [[y.data for y in x if isinstance(y.data, bpy.types.Light)] for x in objects] 
    def getParser(parameter: id, resultType):
        return resultType
class CameraSampler():
    def __init__(self) -> None:
        pass
    def __call__(self, objects: list) -> list:
        return [[y.data for y in x if isinstance(y.data, bpy.types.Camera)] for x in objects]
    def getParser(parameter: id, resultType):
        return resultType
class UnpackSampler():
    def __init__(self) -> None:
        pass
    def __call__(self, objects: list) -> list:
        return [[j] for i in objects for j in i]
    def getParser(parameter: id, resultType):
        return resultType
Samplers: dict = None
def registerSampler(sampler):
    global Samplers
    Samplers[sampler.__name__] = sampler
def _registerAllSamplers():
    registerSampler(ChoiceSampler)
    registerSampler(ValueSampler)
    registerSampler(HSVSampler)
    registerSampler(UniformSampler)
    registerSampler(SelectSampler)
    registerSampler(RootSampler)
    registerSampler(CameraLocationSampler)
    registerSampler(BoolSampler)
    registerSampler(CollectionSampler)
    registerSampler(MergeSampler)
    registerSampler(LightSampler)
    registerSampler(CameraSampler)
    registerSampler(UnpackSampler)
if Samplers is None:
    Samplers = {}
    _registerAllSamplers()