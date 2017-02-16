#!/usr/bin/env bash

cd $(dirname ${BASH_SOURCE[0]})/../

source scripts/routines.sh

# affinity calculation

for dataset in ${TARGET_DATASETS}; do
  n_clusters=$(get_cluster_num ${dataset})
  if [ -z ${n_clusters}  ]; then
    echo "ERROR: no cluster number is obtained from dataset name."
    exit
  fi

  # SC, IDC
  for mat in `find $(get_matrix_dir ${dataset} raw/affinity_\*) -type f|grep W_000.csv`; do
      src_dir=$(dirname ${mat})
      subpath=$(echo ${src_dir}|awk -F"${dataset}/" '{print $2}')
      clustering ${dataset} SC ${subpath} ${subpath}/SC_N "--n_clusters $(expr ${n_clusters})"
      clustering ${dataset} SC ${subpath} ${subpath}/SC_N1 "--n_clusters $(expr ${n_clusters} + 1)"
      clustering ${dataset} IDC ${subpath} ${subpath}/IDC "--min_clusters 3 --max_clusters 20"
      # SG, MODULARITY, SEA
      clustering ${dataset} SG ${subpath} ${subpath}/SG
      clustering ${dataset} MODULARITY ${subpath} ${subpath}/MODULARITY
      clustering ${dataset} SEA ${subpath} ${subpath}/SEA
  done
  exit
  ####################

  # Sparse SC
  for se_path in ${se_paths}; do
    for mat in `find $(get_matrix_dir ${dataset} ${se_path}/affinity_\*) -type f|grep W_000.csv`; do
      src_dir=$(dirname ${mat})
      subpath=$(echo ${src_dir}|awk -F"${dataset}/" '{print $2}')
      clustering ${dataset} SC ${subpath} ${subpath}/SSC_N "--n_clusters $(expr ${n_clusters})"
      clustering ${dataset} SC ${subpath} ${subpath}/SSC_N1 "--n_clusters $(expr ${n_clusters} + 1)"
    done
  done

  # Distance Based Clustering Methods

  # DBSCAN
  for src_type in raw ${pca_paths}; do
    for mat in `find $(get_matrix_dir ${dataset} ${src_type}/distance_\*) -type f|grep W_000.csv`; do
      src_dir=$(dirname ${mat})
      subpath=$(echo ${src_dir}|awk -F"${dataset}/" '{print $2}')
      for eps in dbscan_epss; do
        #######
        clustering ${dataset} DBSCAN ${subpath} ${subpath}/DBSCAN/${eps} "--eps ${eps}"
      done
    done
  done

  # STSC
  for mat in `find $(get_matrix_dir ${dataset} raw/distance_euclidean) -type f|grep W_000.csv`; do
    clustering ${dataset} STSC ${subpath} ${subpath}/STSC "--n_clusters "
  done

done
