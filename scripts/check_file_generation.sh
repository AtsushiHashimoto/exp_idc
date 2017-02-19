#!/usr/bin/env bash

cd $(dirname ${BASH_SOURCE[0]})/../

source scripts/routines.sh


if [ $# -lt 3 ]; then
  echo "USAGE: sh ${BASH_SOURCE[0]} root_data_dir file_template(ex. \"X_%03g.csv\" max_num"
  exit
fi
root_data_dir=$1
template=$2
file_max=$3

file_list=$(seq -f ${template} 0 ${file_max})
# ex) file_list_generate_command=`seq -f ${file_template} 0 99`
#echo "target files: ${file_list}..."

for dir in `find ${root_data_dir}/* -type d`; do

  # check if the directory has only directories or not.
  file_num=$(ls -1 ${dir} | wc -l)
  dir_num=$(find ${dir} -maxdepth 1 -type d | wc -l)
  dir_num=$(expr ${dir_num} - 1)
  #echo ${dir}
  #echo file_num:${file_num}
  #echo dir_num:${dir_num}
  if [ ${file_num} -ne 0 -a ${file_num} -eq ${dir_num} ]; then
    # skip node-directories.
    continue
  fi

  # check if the directory has target files or not.
  is_any_file=0
  for file in ${file_list}; do
    #echo ${dir}/${file} 
    if [ -e ${dir}/${file} ]; then
      is_any_file=1
      break
    fi
  done
  if [ ${is_any_file} -eq 0 ]; then
    echo "### ${dir} contains no target files." >&2
    #rmdir ${dir}
    continue
  fi

  is_all_file=1
  for file in ${file_list}; do
    if [ -e ${dir}/${file} ]; then
      continue
    fi
    is_all_file=0
    echo "!!! ${dir}/${file} not found" >&2
  done
  if [ ${is_all_file} -eq 1 ]; then
    echo "${dir} complete."
  fi
done
