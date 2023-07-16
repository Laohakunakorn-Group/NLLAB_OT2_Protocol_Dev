import pandas as pd 
import json

def generate_well_metadata_dict():
    """
    produces the well dict by reading the design and adding the template metadata.
    """
    
    # import the template and design
    template_metadata = json.load(open("/app/analysis_scripts/template_well_metadata.json"))
    design_df = pd.read_csv("/app/analysis_scripts/design.csv")

    # initialise the final dict
    well_metadata_dict = {}

    #iterate over the rows (wells) in the design
    for i, well in design_df.iterrows():

        # initalise the well dict
        well_dict = {}

        # extract and store all the template metadata in the well dict
        for key, value in template_metadata["Template"].items():
            well_dict[key] = value

        # store the well relevant metrics
        well_dict["MG_Glut"] = well["MG_Glut"]
        well_dict["K_Glut"] = well["K_Glut"]
        well_dict["DTT"] = well["DTT"]
        well_dict["MasterMixTube"] = well["MasterMixTube"]

        # store the whole thing under the well code
        well_metadata_dict[well["Well"]] = well_dict
    
    return well_metadata_dict

#    with open("/app/ana.json", "w") as outfile:
#        json.dump(well_metadata_dict, outfile)