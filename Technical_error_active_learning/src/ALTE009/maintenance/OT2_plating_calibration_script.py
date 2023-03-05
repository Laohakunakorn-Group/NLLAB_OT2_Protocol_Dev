from re import T
from opentrons import protocol_api
import json
import os
import numpy as np

# metadata
metadata = {
    "protocolName": "CFPS Plating Calibration Script",
    "author": "Alex Perkins",
    "email": "a.j.p.perkins@sms.ed.ac.uk",
    "description": "CFPS Plating Calibration Script",
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
    pcr_source_tubes = temperature_module.load_labware(
        "opentrons_96_aluminumblock_generic_pcr_strip_200ul",
        label="Temperature-Controlled Tubes",
    )
    # Defining the 384 nunc well plate
    nunc_384 = protocol.load_labware("corning_384_wellplate_112ul_flat", "7")

    # Defining the 1.5ul eppendorf rack
    eppendorf_2ml_x24_icebox_rack = protocol.load_labware(
        "nllab3dprinted_24_tuberack_2000ul",
         "11")

    # Defining the 20ul tip rack
    tiprack_20ul_1 = protocol.load_labware("opentrons_96_tiprack_20ul", "8")
    tiprack_20ul_2 = protocol.load_labware("opentrons_96_tiprack_20ul", "9")
    tiprack_20ul_3 = protocol.load_labware("opentrons_96_tiprack_20ul", "6")
    tiprack_20ul_4 = protocol.load_labware("opentrons_96_tiprack_20ul", "5")
    tiprack_20ul_5 = protocol.load_labware("opentrons_96_tiprack_20ul", "4")


    # Defining left_pipette (p20)
    left_pipette = protocol.load_instrument(
        "p20_single_gen2", "left", tip_racks=[tiprack_20ul_1,tiprack_20ul_2, tiprack_20ul_3, tiprack_20ul_4, tiprack_20ul_5]
    )

    # Defining the 300ul tip rack
    tiprack_300ul_1 = protocol.load_labware("opentrons_96_tiprack_300ul", "1")
    tiprack_300ul_2 = protocol.load_labware("opentrons_96_tiprack_300ul", "2")
    tiprack_300ul_3 = protocol.load_labware("opentrons_96_tiprack_300ul", "3")

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

    source_well = eppendorf_2ml_x24_icebox_rack["A1"]

    for destination_well, volume in zip(pcr_source_tubes.wells(), cali_array_96x):

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

    # pcr tubes
    right_pipette.pick_up_tip()

    source_well = eppendorf_2ml_x24_icebox_rack["A1"]

    for destination_well, volume in zip(nunc_384.wells(), cali_array_384x):

        distribute_calibration(source_well, destination_well, volume, pipette = "right")

    right_pipette.drop_tip()

    # pcr tubes
    right_pipette.pick_up_tip()

    source_well = eppendorf_2ml_x24_icebox_rack["A1"]

    for destination_well, volume in zip(nunc_384.wells(), cali_array_384x):

        distribute_calibration(source_well, destination_well, volume, pipette = "right")

    right_pipette.drop_tip()