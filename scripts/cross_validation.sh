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

copy_all(){
  dataset=$1
  subpath=$2
  src_dir=$(get_result_dir ${dataset} "${subpath}")
  dest_dir=$(get_cross_validation_dir ${dataset} ${subpath})
  mkdir -p ${dest_dir}
  for file in `find ${src_dir}/*.dat`; do
    for target in closed_best cross_validated random; do
      dest_file=$(basename ${file%.dat}).${target}.dat
      cp -f ${file} ${dest_dir}/${dest_file}
    done
  done
}

# copy no param results
for dataset in ${TARGET_DATASETS}; do
  metrics=(affinity_stsc affinity_cosine)
  methods=(SC_N SC_N1 IDC)
  for metric in ${metrics[@]}; do
    for method in ${methods[@]}; do
      copy_all ${dataset} raw/${metric}/${method}
    done
  done
  if [ ${TEST} -eq 1 ]; then
    break
  fi
done
