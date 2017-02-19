#!/usr/bin/env python
# coding: utf-8

import glob2
import logging
import re
from os.path import basename
from os.path import dirname
import sklearn.metrics as sm

class ClusteringEvaluator():
    # src_pat ex.) "^.*/X_(\d{3}).csv$"
    def __init__(self,criteria,return_type=dict):
        if isinstance(criteria,str):
            self.criteria=[criteria]
        elif isinstance(criteria,list):
            self.criteria = criteria
        else:
            self.criteria = None
        self.return_type = return_type

    def evaluate(self, y_gt,y_est):
        scores = {}
        if 'AMI' in self.criteria:
            scores['AMI'] = sm.adjusted_mutual_info_score(y_gt,y_est)
        if 'ARI' in self.criteria:
            scores['ARI'] = sm.adjusted_rand_score(y_gt,y_est)
        if 'COMP' in self.criteria:
            scores['COMP'] = sm.completeness_score(y_gt,y_est)
        if 'FMS' in self.criteria:
            scores['FMS'] = sm.fowlkes_mallows_score(y_gt,y_est)
        if 'HCVM' in self.criteria:
            scores['HCVM'] = sm.homogeneity_completeness_v_measure(y_gt,y_est)
        if 'HS' in self.criteria:
            scores['HS'] = sm.homogeneity_score(y_gt,y_est)
        if 'MI' in self.criteria:
            scores['MI'] = sm.mutual_info_score(y_gt,y_est)
        if 'NMI' in self.criteria:
            scores['NMI'] = sm.normalized_mutual_info_score(y_gt,y_est)
        if 'VMS' in self.criteria:
            scores['VMS'] = sm.v_measure_score(y_gt,y_est)
        if 'PURITY' in self.criteria:
            scores['PURITY'] = self.purity(y_gt,y_est)
        # for inlier/outlier classification
        if 'F1' in self.criteria:
            scores['F1'] = self.F1score(y_gt,y_est)
        return self.conv_return_type(scores)
        
    def conv_return_type(self,scores):
        if self.return_type==dict:
            return scores
        elif self.return_type==list:
            return [score for key,score in scores.items()]
        else:
            if len(scores)>1:
                warn("Only the first score is returned, other calculated scores are ignored.")
            return self.return_type([score for key,score in scores.items()][0])

    def F1score(self,y_gt,y_est):
        y_gt_bin = y_gt > 0
        y_est_bin = y_est > 0
        return sm.f1_score(y_gt_bin,y_est_bin)

    def purity(self,y_gt,y_est):
        A = np.c_[(y_est,y_gt)]
        n_accurate = 0.
        for j in np.unique(A[:,0]):
            z = A[A[:,0] == j, 1]
            x = np.argmax(np.bincount(z))
            n_accurate += len(z[z == x])
        return n_accurate / A.shape[0]
