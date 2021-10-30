# coding=utf8

import argparse, os, json, string
from queue import Queue
# from asyncio import Queue
from threading import Thread, Lock
import cv2
import h5py
import numpy as np
import xml.etree.ElementTree as ET
import imageio
import pandas as pd

def add_images(h5_file, args):
    fns = []
    ids = []
    idx = []
    file_list = os.listdir(args.image_dir)

    for i, basename in enumerate(file_list):

        filename = os.path.join(args.image_dir, basename)
        if os.path.exists(filename):
            fns.append(filename)
            ids.append(basename.split('.')[0])
            idx.append(i)

    ids = np.array(ids, dtype=np.int32)
    idx = np.array(idx, dtype=np.int32)
    h5_file.create_dataset('image_ids', data=ids)
    h5_file.create_dataset('valid_idx', data=idx)

    num_images = len(fns)

    shape = (num_images, 3, args.image_size, args.image_size)
    image_dset = h5_file.create_dataset('images', shape, dtype=np.uint8)
    original_heights = np.zeros(num_images, dtype=np.int32)
    original_widths = np.zeros(num_images, dtype=np.int32)
    image_heights = np.zeros(num_images, dtype=np.int32)
    image_widths = np.zeros(num_images, dtype=np.int32)

    lock = Lock()
    q = Queue()
    for i, fn in enumerate(fns):
        q.put((i, fn))

    def worker():
        while True:
            i, filename = q.get()

            if i % 1000 == 0:
                print('processing %i images...' % i)
            img = imageio.imread(filename)
            # handle grayscale
            if img.ndim == 2:
                img = img[:, :, None][:, :, [0, 0, 0]]
            H0, W0 = img.shape[0], img.shape[1]
            img = cv2.resize(img, (args.image_size, args.image_size))
            H, W = img.shape[0], img.shape[1]
            # swap rgb to bgr. This can't be the best way right? #fail
            r = img[:, :, 0].copy()
            img[:, :, 0] = img[:, :, 2]
            img[:, :, 2] = r

            lock.acquire()
            original_heights[i] = H0
            original_widths[i] = W0
            image_heights[i] = H
            image_widths[i] = W
            image_dset[i, :, :H, :W] = img.transpose(2, 0, 1)
            lock.release()
            q.task_done()

    for i in range(args.num_workers):
        t = Thread(target=worker)
        t.daemon = True
        t.start()

    q.join()

    h5_file.create_dataset('image_heights', data=image_heights)
    h5_file.create_dataset('image_widths', data=image_widths)
    h5_file.create_dataset('original_heights', data=original_heights)
    h5_file.create_dataset('original_widths', data=original_widths)

    return fns


def create_image_data(args):
    json_path = os.path.join(args.json_dir, "image_data.json")
    data = []
    image_dir = os.path.join(args.image_dir, "JPEGImages-trainval")
    file_list = os.listdir(image_dir)
    i = 0
    for basename in file_list:
        filename = os.path.join(image_dir, basename)
        img = imageio.imread(filename)
        if i % 1000 == 0:
            print(i)
        i += 1
        # if img.shape[0] != 800 or img.shape[1] != 800:
        #     print(basename)
        # if abs(img.shape[0] - 800) >= 50 or abs(img.shape[1] - 800) >= 50:
        #     print("image_name: ")
        #     print(basename)
        data.append({
            "width": img.shape[1],
            "height": img.shape[0],
            "image_id": int(basename.split(".")[0]),
            "url": "",
            "coco_id": None,
            "flickr_id": None,
            "trainval": "trainval"
        })

    image_dir = os.path.join(args.image_dir, "JPEGImages-test")
    file_list = os.listdir(image_dir)
    for basename in file_list:
        filename = os.path.join(image_dir, basename)
        img = imageio.imread(filename)
        if i % 1000 == 0:
            print(i)
        i += 1
        # if img.shape[0] != 800 or img.shape[1] != 800:
        #     print(basename)
        # if abs(img.shape[0] - 800) >= 50 or abs(img.shape[1] - 800) >= 50:
        #     print("image_name: ")
        #     print(basename)
        data.append({
            "width": img.shape[1],
            "height": img.shape[0],
            "image_id": int(basename.split(".")[0]),
            "url": "",
            "coco_id": None,
            "flickr_id": None,
            "trainval": "test"
        })
    with open(json_path, "w") as f:
        json.dump(data, f, indent=4)

