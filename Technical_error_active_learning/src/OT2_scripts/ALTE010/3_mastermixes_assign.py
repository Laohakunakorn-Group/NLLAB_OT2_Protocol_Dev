import json
import pandas as pd
import math
import numpy as np


############

# Intro

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
base_rxn_path = "settings/base_rxn.json"
base_rxn_dict = json.load(open(base_rxn_path, 'r'))


# import the design
experiment_design_df = pd.read_csv("processed_data_files/Experiment_Designs/design_skeleton.csv", index_col=0)

# drop std order and run order
experiment_design_df = experiment_design_df.drop('std.order', axis=1)
experiment_design_df = experiment_design_df.drop('run.order', axis=1)

#get the number of experiments
number_of_experiments = experiment_design_df.shape[0]

##### Compatibility checks

# import experimental design parameters
with open('settings/design_parameters.json') as json_file:
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
with open('settings/experiment_variables.json') as json_file:
    experiment_variables = json.load(json_file)
experiment_variables = pd.DataFrame(experiment_variables)



### Determine if aqueous and or components are modulated.

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
    aqueous_lookup_table = experiment_variables[experiment_variables["Type"] == "Aqueous"]
    aqueous_variables = list(aqueous_lookup_table["Variable"])

    # get the experiment_variables == "Components" and get the list of names
    components_lookup_table = experiment_variables[experiment_variables["Type"] == "Components"]
    components_variables = list(components_lookup_table["Variable"])

elif MasterMixesModulated == "Aqueous":

    # get the experiment_variables == "Aqueous" and get the list of names
    aqueous_lookup_table = experiment_variables[experiment_variables["Type"] == "Aqueous"]
    aqueous_variables = list(aqueous_lookup_table["Variable"])

elif MasterMixesModulated == "Components":

    # get the experiment_variables == "Components" and get the list of names
    components_lookup_table = experiment_variables[experiment_variables["Type"] == "Components"]
    components_variables = list(components_lookup_table["Variable"])

else:
    raise Exception("MasterMixesModulated is neither Aqueous, Components or Both: MasterMixesModulated = " + MasterMixesModulated)



##### define the function to designate master mixes tubes.


