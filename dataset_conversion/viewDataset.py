import cv2
import os
import argparse
import random

def main(args):
    for img_path in os.listdir(os.path.join(args.dataset, "imgs")):
        label_path = os.path.join(args.dataset, "labels", img_path.split(".")[0] + ".txt")
        img = cv2.imread(os.path.join(args.dataset, "imgs", img_path))
        widht = img.shape[1]
        height = img.shape[0]

        with open(label_path) as label_file:
            for line in label_file:
                bb = line.split()
                x = int(float(bb[1]) * widht)
                y = int(float(bb[2]) * height)
                w = int((float(bb[3]) * widht) / 2)
                h = int((float(bb[4]) * height) / 2)
                print((x - w, y - h))
                print((x + w, y + h))
                cv2.rectangle(img, (x - w, y - h), (x + w, y + h), (random.uniform(0, 255), random.uniform(0, 255), random.uniform(0, 255)), 5)
        cv2.imshow("dataset", img)
        cv2.waitKey(0)
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset")
    args = parser.parse_args()    
    main(args)