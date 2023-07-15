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
raw <- read.csv(file = "/app/analysis_scripts/ET_raw.csv")
raw <- as.data.frame(raw)

# drop rep columns
trimmed <- raw[ -c(0,5:7) ]


FirstOrder.rsm <- rsm(Mean.Yield ~ FO(K, Mg, PEG), data = trimmed)
TwoWayInteraction.rsm <- rsm(Mean.Yield ~ TWI(K, Mg, PEG), data = trimmed)
PureQuadratic.rsm <- rsm(Mean.Yield ~ PQ(K, Mg, PEG), data = trimmed)
SecondOrder.rsm <- rsm(Mean.Yield ~ SO(K, Mg, PEG), data = trimmed)

#summary(SecondOrder.rsm)

FirstOrder.lm <- lm(Mean.Yield ~ poly(Mg, K, PEG, degree=3),data = trimmed)


# save model statistics to disk
model.stats <- summary(FirstOrder.lm)
sink(paste(output.path,"model_statistics.txt"))
print(model.stats)
sink()  # returns output to the console

print(class(model.stats))

par(mfrow=c(1,3))


png.hook = list(pre.plot = function(lab) png(file = paste(output.path, "mg_vs_k_heat.png")), post.plot = function(lab) dev.off())
image(FirstOrder.lm, Mg ~ K, hook = png.hook)

png.hook = list(pre.plot = function(lab) png(file = paste(output.path,"mg_vs_PEG_heat.png")), post.plot = function(lab) dev.off())
image(FirstOrder.lm, Mg ~ PEG, hook = png.hook)

png.hook = list(pre.plot = function(lab) png(file = paste(output.path,"k_vs_PEG_heat.png")), post.plot = function(lab) dev.off())
image(FirstOrder.lm, K ~ PEG, hook = png.hook)

png.hook = list(pre.plot = function(lab) png(file = paste(output.path,"mg_vs_k_3D.png")), post.plot = function(lab) dev.off())
persp(FirstOrder.lm,
    Mg ~ K,
    col = "blue",
    zlab = "Mean.Yield",
    theta = -110, phi = 35,
    hook = png.hook
    )

png.hook = list(pre.plot = function(lab) png(file = paste(output.path,"mg_vs_PEG_3D.png")), post.plot = function(lab) dev.off())
persp(FirstOrder.lm,
    Mg ~ PEG,
    col = "red",
    zlab = "Mean.Yield",
    theta = -140, phi = 35,
    hook = png.hook
    )

png.hook = list(pre.plot = function(lab) png(file = paste(output.path,"k_vs_PEG_3D.png")), post.plot = function(lab) dev.off())
persp(FirstOrder.lm,
    K ~ PEG,
    col = "Green",
    zlab = "Mean.Yield",
    theta = 50, phi = 35,
    hook = png.hook
    )
