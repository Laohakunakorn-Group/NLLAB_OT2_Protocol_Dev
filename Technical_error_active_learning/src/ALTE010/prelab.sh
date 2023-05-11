#! /bin/bash

if [ -d "output/" ]; then
rm -r output/
else
:
fi

mkdir output/
mkdir output/Experiment_Designs/
mkdir output/MasterMixes
mkdir output/Instructions


if [ -d "tmp/" ]; then
rm -r tmp/
else
:
fi

mkdir tmp/
mkdir tmp/MasterMixes/
mkdir tmp/Experiment_Designs/

R < 1_doe.r --no-save
python3 2_mastermixes_count.py
python3 3_mastermixes_assign.py
python3 4_mastermix_calculations.py