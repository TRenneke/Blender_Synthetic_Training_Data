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
import itertools

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

class NormalSampler(Sampler):
    def __init__(self, mu: Union[Sampler, tuple[Sampler]], sigma):
        self.mu = mu
        self.sigma = sigma
    def __call__(self):
        _mu = self.mu()
        _sigma = self.sigma()
        if isinstance(_mu, tuple):
            l = min(len(_mu), len(_sigma))
            result = tuple(random.normalvariate(_mu[i], _sigma[i]) for i in range(l))
            return result
        else:
            return random.uniform(_mu, _sigma)
    def getParser(parameter: int, resultType):
        assert resultType == float
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

class ObjectSampler(Sampler):
    def __init__(self, objects: Sampler = None) -> None:
        self.objects = objects
    def __call__(self, objects: list[list[bpy.types.Object]]) -> list[list[bpy.types.Object]]:
        if not self.objects is None:
            objects = self.objects(objects)
        return objects
    def getParser(parameter: id, resultType):
        return resultType
    def getType(self, t):
        if self.objects is None:
            return t
        return self.objects.getType(t)
class SelectSampler(ObjectSampler):
    def __init__(self, val: Sampler, objects: ObjectSampler = None) -> None:
        super().__init__(objects)
        self.val = val
    def __call__(self, objects: list[list[bpy.types.Object]]) -> list[list[bpy.types.Object]]:
        objects = super().__call__(objects)
        r = []
        for objs in objects:
            s = self.val()
            if not isinstance(s, list):
                s = [s]            
            objs = [x for x in objs if x.name.split(".")[0] in s]
            if len(objs) > 0:
                r.append(objs)
        return r
class CollectionChildrenSampler(ObjectSampler):
    def __call__(self, objects: list[list[bpy.types.Collection]]) -> list[list[bpy.types.Collection]]:
        objects = super().__call__(objects)
        lll = [[coll.children.values() for coll in collGroup] for collGroup in objects]
        return [sum(x, []) for x in lll]
    def getType(self, t):
        return super().getType("collections")
class CollectionObjectsSampler(ObjectSampler):
    def __call__(self, objects: list[list[bpy.types.Collection]]) -> list[list[bpy.types.Object]]:
        objects = super().__call__(objects)
        lll = [[coll.all_objects.values() for coll in collGroup] for collGroup in objects]
        return [sum(x, []) for x in lll]
    def getType(self, t):
        return super().getType("collections")

class RootSampler(ObjectSampler):
    def __call__(self, objects: list) -> list:
        objects = super().__call__(objects)
        return [[x for x in objg if x.parent is None] for objg in objects]
    def getType(self, t):
        return super().getType("objects")
class DataSampler(ObjectSampler):
    def __init__(self, data_type, objects: ObjectSampler = None) -> None:
        super().__init__(objects)
        self.data_type = data_type
    def __call__(self, objects: list) -> list:
        objects = super().__call__(objects)
        return [[y.data for y in x if isinstance(y.data, self.data_type)] for x in objects] 
    def getType(self, t):
        return super().getType("objects")

class LightSampler(DataSampler):
    def __init__(self, objects: ObjectSampler = None) -> None:
        super().__init__(bpy.types.Light, objects)
class CameraSampler(DataSampler):
    def __init__(self, objects: ObjectSampler = None) -> None:
        super().__init__(bpy.types.Camera, objects)
class UnpackSampler(ObjectSampler):
    def __call__(self, objects: list) -> list:
        objects = super().__call__(objects)
        print("Unpack", [[j] for i in objects for j in i])
        
        return [[j] for i in objects for j in i]
class PackSampler(ObjectSampler):
    def __call__(self, objects: list[list[bpy.types.Object]]) -> list[list[bpy.types.Object]]:
        objects = super().__call__(objects)   
        return sum(objects, [])

CollOjbsSampler = CollectionObjectsSampler
CollChildsSampler = CollectionChildrenSampler

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
    registerSampler(PackSampler)
    registerSampler(LightSampler)
    registerSampler(CameraSampler)
    registerSampler(UnpackSampler)
    registerSampler(NormalSampler)
    registerSampler(CollectionChildrenSampler)
    registerSampler(CollectionObjectsSampler)
    registerSampler(CollChildsSampler)
    registerSampler(CollOjbsSampler)
if Samplers is None:
    Samplers = {}
    _registerAllSamplers()