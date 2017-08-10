import numpy as np

from charge_method import ChargeMethodSkeleton


class ChargeMethod(ChargeMethodSkeleton):
    NAME = 'formal'
    FULL_NAME = 'Formal charges'

    def initialize(self, options):
        pass

    def calculate_charges(self, molecule):
        return np.fromiter((atom.formal_charge for atom in molecule), dtype=np.float_, count=len(molecule))
