#!/usr/bin/env bash

cd $(dirname ${BASH_SOURCE[0]})/../

source scripts/routines.sh

# dimension reduction
  #test: 100MB
dist_dir=$(get_original_data_dir test)
mkdir -p ${dist_dir}
python tools/make_dbs.py test external/test ${dist_dir}

for n in `seq -f "%02g" 5 15`; do
  dist_dir=$(get_original_data_dir face_feature_${n})
  mkdir -p ${dist_dir}
  python tools/make_dbs.py face_feature external/face_feature ${dist_dir} --n_clusters ${n}
done

dist_dir=$(dirname $(get_original_data_dir preid))
#mkdir -p ${dist_dir}
#python tools/make_dbs.py test external/test ${dist_dir}
