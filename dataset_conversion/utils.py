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
    if not obj_name in rel_graph:
        return obj_name
    return [obj_name] + [get_all_anchestors(rel_graph, child) for child in rel_graph[obj_name]]

def points_facing_forward(points):
    count = 0
    for i in range(len(points)):
        j = (i+1) % len(points)
        k = (i+2) % len(points)
        d1 = points[i] - points[j]
        d2 = points[k] - points[j]
        z = d1[0] * d2[1] - d1[1] * d2[0]
        if z > 0: count+=1 
        else: count-=1
    return count > 0
def bb_from_points(points):
    cv.boundingRect(points)
def camera_points2screen_points(points, img_shape):
    s = np.array(img_shape) / 2
    points =  [(p * (np.array(img_shape) / 2) + s) for p in points]
    print(points)
    points = [np.array([p[0], img_shape[1] - p[1]], np.float32) for p in points]
    print(points)
    
    return points
def obj_points2camera_points(points, object, camera):
    P = np.array(camera["P"])
    K = np.array(camera["K"])
    M = np.array(object["M"])
    PKM = P @ K @ M
    points = [PKM @ np.append(p, 1) for p in points]
    return [p[0:2] / p[3] for p in points]


class ImgBBs:
    name: str
    img_shape: tuple[int, int]
    bbs: list[tuple[int, tuple[float, float, float, float]]]
    def __init__(self, name, shape) -> None:
        self.name = name
        self.img_shape = shape
        self.bbs = []
    def addBB(self, bb):
        self.bbs.append(bb)
    def asDNBB(self):
        return [(x[0], bbRect2darkRect(x[1], self.img_shape)) for x in self.bbs]
    def write_dn(self, dataset):
        out_path = os.path.join(dataset, "labels", self.name + ".txt")
         
        with open(out_path, "w") as out_file:
            for bb in self.asDNBB():
                id, rect = bb
                out_file.write(f"{id} {rect[0]} {rect[1]} {rect[2]} {rect[3]}\n")

