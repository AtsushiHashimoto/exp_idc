#!/usr/bin/env bash

cd $(dirname ${BASH_SOURCE[0]})/../

source scripts/routines.sh


se_paths=`seq -f "sparse_encode/%0.2f" 0.00 0.05 1.00`

gammas=`seq -f "%0.2f" 0.05 0.05 1.00`
# affinity calculation
for exp in ${TARGET_DATASETS}; do
  for subpath in raw ${se_paths}; do
    echo $(get_matrix_dir ${exp} ${subpath})
    # cosine
    make_affinity_matrix ${exp} cosine ${subpath} affinity_cosine
    # euclidean (rbf-kernel) with pair-variant gamma (derived from self-tuning spectral clustering)
    make_affinity_matrix ${exp} euclidean ${subpath} affinity_stsc
    # euclidean (rbf-kernel) with uniform gamma
    for gamma in ${gammas}; do
      make_affinity_matrix ${exp} euclidean ${subpath} affinity_euclidean/median/${gamma} "--gamma=${gamma} --scale_unit=median"
    done
  done
done

pca_paths=pca/64
for exp in ${TARGET_DATASETS}; do
  for subpath in raw ${pca_paths}; do
    make_distance_matrix ${exp} cosine ${subpath} distance_cosine
    make_distance_matrix ${exp} euclidean ${subpath} distance_euclidean
  done
done
