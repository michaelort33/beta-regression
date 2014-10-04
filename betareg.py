# -*- coding: utf-8 -*-

u"""
Beta regression for modeling rates and proportions.

References
----------
Grün, Bettina, Ioannis Kosmidis, and Achim Zeileis. Extended beta regression in R: Shaken, stirred, mixed, and partitioned. No. 2011-22. Working Papers in Economics and Statistics, 2011.

Smithson, Michael, and Jay Verkuilen. "A better lemon squeezer? Maximum-likelihood regression with beta-distributed dependent variables." Psychological methods 11.1 (2006): 54.
"""
import numpy as np
from scipy.special import gammaln as lgamma
from statsmodels.base.model import GenericLikelihoodModel
from statsmodels.api import GLM
from statsmodels.genmod.families import Binomial
import statsmodels.api as sm
import pandas as pd

# this is only need while #2024 is open.
class Logit(sm.families.links.Logit):
    """Logit tranform that won't overflow with large numbers."""
    def inverse(self, z):
        return 1 / (1. + np.exp(-z))

_init_example = """

"""

class Beta(GenericLikelihoodModel):

    """Beta Regression.

    This implementation uses $\phi\$ as a precision parameter equal to
    `a + b` from the Beta parameters.
    """

    def __init__(self, endog, exog, Z=None, link=Logit(),
            link_phi=sm.families.links.Log(), **kwds):
        """
        Parameters
        ----------
        endog : array-like
            1d array of endogenous values (i.e. responses, outcomes,
            dependent variables, or 'Y' values).
        exog : array-like
            2d array of exogeneous values (i.e. covariates, predictors,
            independent variables, regressors, or 'X' values). A nobs x k
            array where `nobs` is the number of observations and `k` is
            the number of regressors. An intercept is not included by
            default and should be added by the user. See
            `statsmodels.tools.add_constant`.
        Z : array-like
            2d array of variables for the precision phi.
        link : link
            Any link in sm.families.links for `exog`
        link_phi : link
            Any link in sm.families.links for `Z`

        Examples
        --------
        {example}
        """.format(example=_init_example)

        assert np.all((0 < endog) & (endog < 1))

        super(Beta, self).__init__(endog, exog, **kwds)
        self.link = link
        self.link_phi = link_phi
        
        if Z is None:
            self.Z = np.ones((self.endog.shape[0], 1), dtype='f')
        else:
            self.Z = np.asarray(Z)
            assert len(self.Z) == len(self.endog)

    def nloglikeobs(self, params):
        """
        Negative log-likelihood.

        Parameters
        ----------

        params : np.ndarray
            Parameter estimates
        """
        return -self._ll_br(self.endog, self.exog, self.Z, params)

    def fit(self, start_params=None, maxiter=100000, maxfun=5000, disp=False,
            method='bfgs', **kwds):
        """
        Fit the model.

        Parameters
        ----------
        start_params : array-like
            A vector of starting values for the regression
            coefficients.  If None, a default is chosen.
        maxiter : integer
            The maximum number of iterations
        disp : bool
            Show convergence stats.
        method : str
            The optimization method to use.
        """

        if start_params is None:
            start_params = GLM(self.endog, self.exog, family=Binomial()
                              ).fit(disp=False).params
            start_params = np.append(start_params, [0.5] * self.Z.shape[1])

        return super(Beta, self).fit(start_params=start_params,
                                        maxiter=maxiter, maxfun=maxfun,
                                        method=method, disp=disp, **kwds)

    def _ll_br(self, y, X, Z, params):
        nz = self.Z.shape[1]

        Xparams = params[:-nz]
        Zparams = params[-nz:]

        mu = self.link.inverse(np.dot(X, Xparams))
        phi = self.link_phi.inverse(np.dot(Z, Zparams))

        if np.any(phi <= np.finfo(float).eps): return np.array(-np.inf)

        ll = lgamma(phi) - lgamma(mu * phi) - lgamma((1 - mu) * phi) \
                + (mu * phi - 1) * np.log(y) + (((1 - mu) * phi) - 1) \
                * np.log(1 - y)

        return ll

if __name__ == "__main__":

    import patsy
    dat = pd.read_table('gasoline.txt')
    Z = patsy.dmatrix('~ temp', dat, return_type='dataframe')
    # using other precison params with
    m = Beta.from_formula('iyield ~ C(batch, Treatment(10)) + temp', dat,
            Z=Z, link_phi=sm.families.links.identity())
    print m.fit().summary()

    fex = pd.read_csv('foodexpenditure.csv')
    m = Beta.from_formula(' I(food/income) ~ income + persons', fex)
    print m.fit().summary()
    #print GLM.from_formula('iyield ~ C(batch) + temp', dat, family=Binomial()).fit().summary()

    dev = pd.read_csv('methylation-test.csv')
    dev['methylation'] = sm.families.links.Logit().inverse(dev['methylation'])
    m = Beta.from_formula('methylation ~ age + gender', dev,
            link_phi=sm.families.links.identity())
    print m.fit().summary()
