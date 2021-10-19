import cv2

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--image_dir',
                        default='/Users/lizeng/workspace/caption/data/detection/DIOR/JPEGImages-trainval')
    parser.add_argument('--annotation_dir', default='/Users/lizeng/workspace/caption/data/detection/DIOR/Annotations')
    parser.add_argument('--image_size', default=800, type=int)
    parser.add_argument('--json_dir', default='DIOR/')