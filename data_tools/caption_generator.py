import json, os

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

def two_object(objects, relationships):
    sentence = ""
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

# def three_object():


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
                "name": obj["names"][0]
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

    caption_data = {}
    relationships_data = json.load(open(relationships_for_caption_path))

    for image_id in relationships_data.keys():
        objects = relationships_data[image_id]["objects"]
        relationships = relationships_data[image_id]["relationships"]
        print("processing the image", image_id)
        if len(objects) == 2:
            sentence = two_object(objects, relationships)
            caption_data[image_id] = sentence
            continue
        # if len(objects) == 3:




    with open(caption_path, 'w') as f:
        json.dump(caption_data, f, indent=4)

    # print(1)
