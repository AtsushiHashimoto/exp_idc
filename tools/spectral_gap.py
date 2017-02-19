#!/usr/bin/env python
# coding: utf-8

import tempfile
import subprocess
from os.path import dirname
from sklearn.base import BaseEstimator, ClusterMixin
from sklearn.utils import check_random_state, check_symmetric
from sklearn.utils.validation import check_array
from sklearn.metrics.pairwise import pairwise_kernels
from sklearn.neighbors import kneighbors_graph
from sklearn.cluster.k_means_ import k_means
from sklearn.cluster.spectral import discretize
from sklearn.manifold.spectral_embedding_ import _graph_is_connected,_set_diag
from sklearn.utils.graph import graph_laplacian
from sklearn.utils.arpack import eigsh
from sklearn.utils.extmath import _deterministic_vector_sign_flip

import numpy as np

class SpectralClusteringSG(BaseEstimator, ClusterMixin):
    # src_pat ex.) "^.*/X_(\d{3}).csv$"
    def __init__(self,
            max_clusters,\
            n_init=10, gamma=1., n_neighbors=10,\
            eigen_tol=0.0, degree=3, coef0=1,
            kernel_params = None,\
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
                                           max_clusters=self.max_clusters,
                                           eigen_solver=self.eigen_solver,
                                           random_state=random_state,
                                           n_init=self.n_init,
                                           eigen_tol=self.eigen_tol,
                                           assign_labels=self.assign_labels)
        return self

    @property
    def _pairwise(self):
            return self.affinity == "precomputed"


    def estimate_num_of_clusters(self,lambdas_list):
        dif = list()
        for i in range(1, len(lambdas_list)-1):
            lambda_K0 = lambdas_list[i]
            lambda_K1 = lambdas_list[i+1]
            dif.append(lambda_K0 - lambda_K1)
        return dif.index(max(dif))+2


    def spectral_clustering_sg(self, affinity, max_clusters=8,
                            eigen_solver=None, random_state=None, n_init=10,
                            eigen_tol=0.0, assign_labels='kmeans'):

        if assign_labels not in ('kmeans', 'discretize'):
            raise ValueError("The 'assign_labels' parameter should be "
                             "'kmeans' or 'discretize', but '%s' was given"
                             % assign_labels)

        random_state = check_random_state(random_state)
        n_components = max_clusters
        maps, lambdas = self.spectral_embedding(affinity, n_components=n_components,
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


    def spectral_embedding(self,adjacency, n_components=8, eigen_solver=None,
                       random_state=None, eigen_tol=0.0,drop_first=True):
        """
        see original at https://github.com/scikit-learn/scikit-learn/blob/14031f6/sklearn/manifold/spectral_embedding_.py#L133
        custermize1: return lambdas with the embedded matrix.
        custermize2: norm_laplacian is always True
        """
        norm_laplacian=True
        adjacency = check_symmetric(adjacency)

        try:
            from pyamg import smoothed_aggregation_solver
        except ImportError:
            if eigen_solver == "amg":
                raise ValueError("The eigen_solver was set to 'amg', but pyamg is "
                                 "not available.")

        if eigen_solver is None:
            eigen_solver = 'arpack'
        elif eigen_solver not in ('arpack', 'lobpcg', 'amg'):
            raise ValueError("Unknown value for eigen_solver: '%s'."
                             "Should be 'amg', 'arpack', or 'lobpcg'"
                             % eigen_solver)

        random_state = check_random_state(random_state)

        n_nodes = adjacency.shape[0]
        # Whether to drop the first eigenvector
        if drop_first:
            n_components = n_components + 1

        if not _graph_is_connected(adjacency):
            warnings.warn("Graph is not fully connected, spectral embedding"
                          " may not work as expected.")

        laplacian, dd = graph_laplacian(adjacency,
                                        normed=norm_laplacian, return_diag=True)
        if (eigen_solver == 'arpack'
            or eigen_solver != 'lobpcg' and
                (not sparse.isspmatrix(laplacian)
                 or n_nodes < 5 * n_components)):
            # lobpcg used with eigen_solver='amg' has bugs for low number of nodes
            # for details see the source code in scipy:
            # https://github.com/scipy/scipy/blob/v0.11.0/scipy/sparse/linalg/eigen
            # /lobpcg/lobpcg.py#L237
            # or matlab:
            # http://www.mathworks.com/matlabcentral/fileexchange/48-lobpcg-m
            laplacian = _set_diag(laplacian, 1, norm_laplacian)

            # Here we'll use shift-invert mode for fast eigenvalues
            # (see http://docs.scipy.org/doc/scipy/reference/tutorial/arpack.html
            #  for a short explanation of what this means)
            # Because the normalized Laplacian has eigenvalues between 0 and 2,
            # I - L has eigenvalues between -1 and 1.  ARPACK is most efficient
            # when finding eigenvalues of largest magnitude (keyword which='LM')
            # and when these eigenvalues are very large compared to the rest.
            # For very large, very sparse graphs, I - L can have many, many
            # eigenvalues very near 1.0.  This leads to slow convergence.  So
            # instead, we'll use ARPACK's shift-invert mode, asking for the
            # eigenvalues near 1.0.  This effectively spreads-out the spectrum
            # near 1.0 and leads to much faster convergence: potentially an
            # orders-of-magnitude speedup over simply using keyword which='LA'
            # in standard mode.
            try:
                # We are computing the opposite of the laplacian inplace so as
                # to spare a memory allocation of a possibly very large array
                laplacian *= -1
                lambdas, diffusion_map = eigsh(laplacian, k=n_components,
                                               sigma=1.0, which='LM',
                                               tol=eigen_tol)
                embedding = diffusion_map.T[n_components::-1] * dd

            except RuntimeError:
                # When submatrices are exactly singular, an LU decomposition
                # in arpack fails. We fallback to lobpcg
                eigen_solver = "lobpcg"
                # Revert the laplacian to its opposite to have lobpcg work
                laplacian *= -1

        if eigen_solver == 'amg':
            # Use AMG to get a preconditioner and speed up the eigenvalue
            # problem.
            if not sparse.issparse(laplacian):
                warnings.warn("AMG works better for sparse matrices")
            # lobpcg needs double precision floats
            laplacian = check_array(laplacian, dtype=np.float64,
                                    accept_sparse=True)
            laplacian = _set_diag(laplacian, 1, norm_laplacian)
            ml = smoothed_aggregation_solver(check_array(laplacian, 'csr'))
            M = ml.aspreconditioner()
            X = random_state.rand(laplacian.shape[0], n_components + 1)
            X[:, 0] = dd.ravel()
            lambdas, diffusion_map = lobpcg(laplacian, X, M=M, tol=1.e-12,
                                            largest=False)
            embedding = diffusion_map.T * dd
            if embedding.shape[0] == 1:
                raise ValueError

        elif eigen_solver == "lobpcg":
            # lobpcg needs double precision floats
            laplacian = check_array(laplacian, dtype=np.float64,
                                    accept_sparse=True)
            if n_nodes < 5 * n_components + 1:
                # see note above under arpack why lobpcg has problems with small
                # number of nodes
                # lobpcg will fallback to eigh, so we short circuit it
                if sparse.isspmatrix(laplacian):
                    laplacian = laplacian.toarray()
                lambdas, diffusion_map = eigh(laplacian)
                embedding = diffusion_map.T[:n_components] * dd
            else:
                laplacian = _set_diag(laplacian, 1,norm_laplacian)
                # We increase the number of eigenvectors requested, as lobpcg
                # doesn't behave well in low dimension
                X = random_state.rand(laplacian.shape[0], n_components + 1)
                X[:, 0] = dd.ravel()
                lambdas, diffusion_map = lobpcg(laplacian, X, tol=1e-15,
                                                largest=False, maxiter=2000)
                embedding = diffusion_map.T[:n_components] * dd
                if embedding.shape[0] == 1:
                    raise ValueError

        embedding = _deterministic_vector_sign_flip(embedding)
        if drop_first:
            return embedding[1:n_components].T, lambdas
        else:
            return embedding[:n_components].T, lambdas
