#!/usr/bin/env python
# coding: utf-8

DESCRIPTION="This script do sparse encoding."
from memory_profiler import profile
import sys

import numpy as np
import argparse
import logging
import random
from sklearn.decomposition import sparse_encode


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


@profile
def main(args,logger):
    X=np.loadtxt(args.src_file,delimiter=",")
    X_ = my_sparse_encode(X,args.alpha,args.method,args.num_references)
    np.savetxt(args.dist_file,X_,delimiter=",")



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

parser.add_argument('src_file', \
        action='store', \
        nargs=None, \
        const=None, \
        default=None, \
        type=str, \
        choices=None, \
        help='File path where the source data are located.', \
        metavar=None)

parser.add_argument('dist_file', \
        action='store', \
        nargs=None, \
        const=None, \
        default=None, \
        type=str, \
        choices=None, \
        help='File path where the dimension-reduced data will be located.', \
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


if __name__ == '__main__':
    args = parser.parse_args()
    logger = logging.getLogger(__file__)
    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler()
    logger.addHandler(sh)

    main(args,logger)
