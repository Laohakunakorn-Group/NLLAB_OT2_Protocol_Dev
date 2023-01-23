from auxillary_scripts.calculators import *
import json
import pandas as pd



all_plates_dict = {}

# retrieve the number of plates in the experiment
design_final_df = pd.read_csv("processed_data_files/Experiment_Designs/design_final.csv")
quantity_of_plates = design_final_df["Plate"].max()

# iterate over the plate number and perform the allocations
for plate_number in range(1, (quantity_of_plates+1), 1):


    print("Starting allocations for plate #: "+str(plate_number))

    # read in the jsons and dataframes
    es_path = "settings/base_energy_solution.json"
    es_dict = json.load(open(es_path, 'r'))

    base_rxn_path = "settings/base_rxn.json"
    base_rxn_dict = json.load(open(base_rxn_path, 'r'))

    # Aqueous
    aqueous_master_mix_dataframe_path = "processed_data_files/MasterMixes/" + str(plate_number)+ "_plate_aqueous_MasterMix_Stocks.pkl"
    aqueous_master_mix_dataframe = pd.read_pickle(aqueous_master_mix_dataframe_path)

    # extract the aqueous variables
    aqueous_variables = list(aqueous_master_mix_dataframe.columns)
    aqueous_variables.remove("Tubes"); aqueous_variables.remove("Experiments")

    # Components
    components_master_mix_dataframe_path = "processed_data_files/MasterMixes/" + str(plate_number)+ "_plate_components_MasterMix_Stocks.pkl"
    components_master_mix_dataframe = pd.read_pickle(components_master_mix_dataframe_path)

    # extract the components variables
    components_variables = list(components_master_mix_dataframe.columns)
    components_variables.remove("Tubes"); components_variables.remove("Experiments")






    def CalculateVolumesForVariableFactors(
        mastermixtype,
        list_variables,
        mastermix_dataframe,
        MasterMix_Tubes_dict,
        list_of_required_mastermix_tubes,
        base_rxn_dict = base_rxn_dict
        ):

        # extract the key identifiers based on master mix type
        if mastermixtype == "aqueous":
            mastermixtype_short = "aqueous"
            rxn_elements_name = "rxn_aqueous_elements"
        elif mastermixtype == "components":
            mastermixtype_short = "components"
            rxn_elements_name = "rxn_components_elements"
        else:
            raise Exception("ArgsL Unknown mastermixtype, Select either 'aqueous' or 'components'")       
        # Iterate over the list_variables
        # perform the dilution calculation
        # add that volume

        for component in list_variables:

            for idx, Tube_list in mastermix_dataframe["Tubes"].items():

                for MasterMix_Tube in Tube_list:

                    # retrieve the corresponding master mix conc (uM)
                    Element_Master_Mix_conc_uM = mastermix_dataframe.loc[idx,component]

                    # Calculate the ul to be added
                    Element_MasterMix_Volume_ul = dilution_calculator(stock_concentration = base_rxn_dict[rxn_elements_name][component]["stock_conc_uM"],
                                                    final_concentration = Element_Master_Mix_conc_uM, 
                                                    final_total_volume = base_rxn_dict["Metainfo"]["Master_Mixes"]["total_tube_volumes_ul"][mastermixtype_short])

                    #### Check that the volume is 1.0 < x < 10
                    if not 0.5 <= Element_MasterMix_Volume_ul <= 15:
                        raise Exception("The required volume is not between 0.5 < x < 10 ul.  "+ str(Element_MasterMix_Volume_ul) +" "+ component) 
                    
                    # Construct the 
                    Element_Pipetting_Instructions_dict = {
                                "Stock_source_well": base_rxn_dict[rxn_elements_name][component]["Stock_source_well"],
                                "Element_stock_volume_ul": Element_MasterMix_Volume_ul
                            }
                    
                    # append to the existing dicts
                    MasterMix_Tubes_dict[MasterMix_Tube][component] = Element_Pipetting_Instructions_dict

                    # update the residual_volume
                    MasterMix_Tubes_dict[MasterMix_Tube]["residual_volume"] = MasterMix_Tubes_dict[MasterMix_Tube]["residual_volume"] - Element_MasterMix_Volume_ul


        #### Add Stock-30 BME Corresponding to the remaining residual volume
        ## delete residual volume from each record

        # find which element in rxn_components_elements has type Buffer
        for element in base_rxn_dict[rxn_elements_name]:

            if base_rxn_dict[rxn_elements_name][element]["Type"] == "Buffer":
                buffer_name = element
            else:
                pass
        

        for MasterMix_Tube in list_of_required_mastermix_tubes:

            MasterMix_Tubes_dict[MasterMix_Tube][buffer_name] = {

                "Stock_source_well": base_rxn_dict[rxn_elements_name][buffer_name]["Stock_source_well"],
                "Element_stock_volume_ul": MasterMix_Tubes_dict[MasterMix_Tube]["residual_volume"]

            }

            # delete the residual volume record
            del MasterMix_Tubes_dict[MasterMix_Tube]["residual_volume"]


        return MasterMix_Tubes_dict










    ############################

    # First do the Aqueous Elements

    aq_tubes = []
    for idx, item in aqueous_master_mix_dataframe['Tubes'].items():
        aq_tubes = aq_tubes + item

    list_of_required_aqueous_mastermix_tubes = aq_tubes
    number_of_required_aqueous_mastermix_tubes = len(aq_tubes)

    # Standard Components that go into every reaction

    Aqueous_MasterMix_Tubes_dict = {}

    for MasterMix_Tube in list_of_required_aqueous_mastermix_tubes:

        # Also add the "residual_volume" to the top level of the tube dict
        # this makes the "make_up to the mark volume" easier to calculate and keep track of.
        Aqueous_MasterMix_Tubes_dict[MasterMix_Tube] = {}
        Aqueous_MasterMix_Tubes_dict[MasterMix_Tube]["residual_volume"] = base_rxn_dict["Metainfo"]["Master_Mixes"]["total_tube_volumes_ul"]["aqueous"]


        Elements_dict = {}

        for element in base_rxn_dict["rxn_aqueous_elements"].keys():

            # check if it is to be added to the master mix or not by cross referencing with the variable list.
            if element in aqueous_variables:
                #print(element + " is in the variables modulated, therefore skipping it's addition to the mastermix..")
                pass

            else:
                # if it's a template then execute this cell
                if base_rxn_dict["rxn_aqueous_elements"][element]["Type"] == "Template":

                    Template_Aqueous_Master_Mix_conc_nM = required_concentration_in_Master_Mix(volume_of_MasterMix_to_rxn =base_rxn_dict["Metainfo"]["Master_Mixes"]["Volumes_added_to_rxn"]["aqueous"],
                                                                                    rxn_concentration= base_rxn_dict["rxn_aqueous_elements"][element]["rxn_conc_nM"],
                                                                                    total_rxn_volume = base_rxn_dict["Metainfo"]["total_reaction_volume_ul"])


                    Element_MasterMix_Volume_ul = DNA_ul_to_add_to_aqueous_MasterMix_from_ng_per_ul_stock(stock_conc_ng_per_ul = base_rxn_dict["rxn_aqueous_elements"][element]["stock_conc_ng_per_ul"],
                                                                                    len_base_pairs = base_rxn_dict["rxn_aqueous_elements"][element]["len_base_pairs"],
                                                                                    avg_daltons_per_bp = base_rxn_dict["rxn_aqueous_elements"][element]["avg_daltons_per_bp"],
                                                                                    Aqueous_Master_Mix_conc_nM = Template_Aqueous_Master_Mix_conc_nM,
                                                                                    Aqueous_Master_mix_volume_ul =  base_rxn_dict["Metainfo"]["Master_Mixes"]["total_tube_volumes_ul"]["aqueous"])
                    
                    Element_Pipetting_Instructions_dict =   {
                                                                "Stock_source_well": base_rxn_dict["rxn_aqueous_elements"][element]["Stock_source_well"],
                                                                "Element_stock_volume_ul": Element_MasterMix_Volume_ul
                                                            }
                    
                    # Also update the "residual_volume" 
                    Aqueous_MasterMix_Tubes_dict[MasterMix_Tube]["residual_volume"] = Aqueous_MasterMix_Tubes_dict[MasterMix_Tube]["residual_volume"] - Element_MasterMix_Volume_ul


                # if its a normal element...
                elif base_rxn_dict["rxn_aqueous_elements"][element]["Type"] == "Standard":

                    Element_Aqueous_Master_Mix_conc_uM = required_concentration_in_Master_Mix(volume_of_MasterMix_to_rxn =base_rxn_dict["Metainfo"]["Master_Mixes"]["Volumes_added_to_rxn"]["aqueous"],
                                                                            rxn_concentration=base_rxn_dict["rxn_aqueous_elements"][element]["rxn_conc_uM"],
                                                                            total_rxn_volume = base_rxn_dict["Metainfo"]["total_reaction_volume_ul"])

                    Element_MasterMix_Volume_ul = dilution_calculator(stock_concentration = base_rxn_dict["rxn_aqueous_elements"][element]["stock_conc_uM"],
                                                    final_concentration = Element_Aqueous_Master_Mix_conc_uM, 
                                                    final_total_volume = base_rxn_dict["Metainfo"]["Master_Mixes"]["total_tube_volumes_ul"]["aqueous"])


                    Element_Pipetting_Instructions_dict =   {
                                                                "Stock_source_well": base_rxn_dict["rxn_aqueous_elements"][element]["Stock_source_well"],
                                                                "Element_stock_volume_ul": Element_MasterMix_Volume_ul
                                                            }
                    
                    # Also update the "residual_volume" 
                    Aqueous_MasterMix_Tubes_dict[MasterMix_Tube]["residual_volume"] = Aqueous_MasterMix_Tubes_dict[MasterMix_Tube]["residual_volume"] - Element_MasterMix_Volume_ul



                elif base_rxn_dict["rxn_aqueous_elements"][element]["Type"] == "Buffer":
                    Element_Pipetting_Instructions_dict = "Placeholder"
                else:
                    raise Exception("Unknown rxn element type: Check base_rxn.json for "+ element)


            Aqueous_MasterMix_Tubes_dict[MasterMix_Tube][element] = Element_Pipetting_Instructions_dict

    ##########

        
    # do the variable factors

    Aqueous_MasterMix_Tubes_dict = CalculateVolumesForVariableFactors(
    "aqueous",
    aqueous_variables,
    aqueous_master_mix_dataframe,
    Aqueous_MasterMix_Tubes_dict,
    list_of_required_aqueous_mastermix_tubes,
    base_rxn_dict = base_rxn_dict
    )



    ####

    # sanity check by confirming that all the volumes add up tobase_rxn_dict["Metainfo"]["Master_Mixes"]["total_tube_volumes_ul"]["aqueous"]
    base_rxn_dict["Metainfo"]["Master_Mixes"]["total_tube_volumes_ul"]["aqueous"]

    for tube in Aqueous_MasterMix_Tubes_dict:

        tube_vol_list = []
        for element in Aqueous_MasterMix_Tubes_dict[tube]:
            tube_vol_list.append(Aqueous_MasterMix_Tubes_dict[tube][element]["Element_stock_volume_ul"])

        if round(sum(tube_vol_list)) == base_rxn_dict["Metainfo"]["Master_Mixes"]["total_tube_volumes_ul"]["aqueous"]:
            pass

        elif round(sum(tube_vol_list)) > base_rxn_dict["Metainfo"]["Master_Mixes"]["total_tube_volumes_ul"]["aqueous"]:
            print(tube)
            print(round(sum(tube_vol_list)))
            raise Exception("The aqueous total volume is greater than: "+str(base_rxn_dict["Metainfo"]["Master_Mixes"]["total_tube_volumes_ul"]["aqueous"])) 
        
        elif round(sum(tube_vol_list)) < base_rxn_dict["Metainfo"]["Master_Mixes"]["total_tube_volumes_ul"]["aqueous"]:
            print(tube)
            print(round(sum(tube_vol_list)))
            raise Exception("The aqueous total volume is less than: "+str(base_rxn_dict["Metainfo"]["Master_Mixes"]["total_tube_volumes_ul"]["aqueous"])) 



    #########################

    # create the plate dict and add the aqueous MM dict under "Aqueous"

    plate_dict = {}

    plate_dict["Aqueous"] = Aqueous_MasterMix_Tubes_dict


    #########################

    # Next Components Elements

    components_MM_tubes = []
    for idx, item in components_master_mix_dataframe['Tubes'].items():
        components_MM_tubes = components_MM_tubes + item

    list_of_required_components_mastermix_tubes = components_MM_tubes
    number_of_required_components_mastermix_tubes = len(components_MM_tubes)

    Components_MasterMix_Tubes_dict = {}

    # empty lists are False in python
    if not components_variables:
        print("No components to be modulated.")
        

        # iterate over the components tube list and dispense the tube volume into each one
        for MasterMix_Tube in list_of_required_components_mastermix_tubes:
                
            Element_Pipetting_Instructions_dict =   {
                                                        "Stock_source_well": base_rxn_dict["rxn_components_elements"][element]["Stock_source_well"],
                                                        "Element_stock_volume_ul": base_rxn_dict["Metainfo"]["Master_Mixes"]["total_tube_volumes_ul"]["components"]
                                                    }

            Elements_dict[element] = Element_Pipetting_Instructions_dict
            Components_MasterMix_Tubes_dict[MasterMix_Tube] = Elements_dict 
        
    else:

        ## Assign 10ul of Master Mix space to each component to be modulated.
        # Do this by:
        # ["Metainfo"]["Master_Mixes"]["total_tube_volumes_ul"]["components"]
        # minus
        # 15 * len(components_variables)
        # and dispense that volume of base_system.

        core_volume_of_base_system = base_rxn_dict["Metainfo"]["Master_Mixes"]["total_tube_volumes_ul"]["components"] - (15 * len(components_variables))

        # find which element in rxn_components_elements has type base system
        for element in base_rxn_dict["rxn_components_elements"]:

            if base_rxn_dict["rxn_components_elements"][element]["Type"] == "Base_System":
                base_system_name = element
            else:
                pass

        # then use the base system to dispense.
        for MasterMix_Tube in list_of_required_components_mastermix_tubes:

            Element_Pipetting_Instructions_dict = {
                "Stock_source_well": base_rxn_dict["rxn_components_elements"][base_system_name]["Stock_source_well"],
                "Element_stock_volume_ul": base_rxn_dict["Metainfo"]["Master_Mixes"]["total_tube_volumes_ul"]["components"] - (15 * len(components_variables))
            }

            Elements_dict = {}
            Elements_dict[base_system_name] = Element_Pipetting_Instructions_dict
            # Add it to the top level dict
            Components_MasterMix_Tubes_dict[MasterMix_Tube]= Elements_dict

            # Also add the "residual_volume" to the top level of the tube dict
            # this makes the "make_up to the mark volume" easier to calculate and keep track of.
            Components_MasterMix_Tubes_dict[MasterMix_Tube]["residual_volume"] = (15 * len(components_variables))


        ######

    # do the variable factors

    Components_MasterMix_Tubes_dict = CalculateVolumesForVariableFactors(
    "components",
    components_variables,
    components_master_mix_dataframe,
    Components_MasterMix_Tubes_dict,
    list_of_required_components_mastermix_tubes,
    base_rxn_dict = base_rxn_dict
    )



    #########################

    # sanity check by confirming that all the volumes add up tobase_rxn_dict["Metainfo"]["Master_Mixes"]["total_tube_volumes_ul"]["aqueous"]

    for tube in Components_MasterMix_Tubes_dict:

        tube_vol_list = []
        for element in Components_MasterMix_Tubes_dict[tube]:
            tube_vol_list.append(Components_MasterMix_Tubes_dict[tube][element]["Element_stock_volume_ul"])

        if round(sum(tube_vol_list)) == base_rxn_dict["Metainfo"]["Master_Mixes"]["total_tube_volumes_ul"]["components"]:
            pass

        elif round(sum(tube_vol_list)) > base_rxn_dict["Metainfo"]["Master_Mixes"]["total_tube_volumes_ul"]["components"]:
            print(tube)
            print(round(sum(tube_vol_list)))
            raise Exception("The aqueous total volume is greater than: "+str(base_rxn_dict["Metainfo"]["Master_Mixes"]["total_tube_volumes_ul"]["components"])) 
        
        elif round(sum(tube_vol_list)) < base_rxn_dict["Metainfo"]["Master_Mixes"]["total_tube_volumes_ul"]["components"]:
            print(tube)
            print(round(sum(tube_vol_list)))
            raise Exception("The aqueous total volume is less than: "+str(base_rxn_dict["Metainfo"]["Master_Mixes"]["total_tube_volumes_ul"]["components"])) 


    ################



    # add the components MM dict to plate dict under "Components"

    plate_dict["Components"] = Components_MasterMix_Tubes_dict

    # add that plate to the top level dict under the plate number
    all_plates_dict[str(plate_number)] = plate_dict

#########################
with open("processed_data_files/MasterMixes/mastermix_calculations.json", 'w') as fp:
    json.dump(all_plates_dict, fp)

print("Saved mastermix_calculations.json")
