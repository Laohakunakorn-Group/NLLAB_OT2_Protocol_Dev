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

#### defining the source tube lists
substrate_source_list_possibles = generate_MasterMixWells_96("Aqueous")
lysate_source_list_possibles = generate_MasterMixWells_96("Components")

# import the design
experiment_design_df = pd.read_csv("processed_data_files/Experiment_Designs/design_skeleton.csv", index_col=0)

# drop std order and run order
experiment_design_df = experiment_design_df.drop('std.order', axis=1)
experiment_design_df = experiment_design_df.drop('run.order', axis=1)

#get the number of experiments
number_of_experiments = experiment_design_df.shape[0]

##### Compatibility checks

# import experimental design parameters
with open('design_parameters.json') as json_file:
    design_parameters = json.load(json_file)


total_reaction_volume = design_parameters["Reaction_Volume"]

# Check Technical replicates is <= 12 if reaction volume is 20 or Technical replicates is <= 24 if reaction volume is 10
### each 200ul PCR tube can supply:
# 25x 10ul reactions - progress to next every 24 (1x row of nunc plate)
# 12x 20ul reactions - progress to next every 12 (0.5x row of nunc plate)

if design_parameters["Reaction_Volume"] == 20:
    if design_parameters["Technical_Replicates"] <= 12:
        print("")
        print("Technical_Replicates and Reaction_Volume compatible.")
        pass 
    else:
        raise ValueError('Too many Technical Replicates requested for Reaction Volume.' )


elif design_parameters["Reaction_Volume"] == 10:
    if design_parameters["Technical_Replicates"] <= 24:
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
with open('experiment_variables.json') as json_file:
    experiment_variables = json.load(json_file)
experiment_variables = pd.DataFrame(experiment_variables)



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

# get the experiment_variables == "Aqueous" and get the list of names
aqueous_lookup_table = experiment_variables[experiment_variables["Type"] == "Aqueous"]
aqueous_variables = list(aqueous_lookup_table["Variable"])

# get the experiment_variables == "Components" and get the list of names
components_lookup_table = experiment_variables[experiment_variables["Type"] == "Components"]
components_variables = list(components_lookup_table["Variable"])



