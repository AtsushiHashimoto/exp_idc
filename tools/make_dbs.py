#!/usr/bin/env python
# coding: utf-8

DESCRIPTION="This script unifies the data format from different datasets."
from memory_profiler import profile

import numpy as np
import argparse
import glob2
import gzip
import logging


try:
   import cPickle as pickle
except:
   import pickle
PROTOCOL = pickle.HIGHEST_PROTOCOL


@profile
def make_test_db(src_dir,dist_dir):
    files = glob2.glob("%s/*pickle.gz"%src_dir)
    for i,file in enumerate(files):
        with open(file,"rb") as fin:
            data = pickle.loads(gzip.decompress(fin.read()))
        X = data['samples']
        np.savetxt("%s/X_%03d.csv"%(dist_dir,i),X,fmt="%.18e",delimiter=',')
        y = data['labels']
        np.savetxt("%s/y_%03d.dat"%(dist_dir,i),y,fmt="%d",delimiter=',')

def main(args,logger):
    src_dir=args.src_dir
    dist_dir=args.dist_dir
    if args.type=='test':
        make_test_db(src_dir,dist_dir)
    elif args.type=='face':
        pass
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



if __name__ == '__main__':
    args = parser.parse_args()
    logger = logging.getLogger(__file__)
    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler()
    logger.addHandler(sh)

    main(args,logger)
