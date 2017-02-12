#!/usr/bin/env python
# coding: utf-8

import glob2
import logging
import re
from os.path import basename
from os.path import dirname

class TargetCounter():
    # src_pat ex.) "^.*/X_(\d{3}).csv$"
    def __init__(self,src_file_pat,dist_file_template,src_dir,dist_dir):
        self.r = re.compile(src_file_pat)
        self.dist_file_template = dist_file_template
        self.src_dir = src_dir
        self.dist_dir = dist_dir

    def listup_targets(self):
        src_files = glob2.glob("%s/*"%self.src_dir)
        targets = map(self.extract_trial_id,\
                      src_files)
        temp = [(t,f) for t,f in zip(targets,src_files) if t!=None]
        targets = [t[0] for t in temp]
        src_files = [t[1] for t in temp]
        #print("targets: ",targets)
        completes = list(map(basename,glob2.glob("%s/*"%self.dist_dir)))
        #print("completes: ",completes)
        return [t for t in targets if self.id2distfile(t) not in completes], src_files

    def extract_trial_id(self,src_file):
        m = self.r.search(src_file)
        if m==None:
            return None
        return m.group(1)

    def id2distfile(self,id):
        return self.dist_file_template%id
