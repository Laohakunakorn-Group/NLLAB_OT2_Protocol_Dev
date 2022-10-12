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

# Import the components to modulate JSON
components_json <- fromJSON(file = "components.json")
# convert to Dataframe
components_df <- as.data.frame(components_json)

# get the number of rows of the df to use as # of variables for generating design_coded
number_of_variables <- nrow(components_df)

# intialises dexperimental design_coded
design_coded <- ccd(basis = number_of_variables,
                n0 = 4,
                blocks = "Block",
                alpha = "orthogonal",
                wbreps = 1,
                bbreps = 1,
                randomize = FALSE,
                inscribed = FALSE)

# convert the design_coded object to a data.frame
design_coded <- as.data.frame(design_coded)

# iterate over the data.frame rows returning row as an integer
for (row in 1:nrow(components_df)) {

    # store the variable name to rename the new column later 
    variable_name <- components_df[row,"Variable"]

    # create a string with the format "x#" with # as the row number.
    coded_column_name <- paste("x", toString(row), sep="")
    
    # use the string: coded_column_name (e.g. "x2") to look up the numerical index of the column name in design_coded.
    col_index = which(colnames(design_coded) == coded_column_name)

    ##### Converting the coded values to real values using linear regression
    ## build the regression training dataset by using the row number to look up the min and max values for the component
    ## and build a data.frame by paring them with -1 and 1 as the Y values
    training_df = data.frame(y = c(components_df[row,"Max"], components_df[row,"Min"]), x = c(1, -1))

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


}

# copy the coded df
design_real <- design_coded

# drop the coded columns
design_real <-design_real %>%
            select(-starts_with('x'))

# write both to disk as .csv
write.csv(design_real,"design_real.csv", row.names = TRUE)
write.csv(design_coded,"design_coded.csv", row.names = TRUE)
