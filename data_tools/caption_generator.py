import json, os
import numpy as np
from collections import Counter

single_to_plural = {
    "airplane": "airplanes",
    "airport": "airports",
    "baseballfield": "baseballfields",
    "basketballcourt": "basketballcourts",
    "bridge": "bridges",
    "chimney": "chimneys",
    "dam": "dams",
    "Expressway-Service-area": "Expressway-Service-areas",
    "Expressway-toll-station": "Expressway-toll-stations",
    "golffield": "golffields",
    "groundtrackfield": "groundtrackfields",
    "harbor": "harbors",
    "ship": "ships",
    "stadium": "stadiums",
    "storagetank": "storagetanks",
    "tenniscourt": "tenniscourts",
    "trainstation": "trainstations",
    "vehicle": "vehicles",
    "windmill": "windmills",
    "overpass": "overpasses"
}

rel_to_word = {
        "close" : "closed to",
        "E" : "east of",
        "SE" : "southeast of",
        "S" : "south",
        "SW" : "southwest of",
        "W" : "west of",
        "NW" : "northwest of",
        "N" : "north of",
        "NE" : "northeast of",
        "touches" : "adjacent to",
        "inside" : "inside",
        "contains" : "contains",
        "intersects" : "intersects",
        "overlap" : "intersects"
    }

nums_English = ["", "one", "two", "three", "four", "five", "six",
    "seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen",
    "fourteen", "fifteen", "sixteen", "seventeen", "eighteen",
    "nineteen"]

def SizeOfObject(w, h):
    area = area_compute(w, h)
    if area < 2500:
        return 1
    elif 2500 <= area < 40000:
        return 2
    elif area >= 40000:
        return 3

def area_compute(w, h):
    return w * h

def two_object(objects, relationships):
    sentence = ""

    rel = relationships[0]
    subject = rel["subject"]["name"]
    relation = rel["relation"]
    object = rel["object"]["name"]
    if subject == object:
        sentence = "There are two " + single_to_plural[subject] + " in the image."
        return sentence
    if relation == "disjoint":
        sentence = "There is a " + subject + " and a " + object + " in the image."
        return sentence
    sentence = "The " + subject + " is " + rel_to_word[relation] + " the " + object + "."
    return sentence

def three_object(objects, relationships):
    sentence = ""

    sizes = [SizeOfObject(obj["w"], obj["h"]) for obj in objects]

    sort_index = np.argsort(sizes, axis=0)[::-1]    #将目标从大到小排序，索引列表

    cls = []
    object_ids = []
    for idx in range(len(sort_index)):
        index_objects = sort_index[idx]
        cls.append(objects[index_objects]["name"])
        object_ids.append(objects[index_objects]["object_id"])
        if idx < 2 and sizes[sort_index[idx]] - sizes[sort_index[idx + 1]] >= 2:
            break

    if len(cls) == 1:
        sentence = "There is a " + cls[0] + ' in the image.'
    elif len(cls) == 2:
        if cls[0] == cls[1]:
            sentence = "There are two " + single_to_plural[cls[0]] + ' in the image.'
        else:
            for rel in relationships:
                if rel["subject"]["object_id"] in object_ids and rel["object"]["object_id"] in object_ids:
                    sentence = "The " + rel["subject"]["name"] + " is " + rel_to_word[rel["relation"]] + " the " + rel["object"]["name"] + "."
                    break
            if sentence == "":
                sentence = "There are a " + cls[0] + ' and a ' + cls[1] + " in the image."
    else:
        count = Counter(cls)
        if len(count) == 1:
            sentence = "There are three " + single_to_plural[cls[0]] + ' in the image.'
        elif len(count) == 2:
            for key in count.keys():
                if count[key] == 2:
                    two_obj = key
                if count[key] == 1:
                    one_obj = key

            rel_two_to_one_A = ""
            rel_two_to_one_B = ""
            for rel in relationships:
                if rel["subject"]["name"] == two_obj and rel["object"]["name"] == one_obj:
                    if rel_two_to_one_A:
                        rel_two_to_one_B = rel["relation"]
                        break
                    else:
                        rel_two_to_one_A = rel["relation"]
            if rel_two_to_one_A and rel_two_to_one_B and rel_two_to_one_A == rel_two_to_one_B:
                sentence = "There are two " + single_to_plural[two_obj] + ' ' + rel_to_word[rel_two_to_one_A] + ' the ' + one_obj + " in the image."
            if sentence == "":
                sentence = "There are two " + single_to_plural[two_obj] + ' and one ' + one_obj + " in the image."
        else:
            object_id_A = objects[sort_index[0]]["object_id"]
            object_id_B = objects[sort_index[1]]["object_id"]
            for rel in relationships:
                if (rel["subject"]["object_id"] == object_id_A and rel["object"]["object_id"] == object_id_B) or \
                        (rel["subject"]["object_id"] == object_id_B and rel["object"]["object_id"] == object_id_A):
                    sentence = "The " + rel["subject"]["name"] + " is " + rel_to_word[rel["relation"]] + " the " + rel["object"]["name"] + "."
                    break
            if sentence == "":
                sentence = "There are a " + cls[0] + ' and a ' + cls[1] + " in the image."

    return sentence

