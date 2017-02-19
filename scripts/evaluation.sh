#!/usr/bin/env bash

cd $(dirname ${BASH_SOURCE[0]})/../

source scripts/routines.sh


for dataset in ${TARGET_DATASETS}; do
  src_dirs=()

  # SC, IDC
  for alg in SC_N SC_N1 IDC SG; do
    subpath=raw/affinity_euclidean/median/${alg}
    src_dir=$(get_cross_validation_dir ${dataset} ${subpath})
    if [ -e ${src_dir} ]; then
      src_dirs+=(${src_dir})
    fi
  done

  for alg in DBSCAN; do

    subpath=raw/distance_euclidean/DBSCAN
    src_dir=$(get_cross_validation_dir ${dataset} ${subpath})
    if [ -e ${src_dir} ]; then
      src_dirs+=(${src_dir})
    fi
    for dim in ${dr_dims}; do
      subpath=pca/${dim}/distance_euclidean/DBSCAN
      src_dir=$(get_cross_validation_dir ${dataset} ${subpath})
      if [ -e ${src_dir} ]; then
        src_dirs+=(${src_dir})
      fi
    done
  done
  if [ ${TEST} -eq 1 ]; then
    break
  fi

  metrics=(affinity_stsc affinity_cosine)
  methods=(SC_N SC_N1 IDC)
  for metric in ${metrics[@]}; do
    for method in ${methods[@]}; do
      subpath=raw/${metric}/${method}
      src_dir=$(get_cross_validation_dir ${dataset} ${subpath})
      if [ -e ${src_dir} ]; then
        src_dirs+=(${src_dir})
      fi
    done
  done

  for target in cross_validated closed_best; do
    echo "python tools/evaluation.py $(get_original_data_dir ${dataset}) ${EXP_DIR}/summery.${dataset}.${target}.csv -t ${target} ${src_dirs[@]}"
  done
  if [ ${TEST} -eq 1 ]; then
    break
  fi
done
