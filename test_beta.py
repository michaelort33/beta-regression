
# in R:
import io
import statsmodels.api as sm
import pandas as pd
import patsy
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
(Intercept)  1.44224    0.03401  42.404   2e-16
genderM      0.06986    0.04359   1.603    0.109    
CpGCpG_1     0.60735    0.04834  12.563   2e-16
CpGCpG_2     0.97355    0.05311  18.331   2e-16"""

_methylation_estimates_precision = u"""\
varname Estimate StdError zvalue Pr(>|z|)    
(Intercept)  8.22829    1.79098   4.594 4.34e-06
age         -0.03471    0.03276  -1.059    0.289"""


expected_income_mean = pd.read_table(io.StringIO(_income_estimates_mean), sep="\s+")
expected_income_precision = pd.read_table(io.StringIO(_income_estimates_precision), sep="\s+")

expected_methylation_mean = pd.read_table(io.StringIO(_methylation_estimates_mean), sep="\s+")
expected_methylation_precision = pd.read_table(io.StringIO(_methylation_estimates_precision), sep="\s+")

income = pd.read_csv('foodexpenditure.csv')
methylation = pd.read_csv('methylation-test.csv')

def check_same(a, b, eps, name):
    assert np.allclose(a, b, rtol=0.01, atol=eps), \
            ("different from expected", name, list(a), list(b))


def test_income_coefficients():
    model = "I(food/income) ~ income + persons"

    mod = Beta.from_formula(model, income)
    rslt = mod.fit()
    yield check_same, rslt.params[:-1], expected_income_mean['Estimate'], 1e-3, "estimates"
    yield check_same, rslt.tvalues[:-1], expected_income_mean['zvalue'], 0.1, "z-scores"
    yield check_same, rslt.pvalues[:-1], expected_income_mean['Pr(>|z|)'], 1e-3, "p-values"


def test_income_precision():
    model = "I(food/income) ~ income + persons"

    mod = Beta.from_formula(model, income)
    rslt = mod.fit()
    # note that we have to exp the phi results for now.
    yield check_same, np.exp(rslt.params[-1:]), expected_income_precision['Estimate'], 1e-3, "estimate"
    #yield check_same, rslt.tvalues[-1:], expected_income_precision['zvalue'], 0.1, "z-score"
    yield check_same, rslt.pvalues[-1:], expected_income_precision['Pr(>|z|)'], 1e-3, "p-values"


def test_methylation_coefficients():
    model = "methylation ~ gender + CpG"
    Z = patsy.dmatrix("~ age", methylation)

    mod = Beta.from_formula(model, methylation, Z=Z, link_phi=sm.families.links.identity())
    rslt = mod.fit()
    yield check_same, rslt.params[:-2], expected_methylation_mean['Estimate'], 1e-2, "estimates"
    yield check_same, rslt.tvalues[:-2], expected_methylation_mean['zvalue'], 0.1, "z-scores"
    yield check_same, rslt.pvalues[:-2], expected_methylation_mean['Pr(>|z|)'], 1e-2, "p-values"

def test_methylation_precision():
    model = "methylation ~ gender + CpG"
    Z = patsy.dmatrix("~ age", methylation)

    mod = Beta.from_formula(model, methylation, Z=Z, link_phi=sm.families.links.identity())
    rslt = mod.fit()
    #yield check_same, sm.families.links.logit()(rslt.params[-2:]), expected_methylation_precision['Estimate'], 1e-3, "estimate"
    #yield check_same, rslt.tvalues[-2:], expected_methylation_precision['zvalue'], 0.1, "z-score"

