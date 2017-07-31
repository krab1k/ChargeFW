import numpy as np

from charge_method import ChargeMethodSkeleton


class ChargeMethod(ChargeMethodSkeleton):
    NAME = 'dummy'
    FULL_NAME = 'Dummy method, outputs zeros'

    def initialize(self, options):
        pass

    def calculate_charges(self, molecule):
        return np.fromiter((0.0 for _ in molecule), dtype=np.float32, count=len(molecule))
