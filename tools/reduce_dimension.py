#!/usr/bin/env python
# coding: utf-8

DESCRIPTION="This script reduce dimensionality of input data."
#from memory_profiler import profile
import numpy as np
import argparse
from sklearn.decomposition import PCA
from sklearn.decomposition import NMF
import logging

import sys
from os.path import dirname
sys.path.append(dirname(__file__))
from my_target_counter import TargetCounter

logger = logging.getLogger(__file__)

#@profile
def main(args):
    src_dir = args.src_dir
    dist_dir = args.dist_dir
    src_pat = "X_(\d{3}).csv$"
    tar_template = "X_%s.csv"
    tc=TargetCounter(src_pat,tar_template,src_dir,dist_dir)
    target_ids,src_files = tc.listup_targets()
    n_targets = len(target_ids)
    if args.count_targets:
        print(len(target_ids))
        sys.exit()
    if n_targets==0:
        logger.warn("There are no before-process src files in '%s'"%src_dir)
        sys.exit()

    if args.algorithm == "pca":
        model = PCA(args.dimensions)
    elif args.algorithm == "nmf":
        model = NMF(args.dimensions,max_iter=args.max_iter)
    else:
        logger.warn("Unknown algorithm '%s'"%args.algorithm)
        sys.exit()
    for id,src_file in zip(target_ids,src_files):
        dist_file = "%s/%s"%(args.dist_dir,tc.id2distfile(id))
        print(id,src_file,dist_file)
        X=np.loadtxt(src_file,delimiter=",")
        model.fit(X)
        X_ = model.transform(X)
        np.savetxt(dist_file,X_,delimiter=",")

parser = argparse.ArgumentParser(description=DESCRIPTION)

parser.add_argument('dimensions', \
        action='store', \
        nargs=None, \
        const=None, \
        default=None, \
        type=int, \
        choices=None, \
        help='Dimensionality of target projection subspace', \
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
        help='Directory path where the dimension-reduced data will be located.', \
        metavar=None)




parser.add_argument('-a', '--algorithm', \
        action='store', \
        nargs='?', \
        const=None, \
        default='pca', \
        type=str, \
        choices=None, \
        help='Algorithm for dimension reduction. pca|nmf are supported (default: pca)', \
        metavar=None)
parser.add_argument('-M', '--max_iter', \
        action='store', \
        nargs='?', \
        const=None, \
        default=1000, \
        type=int, \
        choices=None, \
        help='Maximum iteration number. (default: 1000)', \
        metavar=None)

parser.add_argument('--count_targets',\
        action="store_true", default=False, help='count processing targets, and exit.')

if __name__ == '__main__':
    args = parser.parse_args()
    logger = logging.getLogger(__file__)
    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler()
    logger.addHandler(sh)

    main(args)
