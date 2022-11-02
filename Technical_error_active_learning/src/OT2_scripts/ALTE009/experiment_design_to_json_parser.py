import json
import pandas as pd
import math


############

experiment_prefix = "ALTE009"

###########


# function to generate plate well well_list_384
def generate_well_list_384():
    Letters = ["A", "B", "C", "D", "E", "F","G","H","I", "J", "K", "L", "M", "N", "O", "P"]
    Numbers_1_24 = list(range(1, 25,1))

    well_list_384 = []
    for let in Letters:
        for num in Numbers_1_24:
            well_name = let + str(num)
            well_list_384.append(well_name)

    return well_list_384


# import the design
experiment_design_df = pd.read_csv("processed_data_files/design_real.csv")

print(experiment_design_df.head())

# generate the well well_list_384
well_list_384 = generate_well_list_384()

#  store the number of runs - the num of rows of the df
num_of_runs = experiment_design_df.shape[0]

# if there are fewer experiments than or exactly 384 (the plate capacity), then just label the with enough wells
if num_of_runs <= 384:
    experiment_design_df['Well'] = well_list_384[:num_of_runs]
    experiment_design_df['Plate'] = 1

    print("plates_required: " +str(1))
    plates_required = 1

    print("runs_per_plate: " +str(num_of_runs))


elif num_of_runs > 384:

    # divides by 384 and rounds up to next integer
    plates_required = math.ceil(num_of_runs / 384)

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

    print("plates_required: " +str(plates_required))
    print("runs_per_plate: " +str(runs_per_plate))


else:
    print("There is an error with the number of experiments")






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
        ### each 200ul PCR tube can supply 25x reactions. So progress every 24 (1x row of nunc plate)
        # add one because of python indexing
        experiment_number = index + 1

        if experiment_number <= 24:
            run_experiment_settings_dict['substrates_source_well'] = "A1"
            run_experiment_settings_dict['lysate_source_well'] = "B1"

        elif experiment_number <= 48:
            run_experiment_settings_dict['substrates_source_well'] = "A2"
            run_experiment_settings_dict['lysate_source_well'] = "B2"

        elif experiment_number <= 72:
            run_experiment_settings_dict['substrates_source_well'] = "A3"
            run_experiment_settings_dict['lysate_source_well'] = "B3"

        elif experiment_number <= 96:
            run_experiment_settings_dict['substrates_source_well'] = "A4"
            run_experiment_settings_dict['lysate_source_well'] = "B4"

        elif experiment_number <= 120:
            run_experiment_settings_dict['substrates_source_well'] = "A5"
            run_experiment_settings_dict['lysate_source_well'] = "B5"

        elif experiment_number <= 144:
            run_experiment_settings_dict['substrates_source_well'] = "A6"
            run_experiment_settings_dict['lysate_source_well'] = "B6"

        elif experiment_number <= 168:
            run_experiment_settings_dict['substrates_source_well'] = "A7"
            run_experiment_settings_dict['lysate_source_well'] = "B7"

        elif experiment_number <= 192:
            run_experiment_settings_dict['substrates_source_well'] = "A8"
            run_experiment_settings_dict['lysate_source_well'] = "B8"

        elif experiment_number <= 216:
            run_experiment_settings_dict['substrates_source_well'] = "A9"
            run_experiment_settings_dict['lysate_source_well'] = "B9"

        elif experiment_number <= 240:
            run_experiment_settings_dict['substrates_source_well'] = "A10"
            run_experiment_settings_dict['lysate_source_well'] = "B10"

        elif experiment_number <= 264:
            run_experiment_settings_dict['substrates_source_well'] = "A11"
            run_experiment_settings_dict['lysate_source_well'] = "B12"

        elif experiment_number <= 288:
            run_experiment_settings_dict['substrates_source_well'] = "A12"
            run_experiment_settings_dict['lysate_source_well'] = "B12"

        elif experiment_number <= 312:
            run_experiment_settings_dict['substrates_source_well'] = "A13"
            run_experiment_settings_dict['lysate_source_well'] = "B13"

        elif experiment_number <= 336:
            run_experiment_settings_dict['substrates_source_well'] = "A14"
            run_experiment_settings_dict['lysate_source_well'] = "B14"

        elif experiment_number <= 360:
            run_experiment_settings_dict['substrates_source_well'] = "A15"
            run_experiment_settings_dict['lysate_source_well'] = "B15"

        elif experiment_number <= 384:
            run_experiment_settings_dict['substrates_source_well'] = "A16"
            run_experiment_settings_dict['lysate_source_well'] = "B16"






        # save the run_experiment_settings as an entry of the plate_experiment_settings_dict with the run_name as it's key
        plate_experiment_settings_dict[run_name] = run_experiment_settings_dict

    #asdf
    substrate_source_list_possibles = ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10", "A11", "A12", "A13", "A14", "A15", "A16"]
    lysate_source_list_possibles = ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "B10", "B11", "B12", "B13", "B14", "B15", "B16"]

    platewise_pre_experiment_compliation_dict = {
        "substrate_source_tubes_required": math.ceil(experiment_number/24),
        "substrate_source_tubes_list": substrate_source_list_possibles[0:math.ceil(experiment_number/24)],
        "substrate_source_volume": 210,
        "substrates_source_well": "B2",
        "lysate_source_tubes_required": math.ceil(experiment_number/24),
        "lysate_source_tubes_list": lysate_source_list_possibles[0:math.ceil(experiment_number/24)],
        "lysate_source_volume": 85,
        "lysate_source_well": "B3"
    }

    print("")
    print("lysate_source_tubes_required: "+str(platewise_pre_experiment_compliation_dict["lysate_source_tubes_required"]))
    print("substrate_source_tubes_required: "+str(platewise_pre_experiment_compliation_dict["substrate_source_tubes_required"]))

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