def Designate_MasterMix_Tubes_by_Plate(plate_number, MasterMixesModulated):

    ### divide experiment_design_df by plate
    plate_df = experiment_design_df[experiment_design_df["Plate"] == plate_number]

    # drop "Well", "Plate"
    plate_df = plate_df.drop(["Well", "Plate"], axis=1)


    ### Split design in to aqueous and components columns

    if MasterMixesModulated == "Both":
        # select aqueous variables in experimental design
        plate_df_aqueous = plate_df[aqueous_variables]

        # select Components variables in experimental design
        plate_df_components = plate_df[components_variables]

    elif MasterMixesModulated == "Aqueous":
        # select aqueous variables in experimental design
        plate_df_aqueous = plate_df[aqueous_variables]

    elif MasterMixesModulated == "Components":
        # select Components variables in experimental design
        plate_df_components = plate_df[components_variables]

    else:
        raise Exception("MasterMixesModulated is neither Aqueous, Components or Both: MasterMixesModulated = " + MasterMixesModulated)


    ##### build master mix dfs

    if MasterMixesModulated == "Both":

        # Get unique rows
        aqueous_master_mixes = plate_df_aqueous.copy()
        # Get unique rows
        aqueous_master_mixes = aqueous_master_mixes.drop_duplicates()

        # Get unique rows
        components_master_mixes = plate_df_components.copy()
        # Get unique rows
        components_master_mixes = components_master_mixes.drop_duplicates()

    elif MasterMixesModulated == "Aqueous":

        # Get unique rows
        aqueous_master_mixes = plate_df_aqueous.copy()
        # Get unique rows
        aqueous_master_mixes = aqueous_master_mixes.drop_duplicates()

    elif MasterMixesModulated == "Components":

        # Get unique rows
        components_master_mixes = plate_df_components.copy()
        # Get unique rows
        components_master_mixes = components_master_mixes.drop_duplicates()

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

        aqueous_master_mixes = CountExperimentsPerMasterMix(aqueous_master_mixes, plate_df_aqueous)
        components_master_mixes = CountExperimentsPerMasterMix(components_master_mixes, plate_df_components)

    elif MasterMixesModulated == "Aqueous":

        aqueous_master_mixes = CountExperimentsPerMasterMix(aqueous_master_mixes, plate_df_aqueous)
        components_master_mixes = PopulateAllWellsWithMasterMix(aqueous_master_mixes)
    
    elif MasterMixesModulated == "Components":

        components_master_mixes = CountExperimentsPerMasterMix(components_master_mixes, plate_df_components)
        aqueous_master_mixes = PopulateAllWellsWithMasterMix(components_master_mixes)

    else:
        raise Exception("MasterMixesModulated is neither Aqueous, Components or Both: MasterMixesModulated = " + MasterMixesModulated)


    ###### sanity check to make sure the number of experiments per master mix == total experiments on the plate

    if aqueous_master_mixes["Experiments"].sum() == plate_df.shape[0] and components_master_mixes["Experiments"].sum() == plate_df.shape[0]:
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
    aqueous_master_mixes = DesignateMasterMixTubes(aqueous_master_mixes, substrate_source_list_possibles)
    components_master_mixes = DesignateMasterMixTubes(components_master_mixes, lysate_source_list_possibles)

    # save binaries of these working concentration designs
    aqueous_master_mixes.to_pickle("processed_data_files/MasterMixes/"+str(plate_number)+"_plate_aqueous_MasterMix_Working_Concs.pkl")
    components_master_mixes.to_pickle("processed_data_files/MasterMixes/"+str(plate_number)+"_plate_components_MasterMix_Working_Concs.pkl")
    


    #### Prepare the master mix stock concentrations

    # create a copy
    aqueous_master_mixes_stocks = aqueous_master_mixes.copy()
    components_master_mixes_stocks = components_master_mixes.copy()

    # execute for the necessary mastermixes
    if MasterMixesModulated == "Both":

        # uses dilution factor generated using plating volumes from base_rxn["Metainfo"]
        aqueous_master_mixes_stocks[aqueous_variables] = aqueous_master_mixes_stocks[aqueous_variables] * (base_rxn_dict["Metainfo"]["total_reaction_volume_ul"]/base_rxn_dict["Metainfo"]["Master_Mixes"]["Volumes_added_to_rxn"]["aqueous"])
        components_master_mixes_stocks[components_variables] = components_master_mixes_stocks[components_variables] * (base_rxn_dict["Metainfo"]["total_reaction_volume_ul"]/base_rxn_dict["Metainfo"]["Master_Mixes"]["Volumes_added_to_rxn"]["components"])

    elif MasterMixesModulated == "Aqueous":

        # uses dilution factor generated using plating volumes from base_rxn["Metainfo"]
        aqueous_master_mixes_stocks[aqueous_variables] = aqueous_master_mixes_stocks[aqueous_variables] * (base_rxn_dict["Metainfo"]["total_reaction_volume_ul"]/base_rxn_dict["Metainfo"]["Master_Mixes"]["Volumes_added_to_rxn"]["aqueous"])
        components_master_mixes_stocks["Components"] = components_master_mixes_stocks["Components"] * (base_rxn_dict["Metainfo"]["total_reaction_volume_ul"]/base_rxn_dict["Metainfo"]["Master_Mixes"]["Volumes_added_to_rxn"]["components"])

    
    elif MasterMixesModulated == "Components":

        # uses dilution factor generated using plating volumes from base_rxn["Metainfo"]
        aqueous_master_mixes_stocks["Aqueous"] = aqueous_master_mixes_stocks["Aqueous"] * (base_rxn_dict["Metainfo"]["total_reaction_volume_ul"]/base_rxn_dict["Metainfo"]["Master_Mixes"]["Volumes_added_to_rxn"]["aqueous"])
        components_master_mixes_stocks[components_variables] = components_master_mixes_stocks[components_variables] * (base_rxn_dict["Metainfo"]["total_reaction_volume_ul"]/base_rxn_dict["Metainfo"]["Master_Mixes"]["Volumes_added_to_rxn"]["components"])
    
    else:
        raise Exception("MasterMixesModulated is neither Aqueous, Components or Both: MasterMixesModulated = " + MasterMixesModulated)

    # save human readable CSVs
    aqueous_master_mixes_stocks.to_csv("processed_data_files/MasterMixes/"+str(plate_number)+"_plate_aqueous_MasterMix_Stocks_human_readable"+".csv", index=False)
    components_master_mixes_stocks.to_csv("processed_data_files/MasterMixes/"+str(plate_number)+"_plate_components_MasterMix_Stocks_human_readable"+".csv", index=False)

    # save machine readable binaries
    aqueous_master_mixes_stocks.to_pickle("processed_data_files/MasterMixes/"+str(plate_number)+"_plate_aqueous_MasterMix_Stocks.pkl")
    components_master_mixes_stocks.to_pickle("processed_data_files/MasterMixes/"+str(plate_number)+"_plate_components_MasterMix_Stocks.pkl")


    # end of function

