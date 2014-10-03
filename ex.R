library(betareg)

data("GasolineYield", package = "betareg")
m = betareg(yield ~ batch + temp, data = GasolineYield)
print(summary(m))

