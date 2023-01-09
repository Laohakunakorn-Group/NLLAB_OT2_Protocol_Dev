import json
import pandas as pd
import math


############

experiment_prefix = "ALTE009"

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


#### defining the source tube lists
substrate_source_list_possibles = ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10", "A11", "A12", "A13", "A14", "A15", "A16",
                                   "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C10", "C11", "C12", "C13", "C14", "C15", "C16"]
                                   
lysate_source_list_possibles = ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "B10", "B11", "B12", "B13", "B14", "B15", "B16",
                                "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9", "D10", "D11", "D12", "D13", "D14", "D15", "D16"]

# import the design
experiment_design_df = pd.read_csv("processed_data_files/design_real.csv", index_col=0)

# drop std order and run order
experiment_design_df = experiment_design_df.drop('std.order', axis=1)
experiment_design_df = experiment_design_df.drop('run.order', axis=1)

#get the number of experiments
number_of_experiments = experiment_design_df.shape[0]


##### Compatibility checks

# import experimental design parameters
with open('design_parameters.json') as json_file:
    design_parameters = json.load(json_file)

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


#### Assign Master Mixes to experiments

# import experiment_variables
with open('experiment_variables.json') as json_file:
    experiment_variables = json.load(json_file)
experiment_variables = pd.DataFrame(experiment_variables)




### Split design in to aqueous and components columns

## Aqueous

# get the experiment_variables == "Aqueous" and get the list of names
aqueous_lookup_table = experiment_variables[experiment_variables["Type"] == "Aqueous"]
aqueous_variables = list(aqueous_lookup_table["Variable"])

# select aqueous variables in experimental design
experiment_design_df_aqueous = experiment_design_df[aqueous_variables]

# tag the experiments with an index to make reordering easier later
experiment_design_df_aqueous = experiment_design_df_aqueous.reset_index()


## Components

# get the experiment_variables == "Components" and get the list of names
Components_lookup_table = experiment_variables[experiment_variables["Type"] == "Components"]
Components_variables = list(Components_lookup_table["Variable"])

# select Components variables in experimental design
experiment_design_df_Components = experiment_design_df[Components_variables]

# tag the experiments with an index to make reordering easier later
experiment_design_df_Components = experiment_design_df_Components.reset_index()



##### build master mix dfs

## aqueous

# Get unique rows
aqueous_master_mixes = experiment_design_df_aqueous.copy()
# drop index
aqueous_master_mixes = aqueous_master_mixes.drop("index", axis=1)
# Get unique rows
aqueous_master_mixes = aqueous_master_mixes.drop_duplicates()

## components

# Get unique rows
components_master_mixes = experiment_design_df_Components.copy()
# drop index
components_master_mixes = components_master_mixes.drop("index", axis=1)
# Get unique rows
components_master_mixes = components_master_mixes.drop_duplicates()


## row wise, count the number of instances that that master mix has in the total design
def CountExperimentsPerMasterMix(MasterMixDF, ExperimentDF):

    master_mix_experiment_counter_list = []

    for idx, master_mix in MasterMixDF.iterrows():

        master_mix_experiment_counter = 0

        for idx, exp in ExperimentDF.iterrows():

            exp = exp.drop("index")
            
            if exp.equals(master_mix) == True:
                master_mix_experiment_counter += 1


        master_mix_experiment_counter_list.append(master_mix_experiment_counter)
    MasterMixDF["Experiments"] = master_mix_experiment_counter_list

    return MasterMixDF

aqueous_master_mixes = CountExperimentsPerMasterMix(aqueous_master_mixes, experiment_design_df_aqueous)
components_master_mixes = CountExperimentsPerMasterMix(components_master_mixes, experiment_design_df_Components)


###### sanity check to make sure the number of experiments per master mix == total experiments

if aqueous_master_mixes["Experiments"].sum() == experiment_design_df.shape[0] and components_master_mixes["Experiments"].sum() == experiment_design_df.shape[0]:
    print("Master Mix experiment counts check out..")
else:
    raise ValueError('Experiments per Master mix do not match total number of experiments.' )



#print("experiment_design_df_aqueous.sort_values(by=aqueous_variables)")
#print(aqueous_master_mixes.sort_values(by=aqueous_variables))





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
    print("There is an error with the number of experiments")


print(" ")
print("Assigning reagent sources and wells...")
print(" ")


#### Creating the nested master pipetting settings JSON

# import the components.json and build df
with open('components.json') as json_file:
    components_df = pd.DataFrame(json.load(json_file))

