#!/usr/bin/env python
# coding: utf-8

import tempfile
import subprocess
import numpy as np
from os.path import dirname

class SelfTuningSpectralClustering():
    # src_pat ex.) "^.*/X_(\d{3}).csv$"
    def __init__(self,n_clusters_max):
        self.exe=dirname(__file__)+"/self_tuning_spectral_clustering"
        self.n_clusters_max=n_clusters_max

    def mktemp(self):
        return tempfile.TemporaryFile()
    def fit_predict(self,X):
        ftemp_y = tempfile.NamedTemporaryFile()
        ftemp_X = tempfile.NamedTemporaryFile()
        np.savetxt(ftemp_X.name,X,delimiter=',')
        command="%s %d %s %s"%(self.exe,int(self.n_clusters_max),ftemp_X.name,ftemp_y.name)
        print(command)
        p = subprocess.call( command, shell=True  )
        p.wait()
        y = np.loadtxt(ftemp_y.name,delimiter=',')
        return y
