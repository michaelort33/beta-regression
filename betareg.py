import numpy as np
from scipy.special import gammaln as lgamma
from statsmodels.base.model import GenericLikelihoodModel
from statsmodels.api import GLM
from statsmodels.genmod.families import Binomial
import statsmodels.api as sm

#see http://cran.r-project.org/web/packages/betareg/vignettes/betareg-ext.pdf
class Logit(sm.families.links.Logit):
    def inverse(self, z):
        return 1 / (1. + np.exp(-z))

class BetaReg(GenericLikelihoodModel):
    def __init__(self, endog, exog, Z=None, link=Logit(),
            link_phi=sm.families.links.Log(), **kwds):

        super(BetaReg, self).__init__(endog, exog, **kwds)
        self.link = link
        self.link_phi = link_phi
        # how to set default Z?
        if Z is None:
            self.Z = np.ones((self.endog.shape[0], 1), dtype='f')
        else:
            self.Z = np.asarray(Z)
            assert len(self.Z) == len(self.endog)

    def nloglikeobs(self, params):
        return -self._ll_br(self.endog, self.exog, self.Z, params)

    def fit(self, start_params=None, maxiter=1000000, maxfun=50000,
            method='bfgs', **kwds):
        if start_params is None:
            start_params = GLM(self.endog, self.exog, family=Binomial()).fit().params
            start_params = np.append(start_params, [0.5] * self.Z.shape[1])
            #start_params = np.append(np.zeros(self.exog.shape[1]), 0.5)
        #self.exog[0] = np.mean(self.endog)

        return super(BetaReg, self).fit(start_params=start_params,
                                             maxiter=maxiter,
                                             maxfun=maxfun,
                                             method=method,
                                             **kwds)
    def _ll_br(self, y, X, Z, params):
        nz = self.Z.shape[1]

        Xparams = params[:-nz]
        Zparams = params[-nz:]

        mu = self.link.inverse(np.dot(X, Xparams))
        phi = self.link_phi.inverse(np.dot(Z, Zparams))

        ll = lgamma(phi) - lgamma(mu * phi) - lgamma((1 - mu) * phi) \
                + (mu * phi - 1) * np.log(y) + (((1 - mu) * phi) - 1) * np.log(1 - y)
        return ll

if __name__ == "__main__":

    import pandas as pd
    dat = pd.read_table('gasoline.txt')
    m = BetaReg.from_formula('iyield ~ C(batch, Treatment(10)) + temp', dat)

    fex = pd.read_csv('foodexpenditure.csv')
    m = BetaReg.from_formula(' I(food/income) ~ income + persons', fex)
    print m.fit().summary()
    #print GLM.from_formula('iyield ~ C(batch) + temp', dat, family=Binomial()).fit().summary()
