#! /bin/bash

if [ -d "/app/output/" ]; then
rm -r /app/output/
else
:
fi

mkdir /app/output/
mkdir /app/output/Experiment_Designs/
mkdir /app/output/MasterMixes
mkdir /app/output/Instructions


if [ -d "tmp/" ]; then
rm -r tmp/
else
:
fi

mkdir tmp/
mkdir tmp/MasterMixes/
mkdir tmp/Experiment_Designs/

R < "/app/prelab_scripts/1_doe.r" --no-save
python3 "/app/prelab_scripts/2_mastermixes_count.py"
python3 "/app/prelab_scripts/3_mastermixes_assign.py"
python3 "/app/prelab_scripts/4_mastermix_calculations.py"