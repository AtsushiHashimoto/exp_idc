#!/usr/bin/env bash

cd $(dirname ${BASH_SOURCE[0]})/../

source scripts/routines.sh

# dimension reduction
  #test: 100MB
dist_dir=$(dirname $(get_original_data test 0))
mkdir -p ${dist_dir}
python tools/make_dbs.py test external/test ${dist_dir}

dist_dir=$(dirname $(get_original_data face 0))
#mkdir -p ${dist_dir}
#python tools/make_dbs.py test external/test ${dist_dir}

dist_dir=$(dirname $(get_original_data preid 0))
#mkdir -p ${dist_dir}
#python tools/make_dbs.py test external/test ${dist_dir}
