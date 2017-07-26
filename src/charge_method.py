import abc

import numpy as np

from parameters import Parameters
from structures.molecule import Molecule


class ChargeMethod(abc.ABC):
    NAME = '<name>'
    PUBLICATION = '<doi>'

    COMMON_PARAMETERS = []
    ATOM_PARAMETERS = []

    def __init__(self):
        self._parameters = Parameters(self.COMMON_PARAMETERS, self.ATOM_PARAMETERS)

    @property
    def parameters(self):
        return self._parameters

    @abc.abstractmethod
    def initialize(self):
        pass

    @abc.abstractmethod
    def calculate_charges(self, molecule: Molecule) -> np.ndarray:
        pass
