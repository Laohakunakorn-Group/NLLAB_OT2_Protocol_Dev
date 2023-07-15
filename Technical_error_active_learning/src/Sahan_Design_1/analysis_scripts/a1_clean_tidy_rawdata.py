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

raw_data = pd.read_excel("/app/analysis_scripts/First_Baseline_and_ES_3_05052023.xlsx", header=None)


well_type_dict = json.load(open("/app/analysis_scripts/fdbk_baselining_well_metadata.json"))

### execute preprocessing scripts

model_selected = "GFP_uM_Polynomial_Sarah_Oct_22"

# 1. tidy, trim and annotate the dataset
data_in_progress = preprocessing_tidy(raw_data, well_type_dict, negative_control_designated = True)

# 2. Calibrate signal with selected fluorescent protein model
data_in_progress = Calibration(data_in_progress, negative_control_designated = True, model_selected = "GFP_uM_Polynomial_Sarah_Oct_22")

# 3. Zero GFP signal
data_in_progress = Zero_GFP(data_in_progress, negative_control_designated = True)
   


data_in_progress.to_csv("/app/analysis_output/tidy_dataset.csv")