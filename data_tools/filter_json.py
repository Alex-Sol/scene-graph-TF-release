import argparse, os, json, string

def main(args):
    image_data = json.load(open(args.image_data_path))
    objects_data = json.load(open(args.objects_json))
    relationships_data = json.load(open(args.rel_json_path))
    image_dict = {}
    objects_dict = {}
    for img in image_data:
        image_dict[img['image_id']] = img

    for img in objects_data:
        objects_dict[img['image_id']] = img

    images = []
    objects = []

    for img in relationships_data:
        images.append(image_dict[img['image_id']])
        objects.append(objects_dict[img['image_id']])

    with open(args.filter_img, 'w') as f:
        json.dump(images, f, indent=4)

    with open(args.filter_obj, 'w') as f:
        json.dump(objects, f, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--image_data_path', default="DIOR/total_json/image_data.json")
    parser.add_argument('--objects_json', default="DIOR/total_json/objects.json")
    parser.add_argument('--rel_json_path', default="DIOR/relationships.json")
    parser.add_argument('--filter_img', default="DIOR/image_data.json")
    parser.add_argument('--filter_obj', default="DIOR/objects.json")


    args = parser.parse_args()
    main(args)