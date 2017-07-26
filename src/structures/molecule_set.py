from collections import Counter

from parameters import Parameters, ParameterError
from pte import periodic_table
from structures.molecule import Molecule


class MoleculeSet:
    def __init__(self, molecules):
        self._molecules = list(molecules)

    def __len__(self):
        return len(self._molecules)

    def __getitem__(self, item):
        return self._molecules[item]

    @classmethod
    def load_from_file(cls, filename):
        molecules = []
        molecule_names = set()
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

        return MoleculeSet(molecules)

    def stats(self, classifier):
        atom_types = Counter()
        atom_types_in_molecules = Counter()
        for molecule in self:
            molecule_classes = [(atom.element.symbol, classifier.get_type(molecule, atom)) for atom in molecule]

            atom_types += Counter(molecule_classes)
            atom_types_in_molecules += Counter(set(molecule_classes))

        print('Set statistics')
        print('Molecules: {} Atoms: {} Atom types: {}'.format(len(self), sum(atom_types.values()), len(atom_types)))

        print('Element   Type   # atoms   # molecules')
        sorted_keys = sorted(atom_types.keys(), key=lambda k: (periodic_table[k[0]].number, k[1]))

        for c in sorted_keys:
            element, atom_type = c
            at = '{}_{}'.format(classifier.string, atom_type) if classifier.string != 'plain' else '*'
            print('{:>3s} {:>10s} {:>9d} {:>13d}'.format(element, at, atom_types[c], atom_types_in_molecules[c]))

    def assign_atom_types(self, parameters: Parameters = None):
        if parameters is None:
            return

        for molecule in self:
            for atom in molecule:
                for parameter in parameters.atom:
                    if parameters.atom.matches(parameter, molecule, atom):
                        atom.atom_type = (parameter.element, parameter.classifier, parameter.atom_type)
                        break
                else:
                    raise ParameterError('No suitable parameter found for {}'.format(atom))
