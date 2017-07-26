import sys

import numpy as np

from charge_method import ChargeMethod
from parameters import ParameterError


class EEMChargeMethod(ChargeMethod):
    NAME = 'eem'

    COMMON_PARAMETERS = ['kappa']
    ATOM_PARAMETERS = ['A', 'B']

    def __init__(self):
        super().__init__()

    def initialize(self):

        self.parameters.load_from_file('../data/eem.json')

    def calculate_charges(self, molecule):

        n = len(molecule.atoms)
        matrix = np.empty((n + 1, n + 1), dtype=np.float32)
        vector = np.empty(n + 1, dtype=np.float32)

        # Fill rhs vector
        for i, atom_i in enumerate(molecule.atoms):
            try:
                vector[i] = - self.parameters.atom['A'](molecule, atom_i)
            except ParameterError as error:
                print(error, file=sys.stderr)
                return None

        # Total charge
        vector[n] = molecule.formal_charge

        # Fill the EEM matrix
        for atom_i in molecule.atoms:
            i = atom_i.index
            for atom_j in molecule.atoms[i:]:
                j = atom_j.index
                if i == j:
                    # No ValueError exception can occur here since the previous try would catch it
                    matrix[i, i] = self.parameters.atom['B'](molecule, atom_i)
                else:
                    matrix[i, j] = matrix[j, i] = self.parameters.common['kappa'] / molecule.distance_matrix[i, j]

        matrix[n, :] = 1.0
        matrix[:, n] = 1.0
        matrix[n, n] = 0.0

        try:
            return np.linalg.solve(matrix, vector)[:-1]
        except np.linalg.LinAlgError:
            print('Cannot compute charges by EEM', file=sys.stderr)
            return None
