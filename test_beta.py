
# in R:
import io
import pandas as pd
from betareg import Beta
import numpy as np

# betareg(I(food/income) ~ income + persons, data = FoodExpenditure)
_income_estimates_mean = u"""\
varname        Estimate  StdError   zvalue     Pr(>|z|)
(Intercept) -0.62254806 0.223853539 -2.781051 5.418326e-03
income      -0.01229884 0.003035585 -4.051556 5.087819e-05
persons      0.11846210 0.035340667  3.352005 8.022853e-04"""

_income_estimates_precision = u"""\
varname  Estimate StdError  zvalue     Pr(>|z|)
(phi) 35.60975   8.079598 4.407366 1.046351e-05
"""

_methylation_estimates_mean = u"""\
varname      Estimate StdError zvalue Pr(>|z|)    
(Intercept)  1.44224    0.03401  42.404   <2e-16
genderM      0.06986    0.04359   1.603    0.109    
CpGCpG_1     0.60735    0.04834  12.563   <2e-16
CpGCpG_2     0.97355    0.05311  18.331   <2e-16"""

_methylation_estimates_precision = u"""\
varname Estimate StdError zvalue Pr(>|z|)    
(Intercept)  8.22829    1.79098   4.594 4.34e-06 ***
age         -0.03471    0.03276  -1.059    0.289"""


expected_income_mean = pd.read_table(io.StringIO(_income_estimates_mean), sep="\s+")
expected_income_precision = pd.read_table(io.StringIO(_income_estimates_precision), sep="\s+")

expected_methylation_mean = pd.read_table(io.StringIO(_methylation_estimates_mean), sep="\s+")
expected_methylation_precision = pd.read_table(io.StringIO(_methylation_estimates_precision), sep="\s+")

income = pd.read_csv('foodexpenditure.csv')

def test_income_coefficients():
    model = "I(food/income) ~ income + persons"

    mod = Beta.from_formula(model, income)
    rslt = mod.fit()
    assert np.allclose(rslt.params[:-1], expected_income_mean['Estimate'])
    print rslt.tvalues
    print expected_income_mean['zvalue']
    assert np.allclose(rslt.tvalues[:-1], expected_income_mean['zvalue'], rtol=0.1)

