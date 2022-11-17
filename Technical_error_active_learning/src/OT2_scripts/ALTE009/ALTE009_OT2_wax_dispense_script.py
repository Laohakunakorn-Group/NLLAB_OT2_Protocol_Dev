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
    print(experiment_settings_dict_path)
    #
    #labware_settings_dict_path = "/data/user_storage/"+ experiment_prefix + "/" + experiment_prefix + "_labware_settings.json"
    labware_settings_dict_path = "processed_ot2_settings/" + experiment_prefix + "_labware_settings.json"
    #
    #master_pipetting_settings_dict_path = "/data/user_storage/" + experiment_prefix + "/" + experiment_prefix + "_plate_"+str(plate_number)+"_pipetting_settings.json"
    master_pipetting_settings_dict_path = "processed_ot2_settings/" + experiment_prefix + "_plate_"+str(plate_number)+"_pipetting_settings.json"

    pre_experiment_compilation_dict_path = "processed_ot2_settings/" + experiment_prefix + "_pre_experiment_compilations.json"

    # Reading in json json_settings_file


    experiment_settings_dict = json.load(open(experiment_settings_dict_path, 'r'))
    protocol.comment("Experiment settings json file was read in")

    labware_settings_dict = json.load(open(labware_settings_dict_path, 'r'))
    protocol.comment("Labware settings json file was read in")

    master_pipetting_settings_dict = json.load(open(master_pipetting_settings_dict_path, 'r'))
    protocol.comment("Pipetting settings json file was read in")

    pre_experiment_compilation_dict = json.load(open(pre_experiment_compilation_dict_path, 'r'))
    protocol.comment("Pre experiment compilations json file was read in")

    pre_experiment_compilation_dict = pre_experiment_compilation_dict[plate_number_string]
    protocol.comment("Pre experiment compilations Plate: "+plate_number_string +" Selected.")

    # 1. Defining variables used in protocol-----------------------------------

    # Defining the booleans for the protocol. This controls which parts of
    # the protocol to run.

    temp_toggle = False

    protocol_dispense_wax = True
    # labware

    # Defining the temperature module
    temperature_module = protocol.load_module(labware_settings_dict["temp_module"]["name"], labware_settings_dict["temp_module"]["pos"])


    # Defining the pcr plate ontop of the temperature module
    # Defining the 384 nunc well plate
    nunc_384 = temperature_module.load_labware(labware_settings_dict["nunc_384"]["name"], labware_settings_dict["nunc_384"]["pos"])
    nunc_384.set_offset(x = labware_settings_dict["nunc_384"]["offsets"]["x"],
                        y = labware_settings_dict["nunc_384"]["offsets"]["y"],
                        z = labware_settings_dict["nunc_384"]["offsets"]["z"]
                        )



    # Defining the eppendorf_2ml_x24_icebox_rack.
    # Because this is a custom labware definition, it needs to be loaded in manually to be used with opentrons_execute

    def load_custom_labware(file_path,location):
        with open(file_path) as labware_file:
            labware_def = json.load(labware_file)
        return protocol.load_labware_from_definition(labware_def, location)

    custom_labware_on_ot2_path = "maintenance/custom_labware/nllab3dprinted_24_tuberack_2000ul.json"
    eppendorf_2ml_x24_icebox_rack = load_custom_labware(custom_labware_on_ot2_path, labware_settings_dict["eppendorf_2ml_x24_icebox_rack"]["pos"])
    eppendorf_2ml_x24_icebox_rack.set_offset(x = labware_settings_dict["eppendorf_2ml_x24_icebox_rack"]["offsets"]["x"],
                                             y = labware_settings_dict["eppendorf_2ml_x24_icebox_rack"]["offsets"]["y"],
                                             z = labware_settings_dict["eppendorf_2ml_x24_icebox_rack"]["offsets"]["z"]
                                             )


    # Defining left_pipette (p20)
    #left_pipette = protocol.load_instrument(
    #    labware_settings_dict["left_pipette"]["name"], "left", tip_racks=[tiprack_20ul_1,tiprack_20ul_2, tiprack_20ul_3, tiprack_20ul_4, tiprack_20ul_5]
    #)

    # Defining the 300ul tip rack
    tiprack_300ul_1 = protocol.load_labware(labware_settings_dict["tiprack_300ul_1"]["name"], labware_settings_dict["tiprack_300ul_1"]["pos"])
    tiprack_300ul_1.set_offset(x = labware_settings_dict["tiprack_300ul_1"]["offsets"]["x"],
                              y = labware_settings_dict["tiprack_300ul_1"]["offsets"]["y"],
                              z = labware_settings_dict["tiprack_300ul_1"]["offsets"]["z"]
                              )

    tiprack_300ul_2 = protocol.load_labware(labware_settings_dict["tiprack_300ul_2"]["name"], labware_settings_dict["tiprack_300ul_2"]["pos"])
    tiprack_300ul_2.set_offset(x = labware_settings_dict["tiprack_300ul_2"]["offsets"]["x"],
                              y = labware_settings_dict["tiprack_300ul_2"]["offsets"]["y"],
                              z = labware_settings_dict["tiprack_300ul_2"]["offsets"]["z"]
                              )

    tiprack_300ul_3 = protocol.load_labware(labware_settings_dict["tiprack_300ul_3"]["name"], labware_settings_dict["tiprack_300ul_3"]["pos"])
    tiprack_300ul_3.set_offset(x = labware_settings_dict["tiprack_300ul_3"]["offsets"]["x"],
                              y = labware_settings_dict["tiprack_300ul_3"]["offsets"]["y"],
                              z = labware_settings_dict["tiprack_300ul_3"]["offsets"]["z"]
                              )

    # Defining right_pipette (p300)
    right_pipette = protocol.load_instrument(
        labware_settings_dict["right_pipette"]["name"], "right", tip_racks=[tiprack_300ul_1, tiprack_300ul_2, tiprack_300ul_3]
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
        len_of_dispense_set = math.floor(300/wax_dispense_volume)

        # number of sets in the total list:
        num_of_dispense_sets = math.ceil(len(total_list_of_dispense_wells_for_plate)/len_of_dispense_set)


        for set_idx in range(1, num_of_dispense_sets,1):

            # set the counters as appropriate
            aft_counter = (set_idx-1) * len_of_dispense_set
            fore_counter = set_idx * len_of_dispense_set
            # retrive the list
            dispense_well_list = total_list_of_dispense_wells_for_plate[aft_counter:fore_counter]

            # as all the wax pipetting steps are supposed to be the same - I'll just pull out the first one.
            pipetting_settings_dict = master_pipetting_settings_dict[list(master_pipetting_settings_dict.keys())[0]]


            # Defining the source well for the wax
            #wax_source_well = eppendorf_2ml_x24_icebox_rack.wells_by_name()[experiment_settings_dict[experiment_id]["wax_source_well"]]

            dispense_wax_to_individual_replicate_set(wax_source_well, dispense_well_list, pipetting_settings_dict)

            protocol.comment("Wax dispense step complete for experiment " + experiment_id)

    # Turning off temp module after all experiments have finished
    if temp_toggle:
        temperature_module.deactivate()


            ################ NEED TO USE A TUBE THAT CAN HOLD A PLATE OF 384 * 35ul = 15ml falcon.
