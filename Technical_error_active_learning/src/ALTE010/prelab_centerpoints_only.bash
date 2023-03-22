#!/bin/bash
mkdir output
mkdir output/Experiment_Designs
mkdir output/MasterMixes
mkdir output/Instructions

# remake /tmp
if [ -d "/tmp" ] 
then
    # clear tmp
    rm -r tmp
    mkdir tmp
    mkdir tmp/Experiment_Designs
    mkdir tmp/MasterMixes
else
    mkdir tmp
    mkdir tmp/Experiment_Designs
    mkdir tmp/MasterMixes
    
fi


# run scripts

R < 1_doe_centerpoints.r --no-save

python3 2_mastermixes_count.py

python3 3_mastermixes_assign.py

python3 4_mastermix_calculations.py
