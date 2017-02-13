#!/usr/bin/env bash

cd $(dirname ${BASH_SOURCE[0]})/../

source scripts/routines.sh

#target_datasets=test
target_datasets=`seq -f "face_feature_%02g" 5 15`
se_paths=`seq -f "sparse_encode/%0.2f" 0.00 0.05 1.00`

# affinity calculation
for exp in ${target_datasets}; do
  for subpath in raw ${se_paths}; do
    echo $(get_matrix_dir ${exp} ${subpath})
    # cosine
    make_affinity_matrix ${exp} cosine ${subpath} affinity_cosine
    # euclidean (rbf-kernel) with pair-variant gamma (derived from self-tuning spectral clustering)
    make_affinity_matrix ${exp} euclidean ${subpath} affinity_stsc
    # euclidean (rbf-kernel) with uniform gamma
    make_affinity_matrix ${exp} euclidean ${subpath} affinity_euclidean "--gamma=0.001"
  done
done

pca_paths=pca/64
for exp in ${target_datasets}; do
  for subpath in raw ${pca_paths}; do
    make_distance_matrix ${exp} cosine ${subpath} distance_cosine
    make_distance_matrix ${exp} euclidean ${subpath} distance_euclidean
  done
done
