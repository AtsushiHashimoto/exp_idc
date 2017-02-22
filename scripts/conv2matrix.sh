#!/usr/bin/env bash

cd $(dirname ${BASH_SOURCE[0]})/../

AFF_EUCLID_MEDIAN=0
AFF_EUCLID_ABS=1
AFF_COSINE=0
AFF_STSC=0
DIFF_COSINE=0
DIFF_EUCLID=0
# above settings can be overwrite in scirpts/my_env.sh if necessary

source scripts/routines.sh


# affinity calculation
if [ $(expr $AFF_COSINE + $AFF_STSC + $AFF_EUCLID_ABS + $AFF_EUCLID_MEDIAN) -gt 0 ]; then
for dataset in ${TARGET_DATASETS}; do
  for subpath in raw ${se_paths}; do
    #echo $(get_matrix_dir ${dataset} ${subpath})
    # cosine
    if [ ${AFF_COSINE} -eq 1 ]; then
      make_affinity_matrix ${dataset} cosine ${subpath} affinity_cosine
    fi
    # euclidean (rbf-kernel) with pair-variant gamma (derived from self-tuning spectral clustering)
    if [ ${AFF_STSC} -eq 1 ]; then
      make_affinity_matrix ${dataset} stsc ${subpath} affinity_stsc
    fi
    # euclidean (rbf-kernel) with uniform gamma
    for gamma in ${ea_gammas}; do
      if [ ${AFF_EUCLID_MEDIAN} -eq 1 ]; then
        make_affinity_matrix ${dataset} euclidean ${subpath} affinity_euclidean/median/${gamma} "--gamma=${gamma} --scale_unit=median"
      fi
      if [ ${AFF_EUCLID_ABS} -eq 1 ]; then
        make_affinity_matrix ${dataset} euclidean ${subpath} affinity_euclidean/absolute/${gamma} "--gamma=${gamma} --scale_unit=absolute"
      fi
    done
  done
done
fi

if [ $(expr $DIFF_EUCLID + $DIFF_COSINE) -gt 0 ]; then
for dataset in ${TARGET_DATASETS}; do
  for subpath in raw ${pca_paths}; do
    make_distance_matrix ${dataset} cosine ${subpath} distance_cosine
    make_distance_matrix ${dataset} euclidean ${subpath} distance_euclidean
  done
done
fi
