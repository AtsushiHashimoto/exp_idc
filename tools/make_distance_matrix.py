#!/usr/bin/env python
# coding: utf-8

DESCRIPTION="convert feature list into distance matrix"

import numpy as np
import argparse
import sklearn.metrics as sm
import logging

import sys
from os.path import dirname
sys.path.append(dirname(__file__))
from my_target_counter import TargetCounter

logger = logging.getLogger(__file__)

def main(args):
    src_dir = args.src_dir
    dest_dir = args.dest_dir
    src_pat = "X_(\d{3}).csv$"
    tar_template = "W_%s.csv"
    tc=TargetCounter(src_pat,tar_template,src_dir,dest_dir)
    target_ids,src_files = tc.listup_targets()
    n_targets = len(target_ids)
    if args.count_targets:
        print(len(target_ids))
        sys.exit()
    if n_targets==0:
        logger.warn("There are no before-process src files in '%s'"%src_dir)
        sys.exit()


    for id,src_file in zip(target_ids,src_files):
        dest_file = "%s/%s"%(args.dest_dir,tc.id2destfile(id))
        #print(id,src_file,dest_file)
        X=np.loadtxt(src_file,delimiter=",")
        W = sm.pairwise.pairwise_distances(X, Y=None, metric=args.metric)

        np.savetxt(dest_file,W,delimiter=",")



parser = argparse.ArgumentParser(description=DESCRIPTION)
parser.add_argument('metric', \
        action='store', \
        nargs=None, \
        const=None, \
        default='euclidean', \
        type=str, \
        choices=None, \
        help='Metric for distance calculation, supported by scikit-learn (see http://scikit-learn.org/stable/modules/generated/sklearn.metrics.pairwise.pairwise_distances.html) (default: euclidean)', \
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

parser.add_argument('dest_dir', \
        action='store', \
        nargs=None, \
        const=None, \
        default=None, \
        type=str, \
        choices=None, \
        help='Directory path where the dimension-reduced data will be located.', \
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
