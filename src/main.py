import numpy as np

from methods.eem import EEMChargeMethod
from parameters import Parameters
from structures.molecule_set import MoleculeSet


def main():
    molecules = MoleculeSet.load_from_file('/home/krab1k/Research/NEEMP/examples/set01.sdf')

    t = EEMChargeMethod()
    t.initialize()
    np.set_printoptions(precision=3, suppress=True)

    p = Parameters(['kappa'], 'A B'.split())
    p.load_from_file('../data/eem.json')

    molecules.assign_atom_types(p)


if __name__ == '__main__':
    main()