def create_objects(args):
    json_path = os.path.join(args.json_dir, "objects.json")
    data = []
    file_list = os.listdir(args.annotation_dir)
    object_id = 0
    for basename in file_list:
        annotation_filename = os.path.join(args.annotation_dir, basename)
        tree = ET.parse(annotation_filename)
        image_file = tree.find('filename').text
        objects_data = tree.findall('object')
        image_id = int(image_file.split('.')[0])
        image_url = ""
        objects = []

        for i_object, obj in enumerate(objects_data):
            bbox = obj.find('bndbox')
            x1 = float(bbox.find('xmin').text)
            y1 = float(bbox.find('ymin').text)
            x2 = float(bbox.find('xmax').text)
            y2 = float(bbox.find('ymax').text)
            object = {
                "object_id": object_id,
                "merged_object_ids": [],
                "names": [obj.find('name').text],
                "h": int(y2 - y1),
                "w": int(x2 - x1),
                "x": int(x1),
                "y": int(y1)
            }
            object_id += 1
            objects.append(object)
        data.append({
            "image_id": image_id,
            "image_url": image_url,
            "objects": objects
        })
    with open(json_path, "w") as f:
        json.dump(data, f, indent=4)

def create_objects_in_img(args):
    json_path = os.path.join(args.json_dir, "objects_id-in-img.json")
    data = []
    file_list = os.listdir(args.annotation_dir)

    for basename in file_list:
        annotation_filename = os.path.join(args.annotation_dir, basename)
        tree = ET.parse(annotation_filename)
        image_file = tree.find('filename').text
        objects_data = tree.findall('object')
        image_id = int(image_file.split('.')[0])
        image_url = ""
        objects = []
        object_id = 0
        for i_object, obj in enumerate(objects_data):
            bbox = obj.find('bndbox')
            x1 = float(bbox.find('xmin').text)
            y1 = float(bbox.find('ymin').text)
            x2 = float(bbox.find('xmax').text)
            y2 = float(bbox.find('ymax').text)
            object = {
                "object_id": object_id,
                "merged_object_ids": [],
                "names": [obj.find('name').text],
                "h": int(y2 - y1),
                "w": int(x2 - x1),
                "x": int(x1),
                "y": int(y1)
            }
            object_id += 1
            objects.append(object)
        data.append({
            "image_id": image_id,
            "image_url": image_url,
            "objects": objects
        })
    with open(json_path, "w") as f:
        json.dump(data, f, indent=4)

def create_relationship_from_csv(args):
    data = pd.read_csv(args.csv_path)
    count = data["object"].count()
    relationships = []
    objects_id_in_img_data = json.load(open(args.objects_id_in_img_json))
    objects_data = json.load(open(args.objects_json))
    objects = {}

    for i in range(len(objects_data)):
        image_id = objects_data[i]["image_id"]
        objects[image_id] = {}
        for j in range(len(objects_data[i]["objects"])):
            objects[image_id][objects_id_in_img_data[i]["objects"][j]["object_id"]] = objects_data[i]["objects"][j]
            objects[image_id][objects_id_in_img_data[i]["objects"][j]["object_id"]]["name"] = objects_data[i]["objects"][j]["names"][0]
            objects[image_id][objects_id_in_img_data[i]["objects"][j]["object_id"]].pop("names")


    image_id = data["image_id"][0]
    relationship_id = 0
    for i in range(count):
        if not np.isnan(data["image_id"][i]):
            image_id = int(data["image_id"][i])
            relationships.append({
                "relationships": [],
                "image_id": image_id
            })
        object_id = int(data["object"][i])
        relation = data["relationship"][i]
        subject_id = int(data["subject"][i])
        object = objects[image_id][object_id]
        subject = objects[image_id][subject_id]
        relationships[-1]["relationships"].append({
            "predicate": relation,
            "object": object,
            "relationship_id": relationship_id,
            "subject": subject
        })
        relationship_id += 1
    with open(args.rel_json_path, "w") as f:
        json.dump(relationships, f, indent=4)

