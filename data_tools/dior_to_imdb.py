# coding=utf8

import argparse, os, json, string
from queue import Queue
# from asyncio import Queue
from threading import Thread, Lock
import cv2
import h5py
import numpy as np
import imageio

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


def main(args):
    h5_fn = 'imdb_' + str(args.image_size) + '.h5'
    # write the h5 file
    h5_file = os.path.join(args.imh5_dir, h5_fn)
    f = h5py.File(h5_file, 'w')
    # load images
    im_fns = add_images(f, args)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--image_dir', default='/Users/lizeng/workspace/caption/data/detection/DIOR/JPEGImages-trainval')
    parser.add_argument('--image_size', default=800, type=int)
    parser.add_argument('--imh5_dir', default='.')
    parser.add_argument('--num_workers', default=20, type=int)

    args = parser.parse_args()
    main(args)
