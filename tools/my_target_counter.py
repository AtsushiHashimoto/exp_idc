#!/usr/bin/env python
# coding: utf-8

import glob2
import logging
import re
from os.path import basename
from os.path import dirname

class TargetCounter():
    # src_pat ex.) "^.*/X_(\d{3}).csv$"
    def __init__(self,src_file_pat,dest_file_template,src_dir,dest_dir):
        self.r = re.compile(src_file_pat)
        self.dest_file_template = dest_file_template
        self.src_dir = src_dir
        self.dest_dir = dest_dir

    def listup_targets(self):
        src_files = sorted(glob2.glob("%s/*"%self.src_dir))
        

        targets = map(self.extract_trial_id,\
                      src_files)
        temp = [(t,f) for t,f in zip(targets,src_files) if t!=None]
        targets = [t[0] for t in temp]
        src_files = [t[1] for t in temp]
        #print("targets: ",targets)
        completes = list(map(basename,glob2.glob("%s/*"%self.dest_dir)))
        #print("completes: ",completes)
        return [t for t in targets if self.id2destfile(t) not in completes], src_files

    def extract_trial_id(self,src_file):
        m = self.r.search(src_file)
        if m==None:
            return None
        return m.group(1)

    def id2destfile(self,id):
        return self.dest_file_template%id
