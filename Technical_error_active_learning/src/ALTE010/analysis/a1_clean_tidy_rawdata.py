"""
This script cleans and tidys the rawdata set and returns a csv ready for plotting.
It determines what type of plate reader etc to correctly process the data
"""
### import

import json
import os
from datetime import time
import pandas as pd

from sub_scripts.identify_wells import *
from sub_scripts.preprocessing_tidy import *
from sub_scripts.Calibration import *
from sub_scripts.zero_gfp import *
#from sub_scripts.labstep_annotation import *



### import raw data

raw_data = pd.read_excel("analysis/First_Baseline_and_ES_3_05052023.xlsx", header=None)


print(raw_data)
### execute preprocessing scripts

well_type_dict = {
    "B8": {
        "Well_Type": "Experiment",
        "DNA_Template": "T7_GFP",
        "Lysate_Inventory_Record": "Lysate_007",
        "Energy_Solution": "ES_ET_NTP",
        "Lysate_Owner": "MS"
        },
    "B10": {
        "Well_Type": "Experiment",
        "DNA_Template": "T7_GFP",
        "Lysate_Inventory_Record": "Lysate_007",
        "Energy_Solution": "ES_ET_NTP",
        "Lysate_Owner": "MS"
        },
    "B12": {
        "Well_Type": "Experiment",
        "DNA_Template": "T7_GFP",
        "Lysate_Inventory_Record": "Lysate_007",
        "Energy_Solution": "ES_3",
        "Lysate_Owner": "MS"
        },
    "B14": {
        "Well_Type": "Experiment",
        "DNA_Template": "T7_GFP",
        "Lysate_Inventory_Record": "Lysate_007",
        "Energy_Solution": "ES_3",
        "Lysate_Owner": "MS"
        },
    "D8": {
        "Well_Type": "Experiment",
        "DNA_Template": "T7_DARPIN_GFP",
        "Lysate_Inventory_Record": "Lysate_007",
        "Energy_Solution": "ES_ET_NTP",
        "Lysate_Owner": "MS"
        },
    "D10": {
        "Well_Type": "Experiment",
        "DNA_Template": "T7_DARPIN_GFP",
        "Lysate_Inventory_Record": "Lysate_007",
        "Energy_Solution": "ES_ET_NTP",
        "Lysate_Owner": "MS"
        },
    "D12": {
        "Well_Type": "Negative_Control",
        "DNA_Template": "None",
        "Lysate_Inventory_Record": "Lysate_007",
        "Energy_Solution": "ES_ET_NTP",
        "Lysate_Owner": "MS"
        },
    "D14": {
        "Well_Type": "Negative_Control",
        "DNA_Template": "None",
        "Lysate_Inventory_Record": "Lysate_007",
        "Energy_Solution": "ES_ET_NTP",
        "Lysate_Owner": "MS"
        },
    "F8": {
        "Well_Type": "Experiment",
        "DNA_Template": "T7_INFa2_GFP",
        "Lysate_Inventory_Record": "Lysate_007",
        "Energy_Solution": "ES_ET_NTP",
        "Lysate_Owner": "MS"
        },
    "F10": {
        "Well_Type": "Experiment",
        "DNA_Template": "T7_INFa2_GFP",
        "Lysate_Inventory_Record": "Lysate_007",
        "Energy_Solution": "ES_ET_NTP",
        "Lysate_Owner": "MS"
        },
    "H8": {
        "Well_Type": "Experiment",
        "DNA_Template": "T7_Uricase_GFP",
        "Lysate_Inventory_Record": "Lysate_007",
        "Energy_Solution": "ES_ET_NTP",
        "Lysate_Owner": "MS"
        },
    "H10": {
        "Well_Type": "Experiment",
        "DNA_Template": "T7_Uricase_GFP",
        "Lysate_Inventory_Record": "Lysate_007",
        "Energy_Solution": "ES_ET_NTP",
        "Lysate_Owner": "MS"
        },
    "J8": {
        "Well_Type": "Experiment",
        "DNA_Template": "T7_StefinA_GFP",
        "Lysate_Inventory_Record": "Lysate_007",
        "Energy_Solution": "ES_ET_NTP",
        "Lysate_Owner": "MS"
        },
    "J10": {
        "Well_Type": "Experiment",
        "DNA_Template": "T7_StefinA_GFP",
        "Lysate_Inventory_Record": "Lysate_007",
        "Energy_Solution": "ES_ET_NTP",
        "Lysate_Owner": "MS"
        }

    }




model_selected = "GFP_uM_Polynomial_Sarah_Oct_22"

# 1. tidy, trim and annotate the dataset
data_in_progress = preprocessing_tidy(raw_data, well_type_dict, negative_control_designated = True)

# 2. Calibrate signal with selected fluorescent protein model
data_in_progress = Calibration(data_in_progress, negative_control_designated = True, model_selected = "GFP_uM_Polynomial_Sarah_Oct_22")

# 3. Zero GFP signal
data_in_progress = Zero_GFP(data_in_progress, negative_control_designated = True)
   
print(data_in_progress)

data_in_progress.to_csv("analysis/tidy_dataset.csv")