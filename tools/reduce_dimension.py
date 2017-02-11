#!/usr/bin/env python
# coding: utf-8

DESCRIPTION="This script reduce dimensionality of input data."
#from memory_profiler import profile
import sys
import numpy as np
import argparse
from sklearn.decomposition import PCA
from sklearn.decomposition import NMF
import logging


#@profile
def main(args,logger):
    if args.algorithm == "pca":
        model = PCA(args.dimensions)
    elif algs.algorithm == "nmf":
        model = NMF(args.dimensions,max_iter=args.max_iter)
    else:
        logger.warn("Unknown algorithm '%s'"%args.algorithm)
        sys.exit()
    X=np.loadtxt(args.src_file,delimiter=",")
    model.fit(X)
    X_ = model.transform(X)
    np.savetxt(args.dist_file,X_,delimiter=",")

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

if __name__ == '__main__':
    args = parser.parse_args()
    logger = logging.getLogger(__file__)
    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler()
    logger.addHandler(sh)

    main(args,logger)
