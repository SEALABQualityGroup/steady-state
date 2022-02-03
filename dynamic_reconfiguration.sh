
# REPLICATIONPACKAGE_PATH=/Users/luca/Developer/repos/replication_package_fse20_laaber #put the replication package path here

CSV_DATA=$PWD/data/jmh_dyre
RESULTS=$PWD/data/results_dyre

[[ -d $RESULTS ]] || mkdir $RESULTS

cd $REPLICATIONPACKAGE_PATH/evaluation/study_kotlin
./gradlew runAnalysesData -Dargs="$CSV_DATA $RESULTS"

cd -