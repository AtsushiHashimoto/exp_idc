#!/usr/bin/env python
# coding: utf-8

DESCRIPTION="This script do sparse encoding."
#from memory_profiler import profile

import numpy as np
import argparse
import logging
import random
from sklearn.decomposition import sparse_encode

import sys
from os.path import dirname
sys.path.append(dirname(__file__))
from my_target_counter import TargetCounter

logger = logging.getLogger(__file__)

def my_sparse_encode(X,alpha,method,n_references):
  refs = list(range(X.shape[0]))
  random.shuffle(refs)
  if 0<=n_references:
     # use limited number of samples for space coding (if n_references is directed)
     refs = refs[:n_references]

  X_sparse = np.zeros((X.shape[0],len(refs)))
  references = np.array([X[i] for i in refs])
  for i in range(X.shape[0]):
     if i in refs:
        idx = refs.index(i)
        x_sps = sparse_encode([X[i]],\
                              np.r_[references[:idx],np.array([[0]*X.shape[1]]),references[idx+1:]],\
                              algorithm=method,\
                              alpha=alpha,\
                              n_jobs=1)[0]
        X_sparse[i] = x_sps
     else:
        X_sparse[i] = sparse_encode([X[i]],references,algorithm=method,alpha=alpha,n_jobs=1)[0]
  X_sparse = np.array(X_sparse)
  return X_sparse


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

    for id,src_file in zip(target_ids,src_files):
        dist_file = "%s/%s"%(args.dist_dir,tc.id2distfile(id))
        X=np.loadtxt(src_file,delimiter=",")
        X_ = my_sparse_encode(X,args.alpha,args.method,args.num_references)
        np.savetxt(dist_file,X_,delimiter=",")



parser = argparse.ArgumentParser(description=DESCRIPTION)

parser.add_argument('alpha', \
        action='store', \
        nargs=None, \
        const=None, \
        default=None, \
        type=float, \
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

parser.add_argument('-m', '--method', \
        action='store', \
        nargs='?', \
        const=None, \
        default='lasso_lars', \
        type=str, \
        choices=None, \
        help='Method for sparse coding. lasso_lars|lasso_cd|lars|omp|threshold are supported (default: lasso_lars)', \
        metavar=None)

parser.add_argument('-r','--num_references', \
        action='store', \
        nargs=None, \
        const=None, \
        default=-1, \
        type=int, \
        choices=None, \
        help='Number of reference in the sample used as dictionary for sparse coding. set <0 to use all data as dictionary.(default: -1)', \
        metavar=None)

parser.add_argument('--count_targets',\
        action="store_true", default=False, help='count processing targets, and exit.')

if __name__ == '__main__':
    args = parser.parse_args()
    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler()
    logger.addHandler(sh)

    main(args)
