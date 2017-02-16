# flag to overwrite all calculation results.
# OVERWRITE=1
OVERWRITE=0

# flag to generate qsub command for super computing systems (or any systems with job scheduler).
QSUB=0

# EXE=echo to print command, "sh\ -c" for execution.
#EXE=sh\ -c
EXE=echo

TARGET_DATASETS=test face_feature preid

TARGET_ALGORITHMS=SC IDC SG STSC MODULARITY SEA DBSCAN

#dimension reduction target dims.
dr_dims=(64)

# sparse_encoding gamma
se_alphas=`seq -f "%0.2f" 0.05 0.05 1.01`

# dbscan parameters
dbscan_params=`seq -f "%0.2f" 0.0 0.05 1.01`
