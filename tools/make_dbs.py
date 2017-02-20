#!/usr/bin/env python
# coding: utf-8

DESCRIPTION="This script unifies the data format from different datasets."

import numpy as np
import argparse
import glob2
import gzip
import logging
import os.path
import json
import random

try:
   import cPickle as pickle
except:
   import pickle
PROTOCOL = pickle.HIGHEST_PROTOCOL

def get_dest_files(dest_dir,i):
    dest_X_file = "%s/X_%03d.csv"%(dest_dir,i)
    dest_y_file = "%s/y_%03d.dat"%(dest_dir,i)
    return dest_X_file,dest_y_file

def check_dest_files(dest_dir,i):
    dest_X_file,dest_y_file = get_dest_files(dest_dir,i)
    if os.path.exists(dest_X_file) and os.path.exists(dest_y_file):
        return None,None
    return dest_X_file,dest_y_file

def save_data(X,y,dest_X_file,dest_y_file):
    np.savetxt(dest_X_file,X,fmt="%.18e",delimiter=',')
    np.savetxt(dest_y_file,y,fmt="%d",delimiter=',')

def make_test_db(src_dir,dest_dir):
    files = glob2.glob("%s/*pickle.gz"%src_dir)
    for i,file in enumerate(files):
        dest_X_file,dest_y_file = check_dest_files(dest_dir,i)
        if None == dest_X_file:
            continue
        with open(file,"rb") as fin:
            data = pickle.loads(gzip.decompress(fin.read()))
        X = data['samples']
        y = data['labels']
        save_data(X,y,dest_X_file,dest_y_file)

def make_face_db(src_dir,dest_dir,n_clusters):
    files = sorted(glob2.glob("%s/num%02d/test*_sample_feature.csv"%(src_dir,n_clusters)))
    #print(files)
    for i,file in enumerate(files):
        dest_X_file,dest_y_file = check_dest_files(dest_dir,i)
        if None == dest_X_file:
            continue
        X = np.loadtxt(file,delimiter=',')
        src_y_file = "%s/num%02d/test%02d_groundtruth.txt"%(src_dir,n_clusters,i)
        data = csv.reader(open(src_y_file,'r'))
        y = [int(r[2]) for r in data]
        save_data(X,y,dest_X_file,dest_y_file)

def make_preid_db(src_dir,dest_dir,n_clusters):
    flatten = lambda l: [item for sublist in l for item in sublist]

    Xs = sorted(glob2.glob("%s/X_*.npy"%src_dir))
    ys = sorted(glob2.glob("%s/y_*.npy"%src_dir))
    Xys = [[np.load(X),np.load(y)] for X,y in zip(Xs,ys)]
    for t in range(0,100):
        dest_X_file,dest_y_file = get_dest_files(dest_dir,t)
        if None == dest_X_file:
            continue
        random.shuffle(Xys)
        # inliers
        X_ = []
        y_ = []
        meta = {'inliers':[],'outliers':[]}
        for i,(X,y) in enumerate(Xys[:n_clusters]):
            random.shuffle(X)
            #print("X:",X)
            #print("y:",y)

            sample_num = max(1,int(np.random.normal(8,1)))
            X_.append(np.array(X[0:max(1,min(sample_num,len(X)))]))
            y_ += [i+1]*sample_num
            meta['inliers'].append({'person_id':int(y[0]),'sample_num':sample_num})
        # outliers
        Xys_t_out = Xys[n_clusters:]
        outlier_person_num = len(Xys_t_out)
        # 0 < outlier_num <= 2*outlier_person_num
        outlier_num = min(max(1,int(np.random.normal(8,1))),2*outlier_person_num)
        #print("outlier_person_num=",outlier_person_num)
        #print("outlier_num       =",outlier_num)
        for i,(X,y) in enumerate(Xys_t_out):
            if i >= outlier_num:
                break
            #print("i,outlier_num",i,outlier_num)
            #print("outlier_person_num:",outlier_person_num)
            #print("outlier_num%outlier_person_num",outlier_num%outlier_person_num)
            #print("(i<outlier_num%outlier_person_num))",(i<outlier_num%outlier_person_num))
            sample_num = 1
            if outlier_num>outlier_person_num:
                sample_num += (i<outlier_num%outlier_person_num)
            #print("n_samples:", sample_num)
            random.shuffle(X)
            X_.append(np.mat(X[0:sample_num]))
            y_ += [0]*sample_num
            meta['outliers'].append({'person_id':int(y[0]),'sample_num':sample_num})
        #for X in X_:
        #    print("X.shape",X.shape)
        X__ = np.vstack(X_)
        #print("X__.shape",X__.shape)
        save_data(X__,np.array(y_),dest_X_file,dest_y_file)
        with open("%s/meta_%03d.json"%(dest_dir,t), 'w') as outfile:
            #print(meta)
            json.dump(meta, outfile)

