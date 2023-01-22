import bpy
import random
import colorsys
from typing import Union 
# Placeholder class for code auto completion only 

#def getSamplers():
#    global _Sampler
#    if _Sampler is None:
#        _Sampler = 

class Sampler:
    def __init__(self, parser) -> None:
        pass
    def __call__():
        pass
    def getParser(parameter: id, resultType) -> any:
        return resultType

class ChoiceSampler:
    def __init__(self, values: list, ammount: int = 1) -> None:
        self.values = values
        self.ammount = ammount
    def __call__(self):
        if self.ammount == 1:
            return random.choice(self.values())() 
        return [random.choice(self.values()) for i in range(self.ammount)]
    def getParser(parameter: id, resultType):
        if id == 1:
            int
        return resultType
        
class ValueSampler:
    def __init__(self, value: Sampler):
        self.value = value
    def __call__(self):
        if isinstance(self.value, list):
            return [x() for x in self.value]
        if isinstance(self.value, tuple):
            return tuple(x() for x in self.value)        
        return self.value
    def getParser(parameter: id, resultType):
        return resultType
class HSVSampler:
    def __init__(self, val: Sampler) -> None:
        self.val = val
    def __call__(self):
        h, s, v, a = self.val()
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return (r, g, b, a)
    def getParser(parameter: id, resultType):
        assert resultType == float
        return float
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
    def getParser(parameter: id, resultType):
        assert resultType == float
        return float
class SelectSampler:
    def __init__(self, val: Sampler) -> None:
        self.val = val
    def __call__(self, objects: list[bpy.types.Object]) -> list[bpy.types.Object]:
        s = self.val()
        if not isinstance(s, list):
            s = [s]
        return [obj for obj in objects if obj.name.split(".")[0] in s]
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
if Samplers is None:
    Samplers = {}
    _registerAllSamplers()