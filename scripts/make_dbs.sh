#!/usr/bin/env bash

cd $(dirname ${BASH_SOURCE[0]})/../

source scripts/routines.sh

# make preid_massive_outliers
temp_dir=$(get_data_dir preid_mo format)
mkdir -p ${temp_dir}
for dir in $(find external/preid_mo/* -type d); do
  #echo ${dir}
  basename=$(basename ${dir})
  if [ ${basename} == "shinpuhkan.4.1_jstl_fc7_bn" ]; then
    python tools/format_preid.py ${dir} ${temp_dir}
    continue
  fi
  python tools/format_preid_outliers.py ${dir} ${temp_dir}/X_outliers_${basename}.npy
done

for rate_outliers in 0.5 1.0 3.0; do
  dest_dir=$(get_original_data_dir preid_mo_${rate_outliers}_12)
  #echo ${dest_dir}
  mkdir -p ${dest_dir}
  python tools/make_dbs.py preid_mo ${temp_dir} ${dest_dir} --n_clusters 12 --rate_outliers ${rate_outliers}
done

# make test dataset.
# n_clusters=5
dist_dir=$(get_original_data_dir test_05)
echo ${dist_dir}
mkdir -p ${dist_dir}
python tools/make_dbs.py test sample_data/test ${dist_dir}

# face feature
for n in `seq -f "%02g" 5 15`; do
  dist_dir=$(get_original_data_dir face_feature_${n})
  echo ${dist_dir}
  mkdir -p ${dist_dir}
  python tools/make_dbs.py face_feature external/face_feature ${dist_dir} --n_clusters ${n}
done


temp_dir=$(get_data_dir preid format)
mkdir -p ${temp_dir}
python tools/format_preid.py external/preid ${temp_dir}
for n in `seq -f "%02g" 4 4 12`; do
  dist_dir=$(get_original_data_dir preid_${n})
  echo ${dist_dir}
  mkdir -p ${dist_dir}
  python tools/make_dbs.py preid ${temp_dir} ${dist_dir} --n_clusters ${n}
done


dist_dir=$(dirname $(get_original_data_dir preid))
#mkdir -p ${dist_dir}
#python tools/make_dbs.py test external/test ${dist_dir}