def four_object(objects, relationships):
    sentence = ""

    sizes = [SizeOfObject(obj["w"], obj["h"]) for obj in objects]

    sort_index = np.argsort(sizes, axis=0)[::-1]  # 将目标从大到小排序，索引列表

    cls = []
    object_ids = []
    for idx in range(len(sort_index)):
        index_objects = sort_index[idx]
        cls.append(objects[index_objects]["name"])
        object_ids.append(objects[index_objects]["object_id"])
        if idx < 2 and sizes[sort_index[idx]] - sizes[sort_index[idx + 1]] >= 2:
            break
    count = Counter(cls)

    if len(count) == 1:
        sentence = "There are several " + single_to_plural[cls[0]] + " in the image."
    else:
        more_object_name = count.most_common(1)[0][0]
        less_object_name = count.most_common(2)[1][0]
        count_rel = Counter()
        for rel in relationships:
            if rel["subject"]["name"] == more_object_name and rel["object"]["name"] == less_object_name:
                count_rel[rel["relation"]] += 1
        if len(count_rel) == 0:
            if count[less_object_name] == 1:
                sentence = "There are several " + single_to_plural[more_object_name] + " and one " + less_object_name + ' in the image.'
            elif count[less_object_name] == 2:
                sentence = "There are several " + single_to_plural[more_object_name] + " and two " + single_to_plural[
                    less_object_name] + ' in the image.'
            else:
                sentence = "There are several " + single_to_plural[more_object_name] + " and several " + single_to_plural[
                    less_object_name] + ' in the image.'
        else:
            most_rel = count_rel.most_common(1)[0][0]
            if count_rel[most_rel] > 5:
                if count[less_object_name] == 1:
                    sentence = "Several " + single_to_plural[more_object_name] + " is " + rel_to_word[most_rel] + " the " + less_object_name + '.'
                else:
                    sentence = "Several " + single_to_plural[more_object_name] + " is " + rel_to_word[
                        most_rel] + " the " + single_to_plural[less_object_name] + '.'
            else:
                if count[less_object_name] == 1:
                    sentence = "There are several " + single_to_plural[
                        more_object_name] + " and one " + less_object_name + ' in the image.'
                elif count[less_object_name] == 2:
                    sentence = "There are several " + single_to_plural[more_object_name] + " and two " + \
                               single_to_plural[
                                   less_object_name] + ' in the image.'
                else:
                    sentence = "There are several " + single_to_plural[more_object_name] + " and several " + \
                               single_to_plural[
                                   less_object_name] + ' in the image.'

    return sentence

