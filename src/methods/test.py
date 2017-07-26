import numpy as np

from charge_method import ChargeMethod


class TestChargeMethod(ChargeMethod):
    COMMON_PARAMETERS = 'kappa'.split()
    ATOM_PARAMETERS = 'A B'.split()

    def initialize(self):
        self.parameters.load_from_file('../data/eem.json')

    def calculate_charges(self, molecule):
        return np.fromiter((atom.formal_charge for atom in molecule), np.float32, len(molecule))
