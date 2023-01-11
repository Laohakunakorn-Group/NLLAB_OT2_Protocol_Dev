from auxillary_scripts.calculators import *
import json
import pandas as pd


es_path = "base_settings/base_energy_solution.json"
es_dict = json.load(open(es_path, 'r'))

plate_number = 1
mm_path = "processed_data_files/MasterMixes/" + str(plate_number)+ "_plate_aqueous_MasterMix_Stocks.pkl"
aqueous_master_mixes = pd.read_pickle(mm_path)

base_rxn_path = "base_settings/base_rxn.json"
base_rxn_dict = json.load(open(base_rxn_path, 'r'))

aq_tubes = []
for idx, item in aqueous_master_mixes['Tubes'].items():
    aq_tubes = aq_tubes + item

list_of_required_aqueous_mastermix_tubes = aq_tubes
number_of_required_aqueous_mastermix_tubes = len(aq_tubes)

Aqueous_Master_mix_volume_ul = base_rxn_dict["Metainfo"]["Master_Mixes"]["total_tube_volumes_ul"]["aqueous"]

stock_conc_ng_per_ul = base_rxn_dict["rxn_elements"]["Template"]["stock_conc_ng_per_ul"]
rxn_conc_nM = base_rxn_dict["rxn_elements"]["Template"]["rxn_conc_nM"]
avg_daltons_per_bp = base_rxn_dict["rxn_elements"]["Template"]["avg_daltons_per_bp"]
len_base_pairs = base_rxn_dict["rxn_elements"]["Template"]["len_base_pairs"]

Aqueous_Master_Mix_conc_nM = required_concentration_in_Master_Mix(volume_of_MasterMix_to_rxn =base_rxn_dict["Metainfo"]["Master_Mixes"]["Volumes_added_to_rxn"]["aqueous"],
                                                                  rxn_concentration=rxn_conc_nM,
                                                                  total_rxn_volume = base_rxn_dict["Metainfo"]["total_reaction_volume_ul"])


dna_ul_MM = DNA_ul_to_add_to_aqueous_MasterMix_from_ng_per_ul_stock(stock_conc_ng_per_ul = stock_conc_ng_per_ul,
                                                                 len_base_pairs = len_base_pairs,
                                                                 avg_daltons_per_bp = avg_daltons_per_bp,
                                                                 Aqueous_Master_Mix_conc_nM = Aqueous_Master_Mix_conc_nM,
                                                                 Aqueous_Master_mix_volume_ul = Aqueous_Master_mix_volume_ul)


print("Total Vol of DNA req for plate: "+ str(dna_ul_MM * number_of_required_aqueous_mastermix_tubes)+ "ul")

# chi6

Chi6_Aqueous_Master_Mix_conc_uM = required_concentration_in_Master_Mix(volume_of_MasterMix_to_rxn =base_rxn_dict["Metainfo"]["Master_Mixes"]["Volumes_added_to_rxn"]["aqueous"],
                                                                  rxn_concentration=base_rxn_dict["rxn_elements"]["Chi6"]["rxn_conc_uM"],
                                                                  total_rxn_volume = base_rxn_dict["Metainfo"]["total_reaction_volume_ul"])

Chi6_ul_MM = dilution_calculator(stock_concentration = base_rxn_dict["rxn_elements"]["Chi6"]["stock_conc_uM"],
                                 final_concentration = Chi6_Aqueous_Master_Mix_conc_uM, 
                                 final_total_volume = base_rxn_dict["Metainfo"]["Master_Mixes"]["total_tube_volumes_ul"]["aqueous"])
print()
print(Chi6_Aqueous_Master_Mix_conc_uM)
print(Chi6_ul_MM)
print("Total Vol of Chi6 req for plate: "+ str(Chi6_ul_MM * number_of_required_aqueous_mastermix_tubes)+ "ul")

# MG

MG_Aqueous_Master_Mix_conc_uM = required_concentration_in_Master_Mix(volume_of_MasterMix_to_rxn =base_rxn_dict["Metainfo"]["Master_Mixes"]["Volumes_added_to_rxn"]["aqueous"],
                                                                  rxn_concentration=base_rxn_dict["rxn_elements"]["Malachite_Green"]["rxn_conc_uM"],
                                                                  total_rxn_volume = base_rxn_dict["Metainfo"]["total_reaction_volume_ul"])

MG_ul_MM = dilution_calculator(stock_concentration = base_rxn_dict["rxn_elements"]["Malachite_Green"]["stock_conc_uM"],
                                 final_concentration = MG_Aqueous_Master_Mix_conc_uM, 
                                 final_total_volume = base_rxn_dict["Metainfo"]["Master_Mixes"]["total_tube_volumes_ul"]["aqueous"])
print()
print(MG_Aqueous_Master_Mix_conc_uM)
print(MG_ul_MM)
print("Total Vol of MG req for plate: "+ str(MG_ul_MM * number_of_required_aqueous_mastermix_tubes)+ "ul")
