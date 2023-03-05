from re import T
from opentrons import protocol_api
import json
import os
import numpy as np

# metadata
metadata = {
    "protocolName": "ALTE Calibration Script",
    "author": "Alex Perkins",
    "email": "a.j.p.perkins@sms.ed.ac.uk",
    "description": "ALTE Calibration Script",
    "apiLevel": "2.8",
}

# Add 35ul of lysate to a PCR tube to A1 in cold block
# Defining the aspiration height for 35ul of lysate  "lysate_aspirate_height_init" : 4.5,

# Add 90ul of substrates mix to B1
# Defining the aspiration height for 90ul of substrates: "substrates_aspirate_height_init" : 8.6,

## Substate calculator on Labstep

# Protocol run function. the part after the colon lets your editor know
# where to look for autocomplete suggestions
def run(protocol: protocol_api.ProtocolContext):


    # Defining the temperature module
    temperature_module = protocol.load_module("temperature module gen2", "10")

    # Defining the pcr plate ontop of the temperature module
    # Defining the 384 nunc well plate
    nunc_384 = temperature_module.load_labware("trevor_6_tuberack_50000ul")

    # Defining the custom_15_50_tube_rack.
    # Because this is a custom labware definition, it needs to be loaded in manually to be used with opentrons_execute

    def load_custom_labware(file_path,location):
        with open(file_path) as labware_file:
            labware_def = json.load(labware_file)
        return protocol.load_labware_from_definition(labware_def, location)

    custom_labware_on_ot2_path = "maintenance/custom_labware/trevor_6_tuberack_50000ul.json"

    custom_15_50_tube_rack = load_custom_labware(custom_labware_on_ot2_path, "11")




    # Defining left_pipette (p20)
    #left_pipette = protocol.load_instrument(
    #    "p20_single_gen2", "left", tip_racks=[tiprack_20ul_1,tiprack_20ul_2, tiprack_20ul_3, tiprack_20ul_4, tiprack_20ul_5]
    #)

    # Defining the 300ul tip rack
    tiprack_300ul_1 = protocol.load_labware("opentrons_96_tiprack_300ul", "7")
    tiprack_300ul_2 = protocol.load_labware("opentrons_96_tiprack_300ul", "8")
    tiprack_300ul_3 = protocol.load_labware("opentrons_96_tiprack_300ul", "9")

    # Defining right_pipette (p300)
    right_pipette = protocol.load_instrument(
        "p300_single_gen2", "right", tip_racks=[tiprack_300ul_1, tiprack_300ul_2, tiprack_300ul_3]
    )

    # 2. Arbitary place holder instructions ------------------------------

    def distribute_calibration(source_well, destination_well, volume, pipette):

        if pipette == "left":

            if volume == 0:
                pass

            else:
                left_pipette.aspirate(volume, source_well)
                left_pipette.dispense(volume, destination_well)


        elif pipette == "right":

            if volume == 0:
                pass

            else:
                right_pipette.aspirate(volume, source_well)
                right_pipette.dispense(volume, destination_well)

        else:
            protocol.comment("Pipette not specified..")

    cali_array_96x = np.array([

                        [20, 20, 20, 20, 20, 20, 20, 20],
                        [20, 20, 20, 20, 20, 20, 20, 20],
                        [20, 20, 20, 20, 20, 20, 20, 20],
                        [20, 20, 20, 20, 20, 20, 20, 20],
                        [20, 20, 20, 20, 20, 20, 20, 20],
                        [20, 20, 20, 20, 20, 20, 20, 20],
                        [20, 20, 20, 20, 20, 20, 20, 20],
                        [20, 20, 20, 20, 20, 20, 20, 20],
                        [20, 20, 20, 20, 20, 20, 20, 20],
                        [20, 20, 20, 20, 20, 20, 20, 20],
                        [20, 20, 20, 20, 20, 20, 20, 20],
                        [20, 20, 20, 20, 20, 20, 20, 20]
                        ]).reshape(-1)

    
    # nunc plate
    left_pipette.pick_up_tip()

    source_well = custom_15_50_tube_rack["A1"]

    for destination_well, volume in zip(nunc_384.wells(), cali_array_96x):

        distribute_calibration(source_well, destination_well, volume, pipette = "left")

    left_pipette.drop_tip()


    cali_array_384x = np.array([
                        [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20],
                        [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20],
                        [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20],
                        [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20],
                        [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20],
                        [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20],
                        [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20],
                        [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20],
                        [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20],
                        [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20],
                        [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20],
                        [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20],
                        
                        [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20],
                        [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20],
                        [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20],
                        [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20],
                        [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20],
                        [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20],
                        [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20],
                        [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20],
                        [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20],
                        [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20],
                        [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20],
                        [20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20]
                        ]).reshape(-1)

