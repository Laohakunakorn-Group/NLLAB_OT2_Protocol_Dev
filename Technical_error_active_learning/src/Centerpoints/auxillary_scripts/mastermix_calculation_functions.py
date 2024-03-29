import json
from auxillary_scripts.calculators import *
import math

base_rxn_path = "./settings/base_rxn.json"
base_rxn_dict = json.load(open(base_rxn_path, 'r'))

pipetting_settings_dict_path = "./settings/pipetting_settings.json"
pipetting_settings_dict = json.load(open(pipetting_settings_dict_path, 'r'))






def CalculateResidualVolumeAllocatedForVariableFactors(MasterMix_Tubes_dict, list_variables):

    # check all residule volumes are the same

    residual_volumes = []
    for MasterMix_Tube in MasterMix_Tubes_dict:
        residual_volumes.append(MasterMix_Tubes_dict[MasterMix_Tube]["residual_volume"])

    if not (residual_volumes.count(residual_volumes[0]) == len(residual_volumes)):
        raise Exception("There are varying residual volumes leading into the variable factors..")
    else:
        pass

    # as they are the same, grab the first one
    residual_volume = residual_volumes[0]

    # get the # of variables
    number_of_variables = len(list_variables)

    # divide
    volume_avalible_per_factor = residual_volume/number_of_variables

    # round up to the nearest ul
    volume_avalible_per_factor = round(volume_avalible_per_factor)

    return volume_avalible_per_factor
    



def CalculateVolumesForVariableFactors(
    MasterMixType,
    list_variables,
    mastermix_dataframe,
    MasterMix_Tubes_dict,
    list_of_required_mastermix_tubes,
    volume_avalible_per_factor,
    base_rxn_dict = base_rxn_dict,
    ):

    # extract the key identifiers based on master mix type
    if MasterMixType == "Aqueous":
        MasterMixType_short = "Aqueous"
        rxn_elements_name = "rxn_Aqueous_elements"

    elif MasterMixType == "Components":
        MasterMixType_short = "Components"
        rxn_elements_name = "rxn_Components_elements"
    else:
        raise Exception("Args: Unknown MasterMixType, Select either 'Aqueous' or 'Components'")    


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
                                                final_total_volume = base_rxn_dict["Metainfo"]["Master_Mixes"]["total_tube_volumes_ul"][MasterMixType_short])

                #### Check that the volume is 0.5 < x < volume_avalible_per_factor
                if not 0.5 <= Element_MasterMix_Volume_ul <= volume_avalible_per_factor:
                    raise Exception("The required volume is not between 0.5 < x < " + str(volume_avalible_per_factor) + " ul.  "+ str(Element_MasterMix_Volume_ul) +" "+ component) 
                
                # Construct the 
                Element_Pipetting_Instructions_dict = {
                            "Stock_source_well": base_rxn_dict[rxn_elements_name][component]["Stock_source_well"],
                            "Element_stock_volume_ul": Element_MasterMix_Volume_ul
                        }
                
                # append to the existing dicts
                MasterMix_Tubes_dict[MasterMix_Tube][component] = Element_Pipetting_Instructions_dict

                # update the residual_volume
                MasterMix_Tubes_dict[MasterMix_Tube]["residual_volume"] = MasterMix_Tubes_dict[MasterMix_Tube]["residual_volume"] - Element_MasterMix_Volume_ul

    return MasterMix_Tubes_dict


def AddResiduleVolOfBuffer(
    MasterMix_Tubes_dict,
    MasterMixType,
    list_of_required_mastermix_tubes,
    base_rxn_dict = base_rxn_dict
    ):
    
    # extract the key identifiers based on master mix type
    if MasterMixType == "Aqueous":
        rxn_elements_name = "rxn_Aqueous_elements"

    elif MasterMixType == "Components":
        rxn_elements_name = "rxn_Components_elements"
    else:
        raise Exception("Args: Unknown MasterMixType, Select either 'Aqueous' or 'Components'")    

    
    #### Add Buffer Corresponding to the remaining residual volume
    ## delete residual volume from each record

    # find which element in rxn_Components_elements has type Buffer
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


def VolumeSanityCheck(plate_number, MasterMixType, MasterMix_Tubes_dict, base_rxn_dict = base_rxn_dict):

    # sanity check by confirming that all the volumes add up to
    
    readout = 0

    for tube in MasterMix_Tubes_dict:

        tube_vol_list = []
        for element in MasterMix_Tubes_dict[tube]:
            tube_vol_list.append(MasterMix_Tubes_dict[tube][element]["Element_stock_volume_ul"])


        if round(sum(tube_vol_list)) == base_rxn_dict["Metainfo"]["Master_Mixes"]["total_tube_volumes_ul"][MasterMixType]:
            pass

        elif round(sum(tube_vol_list)) > base_rxn_dict["Metainfo"]["Master_Mixes"]["total_tube_volumes_ul"][MasterMixType]:
            readout += 1
            print(tube)
            print(round(sum(tube_vol_list)))
            raise Exception("The "+MasterMixType+" total volume is greater than: "+str(base_rxn_dict["Metainfo"]["Master_Mixes"]["total_tube_volumes_ul"][MasterMixType])) 
        
        elif round(sum(tube_vol_list)) < base_rxn_dict["Metainfo"]["Master_Mixes"]["total_tube_volumes_ul"][MasterMixType]:
            readout += 1
            print(tube)
            print(round(sum(tube_vol_list)))
            raise Exception("The "+MasterMixType+" total volume is less than: "+str(base_rxn_dict["Metainfo"]["Master_Mixes"]["total_tube_volumes_ul"][MasterMixType])) 
    
    if readout > 0:
        raise Exception("Volumes for "+MasterMixType+" don't add up.")
    else:
        print()
        print("Volumes for "+MasterMixType+" in plate "+str(plate_number)+" add up.") 
        print()

def CalculateTotalVolumesPlate(
    MasterMix_Tubes_dict,
    pipetting_settings_dict = pipetting_settings_dict
    ):

    # first confirm that all of the tubes contain the same elements
    # checking funciton
    def checkList(lst):
        ele = lst[0]
        chk = True
        # Comparing each element with first item
        for item in lst:
            if ele != item:
                chk = False
                break

        if (chk != True):
            raise Exception("Not equal")
        else:
            pass
 
    # build lists of element names
    all_tubes_element_list = []
    tube_element_list = []
    for MasterMixTube in MasterMix_Tubes_dict:

        tube_element_list = []

        for element in MasterMix_Tubes_dict[MasterMixTube]:

            tube_element_list.append(element)
        all_tubes_element_list.append(tube_element_list)
    #execute
    checkList(all_tubes_element_list)

    # initialise the total volume dict using the elements from the last
    # tube_element_list as keys. can do as they are all the same.
    # set all initial values to 0

    vol_dict = {}
    for element in tube_element_list:
        vol_dict[element] = 0

    # iterate over each tube and element
    # required volume = the volume added x pipetting_settings_dict["MasterMix"]["Meta"]["MasterMix_Residual_xFactor"]
    for MasterMixTube in MasterMix_Tubes_dict:
        for element in MasterMix_Tubes_dict[MasterMixTube]:

            required_volume = MasterMix_Tubes_dict[MasterMixTube][element]["Element_stock_volume_ul"] * pipetting_settings_dict["MasterMix"]["Meta"]["MasterMix_Residual_xFactor"]

            # add to the element in vol_dict
            vol_dict[element] = vol_dict[element] + required_volume

    # round up to the nearest integer.
    for element in vol_dict:
        vol_dict[element] = math.ceil(vol_dict[element])

    return vol_dict