def twenty_object(objects, relationships):
    sentence = ""

    sizes = [SizeOfObject(obj["w"], obj["h"]) for obj in objects]

    sort_index = np.argsort(sizes, axis=0)[::-1]  # 将目标从大到小排序，索引列表

    cls = []
    object_ids = []

    large_cls = []
    for idx in range(len(sort_index)):
        index_objects = sort_index[idx]
        cls.append(objects[index_objects]["name"])
        object_ids.append(objects[index_objects]["object_id"])
        if sizes[index_objects] == 3:
            large_cls.append(cls[-1])

    count = Counter(cls)

    most_cls = []

    # count = [(l, k) for k, l in sorted([(j, i) for i, j in count_tmp.items()], reverse=True)]


    for key in count.keys():
        if count[key] >= 10:
            most_cls.append(key)

    if len(large_cls) > 0:
        largest_object_name = large_cls[0]
        num = large_cls.count(largest_object_name)
        if len(most_cls) >= 2:
            if num > 1:
                sentence = "Many " + single_to_plural[most_cls[0]] + " is inside in " + nums_English[num] + " " + single_to_plural[largest_object_name] + " and there are some " + \
                           single_to_plural[most_cls[1]] + " beside the " + single_to_plural[largest_object_name] + '.'
            else:
                sentence = "Many " + single_to_plural[most_cls[0]] + " is inside in the " + \
                           largest_object_name + " and there are some " + \
                           most_cls[1] + " beside the " + largest_object_name + '.'
        else:
            if num > 1:
                sentence = "Many " + single_to_plural[count.most_common(1)[0][0]] + " is inside in " + nums_English[num] + " " + single_to_plural[largest_object_name] + '.'
            else:
                sentence = "Many " + single_to_plural[count.most_common(1)[0][0]] + " is inside in the " + largest_object_name + '.'
    else:
        if len(most_cls) >= 2:
            more_name = most_cls[0]
            second_name = most_cls[1]
            count_rel = Counter()
            for rel in relationships:
                if rel["subject"]["name"] == more_name and rel["object"]["name"] == second_name:
                    count_rel[rel["relation"]] += 1
            if len(count_rel) > 0:
                rel_name = count_rel.most_common(1)[0][0]
                sentence = "Some " + single_to_plural[more_name] + " are " + rel_to_word[rel_name] + " some " + single_to_plural[second_name] + '.'
            else:
                sentence = "Some " + single_to_plural[more_name] + " are disjoint to " + " some " + \
                           single_to_plural[second_name] + ' in the image.'
        else:
            sentence = "There are some " + single_to_plural[count.most_common(1)[0][0]] + " in the image."

    return sentence





def caption_generation(relationships_for_caption_path, caption_path):
    caption_data = {}
    relationships_data = json.load(open(relationships_for_caption_path))
    count1 = 0
    count2 = 0
    for image_id in relationships_data.keys():
        objects = relationships_data[image_id]["objects"]
        relationships = relationships_data[image_id]["relationships"]
        # print("processing the image", image_id)
        if len(objects) == 2:
            sentence = two_object(objects, relationships)
            caption_data[image_id] = sentence
            continue
        elif len(objects) == 3:
            sentence = three_object(objects, relationships)
            caption_data[image_id] = sentence
            continue
        elif 4 <= len(objects) <= 10:
            sentence = four_object(objects, relationships)
            caption_data[image_id] = sentence
            continue
        elif 10 < len(objects) <= 20:
            count1 += 1
            print(image_id, "\t", len(objects))
            sentence = twenty_object(objects, relationships)
            caption_data[image_id] = sentence
            continue
        else:
            count2 += 1
            # print(image_id, "\t", len(objects))
            sentence = twenty_object(objects, relationships)
            caption_data[image_id] = sentence
            continue
    print("count1: ", count1)
    print("count2: ", count2)
    with open(caption_path, 'w') as f:
        json.dump(caption_data, f, indent=4)

def format_relationships(objects_path, relationships_path, relationships_for_caption_path):
    data = {}
    objects = json.load(open(objects_path))
    relationships = json.load(open(relationships_path))
    assert len(objects) == len(relationships)
    for i in range(len(objects)):
        img_objects = objects[i]
        img_relationship = relationships[i]

        data[img_objects["image_id"]] = {
            "objects": [],
            "relationships": []
        }

        for obj in img_objects['objects']:
            object_save = {
                "object_id": obj["object_id"],
                "name": obj["names"][0],
                "w": obj["w"],
                "h": obj["h"],
                "x": obj["x"],
                "y": obj["y"]
            }

            data[img_objects["image_id"]]["objects"].append(object_save)

        for rel in img_relationship["relationships"]:
            # relationships.json中subject和object弄反了,其实subject才是主语的英文,object代表宾语
            relationship_save = {}
            relationship_save["subject"] = {
                "object_id": rel["object"]["object_id"],
                "name": rel["object"]["names"][0]
            }
            relationship_save["relation"] = rel["predicate"]
            relationship_save["object"] = {
                "object_id": rel["subject"]["object_id"],
                "name": rel["subject"]["names"][0]
            }
            data[img_objects["image_id"]]["relationships"].append(relationship_save)

    with open(relationships_for_caption_path, 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":

    #format the relationships and save into the json file: relationships_for_caption.json
    objects_path = "DIOR/objects.json"
    relationships_path = "DIOR/relationships.json"
    relationships_for_caption_path = "DIOR/relationships_for_caption.json"
    caption_path = "DIOR/caption.json"
    # format_relationships(objects_path, relationships_path, relationships_for_caption_path)

    caption_generation(relationships_for_caption_path, caption_path)


    # print(1)
