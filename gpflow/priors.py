# Copyright 2016 Valentine Svensson, James Hensman, alexggmatthews
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import tensorflow as tf
import numpy as np

from . import logdensities
from . import settings

from .params import Parameterized
from .core.base import IPrior


class Prior(Parameterized, IPrior):  # pylint: disable=W0223
    pass


class Exponential(Prior):
    """
    Exponential distribution.

    Support: [0, inf)
    """

    def __init__(self, rate):
        """
        :param float rate: Rate parameter (inverse scale) (rate > 0)
        """
        Prior.__init__(self)
        self.rate = np.atleast_1d(np.array(rate, settings.float_type))
        if rate <= 0:  # pragma: no cover
            raise ValueError("The rate parameter has to be positive.")

    def logp(self, x):
        scale = 1 / self.rate
        return tf.reduce_sum(logdensities.exponential(x, scale))

    def sample(self, shape=(1,)):
        return np.random.exponential(scale=1 / self.rate, size=shape)

    def __str__(self):
        return "Exp({})".format(self.rate)


class Gaussian(Prior):
    def __init__(self, mu, var):
        Prior.__init__(self)
        self.mu = np.atleast_1d(np.array(mu, settings.float_type))
        self.var = np.atleast_1d(np.array(var, settings.float_type))

    def logp(self, x):
        return tf.reduce_sum(logdensities.gaussian(x, self.mu, self.var))

    def sample(self, shape=(1,)):
        return self.mu + np.sqrt(self.var) * np.random.randn(*shape)

    def __str__(self):
        return "N({},{})".format(self.mu, self.var)


class LogNormal(Prior):
    def __init__(self, mu, var):
        Prior.__init__(self)
        self.mu = np.atleast_1d(np.array(mu, settings.float_type))
        self.var = np.atleast_1d(np.array(var, settings.float_type))

    def logp(self, x):
        return tf.reduce_sum(logdensities.lognormal(x, self.mu, self.var))

    def sample(self, shape=(1,)):
        return np.exp(self.mu + np.sqrt(self.var) * np.random.randn(*shape))

    def __str__(self):
        return "logN({},{})".format(self.mu, self.var)


class Gamma(Prior):
    def __init__(self, shape=None, scale=None, mu=None, var=None):
        Prior.__init__(self)
        if mu is not None and var is not None:
            assert shape is None and scale is None, \
                "Cannot provide both shape/scale and mean/var"
            shape = mu ** 2 / var
            scale = var / mu
        self.shape = np.atleast_1d(np.array(shape, settings.float_type))
        self.scale = np.atleast_1d(np.array(scale, settings.float_type))

    def logp(self, x):
        return tf.reduce_sum(logdensities.gamma(x, self.shape, self.scale))

    def sample(self, shape=(1,)):
        return np.random.gamma(self.shape, self.scale, size=shape)

    def __str__(self):
        return "Ga({},{})".format(self.shape, self.scale)


class InverseGamma(Prior):
    def __init__(self, shape=None, scale=None, mu=None, var=None):
        Prior.__init__(self)
        if mu is not None and var is not None:
            assert shape is None and scale is None, \
                "Cannot provide both shape/scale and mean/var"
            shape = 2.0 + mu ** 2 / var
            scale = mu * (1.0 + mu ** 2 / var)
        self.shape = np.atleast_1d(np.array(shape, settings.float_type))
        self.scale = np.atleast_1d(np.array(scale, settings.float_type))

    def logp(self, x):
        return tf.reduce_sum(densities.inverse_gamma(self.shape, self.scale, x))

    def sample(self, shape=(1,)):
        return 1.0 / np.random.gamma(self.shape, 1.0 / self.scale, size=shape)

    def __str__(self):
        return "InvGa("+str(self.shape) + "," + str(self.scale) + ")"


class Laplace(Prior):
    def __init__(self, mu, sigma):
        Prior.__init__(self)
        self.mu = np.atleast_1d(np.array(mu, settings.float_type))
        self.sigma = np.atleast_1d(np.array(sigma, settings.float_type))

    def logp(self, x):
        return tf.reduce_sum(logdensities.laplace(x, self.mu, self.sigma))

    def sample(self, shape=(1,)):
        return np.random.laplace(self.mu, self.sigma, size=shape)

    def __str__(self):
        return "Lap.({},{})".format(self.mu, self.sigma)


class Beta(Prior):
    def __init__(self, a, b):
        Prior.__init__(self)
        self.a = np.atleast_1d(np.array(a, settings.float_type))
        self.b = np.atleast_1d(np.array(b, settings.float_type))

    def logp(self, x):
        return tf.reduce_sum(logdensities.beta(x, self.a, self.b))

    def sample(self, shape=(1,)):
        return np.random.beta(self.a, self.b, size=shape)

    def __str__(self):
        return "Beta({},{})".format(self.a, self.b)


class Uniform(Prior):
    def __init__(self, lower=0., upper=1.):
        Prior.__init__(self)
        self.lower, self.upper = lower, upper

    @property
    def log_height(self):
        return - np.log(self.upper - self.lower)

    def logp(self, x):
        return self.log_height * tf.cast(tf.size(x), settings.float_type)

    def sample(self, shape=(1,)):
        return (self.lower +
                (self.upper - self.lower)*np.random.rand(*shape))

    def __str__(self):
        return "U({},{})".format(self.lower, self.upper)

