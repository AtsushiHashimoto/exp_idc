#!/usr/bin/env bash

cd $(dirname ${BASH_SOURCE[0]})/../

source scripts/routines.sh

# dimension reduction
for dataset in ${TARGET_DATASETS}; do
  #for alg in pca nmf; do
  for alg in pca; do
    for dim in ${dr_dims}; do
      #echo reduce_dimension ${dataset} ${alg} ${dim}
      reduce_dimension ${dataset} ${alg} ${dim}
    done
  done
done
# sparse encoding
method=lasso_lars

for dataset in ${TARGET_DATASETS}; do
  # 0.0 to 1.0 with step 0.05
  for alpha in ${se_alphas}; do
    sparse_encode ${dataset} ${alpha} ${metric} ${method}
  done
done
