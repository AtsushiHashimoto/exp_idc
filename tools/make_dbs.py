#!/usr/bin/env python
# coding: utf-8

DESCRIPTION="This script unifies the data format from different datasets."

import numpy as np
import argparse
import glob2
import gzip
import logging
import os.path

try:
   import cPickle as pickle
except:
   import pickle
PROTOCOL = pickle.HIGHEST_PROTOCOL


def make_test_db(src_dir,dist_dir):
    files = glob2.glob("%s/*pickle.gz"%src_dir)
    for i,file in enumerate(files):
        dist_file = "%s/X_%03d.csv"%(dist_dir,i)
        if os.path.exists(dist_file):
            continue
        with open(file,"rb") as fin:
            data = pickle.loads(gzip.decompress(fin.read()))
        X = data['samples']
        np.savetxt("%s/X_%03d.csv"%(dist_dir,i),X,fmt="%.18e",delimiter=',')
        y = data['labels']
        np.savetxt(dist_file,y,fmt="%d",delimiter=',')

def make_face_db(src_dir,dist_dir,n_clusters):
    files = sorted(glob2.glob("%s/num%s/test*"%(src_dir,n_clusters)))
    for i,file in enumerate(files):
        dist_file = "%s/X_%03d.csv"%(dist_dir,i)
        if os.path.exists(dist_file):
            continue
        print("src_file: %s"%file)
        print("dist_file: %s"%dist_file)
        X = np.loadtxt(file,delimiter=',')
        np.savetxt(dist_file,X,fmt="%.18e",delimiter=',')

def main(args,logger):
    src_dir=args.src_dir
    dist_dir=args.dist_dir
    if args.type=='test':
        make_test_db(src_dir,dist_dir)
    elif args.type=='face_feature':
        make_face_db(src_dir,dist_dir,args.n_clusters)
    elif args.type=='preid':
        pass
    else:
        logger.warn("Unknown dataset type: '%s'."%args.type)



parser = argparse.ArgumentParser(description=DESCRIPTION)
parser.add_argument('type', \
        action='store', \
        nargs=None, \
        const=None, \
        default='test', \
        type=str, \
        choices=None, \
        help='Dataset name. It must be test|face|preid|.', \
        metavar=None)

parser.add_argument('src_dir', \
        action='store', \
        nargs=None, \
        const=None, \
        default=None, \
        type=str, \
        choices=None, \
        help='Directory path where the source data are located.', \
        metavar=None)

parser.add_argument('dist_dir', \
        action='store', \
        nargs=None, \
        const=None, \
        default=None, \
        type=str, \
        choices=None, \
        help='Directory path where the formatted data will be located.', \
        metavar=None)

parser.add_argument('-n','--n_clusters', \
        action='store', \
        nargs='?', \
        const=None, \
        default=None, \
        type=str, \
        choices=None, \
        help='Number of clusters',
        metavar=None)


if __name__ == '__main__':
    args = parser.parse_args()
    logger = logging.getLogger(__file__)
    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler()
    logger.addHandler(sh)

    main(args,logger)
