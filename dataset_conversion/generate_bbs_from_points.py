
import os
os.environ["OPENCV_IO_ENABLE_OPENEXR"]="1"
import cv2 as cv
import json
import yaml
import os
import numpy as np

from utils import obj_points2camera_points, camera_points2screen_points, ImgBBs, generate_relation_graph, get_all_anchestors, get_segmentation_mask

import argparse

def generateBBsFromPoints(dataset, config, filter_side: bool) -> list[ImgBBs]:
    r = []
    for path in os.listdir(os.path.join(dataset, "crypto")):
        crypto_path = os.path.join(dataset, "crypto", path)
        ann_path = os.path.join(dataset, "anns", path.replace(".exr", ".json"))
        name = path.replace(".exr", "")
        
        crypto = cv.imread(crypto_path, cv.IMREAD_UNCHANGED)
        crypto = cv.cvtColor(crypto, cv.COLOR_BGRA2RGBA)
        h, w, _ = crypto.shape
        img_data = ImgBBs(name, (w,h))
        with open(ann_path, "r") as ann_file:
            anns = json.load(ann_file)
            rel_graph = generate_relation_graph(anns["objects"])
            for obj in anns["objects"]:
                
                if "category_id" in obj and obj["category_id"] in config:
                    names = get_all_anchestors(rel_graph, obj["name"])
                    mask = get_segmentation_mask(names, [crypto])
                    
                    if np.count_nonzero(mask) < 100: continue 
                    
                    cfgitems = config[obj["category_id"]]
                    if not isinstance(cfgitems, list): cfgitems = [cfgitems]
                    for cfgitem in cfgitems:
                        points = np.array(cfgitem["points"], float)
                        points = obj_points2camera_points(points, obj, anns["cameras"][0])
                        points = camera_points2screen_points(points, (w, h))
                        img_data.addBB((cfgitem["new_id"], cv.boundingRect(np.array(points, np.float32))))                        
        r.append(img_data)
    return r
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=str, help="path do dataset", required=True)
    parser.add_argument("--config", type=str, help="path to a point config file", required=True)
    parser.add_argument("--filterSide", action="store_true", help="If the points form a 2d polygon, check this to filter backfaces.", default=False)
    
    args = parser.parse_args()
    with open(args.config) as cf_file:
        config = yaml.safe_load(cf_file)
    imgs_bbs = generateBBsFromPoints(args.dataset, config, args.filterSide)
    for item in imgs_bbs: item.write_dn(args.dataset)
    