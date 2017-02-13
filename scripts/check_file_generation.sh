#!/usr/bin/env bash

cd $(dirname ${BASH_SOURCE[0]})/../

source scripts/routines.sh

#target_datasets=(test face)
#target_datasets=face preid

if [ $# -lt 2 ]; then
  echo "USAGE: sh ${BASH_SOURCE[0]} root_data_dir file_template"
  exit
fi
root_data_dir=$1
file_list_generate_command=$2
# ex) file_list_generate_command=`seq -f ${file_template} 0 99`

for dir in `find ${root_data_dir} -type d`; do
  is_any_file=0
  for file in `${file_list_generate_command}`; do
    if [ -e ${dir}/${file} ]; then
      is_any_file=1
      break
    fi
  done
  if [ ${is_any_file} -eq 0 ]; then
    echo "### ${dir} contains no target files."
    continue
  fi

  for file in `${file_list_generate_command}`; do
    if [ -e ${dir}/${file} ]; then
      continue
    fi
    echo "!!! ${dir}/${file} not found"
  done
done
