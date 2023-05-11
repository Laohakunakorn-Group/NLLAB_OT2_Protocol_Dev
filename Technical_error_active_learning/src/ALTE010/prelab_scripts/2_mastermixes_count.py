import json
import pandas as pd
import math
import numpy as np


############

# Intro

# This script works out how many plates, plate wells and master mix tubes are required.

# It also calculates the concentrations in the master mixes and assigns master mix tubes to those compositions.

###########


# function to generate plate well well_list_384
def generate_well_list_384(spacing):

    # choose well spacing:
    if spacing == 0:
        Letters = ["A", "B", "C", "D", "E", "F","G","H","I", "J", "K", "L", "M", "N", "O", "P"]
        Numbers = list(range(1, 25,1))

    if spacing == 1:
        Letters = ["B", "D", "F", "H", "J", "L", "N"]
        Numbers = list(range(2, 23,2))

    well_list_384 = []
    for let in Letters:
        for num in Numbers:
            well_name = let + str(num)
            well_list_384.append(well_name)

    return well_list_384


# function to generate Master Mix Possibles lists
def generate_MasterMixWells_96(MasterMix):

    # choose well spacing:
    if MasterMix == "Aqueous":
        Letters = ["A", "C", "E", "G",]
        Numbers = list(range(1, 13,1))

    if MasterMix == "Components":
        Letters = ["B", "D", "F", "H"]
        Numbers = list(range(1, 13,1))

    MasterMixWells_96 = []
    for let in Letters:
        for num in Numbers:
            well_name = let + str(num)
            MasterMixWells_96.append(well_name)

    return MasterMixWells_96


# import the base_rxn_dict
base_rxn_path = "/app/settings/base_rxn.json"
base_rxn_dict = json.load(open(base_rxn_path, 'r'))


# import the design
experiment_design_df = pd.read_csv("/app/output/Experiment_Designs/design_skeleton.csv", index_col=0)

# drop std order and run order
experiment_design_df = experiment_design_df.drop('std.order', axis=1)
experiment_design_df = experiment_design_df.drop('run.order', axis=1)

#get the number of experiments
number_of_experiments = experiment_design_df.shape[0]

##### Compatibility checks

# import experimental design parameters
with open('/app/settings/design_parameters.json') as json_file:
    design_parameters = json.load(json_file)


total_reaction_volume = design_parameters["Reaction_Volume"]

# Check Technical replicates is <= 12 if reaction volume is 20 or Technical replicates is <= 24 if reaction volume is 10
### each 200ul PCR tube can supply:
# 25x 10ul reactions - progress to next every 24 (1x row of nunc plate)
# 12x 20ul reactions - progress to next every 12 (0.5x row of nunc plate)

if design_parameters["Reaction_Volume"] == 20:

    Rxns_Per_MasterMix = 12

    if design_parameters["Technical_Replicates"] <= Rxns_Per_MasterMix:
        print("")
        print("Technical_Replicates and Reaction_Volume compatible.")
        pass 
    else:
        raise ValueError('Too many Technical Replicates requested for Reaction Volume.' )


elif design_parameters["Reaction_Volume"] == 10:

    Rxns_Per_MasterMix = 24

    if design_parameters["Technical_Replicates"] <= Rxns_Per_MasterMix:
        print("")
        print("Technical_Replicates and Reaction_Volume compatible.")
        pass 
    else:
        raise ValueError('Too many Technical Replicates requested for Reaction Volume.' )

else:
    print("")
    print("Error: Reaction Volume in design_parameters.json is unknown..")
    print("Reaction_Volume: "+str(design_parameters["Reaction_Volume"]))


# import experiment_variables
with open('/app/settings/experiment_variables.json') as json_file:
    experiment_variables = json.load(json_file)
experiment_variables = pd.DataFrame(experiment_variables)



### Determine if Aqueous and or Components are modulated.

if ('Aqueous' in experiment_variables["Type"].values) and ('Components' in experiment_variables["Type"].values):
    MasterMixesModulated = "Both"

