from typing import Dict

import numpy as np

from charge_method import ChargeMethodSkeleton
from options import CommandLineOption
from structures.molecule import Molecule


class ChargeMethod(ChargeMethodSkeleton):
    NAME = 'eem'
    FULL_NAME = 'Electronegativity Equalization Method'
    PUBLICATION = '10.1021/ja00275a013'

    OPTIONS = [
        CommandLineOption(name='par_file', help='File with EEM parameters', type=str, default='../data/eem.json')]

    COMMON_PARAMETERS = ['kappa']
    ATOM_PARAMETERS = ['A', 'B']

    def __init__(self):
        super().__init__()

    def initialize(self, options: Dict):
        self.parameters.load_from_file(options['par_file'])

    def calculate_charges(self, molecule: Molecule):
        np.seterr(divide='ignore')

        n = len(molecule.atoms)
        matrix = np.empty((n + 1, n + 1), dtype=np.float_)
        vector = np.empty(n + 1, dtype=np.float_)

        matrix[:n, :n] = self.parameters.common['kappa'] / molecule.distance_matrix
        for i, atom_i in enumerate(molecule.atoms):
            matrix[i, i] = self.parameters.atom['B'](atom_i)
            vector[i] = - self.parameters.atom['A'](atom_i)

        matrix[n, :] = 1.0
        matrix[:, n] = 1.0
        matrix[n, n] = 0.0
        vector[n] = molecule.formal_charge

        try:
            return np.linalg.solve(matrix, vector)[:-1]
        except np.linalg.LinAlgError:
            return np.full(len(molecule), np.nan, dtype=np.float_)
