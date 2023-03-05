

def dilution_calculator(stock_concentration, final_concentration,final_total_volume):
    """ v1 = (c2 * v2) / c1"""
    return (final_total_volume * final_concentration) / stock_concentration


def DNA_ul_to_add_to_Aqueous_MasterMix_from_ng_per_ul_stock(stock_conc_ng_per_ul, len_base_pairs, avg_daltons_per_bp, Aqueous_Master_Mix_conc_nM, Aqueous_Master_mix_volume_ul):
    """1. Calculates MW of the template
       2. Converts ng / ul to nM
       3. v1 = (c2 * v2) / c1 to get volume to add to the master mix"""
    molecular_weight_of_template = len_base_pairs * avg_daltons_per_bp

    stock_concentration_nM = (stock_conc_ng_per_ul / molecular_weight_of_template) * 1000000

    ul_to_add = dilution_calculator(stock_concentration_nM, Aqueous_Master_Mix_conc_nM, Aqueous_Master_mix_volume_ul)

    return ul_to_add

def required_concentration_in_Master_Mix(volume_of_MasterMix_to_rxn, rxn_concentration, total_rxn_volume):
    """ c1 = (v2 * c2) / v1"""
    return (rxn_concentration * total_rxn_volume) / volume_of_MasterMix_to_rxn