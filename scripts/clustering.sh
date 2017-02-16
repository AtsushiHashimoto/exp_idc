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
  echo ${dataset}
  echo raw/affinity
  echo $(get_matrix_dir ${dataset} raw/affinity_\*)

  # SC, IDC
  for mat in `find $(get_matrix_dir ${dataset} raw/affinity_\*) -type f|grep W_000.csv`; do
      src_dir=$(dirname ${mat})
      subpath=$(echo ${src_dir}|awk -F"${dataset}/" '{print $2}')
      clustering ${dataset} sc ${subpath} ${subpath} "--n_clusters ${n_clusters}"
      echo "expr ${n_clusters} + 1"
      clustering ${dataset} sc ${subpath} ${subpath} "--n_clusters $(expr ${n_clusters} + 1)"
      clustering ${dataset} idc ${subpath} ${subpath} "--min_clusters 3 --max_clusters 20"
  done

  ####################
  continue

  # Sparse SC
  for mat in `find $(get_matrix_dir ${dataset} sparse_encode/affinity_\*) -type f|grep W_000.csv`; do
      src_dir=$(dirname ${mat})
      subpath=$(echo ${src_dir}|awk -F"${dataset}/" '{print $2}')
      clustering ${dataset} sc ${subpath} ${subpath} "--n_clusters ${n_clusters}"
      clustering ${dataset} sc ${subpath} ${subpath} "--n_clusters $(expr ${n_clusters} + 1)"
  done

  # Distance Based Clustering Methods

  # DBSCAN
  for src_type in raw pca/64; do
    for mat in `find $(get_matrix_dir ${dataset} ${src_type}/distance_\*) -type f|grep W_000.csv`; do
      src_dir=$(dirname ${mat})
      subpath=$(echo ${src_dir}|awk -F"${dataset}/" '{print $2}')
      for param in `seq -f "%0.2f" 0.0 0.05 1.0`; do
        #######
        clustering ${dataset} dbscan ${subpath} ${subpath}/${param} "--param ${param}"
      done
    done
  done

  # STSC
  for mat in `find $(get_matrix_dir ${dataset} raw/distance_euclidean) -type f|grep W_000.csv`; do
    clustering ${dataset} stsc ${subpath} ${subpath} "--n_clusters "
  done

#  for src_subpath in affinity_euclidean; do
#    cross_validation ${dataset} spectral_clustering ${src_subpath} "--n_clusters=${n_clusters} --params_from=directories --params_dir='sparse_encode:affinity_euclidean"
#    for dim in 64; do
#      cross_validation ${dataset}/pca/${dim} dbscan ${src_subpath}
#    done
#  done
done
