import pandas as pd 

design_df = pd.read_csv("/app/analysis_scripts/design_final.csv")

design_df = design_df[["MG_Glut", "K_Glut", "DTT"]]


design_df = design_df.iloc[:48,:]


design_df["MasterMixTube"] = ["A1", "A1", "A1", "A2", "A2", "A2", "A3", "A3", "A3","A4", "A4", "A4","A5", "A5", "A5", "A6", "A6", "A6", "A7", "A7", "A7", "A8", "A8", "A8", "A9", "A9", "A9","A10", "A10", "A10", "A11", "A11", "A11", "A12", "A12", "A12", "A13", "A13", "A13", "A14", "A14", "A14", "A15", "A15", "A15", "A16", "A16", "A16"]



design_df["Well"] = ["C3", "C5", "C7", "C9", "C11", "C13", "C15", "C17", "C19", "E3", "E5", "E7", "E9", "E11", "E13", "E15", "E17", "E19", "G3", "G5", "G7", "G9", "G11", "G13", "G15", "G17", "G19", "I3", "I5", "I7", "I9", "I11", "I13", "I15", "I17", "I19", "K3", "K5", "K7", "K9", "K11", "K13", "K15", "K17", "K19", "M3", "M5", "M7"]

print(design_df)

design_df.to_csv("/app/analysis_scripts/design.csv", index=None)