# import the base_experiment_settings:
with open('base_settings/base_experiment_settings.json') as json_file:
    base_experiment_settings_dict = json.load(json_file)



# import the base settings
with open('base_settings/base_pipetting_settings.json') as json_file:
    base_pipetting_settings_dict = json.load(json_file)

# initialise empty a master_plate_pipetting_settings_dict
master_plate_pipetting_settings_dict = {}

# initialise empty a master_plate_experiment_settings_dict
master_plate_experiment_settings_dict = {}

# initialise empty a pre_experiment_compilation_dict
pre_experiment_compilation_dict = {}


# slice the df to deal with one plate at a time
for plate in range(1, plates_required+1,1):


    single_plate_df = experiment_design_df[experiment_design_df['Plate'] == plate]



    # initialise the plate_pipetting_settings_dict
    plate_pipetting_settings_dict = {}

    # initialise the plate_experiment_settings_dict
    plate_experiment_settings_dict = {}

    ### initialise working_index
    # this number keeps track of which PCR tube of master mixes is selected
    working_index = 0

    # iterate over the runs of single_plate_df:
    for index, runner in enumerate(range(0,single_plate_df.shape[0],1)):

        run = single_plate_df.iloc[index,:]
  

        # pipetting_settings:

        # copy the base_pipetting_settings_dict
        run_pipetting_settings_dict = base_pipetting_settings_dict.copy()

        # create the run_name from well name
        run_name = run["Well"]

        # iterate over the variable names and update the run_pipetting_settings_dict with the correct value from the experiment_design_df
        for var in components_df["Variable"]:
            run_pipetting_settings_dict[var] = run[var]

        # save the run_pipetting_settings_dict as an entry of the plate_pipetting_settings_dict with the run_name as it's key
        plate_pipetting_settings_dict[run_name] = run_pipetting_settings_dict


        # experiment settings:

        # copy the base_experiment_settings_dict:
        run_experiment_settings_dict = base_experiment_settings_dict.copy()
        # use the run_name to assign the dispense well.
        run_experiment_settings_dict['dispense_well'] = run_name

        ### attaching the correct substrates_source_well
        ### each 200ul PCR tube can supply:
        # 25x 10ul reactions - progress to next every 24 (1x row of nunc plate)
        # 12x 20ul reactions - progress to next every 12 (0.5x row of nunc plate)
        # add one because of python indexing

        # check reaction volume here
        if base_pipetting_settings_dict['substrates_dispense_volume'] ==  15:
            # sanity check volume
            if (base_pipetting_settings_dict['substrates_dispense_volume'] + base_pipetting_settings_dict['lysate_dispense_volume']) == 20:
                total_reaction_volume = 20
            else:
                print("Error: lysate and substrate volumes don't seem to add up")
                print("Lysate volume: "+ str(base_pipetting_settings_dict['lysate_dispense_volume']))
                print("Substrate volume: "+ str(base_pipetting_settings_dict['substrates_dispense_volume']))
        else:
                print("Error: Unknown Substrate Volume")
                print("Lysate volume: "+ str(base_pipetting_settings_dict['lysate_dispense_volume']))
                print("Substrate volume: "+ str(base_pipetting_settings_dict['substrates_dispense_volume']))

        #### now generate the list of experiments per pcr tube list.
        if total_reaction_volume == 20:
            reactions_per_pcr_tube = 12

        elif total_reaction_volume == 10:
            reactions_per_pcr_tube = 24
        else:
            print("Error: unknown total reaction volume.")

        experiments_per_pcr_tube_list = list(range(reactions_per_pcr_tube, 385, reactions_per_pcr_tube))


        # simply adding one for python indexing
        experiment_number = index + 1

        ### set the lower bound
        if working_index == 0:
            lower_bound = 0
        elif working_index == 1:
            lower_bound = experiments_per_pcr_tube_list[0]
        else:
            lower_bound = experiments_per_pcr_tube_list[(working_index-1)]

        ### set the upper bound
        upper_bound = experiments_per_pcr_tube_list[working_index]

        # now see if the experiment number is between the bounds - the experiments capacity of each pcr tube
        if experiment_number > lower_bound and experiment_number <= upper_bound:

            ### assign the appropriate wells with lookup
            run_experiment_settings_dict['substrates_source_well'] = substrate_source_list_possibles[working_index]
            run_experiment_settings_dict['lysate_source_well'] = lysate_source_list_possibles[working_index]

            if experiment_number == experiments_per_pcr_tube_list[working_index]:
                # if the experiment number has reached the
                # experiments_per_pcr_tube threshold (experiments_per_pcr_tube_list[working_index])
                # increment
                working_index = working_index + 1


        # save the run_experiment_settings as an entry of the plate_experiment_settings_dict with the run_name as it's key
        plate_experiment_settings_dict[run_name] = run_experiment_settings_dict




    ## organising the platewise_pre_experiment_compliation_dict
    platewise_pre_experiment_compliation_dict = {
        "substrate_source_tubes_required": math.ceil(experiment_number/reactions_per_pcr_tube),
        "substrate_source_tubes_list": substrate_source_list_possibles[0:math.ceil(experiment_number/reactions_per_pcr_tube)],
        "substrate_source_volume": 210,
        "substrates_source_well": "B2",
        "lysate_source_tubes_required": math.ceil(experiment_number/reactions_per_pcr_tube),
        "lysate_source_tubes_list": lysate_source_list_possibles[0:math.ceil(experiment_number/reactions_per_pcr_tube)],
        "lysate_source_volume": 85,
        "lysate_source_well": "B3"
    }


    # store the number of substrate source tubes needed
    pre_experiment_compilation_dict[plate] = platewise_pre_experiment_compliation_dict

    # save the plate_pipetting_settings_dict as an entry of the master_plate_pipetting_settings_dict with the plate as it's key
    master_plate_pipetting_settings_dict[plate] = plate_pipetting_settings_dict

    # save the plate_experiment_settings_dict as an entry of the master_plate_experiment_settings_dict with the plate as it's key
    master_plate_experiment_settings_dict[plate] = plate_experiment_settings_dict