#### Execute
## get a list of the plate numbers
plates_list = list(experiment_design_df["Plate"].unique())

# iterate over and feed the number to master mix function
for plate_number in plates_list:
    Designate_MasterMix_Tubes_by_Plate(plate_number=plate_number, MasterMixesModulated = MasterMixesModulated)


############ Add master mix tubes to experimental design 

print(" ")
print("Assigning reagent sources and wells...")
print(" ")

def AllocatingMasterMixTubesBasedOnComparision(master_mix_df, Trimmed_plate_df, variables, col_name, plate_df):

    """
    1. Takes in the master_mix_df and the Trimmed_plate_df
    2. Converts both rows of each to dicts for comparision
    3. if it pings then adds the master mix tube to the list
    4. Assigns list as col_name column on the plate df
    """

    # initialise list of zeros of length plate df rows to be populated later.
    MasterMix_Tube_List = list(np.zeros(plate_df.shape[0]))

    # iterate over the rows
    for mastermix_idx, mastermix_row in master_mix_df.iterrows():

        # extract and segregate key info
        # Have to convert series to dictionaries for comparison bc pandas has thrown a tantrum.
        MasterMixElements = mastermix_row[variables].to_dict()
        Tubes = mastermix_row["Tubes"]

        # initialise counter
        mastermix_allocation_counter = 0
        Working_Tube_idx = 0


        for run_idx, run_row in Trimmed_plate_df.iterrows():

            # Have to convert series to dictionaries for comparison bc pandas has thrown a tantrum.
            run_row = run_row.to_dict()

            # Check if Working_Tube_idx needs progressing
            if mastermix_allocation_counter == Rxns_Per_MasterMix:
                # reset
                mastermix_allocation_counter = 0
                Working_Tube_idx += 1

            if run_row == MasterMixElements:

                # look up the current tube using the mastermix_allocation_counter
                Working_Tube = Tubes[Working_Tube_idx]


                # look up the correct index in the array using run_idx and insert the tube at the position.
                MasterMix_Tube_List[run_idx] = Working_Tube

                #progress the counter
                mastermix_allocation_counter += 1



    plate_df.loc[:, col_name] = MasterMix_Tube_List

    return plate_df