def create_relationship_from_original(args):
    distance_relationships_path = os.path.join(args.original_json_path, "distance_relationships_original.json")
    direction_relationships_path = os.path.join(args.original_json_path, "direction_relationships_original.json")
    topo_relationships_path = os.path.join(args.original_json_path, "topo_relationships_original.json")
    distance_relationships = json.load(open(distance_relationships_path))
    direction_relationships = json.load(open(direction_relationships_path))
    topo_relationships = json.load(open(topo_relationships_path))
    image_data = json.load(open(args.image_data_path))
    objects_data = json.load(open(args.objects_json))
    objects = {}
    for img in objects_data:
        objects[img['image_id']] = img['objects']
    relationships = []
    relationship_id = 0
    for img in image_data:
        image_id = img['image_id']
        distance_relationship = []
        direction_relationship = []
        topo_relationship = []
        image_id_str = str(image_id)
        if (image_id_str in distance_relationships.keys()):
            distance_relationship = distance_relationships[image_id_str]
        if (image_id_str in direction_relationships.keys()):
            direction_relationship = direction_relationships[image_id_str]
        if (image_id_str in topo_relationships.keys()):
            topo_relationship = topo_relationships[image_id_str]
        if (len(distance_relationship) + len(direction_relationship) + len(topo_relationship) > 0):
            relationships.append({
                'relationships': [],
                'image_id': image_id
            })
            for rel in distance_relationship:
                rel['relationship_id'] = relationship_id
                relationship_id += 1
                object_id = rel['object']['object_id']
                object_id = objects[image_id][object_id]['object_id']
                rel['object']['object_id'] = object_id
                object_id = rel['subject']['object_id']
                object_id = objects[image_id][object_id]['object_id']
                rel['subject']['object_id'] = object_id
                relationships[-1]['relationships'].append(rel)

            for rel in direction_relationship:
                rel['relationship_id'] = relationship_id
                relationship_id += 1
                object_id = rel['object']['object_id']
                object_id = objects[image_id][object_id]['object_id']
                rel['object']['object_id'] = object_id
                object_id = rel['subject']['object_id']
                object_id = objects[image_id][object_id]['object_id']
                rel['subject']['object_id'] = object_id
                relationships[-1]['relationships'].append(rel)

            for rel in topo_relationship:
                rel['relationship_id'] = relationship_id
                relationship_id += 1
                object_id = rel['object']['object_id']
                object_id = objects[image_id][object_id]['object_id']
                rel['object']['object_id'] = object_id
                object_id = rel['subject']['object_id']
                object_id = objects[image_id][object_id]['object_id']
                rel['subject']['object_id'] = object_id
                relationships[-1]['relationships'].append(rel)

    with open(args.rel_json_path, 'w') as f:
        json.dump(relationships, f, indent=4)








if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--image_dir', default='/Users/lizeng/workspace/caption/data/detection/DIOR')
    parser.add_argument('--annotation_dir', default='/Users/lizeng/workspace/caption/data/detection/DIOR/Annotations')
    parser.add_argument('--image_size', default=800, type=int)
    parser.add_argument('--json_dir', default='DIOR/total_json')
    parser.add_argument('--csv_path', default="/Users/lizeng/Desktop/relationship.csv")
    parser.add_argument('--objects_id_in_img_json', default="DIOR/total_json/objects_id-in-img.json")
    parser.add_argument('--objects_json', default="DIOR/total_json/objects.json")
    parser.add_argument('--rel_json_path', default="DIOR/relationships.json")
    parser.add_argument('--original_json_path', default="DIOR/original_json")
    parser.add_argument('--image_data_path', default="DIOR/total_json/image_data.json")
    parser.add_argument('--crete_image_data', type=bool, default=True)

    args = parser.parse_args()
    if args.crete_image_data:
        create_image_data(args)
        create_objects(args)
        create_objects_in_img(args)
    else:
        # create_relationship_from_csv(args)
        create_relationship_from_original(args)