# save the pipetting_settings_dict and experiment_settings_dict to individual .jsons based on plate
for plate in range(1, plates_required+1,1):

    #### Pipetting settings

    # segregate dicts
    pipetting_save_dict = master_plate_pipetting_settings_dict[plate]
    # use the experiment_prefix and the plate number to name the file
    pipetting_filename = "processed_ot2_settings/" + experiment_prefix +"_plate_"+str(plate)+"_pipetting_settings.json"
    with open(pipetting_filename, 'w') as fp:
        json.dump(pipetting_save_dict, fp)

    #### _experiment_settings
    # segregate dicts
    experiment_save_dict = master_plate_experiment_settings_dict[plate]
    # use the experiment_prefix and the plate number to name the file
    experiment_filename = "processed_ot2_settings/" + experiment_prefix +"_plate_"+str(plate)+"_experiment_settings.json"
    with open(experiment_filename, 'w') as fp:
        json.dump(experiment_save_dict, fp)


print("")
print("Assigning complete.")
print("")
print(" ")
print(" ")
print("Experiment breakdown:")
print(" ")
print("Number of total runs: "+str(num_of_runs))
print("Plate capacity due to well spacing: "+ str(plate_capacity)+ " runs.")
print("Total rxn volume: " +str(total_reaction_volume)+ "ul")
print("plates_required: " +str(plates_required))
print("runs_per_plate: " +str(runs_per_plate))
print("")
print("")
print("Instructions for each plate:")
print("")
print("lysate_source_tubes_required: "+str(platewise_pre_experiment_compliation_dict["lysate_source_tubes_required"]))
print("substrate_source_tubes_required: "+str(platewise_pre_experiment_compliation_dict["substrate_source_tubes_required"]))
print("")
print("Prepare a substrate master mix in " + platewise_pre_experiment_compliation_dict["substrates_source_well"] +" of the icebox totalling: " + str(210*platewise_pre_experiment_compliation_dict["substrate_source_tubes_required"]*1.2)+"ul.")
print("Aliquot "+ str(85*platewise_pre_experiment_compliation_dict["substrate_source_tubes_required"]*1.2) + "ul of lysate into "+platewise_pre_experiment_compliation_dict["lysate_source_well"] +" of the icebox.")



# save the pre_experiment_compilation_dict

# use the experiment_prefix and the plate number to name the file
pre_experiment_filename = "processed_ot2_settings/" + experiment_prefix +"_pre_experiment_compilations.json"
with open(pre_experiment_filename, 'w') as fp:
    json.dump(pre_experiment_compilation_dict, fp)


# save the experiment_design_df

#drop the first column - it's just crap spat out from R
experiment_design_df = experiment_design_df.iloc[:,1:]
# save the updated design
experiment_design_df.to_csv("processed_data_files/design_real_assigned.csv", index=False)

