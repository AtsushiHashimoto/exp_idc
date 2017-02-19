#!/usr/bin/env bash
# Collection of routine functions


source scripts/my_env.sh
# path to pca data.
pca_paths=$(for dim in ${dr_dims[@]}; do echo "pca/${dim}"; done)
# path to sparse encoding data
se_paths=$(for alpha in ${se_alphas[@]}; do echo "sparse_encode/${alpha}"; done)


ORIG_DATA_DIR=external
EXP_DIR=exp
TEMP_DIR=${EXP_DIR}/temp
DATA_DIR=${EXP_DIR}/datasets
MAT_DIR=${EXP_DIR}/matrices
RESULTS_DIR=${EXP_DIR}/results
CV_DIR=${EXP_DIR}/cross_validation
#TRIALS=`seq -f "%03g" 0 99`
#TRIALS=`seq -f "%03g" 0 0`


QSUB_DIR=${DATASET_DIR}/qsub
QSUB_COMMAND='qsub -ug gr20111 -q tc -A p=1:t=1:c=1:m=128M'
UserGroup=gr20111
Queue=gr20100b


exec_command(){
  comm=$1

  # if len(args)>1 and File.exists($2) and OVERWRITE==0
  if [ $# -gt 1 -a ${OVERWRITE} -eq 0 -a ${QSUB} -eq 1 ]; then
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
  local dataset=$1
  if [ $# -eq 2 ]; then
    local subpath=$2/
  else
    local subpath=
  fi
  local dir=${DATA_DIR}/${dataset}/${subpath}
  echo ${dir}
}
get_original_data_dir(){
  echo $(get_data_dir $1 raw)
}
get_matrix_dir(){
  local dataset=$1
  if [ $# -eq 2 ]; then
    local subpath=/$2
  else
    local subpath=
  fi
  local dir=${MAT_DIR}/${dataset}${subpath}
  echo ${dir}
}

get_result_dir(){
  local dataset=$1
  if [ $# -eq 2 ]; then
    local subpath=/$2
  else
    local subpath=
  fi
  local dir=${RESULTS_DIR}/${dataset}${subpath}
  echo "${dir}"
}

get_cross_validation_dir(){
  local dataset=$1
  if [ $# -eq 2 ]; then
    local subpath=/$2
  else
    local subpath=
  fi
  local dir=${CV_DIR}/${dataset}${subpath}
  echo "${dir}"
}

clustering(){
  local dataset=$1
  local algorithm=$2
  local src_subpath=$3
  local dest_subpath=$4
  if [[ $# -eq 5 ]]; then
    local options=$5
  else
    local options=
  fi

  if [[ $(elementsIn ${algorithm} "${TARGET_ALGORITHMS[@]}") == "out" ]]; then
    return
  fi

  local dest_dir=$(get_result_dir ${dataset} ${dest_subpath})
  mkdir -p ${dest_dir}
  local src_dir=$(get_matrix_dir ${dataset} ${src_subpath})
  local count_command="python tools/do_clustering.py ${src_dir} ${dest_dir} --count_targets"
  exec_command "python tools/do_clustering.py ${algorithm} ${src_dir} ${dest_dir} ${options}" "${count_command}"
}


cross_validation(){
  local dataset=$1
  local subpath=$2
  local dest_dir=$(get_cross_validation_dir ${dataset} $(echo "${subpath}" | sed -e 's#\/\*##g'))
  mkdir -p ${dest_dir}
  #local count_command="python tools/cross_validation.py ${src_dir} ${dest_dir} --count_targets"
  local src_dir=$(get_result_dir ${dataset} "${subpath}")
  local ground_truth_dir=$(get_original_data_dir ${dataset})
  local count_command="python tools/cross_validation.py \"${src_dir}\" ${ground_truth_dir} ${dest_dir} --count_targets"
  exec_command "python tools/cross_validation.py \"${src_dir}\" ${ground_truth_dir} ${dest_dir} --criterion AMI"
}


make_matrix(){
  local type=$1
  local dataset=$2
  local metric=$3
  local src_subpath=$4
  local metric_name=$5
  local dest_subpath=$4/${metric_name}

  if [[ $# -eq 6 ]]; then
    local options=$6
  else
    local options=
  fi

  local dest_dir=$(get_matrix_dir ${dataset} ${dest_subpath})
  mkdir -p ${dest_dir}
  local src_dir=$(get_data_dir ${dataset} ${src_subpath})
  local count_command="python tools/make_${type}_matrix.py ${metric} ${src_dir} ${dest_dir} --count_targets"
  #echo ${count_command}
  exec_command "python tools/make_${type}_matrix.py ${metric} ${src_dir} ${dest_dir} ${options}" "${count_command}"
}

make_affinity_matrix(){
  if [[ $# -eq 5 ]]; then
    local options=$5
  else
    local options=
  fi
  make_matrix affinity $1 $2 $3 $4 ${options}
}
make_distance_matrix(){
  if [[ $# -eq 5 ]]; then
    local options=$5
  else
    local options=
  fi
  make_matrix distance $1 $2 $3 $4 ${options}
}


reduce_dimension(){
  local dataset=$1
  local alg=$2
  local dim=$3

  local dest_dir=$(get_data_dir ${dataset} ${alg}/${dim})
  mkdir -p ${dest_dir}
  local src_dir=$(get_original_data_dir ${dataset})

  local count_command="python tools/reduce_dimension.py ${dim} ${src_dir} ${dest_dir} --count_targets"
  exec_command "python tools/reduce_dimension.py ${dim} ${src_dir} ${dest_dir} --algorithm ${alg}" "${count_command}"
}

sparse_encode(){
  local dataset=$1
  local alpha=$2

  local dest_dir=$(get_data_dir ${dataset} sparse_encode/${alpha})
  mkdir -p ${dest_dir}
  local src_dir=$(get_original_data_dir ${dataset})
  #196MB for 128dim x 1000samples
  local count_command="python tools/sparse_encoding.py ${alpha} ${src_dir} ${dest_dir} --count_targets"
  exec_command "python tools/sparse_encoding.py ${alpha} ${src_dir} ${dest_dir} --method lasso_cd" "${count_command}"
}

get_cluster_num(){
  echo `echo $1 | awk -F'_' '{print $NF}'`
}
elementsIn(){
  local e
  for e in "${@:2}"; do [[ "$e" == "$1" ]] && echo "in"; done
  echo "out"
}
