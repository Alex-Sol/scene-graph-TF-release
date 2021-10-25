import argparse, os, json
import math



class point:
    def __init__(self):
        self.x = 0
        self.y = 0

class bbox:
    def __init__(self):
        # bbox: (x, y, w, h)
        # x,y 为左上角坐标
        # w为水平方向， h为垂直方向
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0

def distance_cal(bbox1, bbox2):
    #计算两个矩形之间的最小距离,并判断是否距离很近（定义min_dist / L_range <= 0.1即为很近）
    L_range = 800 * (2 ** 0.5)

    #https://blog.csdn.net/DeliaPu/article/details/104837064
    #计算两个bbox的中心点
    C1 = point()
    C2 = point()
    C1.x = bbox1.x + bbox1.w / 2
    C1.y = bbox1.y + bbox1.h / 2
    C2.x = bbox2.x + bbox2.w / 2
    C2.y = bbox2.y + bbox2.h / 2

    #分别计算两矩形中心点在X轴和Y轴方向的距离
    Dx = abs(C2.x - C1.x)
    Dy = abs(C2.y - C1.y)

    min_dist = 0
    #两矩形不相交，x方向有重合
    if (Dx < (bbox1.w + bbox2.w) /2 and Dy >= (bbox1.h + bbox2.h / 2)):
        min_dist = Dy - (bbox1.h + bbox2.h) / 2
    # 两矩形不相交，y方向有重合
    elif (Dx >= (bbox1.w + bbox2.w) /2 and Dy < (bbox1.h + bbox2.h / 2)):
        min_dist = Dx - (bbox1.w + bbox2.w) / 2
    # 两矩形不相交，x方向、y方向均无重合
    elif (Dx >= (bbox1.w + bbox2.w) /2 and Dy >= (bbox1.h + bbox2.h / 2)):
        delta_x = Dx - (bbox1.w + bbox2.w) / 2
        delta_y = Dy - (bbox1.h + bbox2.h) / 2
        min_dist = (delta_x * delta_x + delta_y * delta_y) ** 0.5
    #两矩形相交
    else:
        min_dist = -1
    if min_dist <= L_range * 0.1:
        return True
    return False


def create_distance_rel(args, objects):
    distance_relationships = {}
    relationship_id = 0
    for img in objects:
        image_id = img['image_id']
        objs = img['objects']
        obj_count = len(objs)
        if (obj_count > 1):
            for i in range(obj_count - 1):
                for j in range(i + 1, obj_count):
                    id_1 = objs[i]['object_id']
                    id_2 = objs[j]['object_id']
                    bbox1 = bbox()
                    bbox1.x = objs[i]['x']
                    bbox1.y = objs[i]['y']
                    bbox1.w = objs[i]['w']
                    bbox1.h = objs[i]['h']

                    bbox2 = bbox()
                    bbox2.x = objs[j]['x']
                    bbox2.y = objs[j]['y']
                    bbox2.w = objs[j]['w']
                    bbox2.h = objs[j]['h']

                    if (distance_cal(bbox1, bbox2)):
                        relationship1 = {}
                        relationship1["predicate"] = "close"
                        relationship1["object"] = objs[i]
                        relationship1["relationship_id"] = relationship_id
                        relationship1["subject"] = objs[j]
                        relationship_id += 1
                        relationship2 = {}
                        relationship2["predicate"] = "close"
                        relationship2["object"] = objs[j]
                        relationship2["relationship_id"] = relationship_id
                        relationship2["subject"] = objs[i]
                        relationship_id += 1
                        if (image_id not in distance_relationships.keys()):
                            distance_relationships[image_id] = []
                        distance_relationships[image_id].append(relationship1)
                        distance_relationships[image_id].append(relationship2)
    with open(args.distance_rel_path, 'w') as f:
        json.dump(distance_relationships, f, indent=4)

def direction_cal(bbox1, bbox2):
    #计算bbox1在bbox2的什么方向上
    # 计算两个bbox的中心点
    C1 = point()
    C2 = point()
    C1.x = bbox1.x + bbox1.w / 2
    C1.y = bbox1.y + bbox1.h / 2
    C2.x = bbox2.x + bbox2.w / 2
    C2.y = bbox2.y + bbox2.h / 2

    dire = math.atan2(C1.y - C2.y, C1.x - C2.x) * 180 / math.pi
    if (-22.5 <= dire < 22.5):
        return "E"
    elif (22.5 <= dire < 67.5):
        return "SE"
    elif (67.5 <= dire < 112.5):
        return "S"
    elif (112.5 <= dire < 157.5):
        return "SW"
    elif (dire >= 157.5 or dire < -157.5):
        return "W"
    elif (-157.5 <= dire < -112.5):
        return "NW"
    elif (-112.5 <= dire < -67.5):
        return "N"
    elif (-67.5 <= dire < -22.5):
        return "NE"

direct_opposite = {
    "E": "W",
    "NE": "SW",
    "N": "S",
    "NW": "SE",
    "W": "E",
    "SW": "NE",
    "S": "N",
    "SE": "NW"
}

