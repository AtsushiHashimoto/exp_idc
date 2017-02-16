#!/usr/bin/env python
# coding: utf-8

DESCRIPTION="This script applies clustering"

import numpy as np
import argparse
import glob2
import logging
import re
from os.path import basename
from os.path import dirname
import sys

sys.path.append(dirname(__file__))
import my_target_counter
import self_tuning_spectral_clustering


@profile
def main(args):
    src_dir = args.src_dir
    dest_dir = args.dest_dir
    src_pat = "X_(\d{3}).csv$"
    tar_template = "y_%s.dat"
    tc=TargetCounter(src_pat,tar_template,src_dir,dest_dir)
    target_ids,src_files = tc.listup_targets()
    n_targets = len(target_ids)
    if args.count_targets:
        print(len(target_ids))
        sys.exit()
    if n_targets==0:
        logger.warn("There are no before-process src files in '%s'"%src_dir)
        sys.exit()

    model = get_model(args)

    for t in targets:
        X=np.load("%s/X_%s.csv"%(src_dir,t))
        y=model.fit_predict(X)
        np.save("%s/%s"%(dest_dir,id2destfile(t)),y)

def get_model(args):
    alg = args.algorithm
    if alg=='IDC':

    elif arg=='SC':
        model =
    elif arg=='DBSCAN':
    elif arg=='MODULARITY':
    else:
        logger.warn("Unknown Algorithm '%s' is directed."%alg)




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

parser.add_argument('--n_clusters' \
        action='store', \
        nargs=None, \
        const=None, \
        default=None, \
        type=int, \
        choices=None, \
        help='Number of clusters.', \
        metavar=None)




if __name__ == '__main__':
    args = parser.parse_args()

    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler()
    logger.addHandler(sh)
    main(args)
