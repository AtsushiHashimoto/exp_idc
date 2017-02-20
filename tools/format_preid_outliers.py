#!/usr/bin/env python
# coding: utf-8

DESCRIPTION="This script unifies the data format from non-shinpuhkan datasets as outliers"

import numpy as np
import argparse
import glob2
import logging
import os.path
import random

logger = logging.getLogger(__file__)


def sample_persons(src_dir):
    flatten = lambda l: [item for sublist in l for item in sublist]
    y_files = sorted(glob2.glob("%s/test_*_labels.npy"%src_dir))
    y = flatten([np.load(f) for f in y_files])
    X_files = sorted(glob2.glob("%s/test_*_features.npy"%src_dir))
    temp = flatten([np.load(f) for f in X_files])
    X = np.r_[temp]


    labels = set(y)
    feature_dict = {l:[] for l in labels}
    for y, X in zip(y,X):
        feature_dict[y].append(X)

    X_outliers = []
    for y, Xs in feature_dict.items():
        random.shuffle(Xs)
        X_outliers.append(Xs[0])
    return X_outliers


def main(args):
    src_dir=args.src_dir
    dest_file=args.dest_file
    X_outliers = sample_persons(src_dir)
    print("dest_file:",dest_file)
    np.save(dest_file,X_outliers)



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

parser.add_argument('dest_file', \
        action='store', \
        nargs=None, \
        const=None, \
        default=None, \
        type=str, \
        choices=None, \
        help='File path where the formatted data will be located.', \
        metavar=None)

if __name__ == '__main__':
    args = parser.parse_args()
    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler()
    logger.addHandler(sh)

    main(args)
