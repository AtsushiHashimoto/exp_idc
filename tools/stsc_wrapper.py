#!/usr/bin/env python
# coding: utf-8

import tempfile
import subprocess
from os.path import dirname

class SelfTuningSpectralClustering():
    # src_pat ex.) "^.*/X_(\d{3}).csv$"
    def __init__(self,n_clusters_max):
        self.exe=dirname(__file__)+"/self_tuning_spectral_clustering"
        self.n_clusters_max=n_clusters_max

    def mktemp(self):
        return tempfile.TemporaryFile()
    def fit_predict(self,X):
        with tempfile.TemporaryFile() as ftemp_out:
            with tempfile.TemporaryFile() as ftemp:
                numpy.savetxt(ftemp.name,X,delimiter=',')
                command="%s %d %s"%(self.exe,self.n_clusters_max,ftemp.name,ftemp_out.name)
                print(command)
                subprocess.call( command, shell=True  )
            y = np.loadtxt(ftemp_out.name,delimiter=',')
        return y
