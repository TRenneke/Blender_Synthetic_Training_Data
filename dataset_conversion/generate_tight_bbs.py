
from matplotlib import pyplot as plt

import os
os.environ["OPENCV_IO_ENABLE_OPENEXR"]="1"
import cv2 as cv
import json
import os
import numpy as np

from utils import bbRect2darkRect, get_segmentation_mask, generate_relation_graph, get_all_anchestors

import argparse

def create_dn_bbs(dataset: str, class_remap: dict):
    labels_path = os.path.join(dataset, "labels")
    if not os.path.exists(labels_path):
        os.mkdir(labels_path)
    for path in os.listdir(os.path.join(dataset, "crypto")):
        crypto_path = os.path.join(dataset, "crypto", path)
        ann_path = os.path.join(dataset, "anns", path.replace(".exr", ".json"))
        out_path = os.path.join(dataset, "labels", path.replace(".exr", ".txt"))
        
        crypto = cv.imread(crypto_path, cv.IMREAD_UNCHANGED)
        crypto = cv.cvtColor(crypto, cv.COLOR_BGRA2RGBA)
        h, w, _ = crypto.shape
        #print(crypto_path, crypto.shape)
        with open(ann_path, "r") as ann_file:
            with open(out_path, "w+") as out_file:
                anns = json.load(ann_file)
                rel_graph = generate_relation_graph(anns["objects"])
                for obj in anns["objects"]:
                    if "category_id" in obj and obj["category_id"] in class_remap:
                        names = get_all_anchestors(rel_graph, obj["name"])
                        mask = get_segmentation_mask(names, [crypto])
                        
                        rect = cv.boundingRect((mask > 0.5).astype(np.uint8))
                        rect = bbRect2darkRect(rect, (w, h))
                        out_file.write(f"{class_remap[obj['category_id']]} {rect[0]} {rect[1]} {rect[2]} {rect[3]}\n")

                    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=str, help="path do dataset")
    args = parser.parse_args()
    create_dn_bbs(args.dataset, {0: 0, 1: 1, 2: 2, 3: 3, 4: 4})