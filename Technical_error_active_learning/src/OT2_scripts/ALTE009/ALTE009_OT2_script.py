from re import T
from opentrons import protocol_api
import json
import os

# metadata
metadata = {
    "protocolName": "Lysate CFPS Plating Script v1",
    "author": "Alex Perkins",
    "email": "a.j.p.perkins@sms.ed.ac.uk",
    "description": "First draft of script to plate out 10x lysate reactions",
    "apiLevel": "2.3",
}

# Add 35ul of lysate to a PCR tube to A1 in cold block
# Defining the aspiration height for 35ul of lysate  "lysate_aspirate_height_init" : 4.5,

# Add 90ul of substrates mix to B1
# Defining the aspiration height for 90ul of substrates: "substrates_aspirate_height_init" : 8.6,

## Substate calculator on Labstep

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
    experiment_settings_dict_path = experiment_prefix + "_plate_"+str(plate_number)+"_experiment_settings.json"
    print(experiment_settings_dict_path)
    #
    #labware_settings_dict_path = "/data/user_storage/"+ experiment_prefix + "/" + experiment_prefix + "_labware_settings.json"
    labware_settings_dict_path = experiment_prefix + "_labware_settings.json"
    #
    #master_pipetting_settings_dict_path = "/data/user_storage/" + experiment_prefix + "/" + experiment_prefix + "_plate_"+str(plate_number)+"_pipetting_settings.json"
    master_pipetting_settings_dict_path = experiment_prefix + "_plate_"+str(plate_number)+"_pipetting_settings.json"

    pre_experiment_compilation_dict_path = experiment_prefix + "_pre_experiment_compilations.json"

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
    protocol_pre_experiment_compilations = True
    protocol_dispense_lysate = True
    protocol_dispense_substrates = True
    protocol_dispense_wax = True

    # labware

    # Defining the temperature module
    temperature_module = protocol.load_module(labware_settings_dict["temp_module_name"], labware_settings_dict["temp_module_pos"])


    # Defining the pcr plate ontop of the temperature module
    pcr_temp_plate = temperature_module.load_labware(
        labware_settings_dict["pcr_temp_plate_name"],
        label="Temperature-Controlled Tubes",
    )
    # Defining the 384 nunc well plate
    nunc_384 = protocol.load_labware(labware_settings_dict["nunc_384_name"], labware_settings_dict["nunc_384_pos"])

    # Defining the 1.5ul eppendorf rack
    eppendorf_2ml_x24_rack = protocol.load_labware(
        labware_settings_dict["eppendorf_2ml_x24_rack_name"], labware_settings_dict["eppendorf_2ml_x24_rack_pos"]
    )

    # Defining the 20ul tip rack
    tiprack_20ul_1 = protocol.load_labware(labware_settings_dict["tiprack_20ul_1_name"], labware_settings_dict["tiprack_20ul_1_pos"])
    tiprack_20ul_2 = protocol.load_labware(labware_settings_dict["tiprack_20ul_2_name"], labware_settings_dict["tiprack_20ul_2_pos"])
    tiprack_20ul_3 = protocol.load_labware(labware_settings_dict["tiprack_20ul_3_name"], labware_settings_dict["tiprack_20ul_3_pos"])
    tiprack_20ul_4 = protocol.load_labware(labware_settings_dict["tiprack_20ul_4_name"], labware_settings_dict["tiprack_20ul_4_pos"])
    tiprack_20ul_5 = protocol.load_labware(labware_settings_dict["tiprack_20ul_5_name"], labware_settings_dict["tiprack_20ul_5_pos"])


    # Defining left_pipette (p20)
    left_pipette = protocol.load_instrument(
        labware_settings_dict["left_pipette_name"], "left", tip_racks=[tiprack_20ul_1,tiprack_20ul_2, tiprack_20ul_3, tiprack_20ul_4, tiprack_20ul_5]
    )

    # Defining the 300ul tip rack
    tiprack_300ul_1 = protocol.load_labware(labware_settings_dict["tiprack_300ul_1_name"], labware_settings_dict["tiprack_300ul_1_pos"])
    tiprack_300ul_2 = protocol.load_labware(labware_settings_dict["tiprack_300ul_2_name"], labware_settings_dict["tiprack_300ul_2_pos"])
    tiprack_300ul_3 = protocol.load_labware(labware_settings_dict["tiprack_300ul_3_name"], labware_settings_dict["tiprack_300ul_3_pos"])

    # Defining right_pipette (p300)
    right_pipette = protocol.load_instrument(
        labware_settings_dict["right_pipette_name"], "right", tip_racks=[tiprack_300ul_1, tiprack_300ul_2, tiprack_300ul_3]
    )
    # 2. Defining functions used in this protocol------------------------------

    # Distributing master mix Energy Solution, Buffer A, DNA, chi6, water etc.
    def distribute_substrates(well, source_well, substrates_aspirate_height):

        left_pipette.pick_up_tip()

        left_pipette.well_bottom_clearance.aspirate = substrates_aspirate_height
        left_pipette.well_bottom_clearance.dispense = pipetting_settings_dict["substrates_dispense_well_bottom_clearance"]

        # aspirate step
        left_pipette.aspirate(pipetting_settings_dict["substrates_aspirate_volume"], source_well, rate=pipetting_settings_dict["substrates_aspirate_rate"])
        left_pipette.move_to(source_well.top(-2))
        left_pipette.touch_tip()

        # Dispense Step
        left_pipette.dispense(pipetting_settings_dict["substrates_dispense_volume"], nunc_384[well], rate=pipetting_settings_dict["substrates_dispense_rate"])

        left_pipette.drop_tip()


    # Distributing lysate
    def distribute_lysate(well, source_well, lysate_aspirate_height):

        left_pipette.pick_up_tip()

        left_pipette.well_bottom_clearance.aspirate = lysate_aspirate_height
        left_pipette.well_bottom_clearance.dispense = pipetting_settings_dict["lysate_dispense_well_bottom_clearance"]

        # aspirate step
        left_pipette.aspirate(pipetting_settings_dict["lysate_aspirate_volume"], source_well, rate=pipetting_settings_dict["lysate_aspirate_rate"])
        left_pipette.move_to(source_well.top(-2))
        protocol.delay(seconds=2)
        left_pipette.touch_tip()

        # Dispense Step
        left_pipette.dispense(pipetting_settings_dict["lysate_dispense_volume"], nunc_384[well], rate=pipetting_settings_dict["lysate_dispense_rate"])
        left_pipette.touch_tip()

        left_pipette.drop_tip()



    def dispense_wax_to_individual_replicate_set(dispense_well_list):

        """ defines the dispense wax function """

        # Pick up a 300ul tip
        #right_pipette.pick_up_tip()

        # Distributing 35ul of wax ontop of each well in dispense_well_list
        right_pipette.distribute(
            pipetting_settings_dict["wax_dispense_volume"],
            wax_source_well,
            [
                nunc_384.wells_by_name()[well_name].top(pipetting_settings_dict["wax_dispense_height"])
                for well_name in dispense_well_list
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
    #temperature_module.set_temperature(16)



    # 3.1 Pre experiment compliations-------------------------------------------------------------------

    if protocol_pre_experiment_compilations:

        substrate_source_volume = pre_experiment_compilation_dict["substrate_source_volume"]
        substrate_source_tubes_list = pre_experiment_compilation_dict["substrate_source_tubes_list"]

        right_pipette.distribute(
            substrate_source_volume,
            # source well here,
            # need to refer to the right rack substrate_source_tubes_list,
            new_tip = True,
            touch_tip = True,
            air_gap = 10,
            disposal_volume = False,
        )










    # Extracting the different experiments from the experiments
    # settings file
    experiment_ids = experiment_settings_dict.keys()





    # Running the substrate dispense step if protocol_dispense_substrates = True
    if protocol_dispense_substrates:

        # Looping through the different experiments
        for experiment_id in experiment_ids:


            # retrieve the correct pipetting setting for that particular well
            pipetting_settings_dict = master_pipetting_settings_dict[experiment_id]


            # Defining the source well for the substrates master mix
            substrates_source_well = eppendorf_2ml_x24_rack[experiment_settings_dict[experiment_id]["substrates_source_well"]]

            # Defining a list of wells for dispensing
            dispense_well_list = experiment_settings_dict[experiment_id]["dispense_well_list"]

            # Defining the initial lysate aspiration height
            substrates_aspirate_height = pipetting_settings_dict["substrates_aspirate_height_init"]

            # Dispensing substrates into each of the wells in dispense well list
            for well in dispense_well_list:

                # Caliing function to distribute substrates
                distribute_substrates(
                    well, substrates_source_well, substrates_aspirate_height
                )

                # Reducing the aspiration height by subsrates_aspirate_height_inc
                substrates_aspirate_height -= pipetting_settings_dict["substrates_aspirate_height_inc"]

                protocol.comment("substrates_aspirate_height: " + str(substrates_aspirate_height))


            protocol.comment("Substrate dispense step complete for experiment " + experiment_id)




    # Running the lysate dispense step if protocol_dispense_lysate = True
    if protocol_dispense_lysate:

        # Looping through the different experiments
        for experiment_id in experiment_ids:


            # retrieve the correct pipetting setting for that particular well
            pipetting_settings_dict = master_pipetting_settings_dict[experiment_id]

            # Outputting the name of the experiment that is being ran
            protocol.comment("Running experiment " + experiment_id)

            # Defining the source wells for the different components in this experiment
            lysate_source_well = eppendorf_2ml_x24_rack[experiment_settings_dict[experiment_id]["lysate_source_well"]]

            # Defining a list of wells for dispensing
            dispense_well_list = experiment_settings_dict[experiment_id]["dispense_well_list"]

            # Defining the initial lysate aspiration height
            lysate_aspirate_height = pipetting_settings_dict["lysate_aspirate_height_init"]

            # Dispensing lysate into each of the wells in dispense well list
            for well in dispense_well_list:

                # Caliing function to distribute lysate
                distribute_lysate(well, lysate_source_well, lysate_aspirate_height)

                # Reducing the aspiration height by lysate_aspirate_height_inc
                lysate_aspirate_height -= pipetting_settings_dict["lysate_aspirate_height_inc"]

            protocol.comment("Lysate dispense step complete for experiment " + experiment_id)



    # Pausing protocol so the plate can be span down in the centrifuge before

    # Turning off temp module after all experiments have finished
    temperature_module.deactivate()

    protocol.comment("end of plating")

    # adding the wax ontop
    protocol.pause("Check plate and spin down, before replacing for wax")


    # Running the wax dispense step if protocol_dispense_wax = True
    if protocol_dispense_wax:

        # Looping through the different experiments
        for experiment_id in experiment_ids:

            # retrieve the correct pipetting setting for that particular well
            pipetting_settings_dict = master_pipetting_settings_dict[experiment_id]

            # Defining a list of wells for dispensing
            dispense_well_list = experiment_settings_dict[experiment_id]["dispense_well_list"]

            # Defining the source well for the wax
            wax_source_well = eppendorf_2ml_x24_rack.wells_by_name()[experiment_settings_dict[experiment_id]["wax_source_well"]]

            dispense_wax_to_individual_replicate_set(dispense_well_list)

            protocol.comment("Wax dispense step complete for experiment " + experiment_id)
