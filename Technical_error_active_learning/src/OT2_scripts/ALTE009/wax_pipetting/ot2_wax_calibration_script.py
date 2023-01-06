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
    "description": "OT2 CFPS Plating Wax Step Calibation Script",
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
    nunc_384 = temperature_module.load_labware("corning_384_wellplate_112ul_flat")


    # Defining the custom_15_50_tube_rack
    # 3d printed by uses offical api def: opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical
    custom_15_50_tube_rack = protocol.load_labware("opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical", "11")



    # Defining the 300ul tip rack
    tiprack_300ul_1 = protocol.load_labware("opentrons_96_tiprack_300ul", "8")


    # Defining right_pipette (p300)
    right_pipette = protocol.load_instrument(
        "p300_single_gen2", "right", tip_racks=[tiprack_300ul_1]
    )

    pipette = "right"

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
    if pipette == "right":
        right_pipette.pick_up_tip()
    elif pipette == "left":
        left_pipette.pick_up_tip()

    source_well = custom_15_50_tube_rack["A1"]

    for destination_well, volume in zip(nunc_384.wells(), cali_array_96x):

        distribute_calibration(source_well, destination_well, volume, pipette = pipette)

    if pipette == "right":
        right_pipette.drop_tip()
    elif pipette == "left":
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

