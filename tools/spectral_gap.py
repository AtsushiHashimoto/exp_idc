#!/usr/bin/env python
# coding: utf-8

import tempfile
import subprocess
from os.path import dirname
from sklearn.base import BaseEstimator, ClusterMixin
from sklearn.utils import check_random_state
from sklearn.utils.validation import check_array
from sklearn.metrics.pairwise import pairwise_kernels
from sklearn.neighbors import kneighbors_graph
from spectral_embedding import spectral_embedding
from sklearn.cluster.k_means_ import k_means
from sklearn.cluster.spectral import discretize

class SpectralClusteringSG(BaseEstimator, ClusterMixin):
    # src_pat ex.) "^.*/X_(\d{3}).csv$"
    def __init__(self,
            max_clusters,\
            n_init=10, gamma=1., n_neighbors=10,\
            eigen_tol=0.0, degree=3, coef0=1,
            kernel_params = None
            eigen_solver = 'arpack',\
            random_state = 0, \
            affinity = 'precomputed',\
            assign_labels = 'discretize'):
        self.max_clusters = max_clusters
        self.n_init = n_init
        self.gamma = gamma
        self.n_neighbors = n_neighbors
        self.eigen_tol = eigen_tol
        self.degree = degree
        self.coef0=coef0
        self.kernel_params = kernel_params
        self.eigen_solver = eigen_solver
        self.random_state = random_state
        self.affinity = affinity
        self.assign_labels = assign_labels

    def estimate_num_of_clusters(self,lambdas_list):
        dif = list()
        for i in range(1, len(lambdas_list)-1):
            lambda_K0 = lambdas_list[i]
            lambda_K1 = lambdas_list[i+1]
            dif.append(lambda_K0 - lambda_K1)
        return dif.index(max(dif))+2

    def fit(self,X,y=None):
        X = check_array(X, accept_sparse=['csr', 'csc', 'coo'],
                        dtype=np.float64)
        if X.shape[0] == X.shape[1] and self.affinity != "precomputed":
            warnings.warn("The spectral clustering API has changed. ``fit``"
                          "now constructs an affinity matrix from data. To use"
                          " a custom affinity matrix, "
                          "set ``affinity=precomputed``.")

        if self.affinity == 'nearest_neighbors':
            connectivity = kneighbors_graph(X, n_neighbors=self.n_neighbors, include_self=True)
            self.affinity_matrix_ = 0.5 * (connectivity + connectivity.T)
        elif self.affinity == 'precomputed':
            self.affinity_matrix_ = X
        else:
            params = self.kernel_params
            if params is None:
                params = {}
            if not callable(self.affinity):
                params['gamma'] = self.gamma
                params['degree'] = self.degree
                params['coef0'] = self.coef0
            self.affinity_matrix_ = pairwise_kernels(X, metric=self.affinity,
                                                     filter_params=True,
                                                     **params)

        random_state = check_random_state(self.random_state)
        self.labels_ = self.spectral_clustering_sg(self.affinity_matrix_,
                                           n_clusters=self.max_clusters,
                                           eigen_solver=self.eigen_solver,
                                           random_state=random_state,
                                           n_init=self.n_init,
                                           eigen_tol=self.eigen_tol,
                                           assign_labels=self.assign_labels)
        return self



    def spectral_clustering_sg(affinity, max_clusters=8, n_components=None,
                            eigen_solver=None, random_state=None, n_init=10,
                            eigen_tol=0.0, assign_labels='kmeans'):

        if assign_labels not in ('kmeans', 'discretize'):
            raise ValueError("The 'assign_labels' parameter should be "
                             "'kmeans' or 'discretize', but '%s' was given"
                             % assign_labels)

        random_state = check_random_state(random_state)
        n_components = max_clusters if max_components is None else n_components
        maps, lambdas = spectral_embedding(affinity, n_components=n_components,
                                  eigen_solver=eigen_solver,
                                  random_state=random_state,
                                  eigen_tol=eigen_tol, drop_first=False)

        # determin n_clusters by Spectral Gap HERE!!
        n_clusters = self.estimate_num_of_clusters(lambdas)
        if assign_labels == 'kmeans':
            _, labels, _ = k_means(maps, n_clusters, random_state=0,
                                   n_init=n_init)
        else:
            labels = discretize(maps, random_state=random_state)
        return labels



    @property
    def _pairwise(self):
            return self.affinity == "precomputed"
