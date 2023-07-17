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


# output path

output.path <- "/app/analysis_output/plots/"
# read in tidy data
raw <- read.csv(file = "/app/analysis_output/tidy_dataset.csv")
raw <- as.data.frame(raw)

# drop rep columns
trimmed <- raw[ -c(0,5:7) ]


FirstOrder.rsm <- rsm(RFUs ~ FO(MG_Glut, K_Glut, DTT), data = trimmed)
TwoWayInteraction.rsm <- rsm(RFUs ~ TWI(MG_Glut, K_Glut, DTT), data = trimmed)
PureQuadratic.rsm <- rsm(RFUs ~ PQ(MG_Glut, K_Glut, DTT), data = trimmed)
SecondOrder.rsm <- rsm(RFUs ~ SO(MG_Glut, K_Glut, DTT), data = trimmed)

#summary(SecondOrder.rsm)

FirstOrder.lm <- lm(RFUs ~ poly(MG_Glut, K_Glut, DTT, degree=2),data = trimmed)


# save model statistics to disk
model.stats <- summary(FirstOrder.lm)
sink(paste(output.path,"model_statistics.txt"))
print(model.stats)
sink()  # returns output to the console

print(class(model.stats))

par(mfrow=c(1,3))


png.hook = list(pre.plot = function(lab) png(file = paste(output.path, "mg_vs_k_heat.png")), post.plot = function(lab) dev.off())
image(FirstOrder.lm, MG_Glut ~ K_Glut, hook = png.hook)

png.hook = list(pre.plot = function(lab) png(file = paste(output.path,"mg_vs_PEG_heat.png")), post.plot = function(lab) dev.off())
image(FirstOrder.lm, MG_Glut ~ DTT, hook = png.hook)

png.hook = list(pre.plot = function(lab) png(file = paste(output.path,"k_vs_PEG_heat.png")), post.plot = function(lab) dev.off())
image(FirstOrder.lm, K_Glut ~ DTT, hook = png.hook)

png.hook = list(pre.plot = function(lab) png(file = paste(output.path,"mg_vs_k_3D.png")), post.plot = function(lab) dev.off())
persp(FirstOrder.lm,
    MG_Glut ~ K_Glut,
    col = "blue",
    zlab = "RFUs",
    theta = -110, phi = 35,
    hook = png.hook
    )

png.hook = list(pre.plot = function(lab) png(file = paste(output.path,"mg_vs_PEG_3D.png")), post.plot = function(lab) dev.off())
persp(FirstOrder.lm,
    MG_Glut ~ DTT,
    col = "red",
    zlab = "RFUs",
    theta = -140, phi = 35,
    hook = png.hook
    )

png.hook = list(pre.plot = function(lab) png(file = paste(output.path,"k_vs_PEG_3D.png")), post.plot = function(lab) dev.off())
persp(FirstOrder.lm,
    K_Glut ~ DTT,
    col = "Green",
    zlab = "RFUs",
    theta = 50, phi = 35,
    hook = png.hook
    )
