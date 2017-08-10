import numpy as np

from charge_method import ChargeMethodSkeleton
from options import CommandLineOption


class ChargeMethod(ChargeMethodSkeleton):
    NAME = 'test'

    OPTIONS = [CommandLineOption(name='par_file', help='Parameter file', type=int, default=0),
               CommandLineOption(name='grr', help='Another option', type=float, default=-4)]
    COMMON_PARAMETERS = 'kappa'.split()
    ATOM_PARAMETERS = 'A B'.split()

    def initialize(self, options):
        self.parameters.load_from_file('../data/eem.json')

    def calculate_charges(self, molecule):
        return np.fromiter((atom.formal_charge for atom in molecule), np.float_, len(molecule))