elif 'Aqueous' in experiment_variables["Type"].values:
    MasterMixesModulated = "Aqueous"

elif 'Components' in experiment_variables["Type"].values:
    MasterMixesModulated = "Components"

else:
    raise Exception("Please check the Type of Reaction Elements to be modulated in experiemnt_variables.json")


#### defining the source tube lists
substrate_source_list_possibles = generate_MasterMixWells_96("Aqueous")
lysate_source_list_possibles = generate_MasterMixWells_96("Components")



#### Expand the experimental design to include technical replicates


# initialise empty df with the columns of the original
expanded_experimental_design = pd.DataFrame(columns=list(experiment_design_df.columns))

# iterate over the rows and for append that row for Nx the number of technical replicates
for idx, row in experiment_design_df.iterrows():

    for rep in range(design_parameters["Technical_Replicates"]):
        expanded_experimental_design = pd.concat([expanded_experimental_design, row.to_frame().T], axis=0, ignore_index=True)




# rename
experiment_design_df = expanded_experimental_design

#### Assign Plates and Plate Wells

# generate the well well_list_384
well_list_384 = generate_well_list_384(spacing = 1)
plate_capacity = len(well_list_384)

#  store the number of runs - the num of rows of the df
num_of_runs = experiment_design_df.shape[0]

# if there are fewer experiments than or exactly 384 or 77 or whatever (the plate capacity), then just label the with enough wells
if num_of_runs <= plate_capacity:
    experiment_design_df['Well'] = well_list_384[:num_of_runs]
    experiment_design_df['Plate'] = 1

    plates_required = 1
    # calculate runs per plate
    runs_per_plate = int(num_of_runs/plates_required)

elif num_of_runs > plate_capacity:

    # divides by 384 and rounds up to next integer
    plates_required = math.ceil(num_of_runs / plate_capacity)

    # calculate runs per plate
    runs_per_plate = int(num_of_runs/plates_required)

    # build lists of wells and plates to append to df as columns
    exp_wells = []
    exp_plates = []

    for plate in range(1, plates_required+1,1):

        for run in range(1, runs_per_plate+1,1):
            exp_plates.append(plate)
            exp_wells.append(well_list_384[run-1])

    experiment_design_df['Well'] = exp_wells
    experiment_design_df['Plate'] = exp_plates


else:
    raise Exception("There is an error with the number of experiments")



#### Assign Master Mixes to experiments
## retrieve variable types:

if MasterMixesModulated == "Both":

    # get the experiment_variables == "Aqueous" and get the list of names
    Aqueous_lookup_table = experiment_variables[experiment_variables["Type"] == "Aqueous"]
    Aqueous_variables = list(Aqueous_lookup_table["Variable"])

    # get the experiment_variables == "Components" and get the list of names
    Components_lookup_table = experiment_variables[experiment_variables["Type"] == "Components"]
    Components_variables = list(Components_lookup_table["Variable"])

elif MasterMixesModulated == "Aqueous":

    # get the experiment_variables == "Aqueous" and get the list of names
    Aqueous_lookup_table = experiment_variables[experiment_variables["Type"] == "Aqueous"]
    Aqueous_variables = list(Aqueous_lookup_table["Variable"])

elif MasterMixesModulated == "Components":

    # get the experiment_variables == "Components" and get the list of names
    Components_lookup_table = experiment_variables[experiment_variables["Type"] == "Components"]
    Components_variables = list(Components_lookup_table["Variable"])

else:
    raise Exception("MasterMixesModulated is neither Aqueous, Components or Both: MasterMixesModulated = " + MasterMixesModulated)



##### define the function to designate master mixes tubes.


