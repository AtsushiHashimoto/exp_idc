#!/usr/bin/env bash
# Collection of routine functions

ORIG_DATA_DIR=external
EXP_DIR=exp
DATA_DIR=${EXP_DIR}/datasets
AMAT_DIR=${EXP_DIR}/affinity_matrices
RESULTS_DIR=${EXP_DIR}/results
#TRIALS=`seq -w 0 99`
TRIALS=`seq -f "%03g" 0 0`


QSUB=0
QSUB_DIR=${EXP_DIR}/qsub
QSUB_COMMAND='qsub -ug gr20111 -q tc -A p=1:t=1:c=1:m=128M'
#EXE=sh\ -c
EXE=echo
#EXE=${QSUB_COMMAND}


get_data(){
  local exp=$1
  local trial=$2
  if [ $# -eq 3 ]; then
    local subpath=$3/
  else
    local subpath=
  fi
  local file=${DATA_DIR}/${exp}/${subpath}X_${trial}.csv
  echo ${file}
}
get_original_data(){
  echo $(get_data $1 $2 raw)
}


get_affinity_matrix(){
  local exp=$1
  local trial=$2
  if [ $# -eq 3 ]; then
    local subpath=$3/
  else
    local subpath=
  fi
  local file = ${AMAT_DIR}/${exp}/${subpath}affinity_matrix-${trial}.csv
  echo ${file}
}

get_clustering_result(){
  local exp=$1
  local trial=$2
  local file = ${RESULTS_DIR}/${exp}/${trial}.csv
  echo ${file}
}

get_label(){
  local exp=$1
  local trial=$2
  if [ $# -eq 3 ]; then
    local subpath=$3/
  else
    local subpath=
  fi
  local file = ${RESULTS_DIR}/${exp}/${subpath}summery.csv
  echo ${file}
}

do_clustering(){
  local exp=$1
  local metric=$2
  local subpath=$3
  if [[ $# -eq 4 ]]; then
    local options=$4
  else
    local options=
  fi

  temp=$(get_clustering_result ${exp} 00 ${subpath})
  mkdir -p `dirname ${temp}`

  for trial in ${TRIALS}; do
    local src_file=$(get_affinity_matrix ${exp} ${trial} ${subpath})
    local dist_file=$(get_clustering_result ${exp} ${trial} ${subpath})
    ${EXE} "python tools/do_clustering.py ${src_file} ${options} > ${dist_file}"
  done

}

make_affinity_matrix(){
  local exp=$1
  local metric=$2
  local subpath=$3
  if [[ $# -eq 4 ]]; then
    local options=$4
  else
    local options=
  fi

  temp=$(get_affinity_matrix ${exp} 0 ${subpath})
  mkdir -p `dirname ${temp}`

  for trial in ${TRIALS}; do
    local src_file=$(get_data ${exp} ${trial} ${subpath})
    local dist_file=$(get_affinity_matrix ${exp} ${trial} ${subpath})
    ${EXE} "python tools/make_affinity_matrix.py ${src_file} ${metric} ${options} > ${dist_file}"
  done
}

reduce_dimension(){
  local exp=$1
  local alg=$2
  local dim=$3

  temp=$(get_data ${exp} 0 ${alg}/${dim})
  mkdir -p `dirname ${temp}`

  for trial in ${TRIALS}; do
    local src_file=$(get_original_data ${exp} ${trial})
    local dist_file=$(get_data ${exp} ${trial} ${alg}/${dim})
    #128MB
    #${EXE} "python tools/reduce_dimension.py ${dim} ${src_file} ${dist_file} --algorithm ${alg}"
  done
}

sparse_encode(){
  local exp=$1
  local alpha=$2
  local method=$3

  temp=$(get_data ${exp} 0 sparse_encode/${alpha})
  mkdir -p `dirname ${temp}`

  for trial in ${TRIALS}; do
    local src_file=$(get_original_data ${exp} ${trial})
    local dist_file=$(get_data ${exp} ${trial} sparse_encode/${alpha})
    ${EXE} "python tools/sparse_encoding.py ${alpha} ${src_file} ${dist_file}"
  done
}
