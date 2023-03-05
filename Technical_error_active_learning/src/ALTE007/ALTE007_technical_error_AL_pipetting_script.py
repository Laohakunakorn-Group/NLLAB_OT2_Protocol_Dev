from opentrons import protocol_api
import json

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

    # Defining the file paths of raspberry pi
    experiment_settings_dict_path = "/data/user_storage/ALTE007/ALTE007_experiment_settings.json"
    labware_settings_dict_path = "/data/user_storage/ALTE007/ALTE007_labware_settings.json"
    pipetting_settings_dict_path = "/data/user_storage/ALTE007/ALTE007_pipetting_settings.json"

    # Reading in json json_settings_file
    experiment_settings_dict = json.load(open(experiment_settings_dict_path, 'r'))
    protocol.comment("Experiment settings json file was read in")

    labware_settings_dict = json.load(open(labware_settings_dict_path, 'r'))
    protocol.comment("Labware settings json file was read in")

    pipetting_settings_dict = json.load(open(pipetting_settings_dict_path, 'r'))
    protocol.comment("Pipetting settings json file was read in")

    # 1. Defining variables used in protocol-----------------------------------

    # Defining the booleans for the protocol. This controls which parts of
    # the protocol to run.
    protocol_dispense_lysate = True
    protocol_dispense_substrates = True
    protocol_dispense_wax = True

    # labware

    # Defining the temperature module
    protocol.comment(labware_settings_dict["temp_module_name"])
    protocol.comment(labware_settings_dict["temp_module_pos"])
    temperature_module = protocol.load_module(labware_settings_dict["temp_module_name"], labware_settings_dict["temp_module_pos"])

    protocol.pause("Stop")

    # Defining the pcr plate ontop of the temperature module
    pcr_temp_plate = temperature_module.load_labware(
        labware_settings_dict["pcr_temp_plate_name"],
        label="Temperature-Controlled Tubes",
    )
    # Defining the 384 nunc well plate
    nunc_384 = protocol.load_labware(labware_settings_dict["nunc_384_name"], labware_settings_dict["nunc_384_pos"])

    # Defining the 1.5ul eppendorf rack
    eppendorf_1500ul_x24_rack = protocol.load_labware(
        labware_settings_dict["eppendorf_1500ul_x24_rack_name"], labware_settings_dict["eppendorf_1500ul_x24_rack_pos"]
    )

    # Defining the 20ul tip rack
    tiprack_20ul = protocol.load_labware(labware_settings_dict["tiprack_20ul_name"], labware_settings_dict["tiprack_20ul_pos"])

    # Defining left_pipette (p20)
    left_pipette = protocol.load_instrument(
        labware_settings_dict["left_pipette_name"], "left", tip_racks=[tiprack_20ul]
    )

    # Defining the 300ul tip rack
    tiprack_300ul = protocol.load_labware(labware_settings_dict["tiprack_300ul_name"], labware_settings_dict["tiprack_300ul_pos"])

    # Defining right_pipette (p300)
    right_pipette = protocol.load_instrument(
        labware_settings_dict["right_pipette_name"], "right", tip_racks=[tiprack_300ul]
    )

    # 2. Defining functions used in this protocol------------------------------

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


    def dispense_wax_to_individual_replicate_set(dispense_well_list):

        """ defines the dispense wax function """

        # Pick up a 300ul tip
        right_pipette.pick_up_tip()

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
        right_pipette.drop_tip()


    # 3. Running protocol------------------------------------------------------

    # Set temperature of temperature module to 4 degrees. The protocol will pause
    # until this is reached.
    temperature_module.set_temperature(4)

    # Extracting the different experiments from the experiments
    # settings file
    experiment_ids = experiment_settings_dict.keys()




    # Running the lysate dispense step if protocol_dispense_lysate = True
    if protocol_dispense_lysate:

        # Outputting the name of the experiment that is being ran
        protocol.comment("Running lysate for experiment " + "exp1")

        # Defining the source wells for the different components in this experiment
        lysate_source_well = pcr_temp_plate[experiment_settings_dict["exp1"]["lysate_source_well"]]

        # Defining a list of wells for dispensing
        dispense_well_list = experiment_settings_dict["exp1"]["dispense_well_list"]

        # Defining the initial lysate aspiration height
        lysate_aspirate_height = pipetting_settings_dict["lysate_aspirate_height_init"]

        # Dispensing lysate into each of the wells in dispense well list
        for well in dispense_well_list:

            # Caliing function to distribute lysate
            distribute_lysate(well, lysate_source_well, lysate_aspirate_height)

            # Reducing the aspiration height by lysate_aspirate_height_inc
            lysate_aspirate_height -= pipetting_settings_dict["lysate_aspirate_height_inc"]

        protocol.comment("Lysate dispense step complete for experiment " + "exp1")

    # Running the substrate dispense step if protocol_dispense_substrates = True
    if protocol_dispense_substrates:

        # Defining the source well for the substrates master mix
        substrates_source_well = pcr_temp_plate[experiment_settings_dict["exp2"]["substrates_source_well"]]

        # Defining a list of wells for dispensing
        dispense_well_list = experiment_settings_dict["exp2"]["dispense_well_list"]

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


        protocol.comment("Substrate dispense step complete for experiment " + "exp2")



    # Running the substrate dispense step if protocol_dispense_substrates = True
    if protocol_dispense_substrates:

        # Defining the source well for the substrates master mix
        substrates_source_well = pcr_temp_plate[experiment_settings_dict["exp1"]["substrates_source_well"]]

        # Defining a list of wells for dispensing
        dispense_well_list = experiment_settings_dict["exp1"]["dispense_well_list"]

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


        protocol.comment("Substrate dispense step complete for experiment " + "exp1")


    # Running the lysate dispense step if protocol_dispense_lysate = True
    if protocol_dispense_lysate:

        # Outputting the name of the experiment that is being ran
        protocol.comment("Running lysate for experiment " + "exp2")

        # Defining the source wells for the different components in this experiment
        lysate_source_well = pcr_temp_plate[experiment_settings_dict["exp2"]["lysate_source_well"]]

        # Defining a list of wells for dispensing
        dispense_well_list = experiment_settings_dict["exp2"]["dispense_well_list"]

        # Defining the initial lysate aspiration height
        lysate_aspirate_height = pipetting_settings_dict["lysate_aspirate_height_init"]

        # Dispensing lysate into each of the wells in dispense well list
        for well in dispense_well_list:

            # Caliing function to distribute lysate
            distribute_lysate(well, lysate_source_well, lysate_aspirate_height)

            # Reducing the aspiration height by lysate_aspirate_height_inc
            lysate_aspirate_height -= pipetting_settings_dict["lysate_aspirate_height_inc"]

        protocol.comment("Lysate dispense step complete for experiment " + "exp2")





    # Pausing protocol so the plate can be span down in the centrifuge before
    # adding the wax ontop
    protocol.pause("Check plate and spin down, before replacing for wax")


    # Running the wax dispense step if protocol_dispense_wax = True
    if protocol_dispense_wax:

        # Looping through the different experiments
        for experiment_id in experiment_ids:

            # Defining a list of wells for dispensing
            dispense_well_list = experiment_settings_dict[experiment_id]["dispense_well_list"]

            # Defining the source well for the wax
            wax_source_well = eppendorf_1500ul_x24_rack.wells_by_name()[experiment_settings_dict[experiment_id]["wax_source_well"]]

            dispense_wax_to_individual_replicate_set(dispense_well_list)

            protocol.comment("Wax dispense step complete for experiment " + experiment_id)

    # Turning off temp module after all experiments have finished
    temperature_module.deactivate()
