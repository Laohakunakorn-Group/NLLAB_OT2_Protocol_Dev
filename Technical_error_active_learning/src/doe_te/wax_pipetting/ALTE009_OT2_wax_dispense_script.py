from re import T
from opentrons import protocol_api
import json
import os
import math

# metadata
metadata = {
    "protocolName": "Lysate CFPS Plating Script v1",
    "author": "Alex Perkins",
    "email": "a.j.p.perkins@sms.ed.ac.uk",
    "description": "First draft of script to plate out 10x lysate reactions",
    "apiLevel": "2.8",
}



# Protocol run function. the part after the colon lets your editor know
# where to look for autocomplete suggestions
def run(protocol: protocol_api.ProtocolContext):

    # 0. Reading in json setting files-----------------------------------------

    experiment_prefix = "ALTE009"
    plate_number = 1
    plate_number_string = str(plate_number)


    # Defining the file paths of raspberry pi
    #
    #experiment_settings_dict_path = "/data/user_storage/"+ experiment_prefix + "/" + experiment_prefix + "_plate_"+str(plate_number)+"_experiment_settings.json"
    experiment_settings_dict_path = "processed_ot2_settings/" + experiment_prefix + "_plate_"+str(plate_number)+"_experiment_settings.json"

    #
    #wax_labware_settings_dict_path = "/data/user_storage/"+ experiment_prefix + "/" + experiment_prefix + "_wax_labware_settings.json"
    wax_labware_settings_dict_path = "ot2_labware_settings/" + experiment_prefix + "_wax_labware_settings.json"
    #
    #master_pipetting_settings_dict_path = "/data/user_storage/" + experiment_prefix + "/" + experiment_prefix + "_plate_"+str(plate_number)+"_pipetting_settings.json"
    master_pipetting_settings_dict_path = "processed_ot2_settings/" + experiment_prefix + "_plate_"+str(plate_number)+"_pipetting_settings.json"

    pre_experiment_compilation_dict_path = "processed_ot2_settings/" + experiment_prefix + "_pre_experiment_compilations.json"

    # Reading in json json_settings_file


    experiment_settings_dict = json.load(open(experiment_settings_dict_path, 'r'))
    protocol.comment("Experiment settings json file was read in")

    wax_labware_settings_dict = json.load(open(wax_labware_settings_dict_path, 'r'))
    protocol.comment("Labware settings json file was read in")

    master_pipetting_settings_dict = json.load(open(master_pipetting_settings_dict_path, 'r'))
    protocol.comment("Pipetting settings json file was read in")

    pre_experiment_compilation_dict = json.load(open(pre_experiment_compilation_dict_path, 'r'))
    protocol.comment("Pre experiment compilations json file was read in")

    pre_experiment_compilation_dict = pre_experiment_compilation_dict[plate_number_string]
    protocol.comment("Pre experiment compilations Plate: "+plate_number_string +" Selected.")


    # Extracting the different experiments from the experiments
    # settings file
    experiment_ids = experiment_settings_dict.keys()

    # 1. Defining variables used in protocol-----------------------------------

    # Defining the booleans for the protocol. This controls which parts of
    # the protocol to run.

    temp_toggle = False

    protocol_dispense_wax = True
    # labware

    # Defining the temperature module
    temperature_module = protocol.load_module(wax_labware_settings_dict["temp_module"]["name"], wax_labware_settings_dict["temp_module"]["pos"])


    # Defining the pcr plate ontop of the temperature module
    # Defining the 384 nunc well plate
    nunc_384 = temperature_module.load_labware(wax_labware_settings_dict["nunc_384"]["name"])
    nunc_384.set_offset(x = wax_labware_settings_dict["nunc_384"]["offsets"]["x"],
                        y = wax_labware_settings_dict["nunc_384"]["offsets"]["y"],
                        z = wax_labware_settings_dict["nunc_384"]["offsets"]["z"]
                        )


    # Defining the custom_15_50_tube_rack
    # 3d printed by uses offical api def: opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical
    custom_15_50_tube_rack = protocol.load_labware(wax_labware_settings_dict["custom_15_50_tube_rack"]["name"], wax_labware_settings_dict["custom_15_50_tube_rack"]["pos"])
    custom_15_50_tube_rack.set_offset(x = wax_labware_settings_dict["custom_15_50_tube_rack"]["offsets"]["x"],
                                             y = wax_labware_settings_dict["custom_15_50_tube_rack"]["offsets"]["y"],
                                             z = wax_labware_settings_dict["custom_15_50_tube_rack"]["offsets"]["z"]
                                             )




    # Defining the 300ul tip rack
    tiprack_300ul_1 = protocol.load_labware(wax_labware_settings_dict["tiprack_300ul_1"]["name"], wax_labware_settings_dict["tiprack_300ul_1"]["pos"])
    tiprack_300ul_1.set_offset(x = wax_labware_settings_dict["tiprack_300ul_1"]["offsets"]["x"],
                              y = wax_labware_settings_dict["tiprack_300ul_1"]["offsets"]["y"],
                              z = wax_labware_settings_dict["tiprack_300ul_1"]["offsets"]["z"]
                              )

    # Defining right_pipette (p300)
    right_pipette = protocol.load_instrument(
        wax_labware_settings_dict["right_pipette"]["name"], "right", tip_racks=[tiprack_300ul_1]
    )




    # 2. Defining functions used in this protocol------------------------------


    def dispense_wax_to_individual_replicate_set(wax_source_well, dispense_well_list, pipetting_settings_dict):

        """ defines the dispense wax function """

        # Pick up a 300ul tip
        #right_pipette.pick_up_tip()

        # Distributing 35ul of wax ontop of each well in dispense_well
        right_pipette.distribute(
            pipetting_settings_dict["wax_dispense_volume"],
            wax_source_well,
            [
                nunc_384.wells_by_name()[individual_well].top(pipetting_settings_dict["wax_dispense_height"])
                for individual_well in dispense_well_list
            ],
            new_tip = pipetting_settings_dict["wax_new_tip"],
            touch_tip = pipetting_settings_dict["wax_touch_tip"],
            air_gap = pipetting_settings_dict["wax_air_gap"],
            disposal_volume = pipetting_settings_dict["wax_disposal_volume"],
        )

        # Drops tip
        #right_pipette.drop_tip()


    # 3. Running protocol------------------------------------------------------




    # Set temperature of temperature module to 4 degrees. The protocol will pause
    # until this is reached.
    if temp_toggle:
        temperature_module.set_temperature(4)


    # Running the wax dispense step if protocol_dispense_wax = True
    if protocol_dispense_wax:

        # get the experiment ids dispense wells as a list.
        total_list_of_dispense_wells_for_plate = []

        # Looping through the different experiments
        for experiment_id in experiment_ids:

            # Defining a list of wells for dispensing
            total_list_of_dispense_wells_for_plate.append(experiment_settings_dict[experiment_id]["dispense_well"])


        ### As the wax pipetting settings are generally the same, we can use the first one in the dict to get the info we need
        wax_dispense_volume = master_pipetting_settings_dict[list(master_pipetting_settings_dict.keys())[0]]["wax_dispense_volume"]

        #### Now use a counter to loop over sets of dispense wells.
        
        # length of sets = (300ul / 35ul) rounded down
        # Max pipette can do is 7
        len_of_dispense_set = math.floor(300/wax_dispense_volume) - 1
        # 7

        # number of sets in the total list:
        num_of_dispense_sets = math.ceil(len(total_list_of_dispense_wells_for_plate)/len_of_dispense_set)


        for set_idx in range(1, num_of_dispense_sets,1):

            # set the counters as appropriate
            # selects the well before the start of that set according to python indexing
            aft_counter = (set_idx-1) * len_of_dispense_set
            # selects the well at the top of that set but then minuses 1 for python indexing
            fore_counter = (set_idx * len_of_dispense_set)
            # retrive the list
            dispense_well_list = total_list_of_dispense_wells_for_plate[aft_counter:fore_counter]
            print("dispense well list")
            print(dispense_well_list)

            # as all the wax pipetting steps are supposed to be the same - I'll just pull out the first one.
            pipetting_settings_dict = master_pipetting_settings_dict[list(master_pipetting_settings_dict.keys())[0]]


            # Defining the source well for the wax
            wax_source_well = custom_15_50_tube_rack.wells_by_name()[experiment_settings_dict[experiment_id]["wax_source_well"]]

            dispense_wax_to_individual_replicate_set(wax_source_well, dispense_well_list, pipetting_settings_dict)

            protocol.comment("Wax dispense step complete for experiment " + experiment_id)

    # Turning off temp module after all experiments have finished
    if temp_toggle:
        temperature_module.deactivate()

    protocol.comment("")
    protocol.comment("All wax dispense steps complete.")
    protocol.comment("")
    protocol.comment("Place film over plate and start measurement.")