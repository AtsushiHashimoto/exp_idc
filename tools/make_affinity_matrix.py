#!/usr/bin/env python
# coding: utf-8

DESCRIPTION="convert feature list into affinity matrix"

import numpy as np
import argparse
import sklearn.metrics as sm
import logging

import sys
from os.path import dirname
sys.path.append(dirname(__file__))
from my_target_counter import TargetCounter

logger = logging.getLogger(__file__)


def find_nth_smallest(a, n):
    return np.partition(a.flatten(), n-1)[n-1]

def calc_stsc_metric(X):
    D = sm.pairwise.pairwise_distances(X, metric='euclidean')
    sigma = [find_nth_smallest(ds,7) for ds in D]
    W = [[np.exp(-d*d/(sigma[i]*sigma[j])) for i,d in enumerate(ds)] for j,ds in enumerate(D)]
    return np.array(W)

def calc_data_driven_scale_unit(X,scale_unit):
    D = sm.pairwise.pairwise_distances(X, metric='euclidean')
    if scale_unit=='median':
        return np.median(D)
    else:
        return find_nth_smallest(np.ravel(D),int(scale_unit))

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
        if args.metric=='euclidean':
            if args.gamma==None:
                W = calc_stsc_metric(X)
            else:

                W = sm.pairwise.rbf_kernel(X,gamma=args.gamma)
        elif args.metric=='cosine':
            W = (sm.pairwise.cosine_similarity(X)+1.0)/2 # normalize the affinity to [0,1]
            W[W<0]=0
        else:
            logger.warn("unknown metric '%s'."%args.metric)
        #W = sm.pairwise.pairwise_distances(X, Y=None, metric=args.metric)
        np.savetxt(dest_file,W,delimiter=",")



parser = argparse.ArgumentParser(description=DESCRIPTION)
parser.add_argument('metric', \
        action='store', \
        nargs=None, \
        const=None, \
        default='euclidean', \
        type=str, \
        choices=None, \
        help='Metric for affinity calculation (‘cosine’, ‘euclidean’) (default: euclidean)', \
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

parser.add_argument('--gamma', \
        action='store', \
        nargs=None, \
        const=None, \
        default=1.0, \
        type=float, \
        choices=None, \
        help='gamma for rbf_kernel.', \
        metavar=None)

parser.add_argument('-s','--scale_unit', \
        action='store', \
        nargs=None, \
        const=None, \
        default='median', \
        type=str, \
        choices=None, \
        help='Strategy to obtain a data-driven scale unit lamda (gamma*lamda is used as sigma rbf kernel). "median" or an int value (to use the n-th largest distance). (default:median)', \
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
