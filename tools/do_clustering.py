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
from my_target_counter import TargetCounter

logger = logging.getLogger(__file__)


# HOW TO ADD NEW algorithm
# 1. add a process for your algorithm to 'get_model'
# 2. add a process to 'my_fit_predict' if the algorithm has outlier cluster and the outlier label is not 0.

#from memory_profiler import profile
#@profile
def main(args):
    src_dir = args.src_dir
    dest_dir = args.dest_dir

    src_pat = "W_(\d{3}).csv$"
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
    epsilon=0.1**100
    for id,src_file in zip(target_ids,src_files):
        dest_file = "%s/%s"%(args.dest_dir,tc.id2destfile(id))
        print(src_file)
        W = np.loadtxt(src_file,delimiter=",")
        if 'affinity' in src_dir:
        	W[W<epsilon]=epsilon
        y = my_fit_predict(model,W,args)
        np.savetxt(dest_file,y,fmt="%d")

def my_fit_predict(model,X,args):
    alg = args.algorithm
    y = model.fit_predict(X)
    if alg == 'DBSCAN':
        y = y+1 # DBSCAN uses -1 as outlier label, we treat 0 as the label.

    return y

def get_model(args):
    alg = args.algorithm
    if alg=='SC':
        from sklearn.cluster import SpectralClustering
        model = SpectralClustering(\
                    n_clusters=args.n_clusters,\
                    eigen_solver='arpack',\
                    random_state=None,\
                    affinity='precomputed',\
                    assign_labels='discretize',
                    n_jobs=1)
    elif alg=='IDC':
        from isolated_dense_clustering import IsolatedDenseClustering
        search_range = range(args.min_clusters,args.max_clusters)
        model = IsolatedDenseClustering(\
                                  search_range=search_range, \
                                  affinity='precomputed', \
                                  assign_labels='discretize',\
                                  n_jobs=1,\
                                  eigen_solver='arpack', \
                                  random_state=None)
    elif alg=='SG':
        pass
    elif alg=='STSC':
        import self_tuning_spectral_clustering
        pass
    elif alg=='MODULARITY':
        pass
    elif alg=='SEA':
        pass
    elif alg=='DBSCAN':
        from sklearn.cluster import DBSCAN
        model = DBSCAN(
            eps=args.eps,
            min_samples=args.min_samples,
            metric="precomputed")
    else:
        logger.warn("Unknown Algorithm '%s' is directed."%alg)
        sys.exit()
    return model



parser = argparse.ArgumentParser(description=DESCRIPTION)

parser.add_argument('algorithm', \
        action='store', \
        nargs=None, \
        const=None, \
        default=None, \
        type=str, \
        choices=None, \
        help='Clustering algorithm (SC|IDC|SG|STSC|MODULARITY|SEA|DBSCAN).', \
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
        help='Directory path where the formatted data will be located.', \
        metavar=None)

parser.add_argument('--n_clusters', \
        action='store', \
        nargs=None, \
        const=None, \
        default=None, \
        type=int, \
        choices=None, \
        help='Number of clusters.', \
        metavar=None)
parser.add_argument('--min_clusters',\
        action='store', \
        nargs=None, \
        const=None, \
        default=None, \
        type=int, \
        choices=None, \
        help='Minimum number of clusters to set the search range.', \
        metavar=None
        )
parser.add_argument('--max_clusters',\
        action='store', \
        nargs=None, \
        const=None, \
        default=None, \
        type=int, \
        choices=None, \
        help='Maximum number of clusters to set the search range.', \
        metavar=None
        )

parser.add_argument('--eps',\
        action='store', \
        nargs=None, \
        const=None, \
        default=0.5, \
        type=float, \
        choices=None, \
        help='eps for DBSCAN.', \
        metavar=None
        )
parser.add_argument('--min_samples',\
        action='store', \
        nargs=None, \
        const=None, \
        default=3, \
        type=int, \
        choices=None, \
        help='min_samples for DBSCAN.', \
        metavar=None
        )

parser.add_argument('--count_targets',\
        action="store_true", default=False, help='count processing targets, and exit.')


if __name__ == '__main__':
    args = parser.parse_args()

    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler()
    logger.addHandler(sh)
    main(args)