def Designate_MasterMix_Tubes_by_Plate(plate_number):
    ### divide experiment_design_df by plate
    plate_df = experiment_design_df[experiment_design_df["Plate"] == plate_number]

    # drop Original Order
    plate_df = plate_df.drop(["Well", "Plate"], axis=1)


    ### Split design in to aqueous and components columns

    # select aqueous variables in experimental design
    plate_df_aqueous = plate_df[aqueous_variables]

    # select Components variables in experimental design
    plate_df_components = plate_df[components_variables]


    ##### build master mix dfs

    ## aqueous

    # Get unique rows
    aqueous_master_mixes = plate_df_aqueous.copy()

    # Get unique rows
    aqueous_master_mixes = aqueous_master_mixes.drop_duplicates()

    ## components

    # Get unique rows
    components_master_mixes = plate_df_components.copy()
    # drop index
    #components_master_mixes = components_master_mixes.drop("index", axis=1)
    # Get unique rows
    components_master_mixes = components_master_mixes.drop_duplicates()

    ## row wise, count the number of instances that that master mix has in the total design
    def CountExperimentsPerMasterMix(MasterMixDF, PlateDF):
        """
        Iterates over the master mix df rowwise and compares to experimental design df of the plate.
        Everytime it pings, it adds one to the tally and at the end of each MM, it appends that count to the list.
        Concludes by appending count list to master mix df as a Experiments column.
        Finally - Adds Total_Wells column = Experiments * design_parameters["Technical_Replicates"].
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

    aqueous_master_mixes = CountExperimentsPerMasterMix(aqueous_master_mixes, plate_df_aqueous)
    components_master_mixes = CountExperimentsPerMasterMix(components_master_mixes, plate_df_components)


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
        
    aqueous_master_mixes = DesignateMasterMixTubes(aqueous_master_mixes, substrate_source_list_possibles)
    components_master_mixes = DesignateMasterMixTubes(components_master_mixes, lysate_source_list_possibles)

    # save binaries of these working concentration designs
    aqueous_master_mixes.to_pickle("processed_data_files/MasterMixes/"+str(plate_number)+"_plate_aqueous_MasterMix_Working_Concs.pkl")
    components_master_mixes.to_pickle("processed_data_files/MasterMixes/"+str(plate_number)+"_plate_components_MasterMix_Working_Concs.pkl")


    #### Prepare the master mix stock concentrations

    # create a copy
    aqueous_master_mixes_stocks = aqueous_master_mixes.copy()
    components_master_mixes_stocks = components_master_mixes.copy()

    # x 1.333 the final concentrations
    aqueous_master_mixes_stocks[aqueous_variables] = aqueous_master_mixes_stocks[aqueous_variables] * (20/15)
    # x4 the final concentrations
    components_master_mixes_stocks[components_variables] = components_master_mixes_stocks[components_variables] * 4


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
    Designate_MasterMix_Tubes_by_Plate(plate_number=plate_number)


############ Add master mix tubes to experimental design 

print(" ")
print("Assigning reagent sources and wells...")
print(" ")


# use this list to concat together when it's done.
plate_df_list = []



# iterate over and feed the number to reading in the pickled dfs
for plate_number in plates_list:


    aqueous_master_mixes = pd.read_pickle("processed_data_files/MasterMixes/"+str(plate_number)+"_plate_aqueous_MasterMix_Working_Concs.pkl")
    components_master_mixes = pd.read_pickle("processed_data_files/MasterMixes/"+str(plate_number)+"_plate_components_MasterMix_Working_Concs.pkl")

    # slice the experimental design
    plate_df = experiment_design_df[experiment_design_df["Plate"] == plate_number].reset_index(drop=True)

    # initialise two lists of zeros of length plate df rows to be populated later.
    Aqueous_MasterMix_Tube = list(np.zeros(plate_df.shape[0]))
    Components_MasterMix_Tube = list(np.zeros(plate_df.shape[0]))



    ### Aqueous
    # drop unnecessary columns
    Aqueous_plate_df = plate_df[aqueous_variables]

    # iterate over the rows
    for mastermix_idx, mastermix_row in aqueous_master_mixes.iterrows():

        # extract and segregate key info
        # Have to convert series to dictionaries for comparison bc pandas has thrown a tantrum.
        MasterMixElements = mastermix_row[aqueous_variables].to_dict()
        Tubes = mastermix_row["Tubes"]

        # initialise counter
        mastermix_allocation_counter = 0
        Working_Tube_idx = 0

        true = 0

        for run_idx, run_row in Aqueous_plate_df.iterrows():

            # Have to convert series to dictionaries for comparison bc pandas has thrown a tantrum.
            run_row = run_row.to_dict()

            # Check if Working_Tube_idx needs progressing
            if mastermix_allocation_counter == 12:
                # reset
                mastermix_allocation_counter = 0
                Working_Tube_idx += 1

            if run_row == MasterMixElements:

                # look up the current tube using the mastermix_allocation_counter
                Working_Tube = Tubes[Working_Tube_idx]

                #print(Working_Tube_idx)

                # look up the correct index in the array using run_idx and insert the tube at the position.
                Aqueous_MasterMix_Tube[run_idx] = Working_Tube

                true = true + 1


                #progress the counter
                mastermix_allocation_counter += 1

                #print(mastermix_allocation_counter)
        #print()
        #print(MasterMixElements)
        #print("true")
        #print(true)
    
    plate_df.loc[:, "AqueousMasterMixTube"] = Aqueous_MasterMix_Tube


    ### Components

    # drop unnecessary columns
    Components_plate_df = plate_df[components_variables]

    # iterate over the rows
    for mastermix_idx, mastermix_row in components_master_mixes.iterrows():

        # extract and segregate key info
        # Have to convert series to dictionaries for comparison bc pandas has thrown a tantrum.
        MasterMixElements = mastermix_row[components_variables].to_dict()
        Tubes = mastermix_row["Tubes"]

        # initialise counter
        mastermix_allocation_counter = 0
        Working_Tube_idx = 0

        for run_idx, run_row in Components_plate_df.iterrows():

            # Have to convert series to dictionaries for comparison bc pandas has thrown a tantrum.
            run_row = run_row.to_dict()

            # Check if Working_Tube_idx needs progressing
            if mastermix_allocation_counter == 12:
                # reset
                mastermix_allocation_counter = 0
                Working_Tube_idx += 1

            if run_row == MasterMixElements:

                # look up the current tube using the mastermix_allocation_counter
                Working_Tube = Tubes[Working_Tube_idx]

                # look up the correct index in the array using run_idx and insert the tube at the position.
                Components_MasterMix_Tube[run_idx] = Working_Tube

                #progress the counter
                mastermix_allocation_counter += 1

    
    plate_df.loc[:,"ComponentsMasterMixTube"] = Components_MasterMix_Tube


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


