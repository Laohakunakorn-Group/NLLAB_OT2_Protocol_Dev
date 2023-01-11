

def dilution_calculator(stock_concentration, final_concentration,final_total_volume):

    return (final_total_volume * final_concentration) / stock_concentration

def DNA_ul_to_add_to_aqueous_MasterMix_from_ng_per_ul_stock(stock_conc_ng_per_ul, len_base_pairs, avg_daltons_per_bp, rxn_conc_nM, ):

    molecular_weight_of_template = len_base_pairs * avg_daltons_per_bp

    stock_concentration_nM = (stock_conc_ng_per_ul / molecular_weight_of_template) * 1000000


    ul_to_add = 3

    return ul_to_add