#!/usr/bin/env bash

cd $(dirname ${BASH_SOURCE[0]})/../

source scripts/routines.sh


for dataset in ${TARGET_DATASETS}; do
  n_clusters=$(get_cluster_num ${dataset})

  # SC, IDC
  for alg in SC_N SC_N1 IDC SG; do
    subpath=raw/affinity_euclidean/median/*/${alg}
    cross_validation ${dataset} ${subpath}
  done

  for alg in DBSCAN; do
    subpath=raw/distance_euclidean/DBSCAN/*/*
    cross_validation ${dataset} ${subpath}
    for dim in ${dr_dims}; do
      subpath=pca/${dim}/distance_euclidean/DBSCAN/*/*
      cross_validation ${dataset} ${subpath}
    done
  done
  if [ ${TEST} -eq 1 ]; then
    break
  fi
done
