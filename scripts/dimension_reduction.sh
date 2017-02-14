#!/usr/bin/env bash

cd $(dirname ${BASH_SOURCE[0]})/../

source scripts/routines.sh

# dimension reduction
for exp in ${TARGET_DATASETS}; do
  #for alg in pca nmf; do
  for alg in pca; do
    #for dim in 32 64 128; do
    for dim in 64; do
      reduce_dimension ${exp} ${alg} ${dim}
    done
  done
done
# sparse encoding
method=lasso_lars

for exp in ${TARGET_DATASETS}; do
  # 0.0 to 1.0 with step 0.05
  for alpha in `seq -f "%0.2f" 0.00 0.05 1.00`; do
    sparse_encode ${exp} ${alpha} ${metric} ${method}
  done
done
