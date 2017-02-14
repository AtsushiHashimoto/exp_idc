#!/usr/bin/env bash

cd $(dirname ${BASH_SOURCE[0]})/../

source scripts/routines.sh

# affinity calculation

for dataset in ${TARGET_DATASETS}; do
  for src_subpath in affinity_cosine; do
    cross_validation ${dataset}/sparse_encode ssc ${src_subpath}
    for dim in 64; do
      cross_validation ${dataset}/pca/${dim} dbscan ${src_subpath}
    done
  done
done
