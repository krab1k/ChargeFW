import sys
from collections import Counter, defaultdict
from typing import List

from classifier import Classifier, classifiers
from pte import periodic_table
from structures.molecule import Molecule


class MoleculeSet:
    def __init__(self, molecules) -> None:
        self._molecules: List[Molecule] = list(molecules)
        self._atom_types: defaultdict = defaultdict(list)

    def __len__(self):
        return len(self._molecules)

    def __getitem__(self, item):
        return self._molecules[item]

    def __str__(self):
        return 'MoleculeSet: {} molecules'.format(len(self))

    @classmethod
    def load_from_file(cls, filename: str):
        molecules = []
        molecule_names = set()
        try:
            with open(filename) as f:
                mol_record = []
                for line in f:
                    if line.strip() == '$$$$':
                        molecule = Molecule.create_from_mol(mol_record)
                        if molecule.name in molecule_names:
                            raise RuntimeError('Two molecules with the same name! ({})'.format(molecule.name))
                        else:
                            molecule_names.add(molecule.name)
                        molecules.append(molecule)
                        mol_record = []
                        continue

                    mol_record.append(line)
        except IOError:
            print('Cannot open SDF file: {}'.format(filename), file=sys.stderr)
            sys.exit(1)

        return MoleculeSet(molecules)

    def stats(self):
        atom_types = Counter()
        atom_types_in_molecules = Counter()
        for molecule in self:
            molecule_classes = [tuple(atom.atom_type) for atom in molecule]
            atom_types += Counter(molecule_classes)
            atom_types_in_molecules += Counter(set(molecule_classes))

        print('Set statistics')
        print('Molecules: {} Atoms: {} Atom types: {}'.format(len(self), sum(atom_types.values()), len(atom_types)))

        print('Element   Type   # atoms   # molecules')
        sorted_keys = sorted(atom_types.keys(), key=lambda k: (periodic_table[k[0]].number, k[1], k[2]))

        for c in sorted_keys:
            element, classifier, atom_type = c
            at = '{}_{}'.format(classifiers[classifier].string, atom_type) \
                if classifiers[classifier].string != 'plain' else '*'
            print('{:>3s} {:>10s} {:>9d} {:>13d}'.format(element, at, atom_types[c], atom_types_in_molecules[c]))

    def assign_atom_types(self, classifier: Classifier):
        self._atom_types.clear()
        for i, molecule in enumerate(self):
            for j, atom in enumerate(molecule):
                atom.atom_type = atom.element.symbol, *classifier.get_type(molecule, atom)
                self._atom_types[atom.atom_type].append((i, j))

    @property
    def atom_types(self):
        return self._atom_types
