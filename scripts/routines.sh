#!/usr/bin/env bash
# Collection of routine functions

ORIG_DATA_DIR=external
EXP_DIR=exp
TEMP_DIR=${EXP_DIR}/temp
DATA_DIR=${EXP_DIR}/datasets
AMAT_DIR=${EXP_DIR}/affinity_matrices
RESULTS_DIR=${EXP_DIR}/results
#TRIALS=`seq -f "%03g" 0 99`
#TRIALS=`seq -f "%03g" 0 0`

OVERWRITE=0
QSUB=1

QSUB_DIR=${EXP_DIR}/qsub
QSUB_COMMAND='qsub -ug gr20111 -q tc -A p=1:t=1:c=1:m=128M'
UserGroup=gr20111
Queue=gr20100b

EXE=sh\ -c
#EXE=echo

exec_command(){
  comm=$1

  # if len(args)>1 and File.exists($2) and OVERWRITE==0
  if [ $# -gt 1 -a ${OVERWRITE} -eq 0 ]; then
    local tar_num=$($2)
    if [[ ${tar_num} -eq 0 ]]; then
      # skip execution
      return
    fi
  fi
  if [ ${QSUB} -eq 0 ]; then
    ${EXE} "${comm}"
    return
  fi
  if [ $# -gt 2 ]; then
    option=$3
  else
    option="p=1:t=1:c=1:m=256M"
  fi
  if [ $# -gt 3 ]; then
    hours=$4
  else
    hours=18:00
  fi
  #echo "/usr/bin/ls -lha > test.log" > temp|qsub -ug gr20111 -q gr20100b -W 12:00 -A p=1:t=1:c=1:m=1M temp
  temp_id=$(date +"%s.%N");
  temp_sh=${TEMP_DIR}/qsub_${temp_id}.sh
  work_dir=$(pwd)/$(dirname ${BASH_SOURCE[0]})/../
  comm_="echo \"source ~/.bash_profile;cd ${work_dir};${comm}\" > ${temp_sh} | qsub -ug ${UserGroup} -q ${Queue} -W ${hours} -A ${option} ${temp_sh}"
  ${EXE} "${comm_}"
}

get_data_dir(){
  local exp=$1
  if [ $# -eq 2 ]; then
    local subpath=$2/
  else
    local subpath=
  fi
  local dir=${DATA_DIR}/${exp}/${subpath}
  echo ${dir}
}
get_original_data_dir(){
  echo $(get_data_dir $1 raw)
}
get_affinity_matrix_dir(){
  local exp=$1
  if [ $# -eq 2 ]; then
    local subpath=$2/
  else
    local subpath=
  fi
  local dir=${AMAT_DIR}/${exp}/${subpath}.csv
  echo ${dir}
}
get_clustering_result_dir(){
  local exp=$1
  local dir=${RESULTS_DIR}/${exp}/
  echo ${dir}
}

get_result_dir(){
  local exp=$1
  local trial=$2
  if [ $# -eq 3 ]; then
    local subpath=$3/
  else
    local subpath=
  fi
  local dir=${RESULTS_DIR}/${exp}/${subpath}
  echo ${dir}
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

  local dist_dir=$(get_clustering_result_dir ${exp} ${subpath})
  mkdir -p ${dist_dir}
  local src_dir=$(get_affinity_matrix_dir ${exp} ${subpath})
  local count_command="python tools/do_clustering.py ${src_dir} ${dist_dir} --count_targets}"
  exec_command "python tools/do_clustering.py ${src_dir} ${dist_dir} ${options}" ${count_command}
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

  local dist_dir=$(get_affinity_matrix_dir ${exp} ${subpath})
  mkdir -p ${dist_dir}
  local src_dir=$(get_data_dir ${exp} ${subpath})
  local count_command="python tools/make_affinity_matrix.py ${src_dir} ${dist_dir} --count_targets}"
  exec_command "python tools/make_affinity_matrix.py ${metric} ${src_dir} ${dist_dir} ${options}" ${count_command}
}

reduce_dimension(){
  local exp=$1
  local alg=$2
  local dim=$3

  local dist_dir=$(get_data_dir ${exp} ${alg}/${dim})
  mkdir -p ${dist_dir}
  local src_dir=$(get_original_data_dir ${exp})

  local count_command="python tools/reduce_dimension.py ${dim} ${src_dir} ${dist_dir} --count_targets"
  exec_command "python tools/reduce_dimension.py ${dim} ${src_dir} ${dist_dir} --algorithm ${alg}" "${count_command}"
}

sparse_encode(){
  local exp=$1
  local alpha=$2

  local dist_dir=$(get_data_dir ${exp} sparse_encode/${alpha})
  mkdir -p ${dist_dir}
  local src_dir=$(get_original_data_dir ${exp})
  #196MB for 128dim x 1000samples
  local count_command="python tools/sparse_encoding.py ${alpha} ${src_dir} ${dist_dir} --count_targets"
  exec_command "python tools/sparse_encoding.py ${alpha} ${src_dir} ${dist_dir}" "${count_command}"
}
