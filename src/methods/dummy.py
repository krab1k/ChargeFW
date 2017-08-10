import numpy as np

from charge_method import ChargeMethodSkeleton


class ChargeMethod(ChargeMethodSkeleton):
    NAME = 'dummy'
    FULL_NAME = 'Dummy method, outputs zeros'

    def initialize(self, options):
        pass

    def calculate_charges(self, molecule):
        np.full(len(molecule), 0.0, dtype=np.float_)