def AddMasterMixTubesToExperimentDesign(plate_df, MasterMixesModulated = MasterMixesModulated):

    # do Aqueous and then components

    AqueousComponents = ["Aqueous", "Components"]
    for MasterMixType in AqueousComponents:

        
        if (MasterMixesModulated == "Both" and MasterMixType == "Aqueous"):

            # if its a normal modulated allocation, assign the variables
            # and continue to the big comparison loop past this if statement.

            plate_df = AllocatingMasterMixTubesBasedOnComparision(
                master_mix_df = aqueous_master_mixes,
                Trimmed_plate_df = plate_df[aqueous_variables],
                variables = aqueous_variables,
                col_name = "AqueousMasterMixTube",
                plate_df = plate_df
            )

        elif (MasterMixesModulated == "Aqueous" and MasterMixType == "Aqueous"):

            # if its a normal modulated allocation, assign the variables
            # and continue to the big comparison loop past this if statement.

            plate_df = AllocatingMasterMixTubesBasedOnComparision(
                master_mix_df = aqueous_master_mixes,
                Trimmed_plate_df = plate_df[aqueous_variables],
                variables = aqueous_variables,
                col_name = "AqueousMasterMixTube",
                plate_df = plate_df
            )

        elif (MasterMixesModulated == "Both" and MasterMixType == "Components"):

            # if its a normal modulated allocation, assign the variables
            # and continue to the big comparison loop past this if statement.

            plate_df = AllocatingMasterMixTubesBasedOnComparision(
                master_mix_df = components_master_mixes,
                Trimmed_plate_df = plate_df[components_variables],
                variables = components_variables,
                col_name = "ComponentsMasterMixTube",
                plate_df = plate_df
            )

        elif (MasterMixesModulated == "Components" and MasterMixType == "Components"):

            # if its a normal modulated allocation, assign the variables
            # and continue to the big comparison loop past this if statement.

            plate_df = AllocatingMasterMixTubesBasedOnComparision(
                master_mix_df = components_master_mixes,
                Trimmed_plate_df = plate_df[components_variables],
                col_name = "ComponentsMasterMixTube",
                plate_df = plate_df
            )

        else:

            # This means the MasterMixType is not being modulated. 
            # I.e just a normal homogenous master mix that needs doleing out.
            # set the variables as appropriate and then continue.

            if (MasterMixesModulated == "Aqueous" and MasterMixType == "Components"):

                master_mix_df = components_master_mixes
                col_name = "ComponentsMasterMixTube"

            elif (MasterMixesModulated == "Components" and MasterMixType == "Aqueous"):

                master_mix_df = aqueous_master_mixes
                col_name = "AqueousMasterMixTube"
            
            else:
                raise Exception("Unknown MasterMixesModulated: "+ MasterMixesModulated+ " and MasterMixType: "+MasterMixType+" combination.")

            ## This section is a simple counter and progression loop
            # Assigns the MasterMix tubes blindly to the experiment.

            # concatenate all of the tubes together into a 1D list:  Master_Mix_Tube_list
            Master_Mix_Tube_list = []
            for Tubes in master_mix_df["Tubes"]:
                Master_Mix_Tube_list = Master_Mix_Tube_list + Tubes

            # initialise counter
            mastermix_allocation_counter = 0
            Working_Tube_idx = 0

            TubeListToAppend = []

            for i, row in plate_df.iterrows():

                # Check if Working_Tube_idx needs progressing
                if mastermix_allocation_counter == Rxns_Per_MasterMix:
                    # reset
                    mastermix_allocation_counter = 0
                    Working_Tube_idx += 1

                TubeListToAppend.append(Master_Mix_Tube_list[Working_Tube_idx])

                mastermix_allocation_counter += 1

            plate_df.loc[:, col_name] = TubeListToAppend

            # end of else.      

    return plate_df



# use this list to concat together when it's done.
plate_df_list = []

# iterate over and feed the number to reading in the pickled dfs
for plate_number in plates_list:


    aqueous_master_mixes = pd.read_pickle("processed_data_files/MasterMixes/"+str(plate_number)+"_plate_aqueous_MasterMix_Working_Concs.pkl")
    components_master_mixes = pd.read_pickle("processed_data_files/MasterMixes/"+str(plate_number)+"_plate_components_MasterMix_Working_Concs.pkl")

    # slice the experimental design
    plate_df = experiment_design_df[experiment_design_df["Plate"] == plate_number].reset_index(drop=True)

    # execute the function defined above
    plate_df = AddMasterMixTubesToExperimentDesign(plate_df, MasterMixesModulated = MasterMixesModulated)


    ####### Shuffle runs

    if design_parameters["Randomise"] == 1:
        plate_df = plate_df.sample(
                                    frac=1,
                                    random_state=123
                                    ).reset_index(names="Original_Order")


    plate_df_list.append(plate_df)

## Concat plate_dfs together

experiment_design_df = pd.concat(plate_df_list, axis=0).reset_index(drop=True)


print()
print("Assignment Complete.")
print()


### save the full design
experiment_design_df.to_csv("processed_data_files/Experiment_Designs/design_final.csv", index=False)


#############################################################################################################################################

