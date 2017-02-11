#!/usr/bin/env bash

cd $(dirname ${BASH_SOURCE[0]})/../

source scripts/routines.sh

#target_datasets=(test face)
#target_datasets=face preid
target_datasets=face_feature 
# dimension reduction
for exp in ${target_datasets}; do
  for alg in pca nmf; do
    for dim in 32 64 128; do
      reduce_dimension ${exp} ${alg} ${dim}
    done
  done
done

# sparse encoding
method=lasso_lars

for exp in ${target_datasets}; do
  # 0.0 to 1.0 with step 0.05
  for alpha in `seq 0.00 0.05 1.00`; do
    sparse_encode ${exp} ${alpha} ${metric} ${method}
  done
done
