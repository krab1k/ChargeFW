from collections import namedtuple
from typing import List, Generator

import numpy as np
import scipy.spatial

from pte import periodic_table
from structures.atom import Atom

Bond = namedtuple('Bond', 'atom1 atom2 order'.split())


class Molecule:
    def __init__(self, name: str, atoms: List[Atom], bonds: List[Bond]) -> None:
        self._name: str = name
        self._atoms: List[Atom] = atoms
        self._formal_charge: int = sum(atom.formal_charge for atom in self.atoms)

        n = len(self)
        self._hbo: np.ndarray = np.zeros(n, dtype=np.int8)
        self._connectivity_matrix: np.ndarray = np.zeros((n, n), dtype=np.int8)
        for atom1_idx, atom2_idx, order in bonds:
            order = np.int8(order)
            self._connectivity_matrix[atom1_idx, atom2_idx] = order
            self._connectivity_matrix[atom2_idx, atom1_idx] = order
            self._hbo[atom1_idx] = self._hbo[atom1_idx] if self._hbo[atom1_idx] > order else order
            self._hbo[atom2_idx] = self._hbo[atom2_idx] if self._hbo[atom2_idx] > order else order

        atom_coords = np.array([atom.coordinates for atom in self.atoms])
        self._distance_matrix: np.ndarray = scipy.spatial.distance.cdist(atom_coords, atom_coords)

    def __getitem__(self, item):
        return self.atoms[item]

    def __len__(self):
        return len(self.atoms)

    def __repr__(self):
        return 'Molecule({}, {!r},...)'.format(self.name, self.atoms)

    def __str__(self):
        return 'Molecule({}, natoms={})'.format(self.name, len(self))

    @property
    def name(self):
        return self._name

    @property
    def atoms(self):
        return self._atoms

    @property
    def distance_matrix(self):
        return self._distance_matrix

    def distance(self, atom1: Atom, atom2: Atom, units: str = 'angstrom') -> float:
        dist = self._distance_matrix[atom1.index, atom2.index]
        if units == 'au':
            dist *= 1.8897259885789
        return dist

    @property
    def bonds(self):
        for i, atom_i in enumerate(self.atoms):
            for j, atom_j in enumerate(self.atoms[i:]):
                if self._connectivity_matrix[i, j] > 0:
                    yield Bond(atom_i, atom_j, self._connectivity_matrix[i, j])

    @property
    def formal_charge(self) -> int:
        return self._formal_charge

    def highest_bond_order(self, atom) -> np.int:
        return int(self._hbo[atom.index])

    def bonded_atoms(self, atom: Atom) -> Generator[Atom, None, None]:
        line = self._connectivity_matrix[atom.index]
        return (self.atoms[i] for i, order in enumerate(line) if order > 0)

    def is_bonded(self, atom1: Atom, atom2: Atom):
        return self._connectivity_matrix[atom1.index, atom2.index] > 0

    @classmethod
    def create_from_mol(cls, mol_record):

        def read_mol_v2000(data):
            counts_line = data[3]

            # format: aaabbblllfffcccsssxxxrrrpppiiimmmvvvvvv
            # aaa - number of atoms
            # bbb - number of bonds
            # vvvvvv - version (either V2000 or V3000)
            # the rest is not used

            atom_count = int(counts_line[0:3])
            bond_count = int(counts_line[3:6])

            # format: xxxxx.xxxxyyyyy.yyyyzzzzz.zzzz aaaddcccssshhhbbbvvvHHHrrriiimmmnnneee
            # x, y, z - coordinates
            # aaa - atom symbol
            # the rest is not used

            symbols = []
            coordinates = []
            for i in range(4, 4 + atom_count):
                line = data[i]
                *coords, symbol = float(line[0:10]), float(line[10:20]), float(line[20:30]), str(line[30:33])
                symbols.append(symbol.strip())
                coordinates.append(coords)

            pairs = []
            charge_lines = (line[9:] for line in data[4 + atom_count + bond_count:] if line.startswith('M  CHG'))

            for line in charge_lines:
                pairs += zip(line.split()[::2], line.split()[1::2])

            charges = [0] * atom_count
            for atom_no, charge in pairs:
                charges[int(atom_no) - 1] = int(charge)

            atom_list = [Atom(periodic_table[symbol], index, coords, charge)
                         for symbol, index, coords, charge in zip(symbols, range(len(symbols)), coordinates, charges)]

            bond_list = []
            for i in range(4 + atom_count, 4 + atom_count + bond_count):
                line = data[i]
                atom1_idx, atom2_idx, order = int(line[0:3]), int(line[3:6]), int(line[6:9])
                bond_list.append(Bond(atom1_idx - 1, atom2_idx - 1, order))

            return atom_list, bond_list

        name = mol_record[0].strip()
        version = mol_record[3][33:39].strip()
        if version == 'V2000':
            atoms, bonds = read_mol_v2000(mol_record)
        elif version == 'V3000':
            raise NotImplemented('Cannot read V3000 MOL yet!')
        else:
            raise RuntimeError('Incorrect version of MOL record: {}'.format(version))

        return Molecule(name, atoms, bonds)
