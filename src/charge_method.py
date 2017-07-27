import abc
import pkgutil
from typing import Dict

import numpy as np

from parameters import Parameters
from structures.molecule import Molecule


class ChargeMethodSkeleton(abc.ABC):
    NAME = '<name>'
    FULL_NAME = '<full name>'
    PUBLICATION = '<doi>'

    OPTIONS = []
    COMMON_PARAMETERS = []
    ATOM_PARAMETERS = []

    def __init__(self):
        self._parameters = Parameters(self.COMMON_PARAMETERS, self.ATOM_PARAMETERS)

    @property
    def parameters(self):
        return self._parameters

    @abc.abstractmethod
    def initialize(self, options: Dict):
        pass

    @abc.abstractmethod
    def calculate_charges(self, molecule: Molecule) -> np.ndarray:
        pass


def get_charge_methods():
    return list(m.name for m in pkgutil.iter_modules(['methods']))
