import pandas as pd 
import json


template_metadata = json.load(open("/app/analysis_scripts/template_well_metadata.json"))

design_df = pd.read_csv("/app/analysis_scripts/design.csv")

print(template_metadata)
print(type(template_metadata))

print("")


well_metadata_dict = {}

for i, well in design_df.iterrows():

    well_dict = template_metadata

    well_dict["MG_Glut"] = well["MG_Glut"]
    well_dict["K_Glut"] = well["K_Glut"]
    well_dict["DTT"] = well["DTT"]

    well_metadata_dict[well["Well"]] = well_dict


print(well_metadata_dict)