#!/usr/bin/env python
# coding: utf-8

DESCRIPTION="This script applies clustering"

import numpy as np
import argparse
import logging
import re
from os.path import dirname
import sys
import json
import pandas as pd

sys.path.append(dirname(__file__))
from my_target_counter import TargetCounter
from my_clustering_evaluator import ClusteringEvaluator, criteria
logger = logging.getLogger(__file__)


#@profile
def main(args):
    src_dirs = args.src_dirs

    ground_truth_dir = args.ground_truth_dir
    dest_file = args.dest_file


    src_pat = "y_(\d{3}).dat"
    tar_file = "y_%s." + "%s.dat"%args.target
    tc=TargetCounter(src_pat,tar_file,ground_truth_dir,dirname(dest_file))

    target_ids,gt_files = tc.listup_targets()
    n_targets = len(target_ids)

    if args.count_targets:
        print(n_targets)
        sys.exit()
    if n_targets==0:
        logger.warn("There are no before-process src files in '%s'"%ground_truth_dir)
        sys.exit()

    df_columns = criteria()

    scorer = ClusteringEvaluator(df_columns)
    df = pd.DataFrame([[0.0]*len(df_columns)]*len(src_dirs))
    df.columns = df_columns
    df.index = src_dirs

    # results[path][id] = score
    for src_dir in src_dirs:
        for id,gt_file in zip(target_ids,gt_files):
            y_gt = np.loadtxt(gt_file,delimiter=",")
            y_est_file = "%s/%s"%(src_dir,tc.id2destfile(id))
            y_est = np.loadtxt(y_est_file,delimiter=',')
            scores = scorer.evaluate(y_gt,y_est)
            for key,score in scores.items():
                df[key][src_dir] += score/n_targets

    df.to_csv(dest_file)


parser = argparse.ArgumentParser(description=DESCRIPTION)

parser.add_argument('ground_truth_dir',\
        action='store', \
        nargs=None, \
        const=None, \
        default=None, \
        type=str, \
        choices=None, \
        help='Directory path where the ground truth are located.', \
        metavar=None)

parser.add_argument('dest_file', \
        action='store', \
        nargs=None, \
        const=None, \
        default=None, \
        type=str, \
        choices=None, \
        help='File path where the summery will be located.', \
        metavar=None)

parser.add_argument('src_dirs', \
        action='store', \
        nargs='+', \
        const=None, \
        default=None, \
        type=str, \
        choices=None, \
        help='Directory paths where evaluation target results are located.', \
        metavar=None)


parser.add_argument('-t','--target',\
        action='store', \
        nargs=None, \
        const=None, \
        default='cross_validated', \
        type=str, \
        choices=None, \
        help='Set evaluation target (cross_validated|closed_best) (default: cross_validated).', \
        metavar=None)


parser.add_argument('--count_targets',\
        action="store_true", default=False, help='count processing targets, and exit.')

if __name__ == '__main__':
    args = parser.parse_args()

    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler()
    logger.addHandler(sh)
    main(args)
