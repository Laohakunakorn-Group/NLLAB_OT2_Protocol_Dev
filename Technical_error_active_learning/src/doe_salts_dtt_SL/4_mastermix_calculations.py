from auxillary_scripts.mastermix_calculation_functions import *
import json
import pandas as pd


################################

# Intro

# Performs the dilution calculations for the master mixes.
# Calculates 

################################

# initialise the all plates dict
all_plates_dict = {}

# initialise the Total_vol_df
Total_col_df = pd.DataFrame()

# retrieve the number of plates in the experiment
design_final_df = pd.read_csv("output/Experiment_Designs/design_final.csv")
quantity_of_plates = design_final_df["Plate"].max()

# read in the jsons and dataframes
es_path = "settings/base_energy_solution.json"
es_dict = json.load(open(es_path, 'r'))

base_rxn_path = "settings/base_rxn.json"
base_rxn_dict = json.load(open(base_rxn_path, 'r'))

# import experiment_variables
with open('settings/experiment_variables.json') as json_file:
    experiment_variables = json.load(json_file)
experiment_variables = pd.DataFrame(experiment_variables)


### Determine if Aqueous and or Components are modulated.

if ('Aqueous' in experiment_variables["Type"].values) and ('Components' in experiment_variables["Type"].values):
    MasterMixesModulated = "Both"

elif 'Aqueous' in experiment_variables["Type"].values:
    MasterMixesModulated = "Aqueous"

elif 'Components' in experiment_variables["Type"].values:
    MasterMixesModulated = "Components"

else:
    raise Exception("Please check the Type of Reaction Elements to be modulated in experiemnt_variables.json")