def create_direction_rel(args, objects):
    direction_relationships = {}
    relationship_id = 0
    for img in objects:
        image_id = img['image_id']
        objs = img['objects']
        obj_count = len(objs)
        for i in range(obj_count - 1):
            for j in range(i + 1, obj_count):
                id_1 = objs[i]['object_id']
                id_2 = objs[j]['object_id']
                bbox1 = bbox()
                bbox1.x = objs[i]['x']
                bbox1.y = objs[i]['y']
                bbox1.w = objs[i]['w']
                bbox1.h = objs[i]['h']

                bbox2 = bbox()
                bbox2.x = objs[j]['x']
                bbox2.y = objs[j]['y']
                bbox2.w = objs[j]['w']
                bbox2.h = objs[j]['h']
                if (obj_count <= 3 or distance_cal(bbox1, bbox2)):
                    direction = direction_cal(bbox1, bbox2)
                    direction_oppo = direct_opposite[direction]
                    relationship1 = {}
                    relationship1["predicate"] = direction
                    relationship1["object"] = objs[i]
                    relationship1["relationship_id"] = relationship_id
                    relationship1["subject"] = objs[j]
                    relationship_id += 1
                    relationship2 = {}
                    relationship2["predicate"] = direction_oppo
                    relationship2["object"] = objs[j]
                    relationship2["relationship_id"] = relationship_id
                    relationship2["subject"] = objs[i]
                    relationship_id += 1
                    if (image_id not in direction_relationships.keys()):
                        direction_relationships[image_id] = []
                    direction_relationships[image_id].append(relationship1)
                    direction_relationships[image_id].append(relationship2)
    with open(args.direction_rel_path, 'w') as f:
        json.dump(direction_relationships, f, indent=4)

def topo_cal(bbox1, bbox2, obj_count):
    # 计算两个bbox的中心点
    C1 = point()
    C2 = point()
    C1.x = bbox1.x + bbox1.w / 2
    C1.y = bbox1.y + bbox1.h / 2
    C2.x = bbox2.x + bbox2.w / 2
    C2.y = bbox2.y + bbox2.h / 2

    # 分别计算两矩形中心点在X轴和Y轴方向的距离
    Dx = abs(C2.x - C1.x)
    Dy = abs(C2.y - C1.y)

    if (obj_count < 3):
        if (Dx > (bbox1.w + bbox2.w) /2 or Dy > (bbox1.h + bbox2.h) / 2):
            return "disjoint"
    if ((Dx == (bbox1.w + bbox2.w) /2 and Dy <= (bbox1.h + bbox2.h) / 2) or (Dy == (bbox1.h + bbox2.h) / 2 and Dx <= (bbox1.w + bbox2.w) /2)):
        return "touches"
    # 有重叠
    if (Dx < (bbox1.w + bbox2.w) /2 and Dy < (bbox1.h + bbox2.h) / 2):
        if (Dx <= abs(bbox1.w - bbox2.w) / 2 and Dy <= abs(bbox1.h - bbox2.h) / 2):
            if (bbox1.w <= bbox2.w and bbox1.h <= bbox2.h):
                return "inside"
            elif (bbox1.w > bbox2.w and bbox1.h > bbox2.h):
                return "contains"
            else:
                return "intersects"
        else:
            return "overlap"
    return "None"




def create_topo_rel(args, objects):
    topo_relationships = {}
    relationship_id = 0
    for img in objects:
        image_id = img['image_id']
        objs = img['objects']
        obj_count = len(objs)
        for i in range(obj_count - 1):
            for j in range(i + 1, obj_count):
                id_1 = objs[i]['object_id']
                id_2 = objs[j]['object_id']
                bbox1 = bbox()
                bbox1.x = objs[i]['x']
                bbox1.y = objs[i]['y']
                bbox1.w = objs[i]['w']
                bbox1.h = objs[i]['h']

                bbox2 = bbox()
                bbox2.x = objs[j]['x']
                bbox2.y = objs[j]['y']
                bbox2.w = objs[j]['w']
                bbox2.h = objs[j]['h']

                topo = topo_cal(bbox1, bbox2, obj_count)
                if topo != "None":
                    relationship1 = {}
                    relationship1["predicate"] = topo
                    relationship1["object"] = objs[i]
                    relationship1["relationship_id"] = relationship_id
                    relationship1["subject"] = objs[j]
                    relationship_id += 1
                    if (image_id not in topo_relationships.keys()):
                        topo_relationships[image_id] = []
                    topo_relationships[image_id].append(relationship1)

                    if topo == "inside":
                        relationship2 = {}
                        relationship2["predicate"] = "contains"
                        relationship2["object"] = objs[j]
                        relationship2["relationship_id"] = relationship_id
                        relationship2["subject"] = objs[i]
                        relationship_id += 1
                        topo_relationships[image_id].append(relationship2)
                    elif topo == "contains":
                        relationship2 = {}
                        relationship2["predicate"] = "inside"
                        relationship2["object"] = objs[j]
                        relationship2["relationship_id"] = relationship_id
                        relationship2["subject"] = objs[i]
                        relationship_id += 1
                        topo_relationships[image_id].append(relationship2)

    with open(args.topo_rel_path, 'w') as f:
        json.dump(topo_relationships, f, indent=4)

def main(args):
    objects = json.load(open(args.objects_path))
    create_distance_rel(args, objects)
    create_direction_rel(args, objects)
    create_topo_rel(args, objects)
    print(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--distance_rel_path', default="DIOR/original_json/distance_relationships_original.json")
    parser.add_argument('--direction_rel_path', default="DIOR/original_json/direction_relationships_original.json")
    parser.add_argument('--topo_rel_path', default="DIOR/original_json/topo_relationships_original.json")
    parser.add_argument('--objects_path', default="DIOR/objects_id-in-img.json")


    args = parser.parse_args()

    main(args)