def Designate_MasterMix_Tubes_by_Plate(plate_number, MasterMixesModulated):

    ### divide experiment_design_df by plate
    plate_df = experiment_design_df[experiment_design_df["Plate"] == plate_number]

    # drop "Well", "Plate"
    plate_df = plate_df.drop(["Well", "Plate"], axis=1)


    ### Split design in to Aqueous and Components columns

    if MasterMixesModulated == "Both":
        # select Aqueous variables in experimental design
        plate_df_Aqueous = plate_df[Aqueous_variables]

        # select Components variables in experimental design
        plate_df_Components = plate_df[Components_variables]

    elif MasterMixesModulated == "Aqueous":
        # select Aqueous variables in experimental design
        plate_df_Aqueous = plate_df[Aqueous_variables]

    elif MasterMixesModulated == "Components":
        # select Components variables in experimental design
        plate_df_Components = plate_df[Components_variables]

    else:
        raise Exception("MasterMixesModulated is neither Aqueous, Components or Both: MasterMixesModulated = " + MasterMixesModulated)


    ##### build master mix dfs

    if MasterMixesModulated == "Both":

        # Get unique rows
        Aqueous_master_mixes = plate_df_Aqueous.copy()
        # Get unique rows
        Aqueous_master_mixes = Aqueous_master_mixes.drop_duplicates()

        # Get unique rows
        Components_master_mixes = plate_df_Components.copy()
        # Get unique rows
        Components_master_mixes = Components_master_mixes.drop_duplicates()

    elif MasterMixesModulated == "Aqueous":

        # Get unique rows
        Aqueous_master_mixes = plate_df_Aqueous.copy()
        # Get unique rows
        Aqueous_master_mixes = Aqueous_master_mixes.drop_duplicates()

    elif MasterMixesModulated == "Components":

        # Get unique rows
        Components_master_mixes = plate_df_Components.copy()
        # Get unique rows
        Components_master_mixes = Components_master_mixes.drop_duplicates()

    else:
        raise Exception("MasterMixesModulated is neither Aqueous, Components or Both: MasterMixesModulated = " + MasterMixesModulated)


    ######## Two functions to count the number of instances that that master mix has in the total design

    # First CountExperimentsPerMasterMix() counts the Modulated master mixes 

    # Second is only used when only one Master Mix type is modulated and populates all wells with one type.

    ## row wise, count the number of instances that that master mix has in the total design
    def CountExperimentsPerMasterMix(MasterMixDF, PlateDF):
        """
        Iterates over the master mix df rowwise and compares to experimental design df of the plate.
        Everytime it pings, it adds one to the tally and at the end of each MM, it appends that count to the list.
        Concludes by appending count list to master mix df as a Experiments column.
        """

        master_mix_experiment_counter_list = []

        for idx, master_mix in MasterMixDF.iterrows():

            master_mix_experiment_counter = 0

            for idx, exp in PlateDF.iterrows():

                if exp.equals(master_mix) == True:
                    master_mix_experiment_counter += 1


            master_mix_experiment_counter_list.append(master_mix_experiment_counter)

        MasterMixDF["Experiments"] = master_mix_experiment_counter_list

        return MasterMixDF
    
    def PopulateAllWellsWithMasterMix(MasterMixDF):
        """ Builds corresponding df and populates Experiments column with the sum() of the Experiments column of the other."""

        # select the name of the MasterMix to build the df with
        if MasterMixesModulated == "Aqueous":
            name = "Components"
        elif MasterMixesModulated == "Components":
            name = "Aqueous"
        else:
            raise Exception("MasterMixesModulated is neither Aqueous or Components: MasterMixesModulated = " + MasterMixesModulated)

        # build the df setting the concentration to 1
        new_df = pd.DataFrame(
            data = {
                name : [1],
                "Experiments": [MasterMixDF["Experiments"].sum()]
                    }
                )
        
        return new_df


    # execute for the necessary mastermixes
    if MasterMixesModulated == "Both":

        Aqueous_master_mixes = CountExperimentsPerMasterMix(Aqueous_master_mixes, plate_df_Aqueous)
        Components_master_mixes = CountExperimentsPerMasterMix(Components_master_mixes, plate_df_Components)

    elif MasterMixesModulated == "Aqueous":

        Aqueous_master_mixes = CountExperimentsPerMasterMix(Aqueous_master_mixes, plate_df_Aqueous)
        Components_master_mixes = PopulateAllWellsWithMasterMix(Aqueous_master_mixes)
    
    elif MasterMixesModulated == "Components":

        Components_master_mixes = CountExperimentsPerMasterMix(Components_master_mixes, plate_df_Components)
        Aqueous_master_mixes = PopulateAllWellsWithMasterMix(Components_master_mixes)

    else:
        raise Exception("MasterMixesModulated is neither Aqueous, Components or Both: MasterMixesModulated = " + MasterMixesModulated)


    ###### sanity check to make sure the number of experiments per master mix == total experiments on the plate

    if Aqueous_master_mixes["Experiments"].sum() == plate_df.shape[0] and Components_master_mixes["Experiments"].sum() == plate_df.shape[0]:
        print("Master Mix experiment counts check out..")
    else:
        raise ValueError('Experiments per Master mix do not match total number of experiments.' )




    #### Assign Master Mix Tubes
    def DesignateMasterMixTubes(MasterMixDf, MasterMix_Possible_Tubes):
        """
        Takes in the Master Mix DF and the Possible tube list.
        Assigns the required amount of tubes to that master mix.
        """

        # initialise counter to keep track of which tubes in the possibles list have been designated
        tube_counter = 0

        # initialise list of lists to append on df at the end.
        list_of_individual_master_mix_tube_lists = []

        # iterate over the Experiments number column in the Master Mix df
        for exp_num in MasterMixDf['Experiments']:

            # Initialise a list to populate with the tubes for that master mix
            individual_master_mix_tube_list = []

            # set the max_runs_per_mastermix_tube based on reaction volume
            if total_reaction_volume == 20:
                max_runs_per_mastermix_tube = 12

            elif total_reaction_volume == 10:
                max_runs_per_mastermix_tube = 24

            else:
                raise Exception("Unknown total_reaction_volume.")

            ### Assign the master mix tube based on the number of experiments

            # if its less than max_runs_per_mastermix_tube then just the current tube in the list then progress the counter
            if exp_num <= max_runs_per_mastermix_tube:
                individual_master_mix_tube_list.append(MasterMix_Possible_Tubes[tube_counter])
                tube_counter += 1

            # if its greater then..
            elif exp_num > max_runs_per_mastermix_tube:

                # calculate the number of tubes required rounded up
                number_of_tubes_required = math.ceil(exp_num/max_runs_per_mastermix_tube)
                # add that to the current tube counter to get the last index of the last required tube.
                last_tube_selected_index = tube_counter + number_of_tubes_required
                # look the tubes up
                individual_master_mix_tube_list = MasterMix_Possible_Tubes[tube_counter:last_tube_selected_index]
                # use the last index to progress the counter.
                tube_counter = last_tube_selected_index

            else:
                raise Exception("Something is wrong the the tube assignment. Enough possibles?")

            # append the individual_master_mix_tube_list to the list of lists
            list_of_individual_master_mix_tube_lists.append(individual_master_mix_tube_list)

        # append the list of lists to the Master Mix Df as a new column called Tubes
        MasterMixDf["Tubes"] = list_of_individual_master_mix_tube_lists

        return MasterMixDf
    
    # perform for both regardless of MasterMixesModulated
    Aqueous_master_mixes = DesignateMasterMixTubes(Aqueous_master_mixes, substrate_source_list_possibles)
    Components_master_mixes = DesignateMasterMixTubes(Components_master_mixes, lysate_source_list_possibles)

    # save binaries of these working concentration designs
    Aqueous_master_mixes.to_pickle("/app/tmp/MasterMixes/"+str(plate_number)+"_plate_Aqueous_MasterMix_Working_Concs.pkl")
    Components_master_mixes.to_pickle("/app/tmp/MasterMixes/"+str(plate_number)+"_plate_Components_MasterMix_Working_Concs.pkl")
    


    #### Prepare the master mix stock concentrations

    # create a copy
    Aqueous_master_mixes_stocks = Aqueous_master_mixes.copy()
    Components_master_mixes_stocks = Components_master_mixes.copy()

    # execute for the necessary mastermixes
    if MasterMixesModulated == "Both":

        # uses dilution factor generated using plating volumes from base_rxn["Metainfo"]
        Aqueous_master_mixes_stocks[Aqueous_variables] = Aqueous_master_mixes_stocks[Aqueous_variables] * (base_rxn_dict["Metainfo"]["total_reaction_volume_ul"]/base_rxn_dict["Metainfo"]["Master_Mixes"]["Volumes_added_to_rxn"]["Aqueous"])
        Components_master_mixes_stocks[Components_variables] = Components_master_mixes_stocks[Components_variables] * (base_rxn_dict["Metainfo"]["total_reaction_volume_ul"]/base_rxn_dict["Metainfo"]["Master_Mixes"]["Volumes_added_to_rxn"]["Components"])

    elif MasterMixesModulated == "Aqueous":

        # uses dilution factor generated using plating volumes from base_rxn["Metainfo"]
        Aqueous_master_mixes_stocks[Aqueous_variables] = Aqueous_master_mixes_stocks[Aqueous_variables] * (base_rxn_dict["Metainfo"]["total_reaction_volume_ul"]/base_rxn_dict["Metainfo"]["Master_Mixes"]["Volumes_added_to_rxn"]["Aqueous"])
        Components_master_mixes_stocks["Components"] = Components_master_mixes_stocks["Components"] * (base_rxn_dict["Metainfo"]["total_reaction_volume_ul"]/base_rxn_dict["Metainfo"]["Master_Mixes"]["Volumes_added_to_rxn"]["Components"])

    
    elif MasterMixesModulated == "Components":

        # uses dilution factor generated using plating volumes from base_rxn["Metainfo"]
        Aqueous_master_mixes_stocks["Aqueous"] = Aqueous_master_mixes_stocks["Aqueous"] * (base_rxn_dict["Metainfo"]["total_reaction_volume_ul"]/base_rxn_dict["Metainfo"]["Master_Mixes"]["Volumes_added_to_rxn"]["Aqueous"])
        Components_master_mixes_stocks[Components_variables] = Components_master_mixes_stocks[Components_variables] * (base_rxn_dict["Metainfo"]["total_reaction_volume_ul"]/base_rxn_dict["Metainfo"]["Master_Mixes"]["Volumes_added_to_rxn"]["Components"])
    
    else:
        raise Exception("MasterMixesModulated is neither Aqueous, Components or Both: MasterMixesModulated = " + MasterMixesModulated)

    # save human readable CSVs
    Aqueous_master_mixes_stocks.to_csv("/app/output/MasterMixes/"+str(plate_number)+"_plate_Aqueous_MasterMix_Stocks_human_readable"+".csv", index=False)
    Components_master_mixes_stocks.to_csv("/app/output/MasterMixes/"+str(plate_number)+"_plate_Components_MasterMix_Stocks_human_readable"+".csv", index=False)

    # save machine readable binaries
    Aqueous_master_mixes_stocks.to_pickle("/app/tmp/MasterMixes/"+str(plate_number)+"_plate_Aqueous_MasterMix_Stocks.pkl")
    Components_master_mixes_stocks.to_pickle("/app/tmp/MasterMixes/"+str(plate_number)+"_plate_Components_MasterMix_Stocks.pkl")


    # end of function

#### Execute
## get a list of the plate numbers
plates_list = list(experiment_design_df["Plate"].unique())

# iterate over and feed the number to master mix function
for plate_number in plates_list:
    Designate_MasterMix_Tubes_by_Plate(plate_number=plate_number, MasterMixesModulated = MasterMixesModulated)

# save the experiment_design_df
experiment_design_df.to_csv("/app/tmp/Experiment_Designs/design_unassigned.csv")
#############################################################################################################################################


