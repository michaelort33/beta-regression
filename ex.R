library(betareg)

data("GasolineYield", package = "betareg")
data("FoodExpenditure", package = "betareg")

#fe_beta = betareg(I(food/income) ~ income + persons, data = FoodExpenditure)
#print(summary(fe_beta)$coefficients)


#m = betareg(yield ~ batch + temp, data = GasolineYield)
#print(summary(m))



#gy2 <- betareg(yield ~ batch + temp | temp, data = GasolineYield, link.phi="identity")
#print(summary(gy2))


meth = read.csv('methylation-test.csv')
m =  betareg(methylation ~ gender + CpG | age, meth)
print(summary(m))

