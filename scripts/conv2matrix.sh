#!/usr/bin/env bash

cd $(dirname ${BASH_SOURCE[0]})/../

source scripts/routines.sh

# affinity calculation
for dataset in ${TARGET_DATASETS}; do
  for subpath in raw ${se_paths}; do
    #echo $(get_matrix_dir ${dataset} ${subpath})
    # cosine
    make_affinity_matrix ${dataset} cosine ${subpath} affinity_cosine
    # euclidean (rbf-kernel) with pair-variant gamma (derived from self-tuning spectral clustering)
    make_affinity_matrix ${dataset} euclidean ${subpath} affinity_stsc
    # euclidean (rbf-kernel) with uniform gamma
    for gamma in ${ea_gammas}; do
      make_affinity_matrix ${dataset} euclidean ${subpath} affinity_euclidean/median/${gamma} "--gamma=${gamma} --scale_unit=median"
    done
  done
done
exit

for dataset in ${TARGET_DATASETS}; do
  for subpath in raw ${pca_paths}; do
    make_distance_matrix ${dataset} cosine ${subpath} distance_cosine
    make_distance_matrix ${dataset} euclidean ${subpath} distance_euclidean
  done
done
