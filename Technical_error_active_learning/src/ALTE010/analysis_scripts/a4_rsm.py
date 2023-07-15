import pandas as pd
import numpy as np 
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression

from sub_scripts.response_surface_methadology_modelling import *

# Load the dataset from a CSV file (assuming it has headers)
data = pd.read_csv("/app/analysis_scripts/ET_raw.csv")

# delete replicates
data = data.drop(["Yield", "Yield.1", "Yield.2"], axis =1)


# Separate the input features and the output variable
X = data[["Mg", "K", "PEG"]]
Y = data["Mean Yield"]

degree = 2

model, polyfeatures = train_poly_model(X, Y, degree)

response_surface_methadology_plotting(X, Y, model, polyfeatures)

# Test the trained model on new data
new_data = pd.DataFrame({"Mg": [30], "K": [2.5], "PEG": [2.0]})

new_data_poly = polyfeatures.transform(new_data)

prediction = model.predict(new_data_poly)

print("Predicted yield:", prediction)