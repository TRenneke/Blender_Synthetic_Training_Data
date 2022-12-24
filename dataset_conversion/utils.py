import cv2 as cv
import numpy as np
import mmh3
import struct
import os
import json
from matplotlib import pyplot as plt
def float_from_integer(integer):
    return struct.unpack('!f', struct.pack('!i', integer))[0]
def hash_blend_name(name: str) -> float:
    return float_from_integer(mmh3.hash(name))
def get_segmentation_mask(objects: list[str], cryptos: list[np.ndarray]) -> np.ndarray:
    hashes = [hash_blend_name(o) for o in objects]
    mask = np.zeros((cryptos[0].shape[0], cryptos[0].shape[1], 1), dtype=np.float32)
    #print(np.unique(cryptos[0][:, :, 2]) == hashes[0], cryptos[0].dtype)
    for i in range(len(cryptos) * 2):
        cm = i // 2
        c = i % 2
        print(cm)
        print(c)
        for hash in hashes:
            mask[:, :, 0] += (hash == cryptos[cm][:, :, c]) * cryptos[cm][:, :, c + 1]
    return mask
def bbRect2darkRect(rect: np.ndarray, size) -> np.ndarray:
    x = (rect[2] + rect[0] + rect[0]) / (2 * size[0])
    y = (rect[3] + rect[1] + rect[1]) / (2 * size[1])
    w = rect[2] / size[0]
    h = rect[3] / size[1]
    return x, y, w, h
def generate_relation_graph(objects: list[dict]) -> dict[str, list[str]]:
    """Generate the relation Graph for all objects

    Args:
        objects (list[dict]): list of objects

    Returns:
        dict[str, list[str]]: relation graph, key: object name, value: list of child names
    """
    r: dict[str, list] = {}
    for object in objects:
        if "parent" in object and (not object["parent"] is None):
            if not object["parent"] in r:
                r[object["parent"]] = []    
            r[object["parent"]].append(object["name"])
        elif not object["name"] in r:
            r[object["name"]] = []
    return r
def get_all_anchestors(rel_graph: dict[str, list[str]], obj_name: str) -> list[str]:
    assert not rel_graph is None
    return [obj_name] + [get_all_anchestors(child) for child in rel_graph[obj_name]]
    