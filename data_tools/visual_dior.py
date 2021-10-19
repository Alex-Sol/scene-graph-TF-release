import cv2
import argparse, json, os
import numpy as np

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--image_dir',
                        default='/Users/lizeng/workspace/caption/data/detection/DIOR/JPEGImages-trainval')
    parser.add_argument('--annotation_file', default='DIOR/objects_id-in-img.json')
    parser.add_argument('--save_dir', default='/Users/lizeng/workspace/caption/data/scenegraph/DIOR/imgs_objects')

    args = parser.parse_args()

    annotations = json.load(open(args.annotation_file))

    for annotation in annotations:
        image_file = os.path.join(args.image_dir, format(annotation["image_id"], '05d') + ".jpg")
        if not os.path.exists(image_file):
            image_file = os.path.join('/Users/lizeng/workspace/caption/data/detection/DIOR/JPEGImages-test', format(annotation["image_id"], '05d') + ".jpg")
        im = cv2.imread(image_file)
        for obj in annotation["objects"]:
            object_id = obj["object_id"]
            x1 = int(obj["x"])
            y1 = int(obj["y"])
            x2 = int(x1 + obj["w"])
            y2 = int(y1 + obj["h"])
            cv2.rectangle(im, (x1, y1), (x2, y2), (220, 170, 143), 2)
            cv2.putText(im, '%d' %object_id, (x1, y1 + 20), cv2.FONT_HERSHEY_PLAIN,
                        1.5, (0, 0, 255), thickness=2)
        save_path = os.path.join(args.save_dir, format(annotation["image_id"], '05d') + ".jpg")
        cv2.imwrite(save_path, im)
