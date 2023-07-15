import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.metrics import mean_squared_error



def train_poly_model(X, Y, degree):

    # Create PolynomialFeatures object with the desired degree
    polyfeatures = PolynomialFeatures(degree=degree)

    # Transform the input features to polynomial terms
    X_poly = polyfeatures.fit_transform(X)

    # Create and train the multivariate polynomial linear regression model
    model = LinearRegression()
    model.fit(X_poly, Y)

    # Generate predictions on the training data
    y_pred = model.predict(X_poly)

    # Calculate mean squared error
    mse = mean_squared_error(Y, y_pred)

    # Calculate R-squared score
    r2 = r2_score(Y, y_pred)

    # Print the results
    print("Mean Squared Error:", mse)
    print("R-squared Score:", r2)

    return model, polyfeatures



def response_surface_methadology_plotting(X, Y, model, polyfeatures):

    n_points = 100

    # convert X Dataframe to Numpy Array
    X = X.to_numpy()

    # Number of input features i.e. the number of X variables.
    n_dimensions = X.shape[1]

    # Determine the range of input features. i.e the min and the max values of each variable.
    ranges = [(np.min(X[:, i]), np.max(X[:, i])) for i in range(n_dimensions)]

    # Create mesh grid
    """
    # [np.linspace(r[0], r[1], n_points) for r in ranges] is a list comprehension that iterates over the ranges list.
    # For each range (r[0], r[1]), it generates a 1-dimensional array using np.linspace().
    # This array contains n_points equally spaced values between r[0] and r[1].

    # The asterisk * before the list comprehension [*[np.linspace(r[0], r[1], n_points) for r in ranges]] is used to unpack the list comprehension.
    # It expands the elements of the list comprehension into separate arguments.
    # np.meshgrid() takes the unpacked arguments and returns a mesh grid of N-dimensions.
    # For example, if you have two input features (X and Y), it will create a 2D mesh grid where the first mesh is for X values and the second mesh is for Y values.
    """
    mesh_grid = np.meshgrid(*[np.linspace(r[0], r[1], n_points) for r in ranges])

    # create 2D array where each row is a data point
    X_mesh = np.vstack([arr.ravel() for arr in mesh_grid]).T

    # Create the Z_mesh i.e. the array of predicted output values produced by the trained model
    Z_mesh = model.predict(polyfeatures.transform(X_mesh))
    Z_mesh = Z_mesh.reshape(mesh_grid[0].shape)


    #X_mesh = X_mesh[:,[0,2]]
    Z_mesh = Z_mesh[:,[0,2]]

    print(X_mesh.shape)
    print(Z_mesh.shape)
    print(Z_mesh)


    # Create a 3D plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(mesh_grid[0], mesh_grid[1], Z_mesh, cmap='viridis')

    # Set labels and title
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('Multivariate Polynomial Regression')

    fig.save_fig("test.png")