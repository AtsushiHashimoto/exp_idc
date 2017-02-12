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
import self_tuning_spectral_clustering

global logger = logging.getLogger(__file__)
global r = re.compile("^.*/X_(\d{3}).csv$")

@profile
def main(args):
    src_dir = args.src_dir
    dist_dir = args.dist_dir
    targets = get_targets(src_dir,dist_dir)

    if len(targets)==0:
        return

    model = get_model(args)
    for t in targets:
        X=np.load("%s/X_%s.csv"%(src_dir,t))
        y=model.fit_predict(X)
        np.save("%s/%s"%(dist_dir,id2distfile(t)),y)

def get_model(args):
    alg = args.algorithm
    if alg=='IDC':

    elif arg=='SC':
        model =
    elif arg=='DBSCAN':
    elif arg=='MODULARITY':
    else:
        logger.warn("Unknown Algorithm '%s' is directed."%alg)

def extract_trial_id(src_file):
    m = r.search(src_file)
    if m==None:
        return None
    return m.group(1)
def id2distfile(id):
    return "y_%s.dat"%id

def get_targets(src_dir,dist_dir):
    targets = map(extract_trial_id,glob2.glob("%s/*.csv"%src_dir))
    targets = [t for t in targets if t!=None]
    print("targets: ",targets)
    completes = map(basename,glob2.glob("%s/*.dat"%dist_dir))
    print("completes: ",completes)
    return [t for t in targets if id2distfile(t) not in completes]


parser = argparse.ArgumentParser(description=DESCRIPTION)
parser.add_argument('n_clusters' \
        action='store', \
        nargs=None, \
        const=None, \
        default=None, \
        type=int, \
        choices=None, \
        help='Number of clusters.', \
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
    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler()
    logger.addHandler(sh)
    main(args)
