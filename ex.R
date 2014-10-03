library(betareg)

data("GasolineYield", package = "betareg")
data("FoodExpenditure", package = "betareg")

m = betareg(yield ~ batch + temp, data = GasolineYield)
print(summary(m))

fe_beta = betareg(I(food/income) ~ income + persons, data = FoodExpenditure)
print(summary(fe_beta))

