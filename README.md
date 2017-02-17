# Experiments for Clustering CNN features

This project aims at executing clustering method evaluation on face (face_feature) and person re-identification (preid) deep features.

## Installation

Pythonの必要なパッケージを入れる．

1.  python packages: numpy, scipy, scikit-learn, ...


## Download datasets

Download the following datasets.
- face_features
- preid
アップロードできるかわからないので，橋本に聞いてください．


## Prepare data

1.  Create a directory for experiment data and results

        mkdir external/

    or link against another external directory

        ln -s /path/to/your/exp/directory external

3.  scripts/my_env.example.sh  を scripts/my_env.sh に変更し，環境に合わせて編集する．

        cp scripts/my_env.example.conf scripts/my_env.sh

4.  Convert raw datasets into a uniform data format

        sh scripts/make_dbs.sh
   
## Experiments

1.  Perform Dimension Reduction

        sh scripts/dimension_reduction.sh
     
2. Convert to Affinity/Distance Matrices

        sh scripts/conv2matrix.sh
       
3. Clustering all Matrices

        sh scripts/clustering.sh
        
4. Select the best results by Cross-validating parameters.

        sh scripts/cross_vaildation.sh

5. YOU GET RESULTS in exp/results/



## Citation

    not yet.

## Referenced Datasets

We summarize the datasets used in this project as below.

    not yet

