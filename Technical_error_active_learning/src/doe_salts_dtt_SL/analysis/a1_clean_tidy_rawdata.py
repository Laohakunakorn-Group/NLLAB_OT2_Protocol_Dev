"""
This script cleans and tidys the rawdata set and returns a csv ready for plotting.
It determines what type of plate reader etc to correctly process the data
"""
### import

import json
import os
from datetime import time
import pandas as pd

# import experimental design parameters
with open("./settings/design_parameters.json") as json_file:
    design_parameters = json.load(json_file)


# Import the raw datafile.

# look inside ./analysis and look for any files that end with rawdata.exec


# gets all items in directory
items = os.listdir("./analysis")

# lists all .csv
csv_list = []
for names in items:

    if names.endswith("raw_data.xlsx"):
        csv_list.append(names)

try:
    if(len(csv_list) > 1):
        raise UnAcceptedValueError("More than 1x .CSV file in the directory");
except UnAcceptedValueError as e:
    print ("Received error:", e.data)
    # kills the process
    quit()
##########################################################################################
#import dataset as dataframe

print()
print("Reading in data..")
print()
print("Plate_Reader_Protocol: " + design_parameters["Plate_Reader_Protocol"])
print()
print("Slicing data..")
print()

raw_data = pd.read_excel(r"./analysis/" + csv_list[0])

if design_parameters["Plate_Reader_Protocol"] == "AP_TimeCourse":

    core_data = raw_data.iloc[50:412,1:15]
    core_data = core_data.reset_index(drop=True)
    
    ## revamp
    # first rename the temp column to "TempC"
    core_data.iloc[0,1] = "TempC"

    # Set columns
    core_data.columns = core_data.iloc[0,:]
    core_data = core_data.iloc[1:,:]
    core_data = core_data.reset_index(drop=True)

    print("Converting Time to int64 Minutes..")
    print()


    # change time datatype to int mins row wise
    for i, row in core_data.iterrows():
        
        # changes datetime.time to string, splits the string into a list using :, build Series and converts to int64
        times = pd.Series(str(row["Time"]).split(':'), index = ["Hours", "Minutes", "Seconds"]).astype("int64")
        
        # converts to minutes with seconds in base 60 and sets to row
        row["Time"] = (times["Hours"]*60) + times["Minutes"] + (times["Seconds"]/100)

print("Complete.")
print()
print("Saving to: "+"./output/Datasets/tidy_data.csv")
print()

### save
core_data.to_csv("./output/Datasets/tidy_data.csv", index=False)

