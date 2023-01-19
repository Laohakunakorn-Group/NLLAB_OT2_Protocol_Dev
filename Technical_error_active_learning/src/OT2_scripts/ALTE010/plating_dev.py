import json

plate_number_string  = str(1)
MasterMixCalculationsPath = "processed_ot2_settings/mastermix_calculations.json"
MasterMixCalculationsDict = json.load(open(MasterMixCalculationsPath, 'r'))
MasterMixCalculationsDict = MasterMixCalculationsDict[plate_number_string]

MasterMixCalculationsDict = MasterMixCalculationsDict["Aqueous"]
MasterMixCalculationsDict = MasterMixCalculationsDict['A1']
MasterMixCalculationsDict = MasterMixCalculationsDict['Template']
MasterMixCalculationsDict = MasterMixCalculationsDict.keys()

print(MasterMixCalculationsDict)