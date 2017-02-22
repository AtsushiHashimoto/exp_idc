#!/usr/bin/env python
# coding: utf-8

DESCRIPTION="This script applies clustering"

import numpy as np
import argparse
import glob2
import logging
import re
import os.path
import sys
import json
import random

sys.path.append(os.path.dirname(__file__))
from my_target_counter import TargetCounter
from my_clustering_evaluator import ClusteringEvaluator
logger = logging.getLogger(__file__)

'''
def split_path_all(path):
    dirs = []
    while 1:
        path,dir=os.path.split(path)
        if dir != "":
            dirs.append(dir)
        else:
            if path != "":
                dirs.append(path)
            break
    dirs.reverse()
    return dirs
'''
def add_results(results,dest):
    # results[path][id] = score
    for (score,path) in results:
        if path not in dest.keys():
            dest[path]=[]
        dest[path].append(score)
    return dest

def get_results(src_paths,id,y_gt,scorer):
    '''
    for src_path in src_paths:
        print("%s/y_%s.dat"%(src_path,id))
        print(scorer.evaluate(y_gt,np.loadtxt("%s/y_%s.dat"%(src_path,id))))
    '''

    results = [(scorer.evaluate(y_gt,np.loadtxt("%s/y_%s.dat"%(src_path,id))),src_path) \
                for src_path in src_paths]
    '''
    for score,path in results:
        print(score)
        print(path)
        print("score: %0.3f with %s"%(score,path))
    '''
    return results

def cross_validation(results,t_id):
    n_paths = len(results)
    sum_scores = [(sum(score_list)-score_list[int(t_id)],path) for path,score_list in results.items()]
    return max(sum_scores,key=(lambda x:x[0]))[1]

#@profile
def main(args):
    src_paths = glob2.glob(args.src_glob_path+"/")
    if len(src_paths)==0:
        logger.warn("No result files are found in path '%s'"%args.src_glob_path)
        sys.exit()
    #print(src_paths)

    ground_truth_dir = args.ground_truth_dir
    dest_dir = args.dest_dir
    criterion = args.criterion

    src_pat = "y_(\d{3}).dat"
    tar_template_final = "y_%s.cross_validated.dat"
    tc=TargetCounter(src_pat,tar_template_final,ground_truth_dir,dest_dir)

    target_ids,gt_files = tc.listup_targets()
    n_targets = len(target_ids)

    if args.count_targets:
        print(len(target_ids))
        sys.exit()
    if n_targets==0:
        logger.warn("There are no before-process src files in '%s'"%src_paths[0])
        sys.exit()

    # exchange tar_template to temporary result.
    tar_template_temp = "y_%s.closed_best.dat"
    tc=TargetCounter(src_pat,tar_template_temp,ground_truth_dir,dest_dir)

    scorer = ClusteringEvaluator(criterion,return_type=float)
    closed_best_results = []

    all_results={}
    # results[path][id] = score
    for id,gt_file in zip(target_ids,gt_files):
        dest_file = "%s/%s"%(args.dest_dir,tc.id2destfile(id))
        print(dest_file)
        y_gt = np.loadtxt(gt_file,delimiter=",")
        results = get_results(src_paths,id,y_gt,scorer)
        add_results(results,all_results)

        best = max(results,key=(lambda x:x[0]))
        # save y_est as the closed best
        y_est = np.loadtxt("%s/y_%s.dat"%(best[1],id))
        np.savetxt(dest_file,y_est,fmt="%d")


    with open("%s/summary_%s.json"%(dest_dir,criterion),"w") as fout:
        fout.write(json.dumps(all_results))

    # change back the tar_template to final result.
    tc=TargetCounter(src_pat,tar_template_final,src_paths[0],dest_dir)

    cv_paths = []
    for id in target_ids:
        dest_file = "%s/%s"%(args.dest_dir,tc.id2destfile(id))
        path = cross_validation(all_results,id)
        cv_paths.append(path)
        file_name = "%s/y_%s.dat"%(path,id)
        y_est = np.loadtxt(file_name,delimiter=",")
        np.savetxt(dest_file,y_est,fmt="%d")

    with open("%s/cross_validated_paths.dat"%(dest_dir),"w") as fout:
        fout.write("\n".join(cv_paths))

    # save random result
    tar_template_temp = "y_%s.random.dat"
    tc=TargetCounter(src_pat,tar_template_temp,ground_truth_dir,dest_dir)
    for id,gt_file in zip(target_ids,gt_files):
        dest_file = "%s/%s"%(args.dest_dir,tc.id2destfile(id))
        random.shuffle(src_paths)
        y_est = np.loadtxt("%s/y_%s.dat"%(src_paths[0],id))
        np.savetxt(dest_file,y_est,fmt="%d")

parser = argparse.ArgumentParser(description=DESCRIPTION)

parser.add_argument('src_glob_path', \
        action='store', \
        nargs=None, \
        const=None, \
        default=None, \
        type=str, \
        choices=None, \
        help='Path without variables.', \
        metavar=None)

parser.add_argument('ground_truth_dir',\
        action='store', \
        nargs=None, \
        const=None, \
        default=None, \
        type=str, \
        choices=None, \
        help='Directory path where the ground truth are located.', \
        metavar=None)

parser.add_argument('dest_dir', \
        action='store', \
        nargs=None, \
        const=None, \
        default=None, \
        type=str, \
        choices=None, \
        help='Directory path where the chosen results and parameters will be located.', \
        metavar=None)

parser.add_argument('-c','--criterion',\
        action='store', \
        nargs=None, \
        const=None, \
        default='AMI', \
        type=str, \
        choices=None, \
        help='Criterion used to select the best result. ARI|NRI|MI|AMI|PURITY|F1 (default: AMI).', \
        metavar=None        )

parser.add_argument('--count_targets',\
        action="store_true", default=False, help='count processing targets, and exit.')

if __name__ == '__main__':
    args = parser.parse_args()

    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler()
    logger.addHandler(sh)
    main(args)