# iterate over the plate number and perform the allocations
for plate_number in range(1, (quantity_of_plates+1), 1):


    print("Starting allocations for plate #: "+str(plate_number))


    ## extract  variables depening on modulation status.
    if MasterMixesModulated == "Both":

        # Aqueous
        Aqueous_master_mix_dataframe_path = "tmp/MasterMixes/" + str(plate_number)+ "_plate_Aqueous_MasterMix_Stocks.pkl"
        Aqueous_master_mix_dataframe = pd.read_pickle(Aqueous_master_mix_dataframe_path)

        # extract the Aqueous variables
        Aqueous_variables = list(Aqueous_master_mix_dataframe.columns)
        Aqueous_variables.remove("Tubes"); Aqueous_variables.remove("Experiments")

        # Components
        Components_master_mix_dataframe_path = "tmp/MasterMixes/" + str(plate_number)+ "_plate_Components_MasterMix_Stocks.pkl"
        Components_master_mix_dataframe = pd.read_pickle(Components_master_mix_dataframe_path)


        # extract the Components variables
        Components_variables = list(Components_master_mix_dataframe.columns)
        Components_variables.remove("Tubes"); Components_variables.remove("Experiments")

    elif MasterMixesModulated == "Aqueous":

        # Aqueous
        Aqueous_master_mix_dataframe_path = "tmp/MasterMixes/" + str(plate_number)+ "_plate_Aqueous_MasterMix_Stocks.pkl"
        Aqueous_master_mix_dataframe = pd.read_pickle(Aqueous_master_mix_dataframe_path)

        # extract the Aqueous variables
        Aqueous_variables = list(Aqueous_master_mix_dataframe.columns)
        Aqueous_variables.remove("Tubes"); Aqueous_variables.remove("Experiments")

        # Components
        Components_master_mix_dataframe_path = "tmp/MasterMixes/" + str(plate_number)+ "_plate_Components_MasterMix_Stocks.pkl"
        Components_master_mix_dataframe = pd.read_pickle(Components_master_mix_dataframe_path)


        # Components
        Components_master_mix_dataframe_path = "tmp/MasterMixes/" + str(plate_number)+ "_plate_Components_MasterMix_Stocks.pkl"
        Components_master_mix_dataframe = pd.read_pickle(Components_master_mix_dataframe_path)

        # extract the Components variables
        Components_variables = list(Components_master_mix_dataframe.columns)
        Components_variables.remove("Tubes"); Components_variables.remove("Experiments")



    elif MasterMixesModulated == "Components":

        # Components
        Components_master_mix_dataframe_path = "tmp/MasterMixes/" + str(plate_number)+ "_plate_Components_MasterMix_Stocks.pkl"
        Components_master_mix_dataframe = pd.read_pickle(Components_master_mix_dataframe_path)

        # extract the Components variables
        Components_variables = list(Components_master_mix_dataframe.columns)
        Components_variables.remove("Tubes"); Components_variables.remove("Experiments")

        # Aqueous
        Aqueous_master_mix_dataframe_path = "tmp/MasterMixes/" + str(plate_number)+ "_plate_Aqueous_MasterMix_Stocks.pkl"
        Aqueous_master_mix_dataframe = pd.read_pickle(Aqueous_master_mix_dataframe_path)

        # Aqueous
        Aqueous_master_mix_dataframe_path = "tmp/MasterMixes/" + str(plate_number)+ "_plate_Aqueous_MasterMix_Stocks.pkl"
        Aqueous_master_mix_dataframe = pd.read_pickle(Aqueous_master_mix_dataframe_path)

        # extract the Aqueous variables
        Aqueous_variables = list(Aqueous_master_mix_dataframe.columns)
        Aqueous_variables.remove("Tubes"); Aqueous_variables.remove("Experiments")

    else:
        raise Exception("MasterMixesModulated is neither Aqueous, Components or Both: MasterMixesModulated = " + MasterMixesModulated)

    
    # clarity readout
    print()
    if MasterMixesModulated == "Both":
        print("Both Master Mixes are Modulated.")
    elif MasterMixesModulated == "Aqueous":
        print("Only the Aqueous Master Mixes are Modulated.")
    elif MasterMixesModulated == "Components":
        print("Only the Components Master Mixes are Modulated.")
    print()

    

    ############################

    # First do the Aqueous Elements

    aq_tubes = []
    for idx, item in Aqueous_master_mix_dataframe['Tubes'].items():
        aq_tubes = aq_tubes + item

    list_of_required_Aqueous_mastermix_tubes = aq_tubes
    number_of_required_Aqueous_mastermix_tubes = len(aq_tubes)




    #### Standard Components that go into every reaction

    Aqueous_MasterMix_Tubes_dict = {}

    for MasterMix_Tube in list_of_required_Aqueous_mastermix_tubes:

        # Also add the "residual_volume" to the top level of the tube dict
        # this makes the "make_up to the mark volume" easier to calculate and keep track of.
        Aqueous_MasterMix_Tubes_dict[MasterMix_Tube] = {}
        Aqueous_MasterMix_Tubes_dict[MasterMix_Tube]["residual_volume"] = base_rxn_dict["Metainfo"]["Master_Mixes"]["total_tube_volumes_ul"]["Aqueous"]


        Elements_dict = {}

        for element in base_rxn_dict["rxn_Aqueous_elements"].keys():

            # check if it is to be added to the master mix or not by cross referencing with the variable list.
            if base_rxn_dict["rxn_Aqueous_elements"][element]["Type"] == "Variable":
                #print(element + " is in the variables modulated, therefore skipping it's addition to the mastermix..")
                pass

            else:
                # if it's a template then execute this cell
                if base_rxn_dict["rxn_Aqueous_elements"][element]["Type"] == "Template":

                    Template_Aqueous_Master_Mix_conc_nM = required_concentration_in_Master_Mix(volume_of_MasterMix_to_rxn =base_rxn_dict["Metainfo"]["Master_Mixes"]["Volumes_added_to_rxn"]["Aqueous"],
                                                                                    rxn_concentration= base_rxn_dict["rxn_Aqueous_elements"][element]["rxn_conc_nM"],
                                                                                    total_rxn_volume = base_rxn_dict["Metainfo"]["total_reaction_volume_ul"])


                    Element_MasterMix_Volume_ul = DNA_ul_to_add_to_Aqueous_MasterMix_from_ng_per_ul_stock(stock_conc_ng_per_ul = base_rxn_dict["rxn_Aqueous_elements"][element]["stock_conc_ng_per_ul"],
                                                                                    len_base_pairs = base_rxn_dict["rxn_Aqueous_elements"][element]["len_base_pairs"],
                                                                                    avg_daltons_per_bp = base_rxn_dict["rxn_Aqueous_elements"][element]["avg_daltons_per_bp"],
                                                                                    Aqueous_Master_Mix_conc_nM = Template_Aqueous_Master_Mix_conc_nM,
                                                                                    Aqueous_Master_mix_volume_ul =  base_rxn_dict["Metainfo"]["Master_Mixes"]["total_tube_volumes_ul"]["Aqueous"])
                    
                    Element_Pipetting_Instructions_dict =   {
                                                                "Stock_source_well": base_rxn_dict["rxn_Aqueous_elements"][element]["Stock_source_well"],
                                                                "Element_stock_volume_ul": Element_MasterMix_Volume_ul
                                                            }
                    
                    # add pipetting dict
                    Aqueous_MasterMix_Tubes_dict[MasterMix_Tube][element] = Element_Pipetting_Instructions_dict

                    # Also update the "residual_volume" 
                    Aqueous_MasterMix_Tubes_dict[MasterMix_Tube]["residual_volume"] = Aqueous_MasterMix_Tubes_dict[MasterMix_Tube]["residual_volume"] - Element_MasterMix_Volume_ul


                # if its a normal element...
                elif base_rxn_dict["rxn_Aqueous_elements"][element]["Type"] == "Standard":

                    Element_Aqueous_Master_Mix_conc_uM = required_concentration_in_Master_Mix(volume_of_MasterMix_to_rxn =base_rxn_dict["Metainfo"]["Master_Mixes"]["Volumes_added_to_rxn"]["Aqueous"],
                                                                            rxn_concentration=base_rxn_dict["rxn_Aqueous_elements"][element]["rxn_conc_uM"],
                                                                            total_rxn_volume = base_rxn_dict["Metainfo"]["total_reaction_volume_ul"])

                    Element_MasterMix_Volume_ul = dilution_calculator(stock_concentration = base_rxn_dict["rxn_Aqueous_elements"][element]["stock_conc_uM"],
                                                    final_concentration = Element_Aqueous_Master_Mix_conc_uM, 
                                                    final_total_volume = base_rxn_dict["Metainfo"]["Master_Mixes"]["total_tube_volumes_ul"]["Aqueous"])


                    Element_Pipetting_Instructions_dict =   {
                                                                "Stock_source_well": base_rxn_dict["rxn_Aqueous_elements"][element]["Stock_source_well"],
                                                                "Element_stock_volume_ul": Element_MasterMix_Volume_ul
                                                            }
                    
                    # add pipetting dict
                    Aqueous_MasterMix_Tubes_dict[MasterMix_Tube][element] = Element_Pipetting_Instructions_dict

                    # Also update the "residual_volume" 
                    Aqueous_MasterMix_Tubes_dict[MasterMix_Tube]["residual_volume"] = Aqueous_MasterMix_Tubes_dict[MasterMix_Tube]["residual_volume"] - Element_MasterMix_Volume_ul
                    


                elif base_rxn_dict["rxn_Aqueous_elements"][element]["Type"] == "Buffer":

                    Element_Pipetting_Instructions_dict = "Placeholder"

                    # add pipetting dict
                    Aqueous_MasterMix_Tubes_dict[MasterMix_Tube][element] = "Placeholder"

                else:
                    raise Exception("Unknown rxn element type: Check base_rxn.json for "+ element)
            



    ##########

        
    # do the variable factors

    # Calculate Volume Avalible for variable factors
    volume_avalible_per_factor = CalculateResidualVolumeAllocatedForVariableFactors(Aqueous_MasterMix_Tubes_dict, Aqueous_variables)

    print("Volume Avalible per Aqueous factor: " + str(volume_avalible_per_factor))

    # only calculate the varying volumes for the modulated mixes
    if MasterMixesModulated == "Both" or MasterMixesModulated == "Aqueous":

        Aqueous_MasterMix_Tubes_dict = CalculateVolumesForVariableFactors(
        "Aqueous",
        Aqueous_variables,
        Aqueous_master_mix_dataframe,
        Aqueous_MasterMix_Tubes_dict,
        list_of_required_Aqueous_mastermix_tubes,
        volume_avalible_per_factor,
        base_rxn_dict = base_rxn_dict
        )
    
    elif MasterMixesModulated == "Components":
        pass
    else:
        raise Exception("MasterMixesModulated is neither Aqueous, Components or Both: MasterMixesModulated = " + MasterMixesModulated)

    ####
    # Add buffer
    Aqueous_MasterMix_Tubes_dict = AddResiduleVolOfBuffer(
        MasterMix_Tubes_dict = Aqueous_MasterMix_Tubes_dict,
        MasterMixType = "Aqueous",
        list_of_required_mastermix_tubes = list_of_required_Aqueous_mastermix_tubes,
        base_rxn_dict = base_rxn_dict
        )

    ####


    # Perform the sanity check.
    VolumeSanityCheck(
        plate_number=plate_number,
        MasterMixType = "Aqueous",
        MasterMix_Tubes_dict = Aqueous_MasterMix_Tubes_dict,
        base_rxn_dict = base_rxn_dict)

    # Calculate Total volumes
    Aqueous_vol_dict = CalculateTotalVolumesPlate(
    MasterMix_Tubes_dict = Aqueous_MasterMix_Tubes_dict
    )



    #########################

    # create the plate dict and add the Aqueous MM dict under "Aqueous"

    plate_dict = {}

    plate_dict["Aqueous"] = Aqueous_MasterMix_Tubes_dict


    #########################

    # Next Components Elements

    Components_MM_tubes = []
    for idx, item in Components_master_mix_dataframe['Tubes'].items():
        Components_MM_tubes = Components_MM_tubes + item

    list_of_required_Components_mastermix_tubes = Components_MM_tubes
    number_of_required_Components_mastermix_tubes = len(Components_MM_tubes)

    Components_MasterMix_Tubes_dict = {}

    # If aqueous then just dispense the same into each well
    if MasterMixesModulated == "Aqueous":
        print("No Components to be modulated.")


        # iterate over the Components tube list and dispense the tube volume into each one
        for MasterMix_Tube in list_of_required_Components_mastermix_tubes:

            # iterate over the components to find the base system
            for element in base_rxn_dict["rxn_Components_elements"]:
                if base_rxn_dict["rxn_Components_elements"][element]["Type"] == "Base_System":
                    base_system_name = element

            
            # then just dispense the total_tube_volumes_ul of Components of the base system into the well. No buffer.
            Element_Pipetting_Instructions_dict =   {
                                                        "Stock_source_well": base_rxn_dict["rxn_Components_elements"][base_system_name]["Stock_source_well"],
                                                        "Element_stock_volume_ul": base_rxn_dict["Metainfo"]["Master_Mixes"]["total_tube_volumes_ul"]["Components"]
                                                    }

            Elements_dict[base_system_name] = Element_Pipetting_Instructions_dict
            Components_MasterMix_Tubes_dict[MasterMix_Tube] = Elements_dict 
        
    else:

        ## Assign 10ul of Master Mix space to each component to be modulated.
        # Do this by:
        # ["Metainfo"]["Master_Mixes"]["total_tube_volumes_ul"]["Components"]
        # minus
        # 15 * len(Components_variables)
        # and dispense that volume of base_system.

        core_volume_of_base_system = base_rxn_dict["Metainfo"]["Master_Mixes"]["total_tube_volumes_ul"]["Components"] - (15 * len(Components_variables))

        # find which element in rxn_Components_elements has type base system
        for element in base_rxn_dict["rxn_Components_elements"]:


            if base_rxn_dict["rxn_Components_elements"][element]["Type"] == "Base_System":
                base_system_name = element
            
            else:
                pass

        # then use the base system to dispense.
        for MasterMix_Tube in list_of_required_Components_mastermix_tubes:

            Element_Pipetting_Instructions_dict = {
                "Stock_source_well": base_rxn_dict["rxn_Components_elements"][base_system_name]["Stock_source_well"],
                "Element_stock_volume_ul": base_rxn_dict["Metainfo"]["Master_Mixes"]["total_tube_volumes_ul"]["Components"] - (15 * len(Components_variables))
            }

            Elements_dict = {}
            Elements_dict[base_system_name] = Element_Pipetting_Instructions_dict
            # Add it to the top level dict
            Components_MasterMix_Tubes_dict[MasterMix_Tube]= Elements_dict

            # Also add the "residual_volume" to the top level of the tube dict
            # this makes the "make_up to the mark volume" easier to calculate and keep track of.
            Components_MasterMix_Tubes_dict[MasterMix_Tube]["residual_volume"] = (15 * len(Components_variables))


        ######

    # do the variable factors if appropriate
    if MasterMixesModulated == "Both" or MasterMixesModulated == "Components":

        Components_MasterMix_Tubes_dict = CalculateVolumesForVariableFactors(
        "Components",
        Components_variables,
        Components_master_mix_dataframe,
        Components_MasterMix_Tubes_dict,
        list_of_required_Components_mastermix_tubes,
        base_rxn_dict = base_rxn_dict
        )

    elif MasterMixesModulated == "Aqueous":
        pass
    else:
        raise Exception("MasterMixesModulated is neither Aqueous, Components or Both: MasterMixesModulated = " + MasterMixesModulated)


    #########################

    # Perform the sanity check.
    VolumeSanityCheck(
        plate_number=plate_number,
        MasterMixType = "Components",
        MasterMix_Tubes_dict = Components_MasterMix_Tubes_dict,
        base_rxn_dict = base_rxn_dict)

    ################
    # Calculate Total volumes
    Components_vol_dict = CalculateTotalVolumesPlate(
    MasterMix_Tubes_dict = Components_MasterMix_Tubes_dict
    )

    # add the Components MM dict to plate dict under "Components"
    plate_dict["Components"] = Components_MasterMix_Tubes_dict

    # add that plate to the top level dict under the plate number
    all_plates_dict[str(plate_number)] = plate_dict

    # concatenate the vol_dicts
    # add plate number
    # append to the dataframe
    Aqueous_vol_dict.update(Components_vol_dict)
    Total_col_dict = Aqueous_vol_dict
    Total_col_dict["Plate_Number"] = plate_number
    Total_col_df = Total_col_df.append(Total_col_dict, ignore_index=True)


#########################
with open("tmp/MasterMixes/mastermix_calculations.json", 'w') as fp:
    json.dump(all_plates_dict, fp)

print("Saved mastermix_calculations.json")

Total_col_df.to_csv("./output/Instructions/Total_Required_Reagent_Volumes.csv")
print("Saved Total_Required_Reagent_Volumes.csv")