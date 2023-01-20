from re import T
from opentrons import protocol_api
import json
import os
import math
import pandas as pd

# metadata
metadata = {
    "protocolName": "Lysate CFPS Plating Script v1",
    "author": "Alex Perkins",
    "email": "a.j.p.perkins@sms.ed.ac.uk",
    "description": "OT2 Script to compile variable mastermixes followed by the plating of CFPS reactions.",
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

    # 0. Reading in json setting files-----------------------------------------

    experiment_prefix = "ALTE009"
    plate_number = 1
    plate_number_string = str(plate_number)


    # Defining the file paths of raspberry pi

    # import the experimental design
    experimental_design_path = "processed_data_files/Experiment_Designs/design_final.csv"
    experimental_design_df = pd.read_csv(experimental_design_path)

    # select only the experiments for the relevant plate
    experimental_design_df = experimental_design_df[experimental_design_df["Plate"] == plate_number]


    #
    #plating_labware_settings_dict_path = "/data/user_storage/"+ experiment_prefix + "/" + experiment_prefix + "_plating_labware_settings.json"
    plating_labware_settings_dict_path = "ot2_labware_settings/" + experiment_prefix + "_plating_labware_settings.json"

    pipetting_settings_dict_path = "base_settings/base_pipetting_settings.json"

    pre_experiment_compilation_dict_path = "processed_ot2_settings/" + experiment_prefix + "_pre_experiment_compilations.json"

    # Reading in MasterMixCalculationsDict
    MasterMixCalculationsPath = "processed_ot2_settings/mastermix_calculations.json"
    MasterMixCalculationsDict = json.load(open(MasterMixCalculationsPath, 'r'))
    
    # Select only the calculations for the specified plate.
    MasterMixCalculationsDict = MasterMixCalculationsDict[plate_number_string]
    protocol.comment("MasterMixCalculations json file was read in")


    plating_labware_settings_dict = json.load(open(plating_labware_settings_dict_path, 'r'))
    protocol.comment("Plating labware settings json file was read in")

    pipetting_settings_dict = json.load(open(pipetting_settings_dict_path, 'r'))
    protocol.comment("Pipetting settings json file was read in")

    pre_experiment_compilation_dict = json.load(open(pre_experiment_compilation_dict_path, 'r'))
    protocol.comment("Pre experiment compilations json file was read in")

    pre_experiment_compilation_dict = pre_experiment_compilation_dict[plate_number_string]
    protocol.comment("Pre experiment compilations Plate: "+plate_number_string +" Selected.")

    # 1. Defining variables used in protocol-----------------------------------

    # Defining the booleans for the protocol. This controls which parts of
    # the protocol to run.

    temp_toggle = True

    MasterMix_Toggle = True
    Aqueous_MasterMix_Toggle = True
    Components_MasterMix_Toggle = True
    MasterMix_Mix_Toggle = True

    Plating_Toggle = True
    Aqueous_Plating_Toggle = True
    Components_Plating_Toggle = True

    # labware

    # Defining the temperature module
    temperature_module = protocol.load_module(plating_labware_settings_dict["temp_module"]["name"], plating_labware_settings_dict["temp_module"]["pos"])


    # Defining the pcr plate ontop of the temperature module
    pcr_source_tubes = temperature_module.load_labware(
        plating_labware_settings_dict["pcr_source_tubes"]["name"],
        label="Temperature-Controlled Tubes",
    )
    pcr_source_tubes.set_offset(x = plating_labware_settings_dict["pcr_source_tubes"]["offsets"]["x"],
                                y = plating_labware_settings_dict["pcr_source_tubes"]["offsets"]["y"],
                                z = plating_labware_settings_dict["pcr_source_tubes"]["offsets"]["z"]
                                )

    # Defining the 384 nunc well plate
    nunc_384 = protocol.load_labware(plating_labware_settings_dict["nunc_384"]["name"], plating_labware_settings_dict["nunc_384"]["pos"])
    nunc_384.set_offset(x = plating_labware_settings_dict["nunc_384"]["offsets"]["x"],
                        y = plating_labware_settings_dict["nunc_384"]["offsets"]["y"],
                        z = plating_labware_settings_dict["nunc_384"]["offsets"]["z"]
                        )

    # Defining the eppendorf_2ml_x24_icebox_rack.
    # Because this is a custom labware definition, it needs to be loaded in manually to be used with opentrons_execute

    def load_custom_labware(file_path,location):
        with open(file_path) as labware_file:
            labware_def = json.load(labware_file)
        return protocol.load_labware_from_definition(labware_def, location)

    custom_labware_on_ot2_path = "maintenance/custom_labware/nllab3dprinted_24_tuberack_2000ul.json"
    eppendorf_2ml_x24_icebox_rack = load_custom_labware(custom_labware_on_ot2_path, plating_labware_settings_dict["eppendorf_2ml_x24_icebox_rack"]["pos"])
    eppendorf_2ml_x24_icebox_rack.set_offset(x = plating_labware_settings_dict["eppendorf_2ml_x24_icebox_rack"]["offsets"]["x"],
                                             y = plating_labware_settings_dict["eppendorf_2ml_x24_icebox_rack"]["offsets"]["y"],
                                             z = plating_labware_settings_dict["eppendorf_2ml_x24_icebox_rack"]["offsets"]["z"]
                                             )

    # Defining the 20ul tip rack
    tiprack_20ul_1 = protocol.load_labware(plating_labware_settings_dict["tiprack_20ul_1"]["name"], plating_labware_settings_dict["tiprack_20ul_1"]["pos"])
    tiprack_20ul_1.set_offset(x = plating_labware_settings_dict["tiprack_20ul_1"]["offsets"]["x"],
                              y = plating_labware_settings_dict["tiprack_20ul_1"]["offsets"]["y"],
                              z = plating_labware_settings_dict["tiprack_20ul_1"]["offsets"]["z"]
                              )

    tiprack_20ul_2 = protocol.load_labware(plating_labware_settings_dict["tiprack_20ul_2"]["name"], plating_labware_settings_dict["tiprack_20ul_2"]["pos"])
    tiprack_20ul_2.set_offset(x = plating_labware_settings_dict["tiprack_20ul_2"]["offsets"]["x"],
                              y = plating_labware_settings_dict["tiprack_20ul_2"]["offsets"]["y"],
                              z = plating_labware_settings_dict["tiprack_20ul_2"]["offsets"]["z"]
                              )

    tiprack_20ul_3 = protocol.load_labware(plating_labware_settings_dict["tiprack_20ul_3"]["name"], plating_labware_settings_dict["tiprack_20ul_3"]["pos"])
    tiprack_20ul_3.set_offset(x = plating_labware_settings_dict["tiprack_20ul_3"]["offsets"]["x"],
                              y = plating_labware_settings_dict["tiprack_20ul_3"]["offsets"]["y"],
                              z = plating_labware_settings_dict["tiprack_20ul_3"]["offsets"]["z"]
                              )

    tiprack_20ul_4 = protocol.load_labware(plating_labware_settings_dict["tiprack_20ul_4"]["name"], plating_labware_settings_dict["tiprack_20ul_4"]["pos"])
    tiprack_20ul_4.set_offset(x = plating_labware_settings_dict["tiprack_20ul_4"]["offsets"]["x"],
                              y = plating_labware_settings_dict["tiprack_20ul_4"]["offsets"]["y"],
                              z = plating_labware_settings_dict["tiprack_20ul_4"]["offsets"]["z"]
                              )

    tiprack_20ul_5 = protocol.load_labware(plating_labware_settings_dict["tiprack_20ul_5"]["name"], plating_labware_settings_dict["tiprack_20ul_5"]["pos"])
    tiprack_20ul_5.set_offset(x = plating_labware_settings_dict["tiprack_20ul_5"]["offsets"]["x"],
                              y = plating_labware_settings_dict["tiprack_20ul_5"]["offsets"]["y"],
                              z = plating_labware_settings_dict["tiprack_20ul_5"]["offsets"]["z"]
                              )

    # count the amount of tips
    p20_tip_racks = [tiprack_20ul_1,tiprack_20ul_2, tiprack_20ul_3, tiprack_20ul_4, tiprack_20ul_5]
    p20_tip_count_init = len(p20_tip_racks * 96)

    # Defining left_pipette (p20)
    left_pipette = protocol.load_instrument(
        plating_labware_settings_dict["left_pipette"]["name"], "left", tip_racks = p20_tip_racks
    )

    # Defining the 300ul tip rack
    tiprack_300ul_1 = protocol.load_labware(plating_labware_settings_dict["tiprack_300ul_1"]["name"], plating_labware_settings_dict["tiprack_300ul_1"]["pos"])
    tiprack_300ul_1.set_offset(x = plating_labware_settings_dict["tiprack_300ul_1"]["offsets"]["x"],
                              y = plating_labware_settings_dict["tiprack_300ul_1"]["offsets"]["y"],
                              z = plating_labware_settings_dict["tiprack_300ul_1"]["offsets"]["z"]
                              )


    # count the amount of tips
    p300_tip_racks = [tiprack_300ul_1]
    p300_tip_count_init = len(p300_tip_racks * 96)

    # Defining right_pipette (p300)
    right_pipette = protocol.load_instrument(
        plating_labware_settings_dict["right_pipette"]["name"], "right", tip_racks = p300_tip_racks
    )


    #### tip counter dicts

    tip_counter_init_dict = { "p20": p20_tip_count_init,
        "p300": p300_tip_count_init
    }

    tip_counter_dict = {
        "p20": tip_counter_init_dict["p20"],
        "p300": tip_counter_init_dict["p300"]
    }


    # 2. Defining functions used in this protocol------------------------------



    def PlateMasterMix(PlateWell, MasterMixWell, SolutionType, pipetting_settings_dict = pipetting_settings_dict, tip_counter_dict = tip_counter_dict):
        #### Set up.

        # get the volume to be pipetted

        VolumeUL = pipetting_settings_dict["Plating"][SolutionType]["volume"]

        # the aspirate volume is 0.5ul greater than the intended volume for reverse pipetting
        aspirate_volume = VolumeUL + 0.5

        # Select pipette based on aspirate_volume
        
        pipette = left_pipette
        pipette_type = "p20"
        
        # Check if tips need replacing
        if tip_counter_dict[pipette_type] == 0:

            # pause robot
            protocol.pause('Replace all empty tipracks before resuming.')

            # tell the robot that the tips have been refreshed for that pipette
            pipette.reset_tipracks()

            # reset only the selected pipette in the counter
            tip_counter_dict[pipette_type] = tip_counter_init_dict[pipette_type]

        else:
            pass
        

        #### Actions

        pipette.pick_up_tip()

        pipette.well_bottom_clearance.aspirate = 4
        pipette.well_bottom_clearance.dispense = pipetting_settings_dict["Plating"][SolutionType]["well_bottom_clearance"]

        # aspirate step
        pipette.aspirate(aspirate_volume, pcr_source_tubes[MasterMixWell], rate = pipetting_settings_dict["Plating"][SolutionType]["aspirate_rate"])
        pipette.move_to(pcr_source_tubes[MasterMixWell].top(-2))
        pipette.touch_tip()

        # Dispense Step
        pipette.dispense(VolumeUL, nunc_384[PlateWell], rate = pipetting_settings_dict["Plating"][SolutionType]["dispense_rate"])

        pipette.drop_tip()

        # decrement tip counter
        tip_counter_dict[pipette_type] -= 1

        return tip_counter_dict


    
    def CompileMasterMixComponent(MasterMixWell, StockWell, VolumeUL, SolutionType, pipetting_settings_dict = pipetting_settings_dict, tip_counter_dict = tip_counter_dict):

        #### Set up.

        # the aspirate volume is 10% greater than the intended volume for reverse pipetting
        aspirate_volume = VolumeUL * 1.1

        # Select pipette based on aspirate_volume
        if aspirate_volume > 20:

            pipette = right_pipette
            pipette_type = "p300"

        else:
            pipette = left_pipette
            pipette_type = "p20"
        
        # Check if tips need replacing
        if tip_counter_dict[pipette_type] == 0:

            # pause robot
            protocol.pause('Replace all empty tipracks before resuming.')

            # tell the robot that the tips have been refreshed for that pipette
            pipette.reset_tipracks()

            # reset only the selected pipette in the counter
            tip_counter_dict[pipette_type] = tip_counter_init_dict[pipette_type]

        else:
            pass


        #### Actions

        pipette.pick_up_tip()

        pipette.well_bottom_clearance.aspirate = pipetting_settings_dict["MasterMix"][SolutionType]["Stock_Tube_bottom_clearance"]
        pipette.well_bottom_clearance.dispense = pipetting_settings_dict["MasterMix"][SolutionType]["MasterMix_Tube_bottom_clearance"]

        # aspirate step
        pipette.aspirate(aspirate_volume, eppendorf_2ml_x24_icebox_rack[StockWell], rate = pipetting_settings_dict["MasterMix"][SolutionType]["aspirate_rate"])
        pipette.move_to(eppendorf_2ml_x24_icebox_rack[StockWell].top(-2))
        protocol.delay(seconds = 
            float(pipetting_settings_dict["MasterMix"][SolutionType]["pause_time"])
            )
        pipette.touch_tip()

        # Dispense Step
        pipette.dispense(VolumeUL, pcr_source_tubes[MasterMixWell], rate = pipetting_settings_dict["MasterMix"][SolutionType]["dispense_rate"])

        pipette.drop_tip()

        # decrement tip counter
        tip_counter_dict[pipette_type] -= 1

        return tip_counter_dict

    
    def Mix_MasterMix_Tube(MasterMixTube, SolutionType, pipetting_settings_dict = pipetting_settings_dict, tip_counter_dict = tip_counter_dict):
        
        # define pipette
        pipette = right_pipette
        pipette_type = "p300"

        # Check if tips need replacing
        if tip_counter_dict[pipette_type] == 0:

            # pause robot
            protocol.pause('Replace all empty tipracks before resuming.')

            # tell the robot that the tips have been refreshed for that pipette
            pipette.reset_tipracks()

            # reset only the selected pipette in the counter
            tip_counter_dict[pipette_type] = tip_counter_init_dict[pipette_type]

        else:
            pass

        pipette.pick_up_tip()

        # aspirate step

        # Mix Step
        pipette.mix(
            pipetting_settings_dict["MasterMix"][SolutionType]["mix_repetitions"],
            pipetting_settings_dict["MasterMix"][SolutionType]["mix_volume"],
            pcr_source_tubes[MasterMixTube].bottom(5),
        )

        # wait for liquid on outside of tip to pool and then touch tip.

        pipette.move_to(pcr_source_tubes[MasterMixTube].top(-2))
        protocol.delay(seconds = 
            pipetting_settings_dict["MasterMix"][SolutionType]["post_mix_pause"]
            )
        pipette.touch_tip()




        pipette.drop_tip()


        # decrement tip counter
        tip_counter_dict[pipette_type] -= 1

        return tip_counter_dict


        


    # 3. Running protocol------------------------------------------------------




    # Set temperature of temperature module to 4 degrees. The protocol will pause
    # until this is reached.
    if temp_toggle:
        temperature_module.set_temperature(4)



    # 3. Master Mix Compilations-------------------------------------------------------------------

    # master switch for setup
    if MasterMix_Toggle:

        # select Solution Type
        for SolutionType in MasterMixCalculationsDict.keys():
            
            # toggles for ease of development
            if SolutionType == "Aqueous" and not Aqueous_MasterMix_Toggle:
                pass

            elif SolutionType == "Components" and not Components_MasterMix_Toggle:
                pass

            else:

                # Select Master Mix Well to be populated
                for MasterMixWell in MasterMixCalculationsDict[SolutionType]:

                    # Select the reaction element
                    for Element in MasterMixCalculationsDict[SolutionType][MasterMixWell]:

                        # Extract the Element Stock Well
                        Stock_source_well = MasterMixCalculationsDict[SolutionType][MasterMixWell][Element]["Stock_source_well"]
                        
                        # Extract the Volume to be added
                        Element_stock_volume_ul = MasterMixCalculationsDict[SolutionType][MasterMixWell][Element]["Element_stock_volume_ul"]

                        tip_counter_dict = CompileMasterMixComponent(
                            MasterMixWell,
                            StockWell = Stock_source_well,
                            VolumeUL = Element_stock_volume_ul,
                            SolutionType = SolutionType,
                            pipetting_settings_dict = pipetting_settings_dict
                            )

    # Mix step
    if MasterMix_Mix_Toggle:

        # select Solution Type
        for SolutionType in MasterMixCalculationsDict.keys():

            # Select Master Mix Well to be populated
            for MasterMixWell in MasterMixCalculationsDict[SolutionType]:

                tip_counter_dict = Mix_MasterMix_Tube(
                                    MasterMixTube = MasterMixWell,
                                    SolutionType = SolutionType,
                                    pipetting_settings_dict = pipetting_settings_dict,
                                    tip_counter_dict = tip_counter_dict
                                    )




    # 4. Conduct plating -------------------------------------------------------------------

    ### Constructing the MasterMix Tube Aspirate Height Dict to keep track of the decreasing heights
    # use the Stock tubes from the MasterMixCalculationsDict as keys and initalise all with the appropriate aspirate_height_init

    MasterMixTube_Aspiration_Heights_Dict = {}
    
    for SolutionType in pipetting_settings_dict["MasterMix"].keys():
        
        SolutionType_Dict = {}
        for Tube in MasterMixCalculationsDict[SolutionType].keys():
            SolutionType_Dict[Tube] = pipetting_settings_dict["Plating"][SolutionType]["aspirate_height_init"]
        
        MasterMixTube_Aspiration_Heights_Dict[SolutionType] = SolutionType_Dict
        
    # Running the substrate dispense step if protocol_dispense_substrates = True
    if Plating_Toggle:

        # select Solution Type
        for SolutionType in MasterMixCalculationsDict.keys():
            
            # toggles for ease of development
            if SolutionType == "Aqueous" and not Aqueous_Plating_Toggle:
                pass

            elif SolutionType == "Components" and not Components_Plating_Toggle:
                pass

            else:

                # select correct mastermix tube in the df column
                if SolutionType == "Aqueous":

                    MasterMixTube_String = "AqueousMasterMixTube"
                    
                    protocol.comment("Starting Aqueous Plating..")

                elif SolutionType == "Components":

                    MasterMixTube_String = "ComponentsMasterMixTube"

                    protocol.comment("Starting Components Plating..")
                
                for i, row in experimental_design_df.iterrows():

                    tip_counter_dict = PlateMasterMix(
                                            PlateWell = row.loc["Well"],
                                            MasterMixWell = row.loc[MasterMixTube_String],
                                            SolutionType = SolutionType,
                                            pipetting_settings_dict = pipetting_settings_dict,
                                            tip_counter_dict = tip_counter_dict
                                            )

                    # decrement the aspiration height for that MasterMixWell
                    MasterMixTube_Aspiration_Heights_Dict[SolutionType][row.loc[MasterMixTube_String]] = MasterMixTube_Aspiration_Heights_Dict[SolutionType][row.loc[MasterMixTube_String]] - pipetting_settings_dict["Plating"][SolutionType]["aspirate_height_inc"]
                    protocol.comment(" ")
                    protocol.comment("Completed " + SolutionType + " dispense steps: " + str(i+1)+"/"+str(experimental_design_df.shape[0]))



    # Pausing protocol so the plate can be span down in the centrifuge before

    # Turning off temp module after all experiments have finished
    if temp_toggle:
        temperature_module.deactivate()

    protocol.comment("end of plating")


    # adding the wax ontop
    protocol.pause("Check plate and spin down. Then setup OT2 for wax dispense and run #### script.")

