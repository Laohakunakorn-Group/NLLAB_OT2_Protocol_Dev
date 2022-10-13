import json
import pandas as pd
import math

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
experiment_design_df = pd.read_csv("design_real.csv")

# generate the well well_list_384
well_list_384 = generate_well_list_384()

#  store the number of runs - the num of rows of the df
num_of_runs = experiment_design_df.shape[0]

# if there are fewer experiments than or exactly 384 (the plate capacity), then just label the with enough wells
if num_of_runs <= 384:
    experiment_design_df['Well'] = well_list_384[:num_of_runs]
    experiment_design_df['Plate'] = 1

    print("plates_required: " +str(1))
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


experiment_design_df.to_csv("out.csv")