def make_preid_mo_db(src_dir,dest_dir,n_clusters,rate_outliers):
    flatten = lambda l: [item for sublist in l for item in sublist]

    Xs = sorted(glob2.glob("%s/X_*.npy"%src_dir))
    ys = sorted(glob2.glob("%s/y_*.npy"%src_dir))
    Xys = [[np.load(X),np.load(y)] for X,y in zip(Xs,ys)]

    OutlierFiles = sorted(glob2.glob("%s/X_outliers*.npy"%src_dir))
    Outliers_temp = [np.load(f) for f in OutlierFiles]
    X_outliers = np.vstack(Outliers_temp)

    outlier_num = int(8*n_clusters*rate_outliers)
    for t in range(0,5):
        dest_X_file,dest_y_file = get_dest_files(dest_dir,t)
        if None == dest_X_file:
            continue
        random.shuffle(Xys)
        # inliers
        X_ = []
        y_ = []
        meta = {'inliers':[],'outliers':[]}
        for i,(X,y) in enumerate(Xys[:n_clusters]):
            random.shuffle(X)
            #print("X:",X)
            #print("y:",y)

            sample_num = max(1,int(np.random.normal(8,1)))
            X_.append(np.array(X[0:max(1,min(sample_num,len(X)))]))
            y_ += [i+1]*sample_num
            meta['inliers'].append({'person_id':int(y[0]),'sample_num':sample_num})
        X__ = np.vstack(X_)

        np.random.shuffle(X_outliers)
        #for X in X_:
        #    print("X.shape",X.shape)
        X_ = np.r_[X__, X_outliers[:outlier_num]]
        y_+= [0]*outlier_num
        #print("X__.shape",X__.shape)
        save_data(X_,np.array(y_),dest_X_file,dest_y_file)


def main(args,logger):
    src_dir=args.src_dir
    dest_dir=args.dest_dir

    if args.type=='test':
        make_test_db(src_dir,dest_dir)
    elif args.type=='face_feature':
        make_face_db(src_dir,dest_dir,args.n_clusters)
    elif args.type=='preid':
        make_preid_db(src_dir,dest_dir,args.n_clusters)
    elif args.type=='preid_mo':
        make_preid_mo_db(src_dir,dest_dir,args.n_clusters,args.rate_outliers)
    else:
        logger.warn("Unknown dataset type: '%s'."%args.type)



parser = argparse.ArgumentParser(description=DESCRIPTION)
parser.add_argument('type', \
        action='store', \
        nargs=None, \
        const=None, \
        default='test', \
        type=str, \
        choices=None, \
        help='Dataset name. It must be test|face|preid|.', \
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

parser.add_argument('-n','--n_clusters', \
        action='store', \
        nargs='?', \
        const=None, \
        default=None, \
        type=int, \
        choices=None, \
        help='Number of clusters',
        metavar=None)

parser.add_argument('-o','--rate_outliers', \
        action='store', \
        nargs='?', \
        const=None, \
        default=None, \
        type=float, \
        choices=None, \
        help='Rate of outliers',
        metavar=None)


if __name__ == '__main__':
    args = parser.parse_args()
    logger = logging.getLogger(__file__)
    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler()
    logger.addHandler(sh)

    main(args,logger)
