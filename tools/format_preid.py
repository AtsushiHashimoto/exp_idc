#!/usr/bin/env python
# coding: utf-8

DESCRIPTION="This script unifies the data format from different datasets."

import numpy as np
import argparse
import glob2
import gzip
import logging
import os.path
import csv
import random

logger = logging.getLogger(__file__)


def parse_row(r):
    path, person_id = r.strip().split(' ')
    cam,tracklet_info = os.path.split(os.path.splitext(path)[0])
    tracklet_id,frame_id = tracklet_info.split('_')
    return int(person_id),"%s/%s"%(cam,tracklet_id),int(frame_id)

def my_dict_append(a,_dict):
    if a[0] not in _dict.keys():
        _dict[a[0]] = []
    _dict[a[0]].append(a[1:])

def load_meta_data(file):
    fin = open(file,"r")
    return [[*parse_row(r)] for i,r in enumerate(fin)]

def sample_meta_data(meta_data):
    data_hash = {}
    for line, (p,tid,frame_id) in enumerate(meta_data):
        # m[0]:person_id
        if p not in data_hash.keys():
            data_hash[p] = {}
        my_dict_append([tid,frame_id,line],data_hash[p])
    #for p,tracklet_data in data_hash.items():
    #    print(p,tracklet_data.keys())
    person_set = set([p for (p,tid,frame_id) in meta_data])

    # random_sample
    sample_list = {}
    for p in person_set:
        sample_list[p]=[]

    for p,tracklet_data in data_hash.items():
        for t_id,frame_list in tracklet_data.items():
            random.shuffle(frame_list)
            sample_list[p].append(frame_list[0][1])
    return sample_list

def format_preid_data(src_dir,dest_dir):
    flatten = lambda l: [item for sublist in l for item in sublist]

    image_paths = sorted(glob2.glob("%s/test*.txt"%(src_dir)))
    meta_data = flatten([load_meta_data(p) for p in image_paths])
    #print('\n'.join(map(str,meta_data)))
    samples = sample_meta_data(meta_data)
    #print(samples)

    files = ["%s_features.npy"%(os.path.splitext(p)[0]) for p in image_paths ]
    temp = flatten([np.load(f) for f in files])
    X_ = np.r_[temp]

    for p,line_list in samples.items():
        #print(p,": ",line_list)
        data = [[X_[l],p,"%s_%05d.jpg"%(meta_data[l][1],meta_data[l][2])] for l in line_list]
        X = [d[0] for d in data]
        y = [d[1] for d in data]
        image_paths = [d[2] for d in data]
        np.save("%s/X_%02d.npy"%(dest_dir,p),X)
        np.save("%s/y_%02d.npy"%(dest_dir,p),y)
        open("%s/imagepath_%02d.dat"%(dest_dir,p),'w').write('\n'.join(image_paths))

def main(args):
    src_dir=args.src_dir
    dest_dir=args.dest_dir
    format_preid_data(src_dir,dest_dir)



parser = argparse.ArgumentParser(description=DESCRIPTION)

parser.add_argument('src_dir', \
        action='store', \
        nargs=None, \
        const=None, \
        default=None, \
        type=str, \
        choices=None, \
        help='Directory path where the source data are located.', \
        metavar=None)

parser.add_argument('dest_dir', \
        action='store', \
        nargs=None, \
        const=None, \
        default=None, \
        type=str, \
        choices=None, \
        help='Directory path where the formatted data will be located.', \
        metavar=None)

if __name__ == '__main__':
    args = parser.parse_args()
    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler()
    logger.addHandler(sh)

    main(args)
