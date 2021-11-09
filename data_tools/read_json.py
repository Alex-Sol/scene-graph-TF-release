import json

if __name__ == "__main__":
    objects_path = "DIOR/objects.json"
    relation_path = "DIOR/relationships_for_caption.json"
    # objects = json.load(open(objects_path))
    relation = json.load(open(relation_path))
    # for img in objects:
    #     for obj in img["objects"]:
    #         if obj["x"] == 419 and obj["y"] == 311:
    #             print(img["image_id"])
    for image_id, img in relation.items():
        if len(img["objects"]) == 6 and len(img["relationships"]) == 52:
            if img["objects"][0]["name"] == "basketballcourt" and img["objects"][1]["name"] == "basketballcourt" and \
                    img["objects"][2]["name"] == "tenniscourt" and img["objects"][3]["name"] == "tenniscourt":
                print(image_id)
    print(1)