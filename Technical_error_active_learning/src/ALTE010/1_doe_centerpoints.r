# Load the package required to perform Response Surface Optimisation
library(rsm)
# docs:
# https://cran.r-project.org/web/packages/rsm/rsm.pdf

# Load the package required to read JSON files.
library(rjson)

# Load the package required to plot.
library(ggplot2)

# load dplyr
library(dplyr)

# Import the experiment_variables to modulate JSON
experiment_variables_json <- fromJSON(file = "settings/experiment_variables.json")
# convert to Dataframe
experiment_variables_df <- as.data.frame(experiment_variables_json)

# import design_parameters.json
design_parameters_list <- fromJSON(file = "settings/design_parameters.json")


# get the number of rows of the df to use as # of variables for generating design_coded
number_of_variables <- nrow(experiment_variables_df)

# Building a design

## Links

# Tutorial: https://r-inthelab.net/2022/06/15/response-surface-designs-and-their-analysis-with-r/
# Functions docs: https://rdrr.io/cran/rsm/man/ccd.html

# intialises experimental design_coded
design_coded <- ccd(
    
    # Number of diamentions == the number of variables
    basis = number_of_variables,

    # number of centerpoints
    n0 = 2,

    # number of technical replicates
    wbreps = 1,

    blocks = "Block",

    # places the star points on the planes on the box
    alpha = "faces",

    # Combines the design into one block. Note, the centerpoints for both the box and star blocks are kept.
    oneblock = TRUE,
    randomize = 0,
    inscribed = FALSE)

# convert the design_coded object to a data.frame
design_coded <- as.data.frame(design_coded)

# write the basic design to disk
write.csv(design_coded,"output/Experiment_Designs/design_coded.csv", row.names = TRUE)

## Now insert real values

# iterate over the data.frame rows returning row as an integer
for (row in 1:nrow(experiment_variables_df)) {

    # store the variable name to rename the new column later
    variable_name <- experiment_variables_df[row,"Variable"]

    # create a string with the format "x#" with # as the row number.
    coded_column_name <- paste("x", toString(row), sep="")

    # use the string: coded_column_name (e.g. "x2") to look up the numerical index of the column name in design_coded.
    col_index = which(colnames(design_coded) == coded_column_name)

    ##### Converting the coded values to real values using linear regression
    ## build the regression training dataset by using the row number to look up the min and max values for the component
    ## and build a data.frame by paring them with -1 and 1 as the Y values
    training_df = data.frame(y = c(experiment_variables_df[row,"Max"], experiment_variables_df[row,"Min"]), x = c(1, -1))

    ## build the regression model
    model = lm(y ~ x, data = training_df)

    # Generate the input data by using the coded_column_name to look up the correct column in the design_coded df.
    # then make a new df with one column
    input <- data.frame(x = design_coded[,col_index])

    # create a new column with the variable name
    # populate with the predicted values
    design_coded[, variable_name] <- predict(model, newdata = input)


    # create the new column with the variable name as the col name
    # uses the col index to look up the values in the coded design

    # removing negative values and replacing with the min for that parameter
    min_val = experiment_variables_df[row, 'Min']
    design_coded[, variable_name] <- replace(design_coded[,variable_name], design_coded[,variable_name] < 0, min_val)

}


# round all values to 0.01
design_coded <- round(design_coded, digits=2)


# copy the coded df
design_real <- design_coded

# drop the coded columns
design_real <-design_real %>%
            select(-starts_with('x'))


##### Keep only the last two rows to keep only centerpoints
design_real <- tail(design_real, n = 2) 

# write both to disk as .csv
write.csv(design_real,"output/Experiment_Designs/design_skeleton.csv", row.names = TRUE)
